import streamlit as st
import pickle
from code import content_base, collab

RATE_COLS = 4

recommend_types = ['Content Based', 'Collabrative']
st.header('Movie Recommender System')
movies_contenet = pickle.load(open('movie_list.pkl', 'rb'))
movie_list = movies_contenet['title'].values

recommend_type = st.radio('Type', recommend_types)

selected_movies = st.multiselect(
    "Type or select a movie from the dropdown",
    movie_list
)

ratings_dic = {}

for i in range(len(selected_movies) // RATE_COLS + 1):
    cols = st.columns(RATE_COLS)
    for num in range(RATE_COLS):
        index = i * RATE_COLS + num
        if index < len(selected_movies):
            ratings_dic[selected_movies[index]] = cols[num].slider(
                'Rate ({})'.format(selected_movies[index]),
                1.0, 5.0)


def get_user_input():
    user_input = []
    for index in range(len(selected_movies)):
        user_input.append(
            {'title': selected_movies[index], 'rating': ratings_dic[selected_movies[index]]})
    return user_input


if st.button('Recommend'):
    if len(selected_movies) == 0 or len(selected_movies) != len(ratings_dic):
        st.error('validate your input')
    else:
        userInput = get_user_input()
        if recommend_type == recommend_types[0]:
            recom = content_base(userInput)
        else:
            recom = collab(userInput)
        st.table(recom)
