

import streamlit as st
import requests
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

# Your TMDb API key
API_KEY = "01d2a425252c60a07d9035e905a50397"

# Function to fetch all movies from TMDb API
def fetch_all_movies(api_key, total_pages=3):
    base_url = "https://api.themoviedb.org/3"
    movies = []
    
    # Loop through several pages to gather a large dataset
    for page in range(1, total_pages+1):
        url = f"{base_url}/discover/movie"
        params = {
            "api_key": api_key,
            "language": "en-US",
            "page": page,
            "sort_by": "popularity.desc"
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            movies.extend(response.json().get('results', []))
        else:
            st.error(f"Failed to fetch data from API. Status code: {response.status_code}")
            break
            
    return movies

# Function to compute the cosine similarity matrix
def compute_cosine_similarity(movies):
    # Use 'vote_average', 'popularity', and 'vote_count' as features
    features_for_similarity = pd.DataFrame(movies)[['vote_average', 'popularity', 'vote_count']].fillna(0)
    
    # Compute cosine similarity matrix based on features
    cosine_sim_matrix = cosine_similarity(features_for_similarity)
    
    return cosine_sim_matrix

# Function to get movie recommendations based on cosine similarity
def get_recommendations(title, movies, cosine_sim_matrix):
    try:
        # Get the index of the movie that matches the title
        idx = [i for i, movie in enumerate(movies) if movie['title'].lower() == title.lower()][0]
        
        # Get the pairwise similarity scores of all movies with that movie
        sim_scores = list(enumerate(cosine_sim_matrix[idx]))
        
        # Sort the movies based on similarity scores
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        
        # Get the indices of the top 10 most similar movies (excluding the first one)
        movie_indices = [i[0] for i in sim_scores[1:11]]  # Top 10 similar movies
        
        # Return the top 10 most similar movies
        similar_movies = [movies[i]['title'] for i in movie_indices]
        return similar_movies
    except IndexError:
        st.error("Movie not found in the dataset!")
        return []

# Streamlit app interface
st.title("Movie Recommender System")

# Fetch all movies using the API key
movies = fetch_all_movies(API_KEY)

if movies:
    # User input for movie title
    selected_movie = st.text_input('Enter a movie title you like:')
    
    # If user enters a movie title, find similar movies
    if selected_movie:
        # Compute cosine similarity matrix
        cosine_sim_matrix = compute_cosine_similarity(movies)
        
        # Get movie recommendations based on the input
        recommended_movies = get_recommendations(selected_movie, movies, cosine_sim_matrix)
        
        # Display the recommended movies
        if recommended_movies:
            st.write(f"Movies similar to '{selected_movie}':")
            for movie in recommended_movies:
                st.write(f"- {movie}")
        else:
            st.write("No recommendations found. Try another title.")
else:
    st.write("No movies found.")
