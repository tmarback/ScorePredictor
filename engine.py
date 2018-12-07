from statistics import mean
from engine_helpers import *
import numpy as np
from scipy.misc import logsumexp

# Module that handles probability calculations

# Represents an anime in the database.
#
# No fields may be None, except episodeN if type is not TV.
class anime:

    def __init__( self ):

        self.showType = None # The type of show (TV, Movie, OVA, etc) [string]
        self.source = None # The source of the show (Manga, Original, etc) [string]
        self.episodeN = None # The episode count (only when type is TV, otherwise should be None) [int]
        self.rating = None # The rating of the show (PG, M, etc) [string
        self.studio = [] # The studios that made the show [list of string]
        self.genre = [] # The genres of the show [list of string]
        self.duration = None # The duration of each episode in minutes [int]
        self.start_year = None # The year when the show started airing [int]
    
    def __init__( self, sType=None, sSource=None, nEpisode=None, sRating=None, lStudio=None, lGenre=None, nDuration=None, nStart=None ):

        self.showType = sType # The type of show (TV, Movie, OVA, etc) [string]
        self.source = sSource # The source of the show (Manga, Original, etc) [string]
        self.episodeN = nEpisode # The episode count (only when type is TV, otherwise should be None) [int]
        self.rating = sRating # The rating of the show (PG, M, etc) [string]
        if lStudio is None:
            self.studio = [] # The studios that made the show [list of string]
        else:
            self.studio = lStudio
        if lGenre is None:
            self.genre = [] # The genres of the show [list of string]
        else:
            self.genre = lGenre
        self.duration = nDuration # The duration of each episode in minutes [int]
        self.start_year = nStart # The year when the show started airing [int]

    def getTags( self ):

        tags = []
        tags.append( 'type:' + self.showType )
        tags.append( 'source:' + self.source )
        tags.append( 'episodeN:' + str( self.episodeN ) )
        tags.append( 'rating:' + str( self.rating ) )
        for s in self.studio:
            
            tags.append( 'studio:' + s )

        for g in self.genre:
            
            tags.append( 'genre:' + g )

        tags.append( 'duration:' + str( self.duration ) )
        tags.append( 'start_year:' + str( self.start_year ) )

        return tags

    def validate( self ):
        
        assert self.showType is not None
        assert self.source is not None
        assert self.episodeN is not None if self.showType == 'TV' else self.episodeN is None
        assert self.rating is not None
        assert self.studio
        assert self.genre
        assert self.duration is not None
        assert self.start_year is not None

animes = None
animeData = None
tags = None
users = None

animeRatings = None
tagRatings = None

PY_anime = None
PR_anime = None
PY_anime_user = None

PY_tag = None
PR_tag = None
PY_tag_user = None

# Initializes the predictive engine.
# Must be called before calling any other function.
#
# Parameters:
# - animeList: The animes in the database. Must be a map where the key is the title and the value is an instance of the anime class.
# - scores: The scores given to each anime by each user. Must be a list of tuples (username [string], title [string], score [int]).
#           Score must be in the range [1,10].
def initialize( animeList, scores ):

    print( 'Validating data' )

    # Validate all anime entries
    for title, a in animeList.items():

        assert title
        assert a
        a.validate()

    # Map to array indices
    global animes
    global animeData
    animes = {}
    animeData = []
    i = 0
    for anime, data in animeList.items():

        animes[anime] = i
        animeData.append( data )
        i += 1

    print( 'Parsing user lists' )

    # Collapse score list into maps of users to scores
    userAnimeLists = {}
    while scores:

        username, title, score = scores.pop()

        assert username
        assert title
        assert minScore <= score <= maxScore

        if username not in userAnimeLists:
            userAnimeLists[username] = {}

        userAnimeLists[username][title] = score

    # Map users to array indices
    global users
    users = {}
    i = 0
    for username in userAnimeLists:

      users[username] = i
      i += 1

    # Convert anime ratings to array
    global animeRatings
    animeRatings = np.full( ( len( users ), len( animes ) ), -1 )
    for user in users:

        for anime in userAnimeLists[user]:

            animeRatings[users[user]][animes[anime]] = userAnimeLists[user][anime] - minScore
    
    print( 'Calculating per-anime probabilities' )

    # Calculate PY and PR for animes in the database
    global PY_anime
    global PR_anime
    PY_anime, PR_anime = runEM( animeRatings )

    # Precompute PY for each user
    global PY_anime_user
    PY_anime_user = np.zeros( ( PY_anime.size, len( users ) ) )
    for i in range( PY_anime.size ):

        PY_anime_user[i] = vProbY( PY_anime, PR_anime, animeRatings, i )

    assert aTolerantEquals( logsumexp( PY_anime_user, axis = 1 ), 0.0 )

    print( 'Parsing tags' )

    # Obtain tag set
    tagSet = set()
    for title, a in animeList.items():

        for tag in a.getTags():

            tagSet.add( tag )

    # Map tags to array indices
    global tags
    tags = {}
    i = 0
    for tag in tagSet:

        tags[tag] = i
        i += 1

    # Calculate average tag scores for each user
    global tagRatings
    tagRatings = np.full( ( len( users ), len( tags ) ), -1 )
    for user in userAnimeLists:

        tagScore = {}
        tagCount = {}

        for title, score in userAnimeLists[user].items():

            if score is not None:
                for tag in animeList[title].getTags():

                    if tag not in tagScore:
                        tagScore[tag] = 0
                        tagCount[tag] = 0
                    tagScore[tag] += score
                    tagCount[tag] += 1

        for tag in tagScore:
            
            tagRatings[users[user]][tags[tag]] = int( round( tagScore[tag]/tagCount[tag] ) )

    print( 'Calculating per-tag probabilities' )
    
    global PY_tag
    global PR_tag
    PY_tag, PR_tag = runEM( tagRatings )

    # Precompute PY for each user
    global PY_tag_user
    PY_tag_user = np.zeros( ( PY_tag.size, len( users ) ) )
    for i in range( PY_tag.size ):

        PY_tag_user[i] = vProbY( PY_tag, PR_tag, tagRatings, i )

    assert aTolerantEquals( logsumexp( PY_tag_user, axis = 1 ), 0.0 )

    print( 'Engine initialized' )

    return

# Calculates the probability of the given user give the given score to the given show.
#
# Parameters:
# - username: The username of the user to determine. Must be an existing username.
# - score: The score to calculate the probability of. Must be in the range [1,10].
# - title: The title of the show.
# - info: The information of the show, as an instance of the anime class. If None, the engine will use the information given during
#         initialization with a matching title.
#
# Return:
# - The probability [float]. If the username did not match a known user, the score was outside the valid range, or info was None and the title
#   did not match any know show, returns None.
def scoreProb( username, score, title, info=None ):

    if username not in PY_tag_user:
        return None

    if not ( minScore <= score <= maxScore ):
        return None

    if info is None:
        if title not in animes:
            return None
        else:
            info = animes[title]

    return mean([sum( [( PY_tag_user[username][i] * PR_tag[tag][score][i] ) for i in range( len( PY_tag ) )] ) for tag in info.getTags()])

