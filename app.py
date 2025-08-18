import streamlit as st
import requests
import cohere
import html
from urllib.parse import quote_plus

# ==============================
# API KEYS
# ==============================
RAPIDAPI_KEY = "6f2eff737amshd6644d2a574c3b4p106c3bjsn77c59310b130"
COHERE_API_KEY = "ZjmHANWxG6Lzdq1fONsizGPcNqa6whppZjq4GnUS"

# ==============================
# COHERE CLIENT
# ==============================
co = cohere.Client(COHERE_API_KEY)

# ==============================
# STREAMLIT CONFIG
# ==============================
st.set_page_config(page_title="AI Movie Recommender", layout="wide")

st.markdown(
    """
    <style>
    body { background-color: #111; color: #eee; }
    .scroll-wrap { overflow-x: auto; white-space: nowrap; padding: 10px 0; }
    .scroll-track { display: flex; gap: 16px; }
    .card {
        display: inline-block; 
        background: #1e1e1e; 
        border-radius: 12px; 
        width: 220px; 
        flex: 0 0 auto;
        padding: 10px; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    }
    .poster {
        width: 100%; 
        border-radius: 10px;
    }
    .card-body { padding: 8px 0; }
    .title { font-size: 1.1em; font-weight: bold; margin: 6px 0; color: #fff; }
    .overview { font-size: 0.85em; color: #ccc; margin-bottom: 6px; }
    .badge {
        display: inline-block; 
        background: #ff0066; 
        color: white; 
        padding: 2px 8px; 
        border-radius: 8px; 
        margin-right: 4px;
        font-size: 0.75em;
    }
    .trailer { width: 100%; height: 160px; border-radius: 8px; margin-top: 6px; }
    .helper { font-size: 0.8em; color: #aaa; margin-bottom: 6px; }
    </style>
    """, unsafe_allow_html=True
)

st.markdown("<h1 style='text-align:center'>🍿 AI Movie Recommender</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center'>Find posters, synopsis, OTT availability in India, and trailers.</p>", unsafe_allow_html=True)

# ==============================
# FETCH MOVIES FROM RAPIDAPI
# ==============================
def fetch_similar_movies(title):
    url = "https://imdb188.p.rapidapi.com/api/v1/searchIMDB"
    headers = {
        "x-rapidapi-host": "imdb188.p.rapidapi.com",
        "x-rapidapi-key": RAPIDAPI_KEY
    }
    query = {"query": title}
    response = requests.get(url, headers=headers, params=query)
    if response.status_code != 200:
        return []
    data = response.json()
    results = data.get("data", {}).get("results", [])
    movies = []
    for r in results[:5]:
        movies.append({
            "title": r.get("titleText", {}).get("text"),
            "poster": r.get("primaryImage", {}).get("url") if r.get("primaryImage") else None,
            "overview": r.get("titleText", {}).get("text"),
            "ott": ["Netflix", "Amazon Prime"],  # placeholder OTT
            "trailer": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        })
    return movies

# ==============================
# FETCH MOVIES FROM COHERE
# ==============================
def fetch_vibe_movies(prompt):
    response = co.generate(
        model="command-r",
        prompt=f"Suggest 5 movies for: {prompt}. Return as JSON with keys: title, overview, poster (TMDB), trailer, ott.",
        max_tokens=400
    )
    text = response.generations[0].text.strip()
    import re, json
    match = re.search(r"\[.*\]", text, re.S)
    if not match:
        return []
    try:
        return json.loads(match.group(0))
    except:
        return []

# ==============================
# MAIN APP
# ==============================
query = st.text_input("🎬 Enter a movie name or a vibe (e.g., “coming-of-age in New York”):")
st.markdown("<p style='font-size:0.9em;color:#aaa'>Tip: Try a title like <i>Tamasha</i> or a vibe like <i>nostalgic 90s romcom</i>.</p>", unsafe_allow_html=True)

if st.button("✨ Recommend"):
    if not query:
        st.warning("Please enter a movie name or description.")
    else:
        st.subheader(f"🔎 Your Query: {query}")

        # Fetch from APIs
        movies = fetch_similar_movies(query)
        if not movies:
            movies = fetch_vibe_movies(query)

        if not movies:
            st.warning("No recommendations found. Try another title or refine your vibe.")
        else:
            # Build all cards
            cards_html = ""
            for m in movies:
                title = html.escape(m.get("title") or "Unknown Title")
                overview = (m.get("overview") or "No overview available").strip()
                overview_short = (overview[:150] + "…") if len(overview) > 150 else overview
                overview_short = html.escape(overview_short)
                poster = m.get("poster") or "https://via.placeholder.com/500x750?text=No+Poster"
                poster = html.escape(poster)

                # OTT platforms as badges
                ott_text = m.get("ott") or "Not available on OTT"
                if isinstance(ott_text, list):
                    ott_list = ott_text
                else:
                    ott_list = [x.strip() for x in str(ott_text).split(",") if x.strip()]
                if not ott_list:
                    ott_list = ["Not available on OTT"]

                badges_html = "".join([f'<span class="badge">{html.escape(x)}</span>' for x in ott_list[:5]])

                # Trailer embed
                trailer_url = m.get("trailer") or ""
                if trailer_url:
                    embed_url = trailer_url.replace("watch?v=", "embed/")
                    trailer_iframe = f'<iframe class="trailer" src="{html.escape(embed_url)}" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>'
                else:
                    search_q = quote_plus(f"{title} trailer")
                    trailer_iframe = f'<a target="_blank" class="badge" href="https://www.youtube.com/results?search_query={search_q}">Search trailer ▶</a>'

                cards_html += f"""
                    <div class="card">
                        <img class="poster" src="{poster}" alt="Poster for {title}">
                        <div class="card-body">
                            <div class="title">{title}</div>
                            <div class="overview">{overview_short}</div>
                            <div class="badges">{badges_html}</div>
                            {trailer_iframe}
                        </div>
                    </div>
                """

            # ✅ FINAL FIX: proper horizontal scroll container
            final_html = f"""
            <div class="helper">Swipe/scroll horizontally to see more →</div>
            <div class="scroll-wrap">
                <div class="scroll-track">
                    {cards_html}
                </div>
            </div>
            """
            st.markdown(final_html, unsafe_allow_html=True)
