import streamlit as st
import pickle
import pandas as pd
import requests

# --- Load preprocessed movie data and similarity matrix ---
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

similarity = pickle.load(open('similarity.pkl', 'rb'))

# --- Function to fetch movie poster using TMDb API ---
def fetch_poster(movie_id):
    try:
        response = requests.get(
            f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=24c65f88ec1ee8e131f3d100e83d77e9&language=en-US'
        )
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500/{poster_path}"
        else:
            return "https://via.placeholder.com/500x750?text=No+Image"
    except Exception as e:
        return "https://via.placeholder.com/500x750?text=No+Image"

# --- Recommendation function: returns top 8 similar movies ---
def recommend(movie):
    try:
        movie_index = movies[movies['title'] == movie].index[0]
    except IndexError:
        return [], True  # No recommendation flag

    distances = similarity[movie_index]
    movie_scores = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:9]

    recommendations = []
    for i, _ in movie_scores:
        movie_id = movies.iloc[i].movie_id
        title = movies.iloc[i].title
        poster = fetch_poster(movie_id)
        recommendations.append((title, poster))

    return recommendations, False

# --- Streamlit UI Setup ---
st.set_page_config(page_title="Movie Recommender", layout="wide")

st.markdown(
    "<h1 style='text-align: center; color: #F63366;'>🎬 Movie Recommender System</h1>",
    unsafe_allow_html=True,
)

selected_movie = st.selectbox("Choose a movie", movies['title'].values, label_visibility="collapsed")

col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    recommend_btn = st.button("🔍 Recommend", use_container_width=True)

if recommend_btn:
    with st.spinner("Fetching recommendations... 🍿"):
        results, empty = recommend(selected_movie)

    if empty:
        st.warning("❌ No recommendations found for this title.")
    else:
        st.markdown("<h3 style='text-align:center; color:#F63366;'>Recommended Movies</h3>", unsafe_allow_html=True)

        # Add CSS for hover effect on movie cards
        st.markdown(
            """
            <style>
            .movie-card:hover {
                box-shadow: 0 8px 20px rgba(246, 51, 102, 0.6);
                transform: scale(1.05);
                transition: all 0.3s ease-in-out;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        # Display 8 recommended movies in 2 rows of 4 columns each
        for i in range(0, 8, 4):
            cols = st.columns(4)
            for col, (title, poster_url) in zip(cols, results[i:i+4]):
                with col:
                    st.markdown(
                        f"""
                        <div class="movie-card" style="
                            border: 2px solid #444; 
                            border-radius: 10px; 
                            padding: 10px; 
                            text-align: center; 
                            background-color: #111; 
                            margin: 5px;">
                            <img src="{poster_url}" style="width: 100%; border-radius: 10px;" />
                            <h5 style='color:white; margin-top: 10px;'>{title}</h5>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            if i == 0:
                st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)
