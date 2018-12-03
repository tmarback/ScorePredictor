import random
from engine_helpers import *

# Module that handles probability calculations

# Represents an anime in the database.
#
# No fields may be None, except episodeN if type is not TV.
class anime:

    def __init__( self ):

        self.showType = None # The type of show (TV, Movie, OVA, etc) [string]
        self.source = None # The source of the show (Manga, Original, etc) [string]
        self.episodeN = None # The episode count (only when type is TV, otherwise should be None) [int]
        self.rating = None # The rating of the show (PG, M, etc) [string]
        self.studio = [] # The studios that made the show [list of string]
        self.genre = [] # The genres of the show [list of string]
        self.duration = None # The duration of each episode in minutes [int]
        self.start_year = None # The year when the show started airing [int]

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

    # Validate all anime entries
    for title, a in animeList.items():

        assert title
        a.validate()

    # Save to global
    global animes
    animes = animeList

    # Collapse score list into maps of users to scores
    userAnimeLists = {}
    for username, title, score in scores:

        assert username
        assert title
        assert minScore <= score <= maxScore

        if username not in userAnimeLists:
            userAnimeLists[username] = {}

        userAnimeLists[username][title] = score

    # Add unrated shows
    for userList in userAnimeLists.values():

        for title in animeList:

            if title not in userList:
                userList[title] = None

    # Calculate PY and PR for animes in the database
    global PY_anime
    global PR_anime
    PY_anime, PR_anime = runEM( animeList.keys(), userAnimeLists )

    # Precompute PY for each user
    global PY_anime_user
    PY_anime_user = {username:[probY( PY_anime, PR_anime, userAnimeLists[username], i ) for i in range( len( PY_anime ) )] for username in userAnimeLists}
    for PY in PY_anime_user.values():

        assert tolerantEquals( sum( PY ), 1.0 )

    # Obtain tag set
    tags = set()
    for title, a in animeList.items():

        for tag in a.getTags():

            tags.add( tag )

    # Calculate average tag scores for each user
    userTagLists = {}
    for user in userAnimeLists:

        tagScore = {t:0 for t in tags}
        tagCount = {t:0 for t in tags}

        for title, score in userAnimeLists[user].items():

            if score is not None:
                for tag in animeList[title].getTags():

                    tagScore[tag] += score
                    tagCount[tag] += 1

        userTagLists[user] = {tag:(int( round( tagScore[tag]/tagCount[tag] ) ) if tagCount[tag] > 0 else None) for tag in tags}

    global PY_tag
    global PR_tag
    PY_tag, PR_tag = runEM( tags, userTagLists )

    # Precompute PY for each user
    global PY_tag_user
    PY_tag_user = {username:[probY( PY_tag, PR_tag, userTagLists[username], i ) for i in range( len( PY_tag ) )] for username in userTagLists}
    for PY in PY_tag_user.values():

        assert tolerantEquals( sum( PY ), 1.0 )
    
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

    p = 1.0
    for tag in info.getTags():

        p *= sum( [( PY_tag_user[username][i] * PR_tag[tag][score][i] ) for i in range( len( PY_tag ) )] )

    return p
