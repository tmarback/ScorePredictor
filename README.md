# Score Predictor

Score prediction engine for animated TV shows based on a Naive Bayes model.
This program uses the history of ratings given by each user to each show to predict the most likely score that a certain user will give to a certain show. In order to be able to predict scores for shows that have no past ratings (say, for example, a show that was just released), the model does not consider the shows directly, but rather it computes probabilites for certain "components" of a show (the studio that made it, the genre, episode length, etc) to receive a certain score by a certain user, then combines these component probabilities to obtain the probability of a certain score for a certain show.
