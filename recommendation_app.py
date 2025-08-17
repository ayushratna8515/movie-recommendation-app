import os



import requests
import streamlit as st
import cohere

# Load secrets (do not change key names!)
RAPID_API_KEY = st.secrets["api_keys"]["rapidapi_key"]
TMDB_API_KEY = st.secrets["api_keys"]["tmdb_api"]
COHERE_API_KEY = st.secrets["api_keys"]["cohere_api"]
YOUTUBE_API_KEY = st.secrets["api_keys"]["youtube_api"]

co = cohere.Client(COHERE_API_KEY)

# ---------------- IMDb Similar Movie Search ----------------
def search_imdb_similar(movie_title):
    url = "https://imdb188.p.rapidapi.com/api/v1/searchIMDB"
    headers = {
        "x-rapidapi-key": RAPID_API_KEY,
        "x-rapidapi-host": "imdb188.p.rapidapi.com"
    }
    try:
        response = requests.get(url, headers=headers, params={"query": movie_title}, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print("Error fetching IMDb:", e)
    return None

# ---------------- Cohere Vibe Search ----------------
def search_vibe_movies(vibe_text):
    prompt = f"Suggest 5 movies for: {vibe_text}"
    try:
        resp = co.chat(model="command-r", messages=[{"role": "user", "content": prompt}])
        return resp.text.split("\n")
    except Exception as e:
        print("Error with Cohere:", e)
        return []

# ---------------- TMDB Metadata ----------------
def get_movie_details(title):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={title}"
    try:
        resp = requests.get(url, timeout=10).json()
        if resp.get("results"):
            movie = resp["results"][0]
            return {
                "title": movie.get("title", title),
                "overview": movie.get("overview", "No synopsis available."),
                "poster": f"https://image.tmdb.org/t/p/w500{movie.get('poster_path')}" if movie.get("poster_path") else None
            }
    except Exception as e:
        print("Error fetching TMDB:", e)
    return {"title": title, "overview": "No synopsis available.", "poster": None}

# ---------------- YouTube Trailer ----------------
def get_youtube_trailer(title):
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=1&q={title}+trailer&key={YOUTUBE_API_KEY}"
    try:
        resp = requests.get(url, timeout=10).json()
        if "items" in resp and resp["items"]:
            vid = resp["items"][0]["id"].get("videoId")
            if vid:
                return f"https://www.youtube.com/watch?v={vid}"
    except Exception as e:
        print("Error fetching YouTube:", e)
    return None

# ---------------- Main Aggregator ----------------
def recommend_movies(query):
    results = []

    # 1. Try IMDb search first
    imdb_data = search_imdb_similar(query)
    if imdb_data and "data" in imdb_data:
        for item in imdb_data["data"][:5]:
            title = item.get("titleText", "")
            if title:
                details = get_movie_details(title)
                details["trailer"] = get_youtube_trailer(title)
                details["ott"] = "Not available in India"  # Placeholder for OTT integration
                results.append(details)

    # 2. If no IMDb hit, fallback to vibe via Cohere
    if not results:
        vibe_movies = search_vibe_movies(query)
        for title in vibe_movies[:5]:
            if title.strip():
                details = get_movie_details(title.strip())
                details["trailer"] = get_youtube_trailer(title.strip())
                details["ott"] = "Not available in India"
                results.append(details)

    return results
