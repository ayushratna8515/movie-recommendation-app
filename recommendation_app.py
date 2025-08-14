import requests
import cohere
import streamlit as st

# Load API keys from Streamlit secrets
RAPID_API_KEY = st.secrets["api_keys"]["rapidapi_key"]
COHERE_API_KEY = st.secrets["api_keys"]["cohere_api"]

# IMDb Similar Movie Search via RapidAPI
def search_imdb_similar(movie_title):
    url = "https://imdb8.p.rapidapi.com/title/find"
    headers = {
        "x-rapidapi-key": RAPID_API_KEY,
        "x-rapidapi-host": "imdb8.p.rapidapi.com"
    }
    params = {"q": movie_title}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        return []

    data = response.json()
    if "results" not in data or not data["results"]:
        return []

    # First match → get similar movies
    movie_id = data["results"][0].get("id", "").split("/")[-2]
    if not movie_id:
        return []

    sim_url = f"https://imdb8.p.rapidapi.com/title/get-more-like-this"
    sim_params = {"tconst": movie_id}
    sim_response = requests.get(sim_url, headers=headers, params=sim_params)

    if sim_response.status_code != 200:
        return []

    sim_data = sim_response.json()
    movie_list = []
    for item in sim_data:
        movie_id_clean = item.split("/")[-2]
        movie_list.append(movie_id_clean)

    # Fetch titles for each similar movie
    final_movies = []
    for m_id in movie_list[:5]:
        title_url = "https://imdb8.p.rapidapi.com/title/get-overview-details"
        title_params = {"tconst": m_id}
        title_resp = requests.get(title_url, headers=headers, params=title_params)
        if title_resp.status_code == 200:
            tdata = title_resp.json()
            title = tdata.get("title", {}).get("title")
            if title:
                final_movies.append(title)

    return final_movies


# Cohere Fallback for Description-Based Recommendations
def cohere_fallback(description):
    co = cohere.Client(COHERE_API_KEY)
    prompt = f"""
    Suggest 5 movies based on the following description:
    {description}

    Provide only the movie titles in a list.
    """

    response = co.generate(
        model="command-xlarge-nightly",
        prompt=prompt,
        max_tokens=100,
        temperature=0.7
    )

    text = response.generations[0].text.strip()
    movies = [line.strip("-• ") for line in text.split("\n") if line.strip()]
    return movies[:5]


# Master Recommendation Function
def recommend_movies(query):
    # Try RapidAPI first (movie title flow)
    similar_movies = search_imdb_similar(query)
    if similar_movies:
        return similar_movies

    # If no match, fallback to Cohere (description flow)
    ai_movies = cohere_fallback(query)
    return ai_movies
