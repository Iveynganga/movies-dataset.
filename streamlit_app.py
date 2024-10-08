import streamlit as st
import pandas as pd
import numpy as np
import requests
import pickle
import sklearn
import cosine_similarity

st.set_page_config(layout="wide")

# Load your data
movies_dict = pickle.load(open("movies_dict.pkl", "rb"))
movies = pd.DataFrame(movies_dict)
movies.drop_duplicates(inplace=True)

# Load the pre-trained model and other required files
with open('csr_data_tf.pkl', 'rb') as file:
    csr_data = pickle.load(file)
model = pickle.load(open("model.pkl", "rb"))

# Load TMDb API key
API_KEY = "01d2a425252c60a07d9035e905a50397"

# Function to fetch movie poster from TMDb
def fetch_poster(movie_id):
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}'
    response = requests.get(url)
    data = response.json()
    if 'poster_path' in data and data['poster_path']:
        return "https://image.tmdb.org/t/p/w500/" + data['poster_path']
    else:
        return "https://via.placeholder.com/500x750.png?text=No+Image"

# Function to recommend movies based on similarity
def recommend(movie_name):
    n_movies_to_recommend = 5
    idx = movies[movies['title'] == movie_name].index[0]
    
    distances, indices = model.kneighbors(csr_data[idx], n_neighbors=n_movies_to_recommend + 1)
    idx = list(indices.squeeze())
    recommended_movies = movies.iloc[idx[1:]]  # Exclude the input movie
    
    movie_titles = recommended_movies['title'].values
    movie_ids = recommended_movies['movie_id'].values
    
    posters = [fetch_poster(movie_id) for movie_id in movie_ids]
    
    return movie_titles, posters

# Streamlit UI
st.title("Movie Recommender System")

st.write("""
Welcome to the Movie Recommender System! 
Select a movie, and we'll recommend a few similar movies for you to enjoy.
""")

selected_movie = st.selectbox("Choose a movie", movies['title'].values)

if st.button("Recommend Movies"):
    movie_titles, posters = recommend(selected_movie)
    
    st.write(f"### Movies similar to {selected_movie}:")
    
    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            st.image(posters[i], width=150)
            st.write(movie_titles[i])

# About section
st.sidebar.write("## About")
st.sidebar.write("This is a Similarity-based Movie Recommender System built with Streamlit and The Movie Database (TMDb) API.")
