# Module that handles probability calculations

# Represents an anime in the database.
#
# No fields may be None, except episodeN if type is not TV.
class anime:

    showType = None # The type of show (TV, Movie, OVA, etc) [string]
    source = None # The source of the show (Manga, Original, etc) [string]
    episodeN = None # The episode count (only when type is TV, otherwise should be None) [int]
    rating = None # The rating of the show (PG, M, etc) [string]
    studio = [] # The studios that made the show [list of string]
    genre = [] # The genres of the show [list of string]
    duration = None # The duration of each episode in minutes [int]
    start_year = None # The year when the show started airing [int]

# Initializes the predictive engine.
# Must be called before calling any other function.
#
# Parameters:
# - animeList: The animes in the database. Must be a map where the key is the title and the value is an instance of the anime class.
# - scores: The scores given to each anime by each user. Must be a list of tuples (username [string], title [string], score [int]).
#           Score must be in the range [1,10].
def intialize( animeList, scores ):

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
