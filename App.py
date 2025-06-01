import streamlit as st
import pickle
import pandas as pd
import requests

# Load data
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Poster fetch function
def fetch_poster(movie_id):
    try:
        response = requests.get(
            f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=24c65f88ec1ee8e131f3d100e83d77e9&language=en-US'
        )
        data = response.json()
        return "https://image.tmdb.org/t/p/w500/" + data.get('poster_path', "")
    except:
        return ""

# Recommend function with grouping by year and fallback
def recommend(movie):
    try:
        movie_index = movies[movies['title'] == movie].index[0]
    except IndexError:
        return {}, True

    distances = similarity[movie_index]
    movie_scores = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:100]

    grouped = {2025: [], 2024: [], 2023: []}
    all_recommended_indices = set()

    # Get up to 4 movies per year for 2025, 2024, 2023
    for i, _ in movie_scores:
        year = movies.iloc[i].get("year")
        if year in grouped and len(grouped[year]) < 4:
            movie_id = movies.iloc[i].movie_id
            title = movies.iloc[i].title
            poster = fetch_poster(movie_id)
            grouped[year].append((title, poster))
            all_recommended_indices.add(i)
        if all(len(g) == 4 for g in grouped.values()):
            break

    total_found = sum(len(g) for g in grouped.values())

    # Fill with extras if fewer than 12 found
    if total_found < 12:
        extras_needed = 12 - total_found
        extras = []
        for i, _ in movie_scores:
            if i not in all_recommended_indices:
                movie_id = movies.iloc[i].movie_id
                title = movies.iloc[i].title
                poster = fetch_poster(movie_id)
                extras.append((title, poster))
                all_recommended_indices.add(i)
                if len(extras) == extras_needed:
                    break
        grouped['Others'] = extras

    if total_found == 0 and ('Others' not in grouped or len(grouped['Others']) == 0):
        return {}, True

    return grouped, False

# --- Streamlit App ---
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
        # Show recommendations grouped by year, skipping empty years
        for year in [2025, 2024, 2023]:
            movies_for_year = results.get(year, [])
            if movies_for_year:
                st.markdown(f"<h3 style='text-align: center;'>📅 Top Picks from {year}</h3>", unsafe_allow_html=True)
                cols = st.columns(4)
                for col, (title, poster_url) in zip(cols, movies_for_year):
                    with col:
                        st.markdown(
                            f"""
                            <div style="border: 2px solid #ddd; border-radius: 10px; padding: 10px; text-align: center;">
                                <h5>{title}</h5>
                                <img src="{poster_url}" style="width: 100%; border-radius: 10px;" />
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
        # Show extras if any
        extras = results.get('Others', [])
        if extras:
            st.markdown(f"<h3 style='text-align: center;'>✨ Additional Recommendations</h3>", unsafe_allow_html=True)
            cols = st.columns(4)
            for col, (title, poster_url) in zip(cols, extras):
                with col:
                    st.markdown(
                        f"""
                        <div style="border: 2px solid #ddd; border-radius: 10px; padding: 10px; text-align: center;">
                            <h5>{title}</h5>
                            <img src="{poster_url}" style="width: 100%; border-radius: 10px;" />
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
