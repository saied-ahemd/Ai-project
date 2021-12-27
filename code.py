

# %%
import pickle
import numpy as np
import pandas as pd

def collab(userInput):
    movies_df = pd.read_csv('../movie.csv')
    ratings_df = pd.read_csv('../rating.csv')

    movies_df['year'] = movies_df.title.str.extract(
        '(\(\d\d\d\d\))', expand=False)
    movies_df['year']

    movies_df['year'] = movies_df.year.str.extract('(\d\d\d\d)', expand=False)
    movies_df['year']

    movies_df['title']

    movies_df['title'] = movies_df.title.str.replace('(\(\d\d\d\d\))', '')
    movies_df['title']

    movies_df['title'] = movies_df['title'].apply(lambda x: x.strip())

    movies_df = movies_df.drop('genres', 1)
    # pickle.dump(movies_df, open('movie_list_col.pkl', 'wb'))

    ratings_df = ratings_df.drop('timestamp', 1)

    inputMovies = pd.DataFrame(userInput)

    # %%
    # Filtering out the movies by title
    inputId = movies_df[movies_df['title'].isin(inputMovies['title'].tolist())]

    # Then merging it so we can get the movieId. It's implicitly merging it by title.
    inputMovies = pd.merge(inputId, inputMovies)

    # Dropping information we won't use from the input dataframe
    inputMovies = inputMovies.drop('year', 1)

    userSubset = ratings_df[ratings_df['movieId'].isin(
        inputMovies['movieId'].tolist())]

    # rames where they all have the same value in the column specified as the parameter
    userSubsetGroup = userSubset.groupby(['userId'])

    userSubsetGroup = sorted(
        userSubsetGroup,  key=lambda x: len(x[1]), reverse=True)

    userSubsetGroup = userSubsetGroup[0:100]

    pearsonCorrelationDict = {}

    # For every user group in our subset
    for name, group in userSubsetGroup:

        # Let's start by sorting the input and current user group so the values aren't mixed up later on
        group = group.sort_values(by='movieId')
        inputMovies = inputMovies.sort_values(by='movieId')

        # Get the N (total similar movies watched)
        nRatings = len(group)

        # Get the review scores for the movies that they both have in common
        temp_df = inputMovies[inputMovies['movieId'].isin(
            group['movieId'].tolist())]

        # And then store them in a temporary buffer variable in a list format to facilitate future calculations
        tempRatingList = temp_df['rating'].tolist()

        # Let's also put the current user group reviews in a list format
        tempGroupList = group['rating'].tolist()

        # Now let's calculate the pearson correlation between two users, so called, x and y

        # For package based
        # scipy.stats import pearsonr
        # pearsonr(tempRatingList,tempGroupList)[0]

        # from scratch
        Sxx = sum([i**2 for i in tempRatingList]) - \
            pow(sum(tempRatingList), 2)/float(nRatings)
        Syy = sum([i**2 for i in tempGroupList]) - \
            pow(sum(tempGroupList), 2)/float(nRatings)
        Sxy = sum(i*j for i, j in zip(tempRatingList, tempGroupList)) - \
            sum(tempRatingList)*sum(tempGroupList)/float(nRatings)

        # If the denominator is different than zero, then divide, else, 0 correlation.
        if Sxx != 0 and Syy != 0:
            pearsonCorrelationDict[name] = Sxy/np.sqrt(Sxx*Syy)
        else:
            pearsonCorrelationDict[name] = 0

    # %%
    pearsonDF = pd.DataFrame.from_dict(pearsonCorrelationDict, orient='index')

    # %%
    pearsonDF.columns = ['similarityIndex']
    pearsonDF['userId'] = pearsonDF.index
    pearsonDF.index = range(len(pearsonDF))

    # %%
    topUsers = pearsonDF.sort_values(
        by='similarityIndex', ascending=False)[0:50]

    # %%
    topUsersRating = topUsers.merge(
        ratings_df, left_on='userId', right_on='userId', how='inner')

    topUsersRating['weightedRating'] = topUsersRating['similarityIndex'] * \
        topUsersRating['rating']

    # %%

    tempTopUsersRating = topUsersRating.groupby(
        'movieId').sum()[['similarityIndex', 'similarityIndex']]
    tempTopUsersRating.columns = ['sum_similarityIndex', 'sum_weightedRating']

    # %%
    # Creates an empty dataframe
    recommendation_df = pd.DataFrame()
    # Now we take the weighted average
    recommendation_df['weighted average recommendation score'] = tempTopUsersRating['sum_weightedRating'] / \
        tempTopUsersRating['sum_similarityIndex']
    recommendation_df['movieId'] = tempTopUsersRating.index

    # %%
    recommendation_df = recommendation_df.sort_values(
        by='weighted average recommendation score', ascending=False)

    # %%
    col_recom = movies_df.loc[movies_df['movieId'].isin(
        recommendation_df.head(20)['movieId'].tolist())]

    return col_recom


