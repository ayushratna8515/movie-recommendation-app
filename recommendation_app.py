import os



import requests
import streamlit as st
import cohere

# Load API keys safely
RAPIDAPI_KEY = st.secrets["api_keys"]["rapidapi_key"]
TMDB_API_KEY = st.secrets["api_keys"]["tmdb_api"]
COHERE_API_KEY = st.secrets["api_keys"]["cohere_api"]
YOUTUBE_API_KEY = st.secrets["api_keys"]["youtube_api"]

# Initialize Cohere
co = cohere.Client(COHERE_API_KEY)


# -----------------------------
# TMDB Poster Fetch
# -----------------------------
def get_movie_poster(movie_id):
    """Fetch poster URL for a movie from TMDB"""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data.get("poster_path"):
            return f"https://image.tmdb.org/t/p/w500{data['poster_path']}"
    return None


# -----------------------------
# YouTube Trailer Fetch
# -----------------------------
def get_youtube_trailer(query):
    """Fetch first YouTube trailer link"""
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": f"{query} official trailer",
        "key": YOUTUBE_API_KEY,
        "maxResults": 1,
        "type": "video"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        items = response.json().get("items")
        if items:
            return f"https://www.youtube.com/watch?v={items[0]['id']['videoId']}"
    return None


# -----------------------------
# Cohere Fallback for Natural Language Queries
# -----------------------------
def cohere_fallback(query):
    """Generate movie recommendations using Cohere when TMDB search fails"""
    prompt = (
        f"Suggest 5 movies for the description: {query}. "
        "Return a JSON list with exactly 5 objects. "
        "Each object must have keys: title, overview, release_date."
    )

    response = co.chat(
        model="command-r-plus",  # ✅ using chat API (generate is deprecated)
        message=prompt,
    )

    # Cohere sometimes outputs text → we parse manually
    text_output = response.text
    movies = []
    try:
        import json
        movies = json.loads(text_output)
    except:
        # crude parsing if JSON fails
        for line in text_output.split("\n"):
            if line.strip():
                movies.append({
                    "title": line.strip(),
                    "overview": "No overview available",
                    "release_date": "Unknown"
                })

    return movies[:5]


# -----------------------------
# Main Recommender
# -----------------------------
def recommend_movies(query):
    """Fetch recommendations either from TMDB or fallback to Cohere"""
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={query}"
    response = requests.get(url)

    movies = []

    if response.status_code == 200:
        data = response.json()
        results = data.get("results", [])[:5]  # ✅ Always 5 results max

        for movie in results:
            movies.append({
                "title": movie.get("title"),
                "overview": movie.get("overview"),
                "poster": f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie.get("poster_path") else None,
                "release_date": movie.get("release_date", "Unknown"),
                "trailer": get_youtube_trailer(movie.get("title")),
                "ott": "Netflix / Prime (sample)"  # Placeholder
            })

    # If TMDB gives nothing → fallback
    if not movies:
        cohere_results = cohere_fallback(query)
        for movie in cohere_results:
            movies.append({
                "title": movie.get("title"),
                "overview": movie.get("overview"),
                "poster": None,
                "release_date": movie.get("release_date", "Unknown"),
                "trailer": get_youtube_trailer(movie.get("title")),
                "ott": "Not available on OTT"
            })

    return movies[:5]  # ✅ Ensure always 5
