import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st
import requests

API_KEY = '01d2a425252c60a07d9035e905a50397'

# Function to search for a movie by title
def search_movie_by_title(api_key, title):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={title}"
    response = requests.get(url)
    if response.status_code == 200:
        results = response.json().get('results', [])
        if results:
            return results[0]  # Return the first result
    return None

# Function to fetch detailed movie info
def fetch_movie_details(api_key, movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

# Function to fetch similar movies
def fetch_similar_movies(api_key, movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/similar?api_key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('results', [])
    return []

# Function to compute cosine similarity considering genre
def compute_cosine_similarity_with_genre(similar_movies, selected_movie_genre_ids):
    # Create a DataFrame for similar movies
    similar_movies_df = pd.DataFrame(similar_movies)
    
    # Extract genres and convert to dummy variables
    similar_movies_df['genre_ids'] = similar_movies_df['genre_ids'].apply(lambda x: [genre['id'] for genre in x])
    genre_dummies = pd.get_dummies(similar_movies_df['genre_ids'].apply(pd.Series).stack()).sum(level=0)
    
    # Combine genre dummies with vote_average
    movie_features = pd.concat([genre_dummies, similar_movies_df['vote_average']], axis=1)
    
    # Compute cosine similarity matrix
    cosine_sim_matrix = cosine_similarity(movie_features)
    
    return cosine_sim_matrix

# Streamlit app
st.title('Movie Recommender System')

st.write("""
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
                        # Check if the poster and vote_average exist before displaying
                        poster_path = sim_movie.get('poster_path', None)
                        vote_average = sim_movie.get('vote_average', 'N/A')
                        
                        if poster_path:
                            st.image(f"https://image.tmdb.org/t/p/w500{poster_path}")
                        else:
                            st.write("No poster available")
                        
                        st.write(f"**{sim_movie['title']}**")
                        st.write(f"Rating: {vote_average}")
                        st.write(f"Release Date: {sim_movie['release_date']}")
            else:
                st.write("No similar movies found.")
        else:
            st.write("Failed to fetch movie details.")
    else:
        st.write("Movie not found.")