def content_base(userInput):
    movies_df = pd.read_csv('../movie.csv')
    ratings_df = pd.read_csv('../rating.csv')

    movies_df['year'] = movies_df.title.str.extract(
        '(\(\d\d\d\d\))', expand=False)
    movies_df['year'] = movies_df.year.str.extract('(\d\d\d\d)', expand=False)
    movies_df['title'] = movies_df.title.str.replace('(\(\d\d\d\d\))', '')
    movies_df['title'] = movies_df['title'].apply(lambda x: x.strip())

    movies_df['genres'] = movies_df.genres.str.split('|')

    ratings_df = ratings_df.drop('timestamp', 1)
    moviesWithGenres_df = movies_df.copy()

    # For every row in the dataframe, iterate through the list of genres and place a 1 into the corresponding column
    for index, row in movies_df.iterrows():
        for genre in row['genres']:
            moviesWithGenres_df.at[index, genre] = 1

    # Filling in the NaN values with 0 to show that a movie doesn't have that column's genre
    moviesWithGenres_df = moviesWithGenres_df.fillna(0)

    inputMovies = pd.DataFrame(userInput)
    # print(inputMovies)

    inputId = movies_df[movies_df['title'].isin(inputMovies['title'].tolist())]

    inputMovies = pd.merge(inputId, inputMovies)

    inputMovies = inputMovies.drop('genres', 1).drop('year', 1)

    userMovies = moviesWithGenres_df[moviesWithGenres_df['movieId'].isin(
        inputMovies['movieId'].tolist())]

    userMovies = userMovies.reset_index(drop=True)

    userGenreTable = userMovies.drop('movieId', 1).drop(
        'title', 1).drop('genres', 1).drop('year', 1)

    userProfile = userGenreTable.transpose().dot(inputMovies['rating'])

    genreTable = moviesWithGenres_df.set_index(moviesWithGenres_df['movieId'])

    genreTable = genreTable.drop('movieId', 1).drop(
        'title', 1).drop('genres', 1).drop('year', 1)

    # %%
    # Multiply the genres by the weights and then take the weighted average
    recommendationTable_df = (
        (genreTable*userProfile).sum(axis=1))/(userProfile.sum())

    recommendationTable_df = recommendationTable_df.sort_values(
        ascending=False)

    recom = movies_df.loc[movies_df['movieId'].isin(
        recommendationTable_df.head(20).keys())]
    return recom


userInput = [
    {'title': 'Breakfast Club, The', 'rating': 5},
    {'title': 'Toy Story', 'rating': 3.5},
    {'title': 'Jumanji', 'rating': 2},
    {'title': "Pulp Fiction", 'rating': 5},
    {'title': 'Akira', 'rating': 4.5}
]
col = collab(userInput)
cont = content_base(userInput)
print('cont', cont, '\n')
print('col', col)
