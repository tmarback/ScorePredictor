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

    ratings = np.equal( r[:,np.newaxis], np.arange( PR.shape[1] )[np.newaxis,:] )
    P = PY + np.sum( PR[ratings] )
    assert P <= 0
    return P

# Vectorized version of logQ
#vLogQ = np.vectorize( logQ, signature = '(),(j,r),(j)->()' )
#
# PY - PY[y] = log P(Y=y)
# PR - PR[y][j][r] = log P(R_j=r|Y=y)
# r - r[t][j] = r^t_j - The user's ratings
# 
# Returns:
# - P[t][y] = log P(Y=y)PROD[P(R=r^t|Y=y)]
def vLogQ( PY, PR, r ):

    ratings = np.equal( r[:,:,np.newaxis], np.arange( PR.shape[2] )[np.newaxis,np.newaxis,:] )
    PR_picked = ratings[:,np.newaxis,:,:] * PR[np.newaxis,:,:,:]
    PR_picked[np.isnan( PR_picked )] = 0 # In case of -inf
    P = PY[np.newaxis,:] + np.sum( PR_picked, axis = ( 2, 3 ) )
    assert np.all( np.less_equal( P, 0 ) )
    return P

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

    qs = vLogQ( PY, PR, r[np.newaxis,:] ) # Calculate log q for each y
    P = logsumexp( qs )
    assert P <= 0
    return P

# Vectorized version of probEvidenceForUser
#vProbEvidenceForUser = np.vectorize( probEvidenceForUser, signature = '(y),(y,j,r),(j)->()' )
#
# Parameters:
# PY - PY[y] = log P(Y=y)
# PR - PR[y][j][r] = log P(Rj=r|Y=y)
# r - r[t][j] = r^t_j - The user's ratings
#
# Returns:
# - P[t] = log P(R=r^t)
def vProbEvidenceForUser( PY, PR, r ):

    qs = vLogQ( PY, PR, r )
    P = logsumexp( qs, axis = 1 )
    assert np.all( np.less_equal( P, 0 ) )
    return P

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

    P = vProbEvidenceForUser( PY, PR, r )
    L = np.sum( P ) / len( r )
    assert L <= 0
    return L

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

    P = logQ( PY[y], PR[y], r ) - probEvidenceForUser( PY, PR, r )
    assert P <= 0

# Vectorized version of probY over t
# (y),(y,j,r),(t,j),()->(t)
#
# Parameters:
# PY - PY[y] = log P(Y=y)
# PR - PR[y][j][r] = log P(Rj=r|Y=y)
# r - r[j] = r^t_j - The user's ratings
#
# Returns:
# - P[t][y] = log P(Y=y|{R=r^t})
def vProbY( PY, PR, r ):

    qs = vLogQ( PY, PR, r )
    pEv = vProbEvidenceForUser( PY, PR, r )
    P = qs - pEv[:,np.newaxis]
    assert np.all( np.less_equal( P, 0 ) )
    return P

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
    pit = np.transpose( vProbY( PY, PR, r ) )
    pi = logsumexp( pit, axis = 1 )
    newPY = np.log( 1 / T ) + pi

    assert np.all( np.less_equal( PY, 0 ) )
    assert not np.any( np.isnan( PY ) )
    assert not np.any( np.isinf( PY ) )
    
    assert not np.any( np.isinf( pit ) )
    assert not np.any( np.isinf( pi ) )
    
    newPR = np.zeros( ( k, n, S ) )
    scores = np.transpose( r )
    unrated = np.equal( scores, -1 )
    s = np.arange( PR.shape[2] )
    match = np.equal( scores[:,:,np.newaxis], s[np.newaxis,np.newaxis,:] )
    notMatch = np.logical_not( np.logical_or( match, unrated[:,:,np.newaxis] ) )
    notMatchFactor = np.zeros( ( n, T, S ) )
    notMatchFactor[notMatch] = -np.inf
    unratedFactor = PR[:,:,np.newaxis,:] * unrated[np.newaxis,:,:,np.newaxis]
    unratedFactor[np.isnan( unratedFactor )] = 0
    A = notMatchFactor[np.newaxis,:,:,:] + unratedFactor
    newPR = logsumexp( pit[:,np.newaxis,:,np.newaxis] + A, axis = 2 )
    newPR -= pi[:,np.newaxis,np.newaxis]

    assert not np.any( np.isnan( newPR ) )
    assert np.all( np.less_equal( newPR, 0 ) )

    return newPY, newPR

# userLists - userLists[t][j] = r^t_j - The ratings of each user
def runEM( userLists ):

    assert np.all( np.logical_or( np.equal( userLists, -1 ), 
            np.logical_and( np.greater_equal( userLists, 0 ), np.less_equal( userLists, maxScore - minScore + 1 ) ) ) )

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

        PY, PR = update( PY, PR, userLists )
        likelihood = logLikelihood( PY, PR, userLists )
        assert likelihood >= oldLikelihood # Ensure likelihood does not decrease
        oldLikelihood = likelihood

        completedSteps = int( ( i + 1 ) * 100 / runs )
        if completedSteps > oldCompletedSteps:
            print( '%d%% complete' % completedSteps )
            oldCompletedSteps = completedSteps

    print( 'Final log-likelihood: %.5f' % oldLikelihood )
    
    # Validate output
    assert tolerantEquals( logsumexp( PY ), 0.0 )
    a = logsumexp( PR, axis = 2 )
    assert np.all( np.less_equal( logsumexp( PR, axis = 2 ), errorTolerance ) )

    return PY, PR
