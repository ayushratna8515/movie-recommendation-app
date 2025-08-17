import os
import cohere
import requests
import streamlit as st

# Load API keys from Streamlit secrets
RAPID_API_KEY = st.secrets["api_keys"]["rapidapi_key"]
TMDB_API_KEY = st.secrets["api_keys"]["tmdb_api"]
COHERE_API_KEY = st.secrets["api_keys"]["cohere_api"]
YOUTUBE_API_KEY = st.secrets["api_keys"]["youtube_api"]

# IMDb Similar Movie Search via RapidAPI
def search_imdb_similar(movie_title):
    url = "https://imdb8.p.rapidapi.com/title/find"
    headers = {"x-rapidapi-key": RAPID_API_KEY, "x-rapidapi-host": "imdb8.p.rapidapi.com"}
    params = {"q": movie_title}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        if "results" in data:
            return [m["title"] for m in data["results"] if "title" in m][:5]
    return []

# Cohere AI fallback for natural language queries
# Cohere AI fallback for natural language queries (updated for Chat API)
def cohere_recommend(query):
    import cohere
    co = cohere.Client(COHERE_API_KEY)

    try:
        response = co.chat(
            model="command-r-plus",  # supported chat model
            message=f"Suggest 5 movies for: {query}"
        )

        if response.text:
            movies = response.text.strip().split("\n")
            return [m.strip(" -0123456789.") for m in movies if m.strip()][:5]

    except Exception as e:
        print("Error from Cohere:", e)
        return []

    return []

# TMDB poster fetch
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

# YouTube trailer fetch
def get_youtube_trailer(title):
    query = f"{title} trailer"
    search_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=1&q={query}&key={YOUTUBE_API_KEY}"
    response = requests.get(search_url)
    if response.status_code == 200:
        data = response.json()
        if "items" in data and data["items"]:
            video_id = data["items"][0]["id"]["videoId"]
            return f"https://www.youtube.com/embed/{video_id}"
    return None

# Main recommend function
def recommend_movies(query):
    movies = search_imdb_similar(query)
    if not movies:  # fallback if IMDb fails
        movies = cohere_recommend(query)
    return movies[:5]
