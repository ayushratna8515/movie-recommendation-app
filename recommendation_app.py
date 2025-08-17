import os
import cohere


import requests
import streamlit as st

# API Keys from Streamlit secrets
TMDB_API_KEY = st.secrets["api_keys"]["tmdb_api"]
COHERE_API_KEY = st.secrets["api_keys"]["cohere_api"]
RAPIDAPI_KEY = st.secrets["api_keys"]["rapidapi_key"]
YOUTUBE_API_KEY = st.secrets["api_keys"]["youtube_api"]

# ✅ TMDB: Fetch movie poster
def get_movie_poster(movie):
    if "poster" in movie and movie["poster"]:
        return movie["poster"]
    # fallback poster
    return "https://via.placeholder.com/300x450?text=No+Image"

# ✅ YouTube: Fetch trailer
def get_youtube_trailer(movie_title):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": f"{movie_title} official trailer",
        "key": YOUTUBE_API_KEY,
        "type": "video",
        "maxResults": 1
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if "items" in data and len(data["items"]) > 0:
            return f"https://www.youtube.com/watch?v={data['items'][0]['id']['videoId']}"
        return None
    except Exception:
        return None

# ✅ OTT availability in India via JustWatch API (RapidAPI)
def get_ott_availability(movie_title):
    url = "https://streaming-availability.p.rapidapi.com/v2/search/title"
    querystring = {
        "title": movie_title,
        "country": "IN",
        "show_type": "movie",
    }

    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "streaming-availability.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=10)
        data = response.json()

        if "result" in data and len(data["result"]) > 0:
            streaming_info = data["result"][0].get("streamingInfo", {}).get("in", {})
            otts = []
            for provider, provider_data in streaming_info.items():
                otts.append(provider.capitalize())
            return ", ".join(otts) if otts else "Not available on OTT"
        return "Not available on OTT"

    except Exception as e:
        return f"Error fetching OTT info: {e}"

# Dummy recommendation function (replace with Cohere + TMDB later if needed)
def recommend_movies(query):
    """
    Currently returns dummy hardcoded movies.
    Replace this with your Cohere/TMDB integration.
    """
    sample_movies = [
        {
            "title": "Lady Bird",
            "overview": "A teenager navigates life, school and her turbulent relationship with her mother.",
            "poster": "https://image.tmdb.org/t/p/w500/iyI4yYy3l6PvJEa3TBUnIFVnyG7.jpg",
            "release_date": "2017-09-01",
        },
        {
            "title": "The Perks of Being a Wallflower",
            "overview": "A socially awkward teen befriends two seniors who welcome him to the real world.",
            "poster": "https://image.tmdb.org/t/p/w500/aKCvdFFF5ph3p2doH0j0lY5D0Sm.jpg",
            "release_date": "2012-09-20",
        }
    ]
    return sample_movies
