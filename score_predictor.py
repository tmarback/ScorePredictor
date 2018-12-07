# Module that handles startup and user interaction
import AnimeDatasetParser
import engine

def main():
    print("This program shall predict the probability of a known user givng a show a certain score.")
    restart = True
    while(restart == True):
        user_check = False
        tit_check  = False
        info_check = False
        username_input = ""
        score_input = 0
        title_input = ""
        info_input

        # Get username
        while (user_check == False):
            username_input = input("Please enter a username. (Ex: Lilithmon, Black_Swanny, or MotokoAramaki)")
            if username_input not in engine.PY_tag_user:
                print("This username is not in our list of known users")
            else:
                user_check = True

        # Get predicted score
        while not ( 1 <= score_input <= 10):
            score_input = int(input("Please choose an integer between 1 and 10."))
            if not ( 1 <= score_input <= 10):
                print("Integer between 1 and 10 only.")

        # Getting input for title
        while (tit_check == False):
            answer = input("If you want to use a show is in our database, submit Y otherwise we'll ask for the info")
            if answer in ['y','Y','yes','Yes']:
                while (title_input not in engine.animes):
                    title_input = input("Please put in the title of the show, correctly please")
                    if title_input not in engine.animes:
                        print("That was not found in our database, please try again")
                        print("You can quit by submitting N")
                    if title_input in ['n','N']:
                        tit_check = True
                        break
            else:
                title_input = None
                tit_check   = True

        print("Please submit information about the show,")
        print("if the show is not in our database, then here is where you will submit the information.")
        print("If you do not know or wish to skip, then sumbit the string 'None'. ")
        # Getting input for info
        while (info_check == False):
            info_type       = None
            info_source     = None
            info_episode    = None
            info_rating     = None
            info_studio     = []
            info_genre      = []
            info_duration   = None
            info_start_year = None

            while (info_type == None):
                info_type = input("Please enter the type of show: TV, Movie, OVA, Special, Other.")
                if info_type not in ['TV', 'Movie','OVA','Special','Other']:
                    print("Please try again, exact spelling")
                    info_type = None
                if info_type == "" or info_type == 'None':
                    print("Default to None then.")
                    info_type = None
                    break

            while (info_source == None):
                info_source = input("Please enter the source: Manga, Original, Light Novel, Game, Visual Novel, Other.")
                if info_source not in ['Manga', 'Original', 'Light Novel', 'Game', 'Visual Novel', 'Other']:
                    print("Please try again, check capitalization/spelling")
                    info_source == None
                if info_source == "" or info_type == "None":
                    print("Default to None then.")
                    info_source == None
                    break

            while (info_episode == None and info_type == "TV"):
                info_episode = int(input("Please enter the number of episodes, 0 if you want to skip"))
                if info_episode == 0:
                    print("Default to None then")
                    info_episode = None
                    break

            while (info_rating == None):
                info_rating = input("Please enter the rating: G, PG, PG13, R, R+, Rx")
                if info_rating not in ['G', 'PG13', 'R', 'R+', 'Rx']:
                    print("Please enter the exact rating as shown")
                    info_rating = None
                if info_rating == "" or info_rating == "None":
                    print("Default to None then.")
                    info_source == None
                    break

            while (info_studio == []):
                print("Submit 'None' if you don't know")
                studio_list = input("Please submit the studio(s), properly formatted, that helped create the show, separated by comma. Ex: A-1 Pictures, Madhouse, Kyoto Animation ")
                info_studio = studio_list.split(',')
                if info_studio == "" or info_studio == "None":
                    print("Default to [] then.")
                    info_studio == []
                    break

            while (info_genre == []):
                print("You can skip this by submitting 'None' ")
                genre_list = input("Pleae put in the genre(s) separated by comma Ex: Action, Horror, Romance.")
                info_genre = genre_list.split(',')
                if info_genre == "None" or info_genre == []:
                    print("Default to [] then.")
                    info_source == []
                    break

            while (info_duration == None):
                info_duration = int(input("Please enter the length in minutes of each episode or special/movie, 0 if you don't know"))
                if info_duration == 0:
                    print("Default to None then.")
                    info_source == None
                    break

            while (info_start_year == None):
                info_start_year = int(input("Please put in the year the show first aired, 0 if you don't know or want to skip"))
                if info_start_year == 0:
                    print("Default to None then.")
                    info_source == None
                    break
            #Get out of this while loop with info
            info_input = anime(info_type, info_source, info_episode, info_rating, info_studio, info_genre, info_duration, info_start_year)
            info_check = True 

        print("Submitting information")

        #Hope that there is no mismatch to throw an error not found
        result = engine.scoreProb( username_input, score_input, title_input, info_input )
        print("User: {username_input} giving the show a {score_input} is a {result} chance.").format(username_input = username_input, score_input = score_input, result = result)

        go_again = input("Thank you for using me, would you like to try again (y/n)?")
        if go_again in ['n','N','no']:
            print("Goodbye")
            restart = False
        else:
            print("Going back to start, please exit with ctrl-C or n next time if you didn't mean to go back")


main()
