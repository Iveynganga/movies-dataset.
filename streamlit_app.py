

import streamlit as st
import requests
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

# Your TMDb API key
API_KEY = "01d2a425252c60a07d9035e905a50397"

# Function to search for a movie by title using TMDb API
def search_movie_by_title(api_key, title):
    base_url = "https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": api_key,
        "query": title,
        "language": "en-US"
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        results = response.json().get('results', [])
        if results:
            return results[0]  # Return the first matching result
        else:
            st.error("Movie not found!")
            return None
    else:
        st.error(f"Failed to search movie. Status code: {response.status_code}")
        return None

# Function to fetch movie details using movie ID and return similar movies
def fetch_movie_details(api_key, movie_id):
    base_url = f"https://api.themoviedb.org/3/movie/{movie_id}/similar"
    params = {
        "api_key": api_key,
        "language": "en-US",
        "page": 1
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json().get('results', [])
    else:
        st.error(f"Failed to fetch similar movies. Status code: {response.status_code}")
        return []

# Streamlit app interface
st.title("Movie Recommender System")

# User input for movie title
selected_movie = st.text_input('Enter a movie title you like:')

if selected_movie:
    # Search for the movie using the title
    movie = search_movie_by_title(API_KEY, selected_movie)
    
    if movie:
        st.write(f"Selected Movie: {movie['title']} (Release Date: {movie['release_date']})")
        
        # Fetch similar movies using the movie ID
        similar_movies = fetch_movie_details(API_KEY, movie['id'])
        
        if similar_movies:
            # Sort similar movies by release date in descending order (most recent first)
            sorted_similar_movies = sorted(similar_movies, key=lambda x: x['release_date'], reverse=True)
            
            # Get the top 10 most recent similar movies
            top_10_recent_movies = sorted_similar_movies[:10]
            
            st.write(f"Top 10 most recent movies similar to '{movie['title']}':")
            for sim_movie in top_10_recent_movies:
                st.write(f"- {sim_movie['title']} (Release Date: {sim_movie['release_date']})")
        else:
            st.write("No similar movies found.")
