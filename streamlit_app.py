

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

# Function to fetch similar movies using movie ID
def fetch_similar_movies(api_key, movie_id):
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

# Function to fetch detailed movie info (including genres)
def fetch_movie_details(api_key, movie_id):
    base_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    params = {
        "api_key": api_key,
        "language": "en-US"
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch movie details. Status code: {response.status_code}")
        return None

# Function to calculate cosine similarity considering genre
def compute_cosine_similarity_with_genre(movies, movie_genres):
    # Convert genres into one-hot encoding for cosine similarity
    genre_df = pd.DataFrame(movies)
    genre_df['genres'] = genre_df['genre_ids'].apply(lambda ids: [1 if genre_id in ids else 0 for genre_id in movie_genres])
    
    # Extract relevant features for similarity
    features_df = pd.concat([genre_df['genres'].apply(pd.Series), genre_df[['vote_average', 'popularity', 'vote_count']]], axis=1)
    
    # Compute cosine similarity matrix based on features
    cosine_sim_matrix = cosine_similarity(features_df)
    
    return cosine_sim_matrix

# Streamlit app interface
st.title("Movie Recommender System")

# Catchy welcome note and explanation of cosine similarity
st.write("""
Welcome to the **Movie Recommender System**! 🎬 
Here, you’ll get movie suggestions using *cosine similarity*, a technique that helps us find movies similar to the one you love by measuring how 'close' they are in terms of features like ratings, popularity, and genres.

Don't worry, it's just math doing the magic in the background 😉✨.
""")

# User input for movie title
selected_movie = st.text_input('Enter a movie title you like:')

if selected_movie:
    # Search for the movie using the title
    movie = search_movie_by_title(API_KEY, selected_movie)
    
    if movie:
        st.write(f"Selected Movie: **{movie['title']}** (Release Date: {movie['release_date']})")
        
        # Fetch detailed movie info (including genres)
        movie_details = fetch_movie_details(API_KEY, movie['id'])
        
        if movie_details:
            # Extract genre IDs from the selected movie
            selected_movie_genres = movie_details.get('genres', [])
            selected_movie_genre_ids = [genre['id'] for genre in selected_movie_genres]
            
            # Fetch similar movies using the movie ID
            similar_movies = fetch_similar_movies(API_KEY, movie['id'])
            
            if similar_movies:
                st.write(f"Movies similar to '{movie['title']}':")
                
                # Compute cosine similarity considering genre
                cosine_sim_matrix = compute_cosine_similarity_with_genre(similar_movies, selected_movie_genre_ids)
                
                # Sort movies by similarity score and display the top 5
                top_indices = cosine_sim_matrix[0].argsort()[::-1][1:6]
                cols = st.columns(5)
                
                for i, idx in enumerate(top_indices):
                    sim_movie = similar_movies[idx]
                    with cols[i]:
                        # Check if the poster exists before displaying
                        poster_path = sim_movie.get('poster_path', None)
                        
                        if poster_path:
                            st.image(f"https://image.tmdb.org/t/p/w500{poster_path}")
                        else:
                            st.write("No poster available")
                        
                        st.write(f"**{sim_movie['title']}**")
                        st.write(f"Release Date: {sim_movie['release_date']}")
            else:
                st.write("No similar movies found.")
