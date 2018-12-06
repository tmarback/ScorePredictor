# Helper functions for the probability engine.
import math
import random
import numpy as np
from scipy.misc import logsumexp

numUserTypes = 15
maxScore = 10
minScore = 1

minInitialProbFrac = 0.1
maxInitialProbFrac = 1.0 - minInitialProbFrac
random.seed( a = 'OmaeWaMouShindeiru' )

runs = 128

errorTolerance = 0.000000001

# Determines if the given value is equal to the given expected value,
# within tolerance (used to account for rounding errors in floating-point
# values)
def tolerantEquals( val, expected ):

    return ( expected - errorTolerance ) <= val <= ( expected + errorTolerance )

# Determines if the values in the given array are equal to the given expected value,
# within tolerance (used to account for rounding errors in floating-point
# values)
def aTolerantEquals( array, expected ):
 
    return np.all( np.logical_and( np.greater_equal( array, expected - errorTolerance ), np.less_equal( array, expected + errorTolerance ) ) )

# Calculates part of the likelihood (a single value of y)
# of a user's ratings.
# In other words, calculates P(Y=y)PROD[P(R=r|Y=y)]
# 
# Parameters:
# PY - PY = log P(Y=y)
# PR - PR[j][r] = log P(R_j=r|Y=y)
# r - r[j] = r^t_j - The user's ratings
# 
# Returns:
# - log P(Y=y)PROD[P(R=r|Y=y)]
def logQ( PY, PR, r ):

    rated = np.not_equal( r, np.full( r.size, -1 ) )
    rated_j = np.extract( rated, np.arange( 0, r.size ) )
    ratings = np.extract( rated, r )
    return PY + np.sum( PR[rated_j, ratings] )

# Vectorized version of logQ
vLogQ = np.vectorize( logQ, signature = '(),(j,r),(j)->()' )

# Calculates the (log) likelihood of a user's ratings.
# In other words, calculates log P(R=r(t))
#
# Parameters:
# PY - PY[y] = log P(Y=y)
# PR - PR[y][j][r] = log P(Rj=r|Y=y)
# r - r[j] = r^t_j - The user's ratings
#
# Returns:
# - log P(R=r(t))
def probEvidenceForUser( PY, PR, r ):

    qs = vLogQ( PY, PR, r ) # Calculate log q for each y
    return logsumexp( qs )

# Vectorized version of probEvidenceForUser
vProbEvidenceForUser = np.vectorize( probEvidenceForUser, signature = '(y),(y,j,r),(j)->()' )

# Calculates the log-likelihood of the current state.
#
# Parameters:
# PY - PY[y] = log P(Y=y)
# PR - PR[y][j][r] = log P(Rj=r|Y=y) 
# r - r[t][j] = r^t_j - The ratings of each user
#
# Returns:
# - The log-likelihood
def logLikelihood( PY, PR, r ):

    return np.sum( vProbEvidenceForUser( PY, PR, r ) ) / len( r )

# Calculates log P(Y=y|{Rj=rj(t)}) for a specific user t.
#
# Parameters:
# PY - PY[y] = log P(Y=y)
# PR - PR[y][j][r] = log P(Rj=r|Y=y)
# r - r[j] = r^t_j - The user's ratings
# y - The value of y
#
# Returns:
# - log P(Y=y|{Rj=rj(t)})
def probY( PY, PR, r, y ):

    return logQ( PY[y], PR[y], r ) - probEvidenceForUser( PY, PR, r )

# Vectorized version of probY over t
# (y),(y,j,r),(t,j),()->(t)
def vProbY( PY, PR, r, y ):

    return vLogQ( PY[y], PR[y], r ) - vProbEvidenceForUser( PY, PR, r )

# Runs an iteration of the EM algorithm.
#
# Parameters:
# PY - PY[y] = log P(Y=y)
# PR - PR[y][j][r] = log P(Rj=r|Y=y) 
# r - r[t][j] = r^t_j - The ratings of each user
#
# Returns:
# - The updated PY
# - The updated PR
def update( PY, PR, r ):

    T = r.shape[0]
    k, n, S = PR.shape
    pit = np.empty( ( k, T ) )
    for i in range( T ):

        pit[i] = vProbY( PY, PR, r, i )

    pi = logsumexp( pit, axis = 1 )
    newPY = np.log( 1 / T ) + pi
    
    unrated = np.equal( r, -1 )
    newPR = np.zeros( k, n, s )
    for j in range( n ):

        for s in range( s ):
 
            scoreMatch = np.equal( r[:,j], s )
            unrated = np.equal( r[:,j], -1 )
            for i in range( k ):

                newPR[i][j][s] = np.logaddexp( logsumexp( np.extract( scoreMatch, pit[i] ) ), logsumexp( np.extract( unrated, pit[i] ) + PR[i][j][s] ) ) - pi[i]
        
    return newPY, newPR

# userLists - userLists[t][j] = r^t_j - The ratings of each user
def runEM( userLists ):

    # Intialize probability of Y and R
    PY = np.full( numUserTypes, np.log( 1 / numUserTypes ) )
    PR = np.zeros( ( numUserTypes, userLists.shape[1], maxScore - minScore + 1 ) )
    for i in range( PR.shape[0] ):

        for j in range( PR.shape[1] ):

            remaining = 1.0
            for s in range( PR.shape[2] - 1 ):

                p = remaining * random.uniform( minInitialProbFrac, maxInitialProbFrac )
                PR[i][j][s] = p
                remaining -= p

            PR[i][j][PR.shape[2] - 1] = remaining

    PR = np.log( PR )

    # Run EM algorithm
    oldCompletedSteps = 0
    oldLikelihood = logLikelihood( PY, PR, userLists )
    for i in range( runs ):

        print( 'Running iteration %d' % ( i + 1 ) )
        PY, PR = update( PY, PR, userLists )
        likelihood = logLikelihood( PY, PR, userLists )
        assert likelihood >= oldLikelihood # Ensure likelihood does not decrease
        oldLikelihood = likelihood
        print( 'Iteration completed' )

        completedSteps = ( i + 1 ) * 100 / runs 
        if completedSteps > oldCompletedSteps:
            print( '%d%% complete' % completedSteps )
            oldCompletedSteps = completedSteps

    print( 'Final log-likelihood: %.5f' % oldLikelihood )
    
    # Validate output
    assert tolerantEquals( logsumexp( PY ), 0.0 )
    assert aTolerantEquals( logsumexp( PR, axis = 2 ), 0.0 )

    return PY, PR
