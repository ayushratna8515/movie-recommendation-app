import os
import requests
import cohere
import streamlit as st

# Load API keys from Streamlit secrets
RAPID_API_KEY = st.secrets["api_keys"]["rapidapi_key"]
TMDB_API_KEY = st.secrets["api_keys"]["tmdb_api"]
COHERE_API_KEY = st.secrets["api_keys"]["cohere_api"]
YOUTUBE_API_KEY = st.secrets["api_keys"]["youtube_api"]

# Initialize Cohere client
co = cohere.Client(COHERE_API_KEY)


# ----------------- IMDb Similar Movies via RapidAPI -----------------
def search_imdb_similar(movie_title):
    url = "https://imdb8.p.rapidapi.com/title/find"
    querystring = {"q": movie_title}
    headers = {
        "x-rapidapi-host": "imdb8.p.rapidapi.com",
        "x-rapidapi-key": RAPID_API_KEY
    }

    response = requests.get(url, headers=headers, params=querystring)
    if response.status_code == 200:
        data = response.json()
        results = []
        if "results" in data:
            for item in data["results"][:5]:
                if "title" in item and "id" in item:
                    results.append({
                        "title": item["title"],
                        "id": item["id"],
                        "year": item.get("year", "N/A")
                    })
        return results
    else:
        return []


# ----------------- TMDB Metadata -----------------
def fetch_tmdb_details(title):
    url = f"https://api.themoviedb.org/3/search/movie"
    params = {"api_key": TMDB_API_KEY, "query": title}
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        if data["results"]:
            movie = data["results"][0]
            return {
                "title": movie["title"],
                "overview": movie.get("overview", "No description available."),
                "poster": f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie.get("poster_path") else None,
                "release_date": movie.get("release_date", "N/A")
            }
    return {"title": title, "overview": "Not found", "poster": None, "release_date": "N/A"}


# ----------------- YouTube Trailer -----------------
def fetch_youtube_trailer(title):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": f"{title} official trailer",
        "key": YOUTUBE_API_KEY,
        "maxResults": 1,
        "type": "video"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if "items" in data and len(data["items"]) > 0:
            video_id = data["items"][0]["id"]["videoId"]
            return f"https://www.youtube.com/watch?v={video_id}"
    return None


# ----------------- Cohere Fallback -----------------
def cohere_fallback(query):
    response = co.generate(
        model="command-r-plus",   # ✅ Updated model
        prompt=f"Suggest 5 movies based on this description: {query}. Only return movie names, comma separated.",
        max_tokens=100,
        temperature=0.7
    )
    text = response.generations[0].text.strip()
    movies = [m.strip() for m in text.split(",") if m.strip()]
    return movies


# ----------------- Main Recommendation Function -----------------
def recommend_movies(query):
    # Try searching IMDb first
    imdb_results = search_imdb_similar(query)

    movies = []
    if imdb_results:
        for r in imdb_results:
            details = fetch_tmdb_details(r["title"])
            trailer = fetch_youtube_trailer(r["title"])
            details["trailer"] = trailer
            movies.append(details)
    else:
        # Fall back to Cohere if no IMDb results
        ai_movies = cohere_fallback(query)
        for m in ai_movies:
            details = fetch_tmdb_details(m)
            trailer = fetch_youtube_trailer(m)
            details["trailer"] = trailer
            movies.append(details)

    return movies
