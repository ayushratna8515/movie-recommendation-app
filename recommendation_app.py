import os



import requests
import streamlit as st
import cohere

# --- API keys from Streamlit secrets (do not change names!) ---
RAPID_API_KEY = st.secrets["api_keys"]["rapidapi_key"]
TMDB_API_KEY = st.secrets["api_keys"]["tmdb_api"]
COHERE_API_KEY = st.secrets["api_keys"]["cohere_api"]
YOUTUBE_API_KEY = st.secrets["api_keys"]["youtube_api"]

co = cohere.Client(COHERE_API_KEY)

# ---------------- IMDb Similar Movie Search via RapidAPI ----------------
def search_imdb_similar(movie_title: str):
    """
    Uses RapidAPI IMDb endpoint to find titles related to the given movie_title.
    Returns a list of up to 5 title strings.
    """
    url = "https://imdb146.p.rapidapi.com/v1/find/"
    headers = {"x-rapidapi-key": RAPID_API_KEY}
    params = {"query": movie_title}

    try:
        r = requests.get(url, headers=headers, params=params, timeout=12)
        r.raise_for_status()
        data = r.json()
        if "titleResults" in data and "results" in data["titleResults"]:
            titles = [m.get("titleNameText") for m in data["titleResults"]["results"] if m.get("titleNameText")]
            return titles[:5]
    except Exception as e:
        print("Error fetching IMDb (RapidAPI):", e)
    return []

# ---------------- Cohere Vibe-Based Recommendations ----------------
def ai_based_recommendations(user_query: str):
    """
    Uses Cohere Chat API to produce up to 5 movie names (one per line).
    Cleans numbering like '1. Inception' → 'Inception'.
    """
    try:
        resp = co.chat(
            model="command-r",
            message=f"Recommend 5 movies based on this description: {user_query}. "
                    f"Return only movie names, one per line. No extra text."
        )
        raw_lines = resp.text.split("\n")
        cleaned = []
        for line in raw_lines:
            s = line.strip()
            if not s:
                continue
            # remove common numbering patterns e.g., "1) ", "1. ", "1 - "
            while len(s) and (s[0].isdigit() or s[0] in ".-)"):
                s = s[1:].strip()
            cleaned.append(s)
        return [t for t in cleaned if t][:5]
    except Exception as e:
        print("Error with Cohere Chat:", e)
        return []

# ---------------- TMDB Movie Search (metadata) ----------------
def get_movie_details(title: str):
    """
    Searches TMDB by title and returns a dict with id, title, overview, poster.
    Always returns a poster (placeholder if missing).
    """
    url = "https://api.themoviedb.org/3/search/movie"
    params = {"api_key": TMDB_API_KEY, "query": title}
    try:
        r = requests.get(url, params=params, timeout=12)
        r.raise_for_status()
        data = r.json()
        if data.get("results"):
            movie = data["results"][0]
            poster = (
                f"https://image.tmdb.org/t/p/w500{movie.get('poster_path')}"
                if movie.get("poster_path")
                else "https://via.placeholder.com/500x750?text=No+Poster"
            )
            return {
                "tmdb_id": movie.get("id"),
                "title": movie.get("title", title),
                "overview": movie.get("overview", "No description available."),
                "poster": poster,
                "release_date": movie.get("release_date", "N/A"),
                "rating": movie.get("vote_average", "N/A"),
            }
    except Exception as e:
        print("Error fetching TMDB details:", e)
    # fallback if nothing found
    return {
        "tmdb_id": None,
        "title": title,
        "overview": "No description available.",
        "poster": "https://via.placeholder.com/500x750?text=No+Poster",
        "release_date": "N/A",
        "rating": "N/A",
    }

# ---------------- TMDB Watch Providers (India) ----------------
def get_ott_providers_by_id(tmdb_id: int, country: str = "IN"):
    """
    Returns a list of OTT provider names available in the given country for a TMDB movie id.
    Aggregates flatrate/ads/free/rent/buy, prioritizing flatrate first.
    """
    if not tmdb_id:
        return []

    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}/watch/providers"
    params = {"api_key": TMDB_API_KEY}
    try:
        r = requests.get(url, params=params, timeout=12)
        r.raise_for_status()
        data = r.json()
        region = data.get("results", {}).get(country)
        if not region:
            return []

        provider_order = ["flatrate", "ads", "free", "rent", "buy"]
        seen = set()
        ordered_names = []
        for key in provider_order:
            entries = region.get(key) or []
            for item in entries:
                name = item.get("provider_name")
                if name and name not in seen:
                    seen.add(name)
                    ordered_names.append(name)

        return ordered_names
    except Exception as e:
        print("Error fetching TMDB watch/providers:", e)
        return []

# ---------------- YouTube Trailer ----------------
def get_youtube_trailer(title: str):
    """
    Returns a YouTube watch URL (UI will convert to embed).
    """
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "maxResults": 1,
        "q": f"{title} trailer",
        "key": YOUTUBE_API_KEY
    }
    try:
        r = requests.get(url, params=params, timeout=12)
        r.raise_for_status()
        data = r.json()
        if data.get("items"):
            vid = data["items"][0]["id"].get("videoId")
            if vid:
                return f"https://www.youtube.com/watch?v={vid}"
    except Exception as e:
        print("Error fetching YouTube trailer:", e)
    return None

# ---------------- Main Aggregator ----------------
def recommend_movies(user_input: str):
    """
    Master function that:
      1) Tries RapidAPI IMDb similar search.
      2) Falls back to Cohere vibe-based suggestions.
      3) Enriches with TMDB metadata + Watch Providers (India) + YouTube trailer.
    Returns a list of dicts with keys: title, overview, poster, trailer, ott, release_date, rating
    """
    # Try title-based first
    titles = search_imdb_similar(user_input)

    # Fallback to vibe-based
    if not titles:
        titles = ai_based_recommendations(user_input)

    results = []
    for title in titles[:5]:
        details = get_movie_details(title)
        tmdb_id = details.get("tmdb_id")

        # OTT providers in India (IN)
        providers = get_ott_providers_by_id(tmdb_id, "IN") if tmdb_id else []

        # Trailer
        trailer = get_youtube_trailer(details["title"])

        details["ott"] = providers if providers else ["Not on major OTT in India"]
        details["trailer"] = trailer

        results.append(details)

    return results
