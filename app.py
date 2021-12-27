import pandas as pd
import streamlit as st
import pickle
from code import content_base, collab
from streamlit_player import st_player


recommend_types = ['Content Based', 'Collabrative']
st.header('Movie Recommender System')
movies_contenet = pickle.load(open('movie_list.pkl', 'rb'))
movie_list = movies_contenet['title'].values

recommend_type = st.radio('Type', recommend_types)

selected_movies = st.multiselect(
    "Type or select a movie from the dropdown",
    movie_list
)


def float_range(start, stop, step):
    i = start
    while i < stop:
        yield i
        i += step


numbers = []
for i in float_range(1, 5, 0.1):
    numbers.append(round(i, 1))


ratings = st.multiselect('Movie Rating', numbers)
print(ratings)


def getUserInput():
    userInput = []
    ratingsSplit = ratings
    for i in range(len(selected_movies)):
        userInput.append(
            {'title': selected_movies[i], 'rating': float(ratingsSplit[i])})
    return userInput


if st.button('Recommend'):
    if len(selected_movies) == 0 or len(selected_movies) != len(ratings):
        st.error('validate your input')
    else:
        userInput = getUserInput()
        if recommend_type == recommend_types[0]:
            recom = content_base(userInput)
        else:
            recom = collab(userInput)
        st.table(recom)
