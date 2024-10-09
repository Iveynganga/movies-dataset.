

import streamlit as st
import requests

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

# Function to fetch movie poster URL
def fetch_poster_url(poster_path):
    if poster_path:
        return f"https://image.tmdb.org/t/p/w500{poster_path}"
    return None

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
            st.write(f"Movies similar to '{movie['title']}':")
            
            # Show the first 5 similar movies with posters and ratings
            for sim_movie in similar_movies[:5]:  # Limiting to the first 5 movies
                poster_url = fetch_poster_url(sim_movie.get('poster_path'))
                rating = sim_movie.get('vote_average', 'N/A')
                release_date = sim_movie.get('release_date', 'N/A')
                
                st.write(f"**{sim_movie['title']}** (Release Date: {release_date})")
                st.write(f"Rating: {rating}")
                
                if poster_url:
                    st.image(poster_url)
                else:
                    st.write("No poster available.")
                
                st.write("---")  # Separator between movie recommendations
        else:
            st.write("No similar movies found.")
