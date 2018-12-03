# Helper functions for the probability engine.

import math
import random

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
# values),
def tolerantEquals( val, expected ):

    return ( expected - errorTolerance ) <= val <= ( expected + errorTolerance )

# Calculates part of the likelihood (a single value of y)
# of a user's ratings.
# In other words, calculates P(Y=y)PROD[P(R=r|Y=y)]
# 
# Parameters:
# PY - PY[y] = P(Y=y)
# PR - PR[j][r][y] = P(Rj=r|Y=y) (j is the title)
# y - The value of Y
# r - The user's ratings (map from title to rating)
# 
# Returns:
# - P(Y=y)PROD[P(R=r|Y=y)]
def probEvidenceForUserPartial( PY, PR, y, r ):

    P = PY[y]
    for j in r:

        if r[j] != None: # Student watched this movie
            P *= PR[j][r[j]][y]

    return P

# Calculates the likelihood of a user's ratings.
# In other words, calculates P(R=r(t))
#
# Parameters:
# PY - PY[y] = P(Y=y)
# PR - PR[j][r][y] = P(Rj=r|Y=y) (j is the title)
# r - The user's ratings (map from title to rating)
#
# Returns:
# - P(R=r(t))
def probEvidenceForUser( PY, PR, r ):

    P = 0
    for i in range( len( PY ) ):

        P += probEvidenceForUserPartial( PY, PR, i, r )
        
    return P

# Calculates the log-likelihood of the current state.
#
# Parameters:
# PY - PY[y] = P(Y=y)
# PR - PR[j][r][y] = P(Rj=r|Y=y) (j is the title)
# r - The ratings of each user, where r[t] is the map
#     of ratings for student t (map from title to rating)
#
# Returns:
# - The log-likelihood
def logLikelihood( PY, PR, r ):

    L = 0.0
    for t in r:

        L += math.log( probEvidenceForUser( PY, PR, r[t] ) )

    return L / len( r )

# Calculates P(Y=y|{Rj=rj(t)}) for a specific user t.
#
# Parameters:
# PY - PY[y] = P(Y=y)
# PR - PR[j][r][y] = P(Rj=r|Y=y) (j is the title)
# r - The user's ratings (map from title to rating)
# y - The value of y
#
# Returns:
# - P(Y=y|{Rj=rj(t)})
def probY( PY, PR, r, y ):

    return probEvidenceForUserPartial( PY, PR, y, r ) / probEvidenceForUser( PY, PR, r )

# Runs an iteration of the EM algorithm.
#
# Parameters:
# PY - PY[y] = P(Y=y)
# PR - PR[j][r][y] = P(Rj=r|Y=y) (j is the title)
# r - The ratings of each user, where r[t] is the map
#     of ratings for the t-th user (map from title to rating)
#
# Returns:
# - The updated PY
# - The updated PR
def update( PY, PR, r ):

    T = len( r )
    newPY = [0] * len( PY )
    newPR = {t:{r:[0 for i in PR[t][r]] for r in PR[t]} for t in PR}
    for i in range( len( PY ) ):

        pit = {rt:probY( PY, PR, r[rt], i ) for rt in r}

        total = 0
        for p in pit:
      
            total += pit[p]

        newPY[i] = total/T

        for j in PR:

            for score in PR[j]:

                totalRated = 0
                totalUnrated = 0
                for t in r:

                    if r[t][j] != None:
                        totalRated += pit[t] if r[t][j] == score else 0
                    else:
                        totalUnrated += pit[t] * PR[j][score][i]

                newPR[j][score][i] = ( totalRated + totalUnrated ) / total

    return newPY, newPR

def runEM( tagList, userLists ):

    # Intialize probability of Y and R
    PY = [1 / numUserTypes for i in range( numUserTypes )]
    PR = {t:{r:[0 for i in range( numUserTypes )] for r in range( minScore, maxScore + 1 )} for t in tagList}
    for t in PR:

        for i in range( numUserTypes ):

            remaining = 1.0
            for r in range( minScore, maxScore ):
                
                PR[t][r][i] = remaining * random.uniform( minInitialProbFrac, maxInitialProbFrac )
                remaining -= PR[t][r][i]

            PR[t][maxScore][i] = remaining

    # Run EM algorithm
    oldLikelihood = logLikelihood( PY, PR, userLists )
    for i in range( runs ):

        PY, PR = update( PY, PR, userLists )
        likelihood = logLikelihood( PY, PR, userLists )
        assert likelihood >= oldLikelihood # Ensure likelihood does not decrease

    # Validate output
    sumPY = 0.0
    for p in PY:

        sumPY += p

    assert tolerantEquals( sumPY, 1.0 )

    for t in PR.values():

        for i in range( len( PY ) ):

            sumPR = 0.0
            for r in t.values():

                sumPR += r[i]

            assert tolerantEquals( sumPR, 1.0 )

    return PY, PR
