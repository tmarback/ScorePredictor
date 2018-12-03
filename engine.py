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

    # Collapse score list into maps of users to scores
    userLists = {}
    for username, title, score in scores:

        assert username
        assert title
        assert 1 <= score <= 10

        if username not in userLists:
            userLists[username] = {}

        userLists[username][title] = score

    # TODO: Calculate probs

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

    return 0.0
