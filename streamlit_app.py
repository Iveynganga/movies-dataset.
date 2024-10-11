

import streamlit as st
import requests
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from datetime import datetime

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

# Function to filter movies that are super recent (e.g., last 10 years)
def filter_recent_movies(movies, years=10):
    current_year = datetime.now().year
    recent_movies = [movie for movie in movies if movie.get('release_date') and int(movie['release_date'][:4]) >= (current_year - years)]
    return recent_movies

# Streamlit app interface
st.title("Movie Recommender System")

# Catchy welcome note and explanation of cosine similarity
st.write("""
Welcome to **Your Personalized Movie Recommender System**! 🎬 
Here, you’ll get movie suggestions using *cosine similarity*, a technique that helps us find movies similar to the one you love by measuring how 'close' they are in terms of features like ratings and popularity. 

Don't worry, it's just math doing the magic in the background 😉✨.
""")

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
            # Filter to only keep recent movies (e.g., released in the last 2 years)
            recent_similar_movies = filter_recent_movies(similar_movies, years=2)
            
            if recent_similar_movies:
                st.write(f"Recent movies similar to '{movie['title']}':")
                cols = st.columns(5)  # Arrange posters in 5 columns horizontally
                
                for i, sim_movie in enumerate(recent_similar_movies[:5]):
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
            else:
                st.write("No recent similar movies found.")
        else:
            st.write("No similar movies found.")
