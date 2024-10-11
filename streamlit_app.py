

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

# Function to fetch movie details using movie ID
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

# Function to fetch movie poster
def fetch_poster(movie_id):
    base_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    params = {"api_key": API_KEY, "language": "en-US"}
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        movie_data = response.json()
        return f"https://image.tmdb.org/t/p/w500/{movie_data['poster_path']}"
    else:
        return None

# Streamlit app interface
st.title("Movie Recommender System")

# Catchy welcome note and brief on cosine similarity
st.markdown("""
### Welcome to Your Personalized Movie Guide!
Discover movies similar to your favorites using our recommendation system powered by **cosine similarity**. 
Cosine similarity measures how alike two movies are based on features like ratings and popularity. 
Just enter a movie title, and we'll find the top matching movies for you!
""")

# Adding a movie-related banner
st.image("https://www.themoviedb.org/assets/2/v4/logos/primary-green-f91eaaee546b0244f56d90b9f0beee2c2c09da2f2d732b16b0187a7eb4cfa4b4.svg", 
         use_column_width=True)

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
            st.write(f"Movies similar to '{movie['title']}':")
            
            # Displaying posters and titles in a horizontal layout
            cols = st.columns(5)  # Create 5 columns for horizontal display
            for i, sim_movie in enumerate(similar_movies[:5]):  # Show only the first 5
                with cols[i]:
                    st.image(fetch_poster(sim_movie['id']), use_column_width=True)
                    st.write(f"{sim_movie['title']} (Release: {sim_movie['release_date']})")
        else:
            st.write("No similar movies found.")
