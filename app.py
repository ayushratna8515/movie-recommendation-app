import streamlit as st
import requests
from recommendation_app import recommend_movies

# Load API keys from secrets.toml
TMDB_API_KEY = st.secrets["api_keys"]["tmdb_api"]
YOUTUBE_API_KEY = st.secrets["api_keys"]["youtube_api"]

# --- Helper Functions ---
def get_movie_poster(title):
    search_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={title}"
    response = requests.get(search_url)
    if response.status_code == 200:
        data = response.json()
        if data["results"]:
            poster_path = data["results"][0].get("poster_path")
            if poster_path:
                return f"https://image.tmdb.org/t/p/w500{poster_path}"
    return "https://via.placeholder.com/500x750?text=No+Image"

def get_youtube_trailer(title):
    query = f"{title} trailer"
    search_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=1&q={query}&key={YOUTUBE_API_KEY}"
    response = requests.get(search_url)
    if response.status_code == 200:
        data = response.json()
        if data["items"]:
            video_id = data["items"][0]["id"]["videoId"]
            return f"https://www.youtube.com/embed/{video_id}"
    return None

# --- Streamlit UI ---
st.set_page_config(layout="wide")
st.title("🎬 AI Movie Recommendation App")

st.markdown("""
<style>
body {background-color: #111;}
h1 {color: #FFD700;}
.movie-card {
    background-color: #222;
    padding: 10px;
    border-radius: 12px;
    text-align: center;
    color: white;
}
</style>
""", unsafe_allow_html=True)

query = st.text_input("Enter a movie name or describe the vibe 🎥")
if st.button("Get Recommendations"):
    if query.strip():
        movies = recommend_movies(query)
        if not movies:
            st.warning("No recommendations found.")
        else:
            cols = st.columns(len(movies))
            for idx, col in enumerate(cols):
                movie = movies[idx]
                poster_url = get_movie_poster(movie)
                trailer_url = get_youtube_trailer(movie)
                with col:
                    st.markdown(f"<div class='movie-card'><b>{movie}</b></div>", unsafe_allow_html=True)
                    st.image(poster_url, use_column_width=True)
                    if trailer_url:
                        st.markdown(f'<iframe width="100%" height="200" src="{trailer_url}" frameborder="0" allowfullscreen></iframe>', unsafe_allow_html=True)
    else:
        st.error("Please enter a movie name or description.")
