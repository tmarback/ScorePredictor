
# coding: utf-8

# In[1]:


import pandas as pd
from collections import defaultdict
from engine import anime
import engine

# In[2]:


#files 
anime_cl = "anime_cleaned.csv"
users_cl = "users_cleaned.csv"
anime_watched = "animelists_tinier.csv"

chunksize = 10 ** 6


# In[3]:


# - type
# - source
# - #episodes (source=TV only) (ranges)
# - rating
# - studio (list)
# - genre (list)
# - duration_min (ranges)
# - aired_from_year
# Should call with "anime_cl.csv" which has the columns anime_id, title, type, source, etc which we want to use 
# for how 
def getAnimeList(anime_csv):
    # Reading from the anime_cleaned, the list of anime and their related data
    anicols_to_use = ['anime_id', 'title', 'type', 'source', 'episodes', 'rating','studio','genre','duration_min','aired_from_year']
    chunky_a = []
    for chunk in pd.read_csv(anime_csv, index_col=1, usecols=anicols_to_use, chunksize=chunksize):
        chunky_a.append(chunk)
    anime_list = pd.concat(chunky_a, axis=0)
    del chunky_a
    
    # Convert anime_list into Anime datatype
    anime_list = anime_list.T.to_dict()
    
    # Create anime instances
    animeclass_list = defaultdict(list)

    for a, i in anime_list.items():
        if None in i:
            continue
        SType    = i['type']
        SSource  = i['source']
        if (SType == 'TV'):
            NEpisode = int(i['episodes'])
        else:
            NEpisode = None
        SRating  = i['rating']
        LStudio  = i['studio']
        LGenre   = i['genre']
        NDura    = int(i['duration_min'])
        NStart   = int(i['aired_from_year'])
        anime_obj = anime(SType, SSource, NEpisode, SRating, LStudio, LGenre, NDura, NStart)
        animeclass_list[a].append(anime_obj)
        
    return animeclass_list


# In[4]:


# Getting a dict of id to title
# Should pass in "anime_cleaned.csv" as that has the titles and id
def getAnimeIdDict(anime_csv):
    chunky_b = []
    for chunk in pd.read_csv(anime_csv, index_col = 0, usecols=['anime_id', 'title'], chunksize=chunksize):
        chunky_b.append(chunk)
    anime_dict = pd.concat(chunky_b, axis=0).to_dict()
    id_titles = anime_dict['title']
    del chunky_b
    return id_titles

#
#anime_list = pd.concat(chunky_a, axis=0)
#del chunky_a
#animeids_dict = pd.concat(chunky_b, axis=0).to_dict()
#id_titles = animeids_dict['title']
#del chunky_b


# In[ ]:





# In[5]:


# Use for reading from users_cleaned.csv, the list of users
def getUserList(users_csv):
    chunky_u = []
    for chunk in pd.read_csv(users_csv, usecols=['username'], chunksize=chunksize):
        chunky_u.append(chunk)

    user_list = pd.concat(chunky_u, axis=0)
    del chunky_u
    return user_list


# In[6]:


# Reading in the data animelists_cleaned which details the user and anime watched
# Gets a csv file with 'username','anime_id','scores' in anime_watch aka "animelists_cleaned.csv"
# anime_csv has the list of corresponding anime-id and title aka "anime_cleaned.csv"
# match the id with an anime title from anime_cleaned.csv
# Then return a list of tuples of (username, anime_title, score)
def getScore(anime_watch_csv, anime_csv):
    watchcols_to_use = ['username', 'anime_id', 'my_score']
    chunky_ua = []
    for chunk in pd.read_csv(anime_watch_csv, usecols=watchcols_to_use, chunksize=chunksize):
        chunky_ua.append(chunk)
    
    users_anime_watched = pd.concat(chunky_ua, axis=0)
    del chunky_ua

    #  Pull out the columns
    usernames  = users_anime_watched['username'].tolist()
    ids        = users_anime_watched['anime_id'].tolist()
    users_scores = users_anime_watched['my_score'].tolist()

    #get the titles to match with id
    id_titles = getAnimeIdDict(anime_csv)
    
     # Connect id with title
    titles = []
    for i in ids:
        titles.append(id_titles[i])
        
    # Create the tuple of scores (username [string], title [string], score [int])
    user_scores = []
    for i in range(0,len(usernames)):
        if(1 <= users_scores[i] <= 10):
            user_scores.append( (usernames[i], titles[i], users_scores[i]) )
    
    return user_scores
    
    


# In[7]:


#animeList: map where the key is the title and the value is an instance of the anime class
animeList_from_csv = getAnimeList(anime_cl)
animeList = {title:anime[0] for title, anime in animeList_from_csv.items()} # Convert 1-element lists into pure values. TEMP FIX

#scoreList: list of tuples (username [string], title [string], score [int]).
#           Score must be in the range [1,10].
scoreList = getScore(anime_watched, anime_cl)

import numpy as np
engine.initialize( animeList, scoreList )
tests = [ ( 'karthiga', 'One Piece', 9 ),
          ( 'karthiga', 'Bakuman. 2nd Season', 8 ),
          ( 'Damonashu', 'Ghost in the Shell: Stand Alone Complex - Solid State Society', 8 ),
          ( 'bskai', 'Suzumiya Haruhi no Shoushitsu', 10 ),
          ( 'MistButterfly', 'Accel World', 6 ),
          ( 'MistButterfly', 'Detective Conan Movie 17: Private Eye in the Distant Sea', 6 ),
          ( 'Lithuelle', 'Senyuu. 2', 6 ),
          ( 'magedgamed', 'Burn Up!', 8 ) ]

for user, title, actual in tests:

    print( '\nActual score: %d' % actual )
    for i in range( 1, 11 ):

        print( 'P(R=%d) = %.5f%%' % ( i, np.exp( engine.scoreProb( user, i, title ) ) * 100 ) )

# In[143]:


# Convert anime_list into Anime datatype
#anime_list = anime_list.T.to_dict()


# In[150]:


# Create anime instances
#animeclass_list = defaultdict(list)


#for a, i in anime_list.items():
#    if None in i:
#        continue
#    SType    = i['type']
#    SSource  = i['source']
#    if (SType == 'TV'):
#        NEpisode = int(i['episodes'])
#    else:
#        NEpisode = None
#    SRating  = i['rating']
#    LStudio  = i['studio']
#    LGenre   = i['genre']
#    NDura    = int(i['duration_min'])
#    NStart   = int(i['aired_from_year'])
#    anime_obj = anime(SType, SSource, NEpisode, SRating, LStudio, LGenre, NDura, NStart)
#    animeclass_list[a].append(anime_obj)



# In[145]:


# Also want a tuple of user and the score
# The scores given to each anime by each user. Must be a list of tuples (username [string], title [string], score [int]).
#           Score must be in the range [1,10]

#  Pull out the columns
#usernames  = users_anime_watched['username'].tolist()
#ids        = users_anime_watched['anime_id'].tolist()
#users_cores = users_anime_watched['my_score'].tolist()


# In[146]:


# Connect id with title
#titles = []
#for i in ids:
#    titles.append(id_titles[i])


# In[148]:


# Create the tuple of scores (username [string], title [string], score [int])
#user_scores = []
#for i in range(0,len(usernames)):
#    user_scores.append( (usernames[i], titles[i], users_cores[i]) )
