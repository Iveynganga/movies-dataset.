import streamlit as st
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# Load your data 
movies_with_credits = pd.read_csv('/content/movies_with_credits.csv')

# Function to compute cosine similarity
def compute_cosine_similarity(movies_with_credits):
    features_for_similarity = movies_with_credits[['budget', 'popularity', 'revenue', 'vote_average']]
    cosine_sim_matrix = cosine_similarity(features_for_similarity)
    return pd.DataFrame(cosine_sim_matrix, index=movies_with_credits['title'], columns=movies_with_credits['title'])

# Load and compute similarity
cosine_sim_df = compute_cosine_similarity(movies_with_credits)

# Streamlit title
st.title('Movie Recommender System')

# Dropdown for the movie title
movie_title = st.selectbox('Select or Enter a Movie Title:', movies_with_credits['title'].values)

# When the user clicks the "Recommend" button
if st.button('Recommend'):
    if movie_title:
        similar_movies = cosine_sim_df[movie_title].sort_values(ascending=False).head(10)
        st.write('Top 10 movie recommendations:')
        for i, movie in enumerate(similar_movies.index):
            st.write(f"{i + 1}. {movie} - Similarity Score: {similar_movies[movie]:.4f}")
    else:
        st.write("Please select a movie title.")
