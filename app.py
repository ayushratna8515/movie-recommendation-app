import streamlit as st
from recommendation_app import recommend_movies, get_movie_poster, get_youtube_trailer

# ---------------- PAGE CONFIG ---------------- #
st.set_page_config(
    page_title="LoveCinema 🎬",
    page_icon="🎥",
    layout="wide"
)

# ---------------- HEADER ---------------- #
st.markdown(
    """
    <style>
        body {
            background-color: #0f0f0f;
            color: #ffffff;
        }
        .movie-card {
            background-color: #1c1c1c;
            padding: 15px;
            border-radius: 15px;
            margin: 10px;
            text-align: center;
            box-shadow: 0px 4px 12px rgba(0,0,0,0.5);
            min-width: 250px;
            max-width: 250px;
            display: inline-block;
            vertical-align: top;
        }
        .movie-title {
            font-size: 18px;
            font-weight: bold;
            margin-top: 10px;
            color: #f5c518;
        }
        .movie-synopsis {
            font-size: 14px;
            color: #cccccc;
            margin: 10px 0;
            height: 60px;
            overflow: hidden;
        }
        .scrolling-container {
            display: flex;
            overflow-x: auto;
            padding: 10px;
        }
        .scrolling-container::-webkit-scrollbar {
            height: 8px;
        }
        .scrolling-container::-webkit-scrollbar-thumb {
            background: #555;
            border-radius: 10px;
        }
        .quote-banner {
            font-size: 22px;
            font-style: italic;
            color: #f5c518;
            text-align: center;
            margin-bottom: 20px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🍿 LoveCinema – Your Movie Recommendation Hub")

# Random movie quote banner
st.markdown(
    '<div class="quote-banner">"Cinema is a matter of what’s in the frame and what’s out." – Martin Scorsese</div>',
    unsafe_allow_html=True
)

# ---------------- INPUT PANEL ---------------- #
query = st.text_input("🎯 Enter a movie name or describe the vibe you want:", "")

if query:
    with st.spinner("Fetching recommendations... 🎬"):
        movies = recommend_movies(query)

    if movies:
        st.subheader("✨ Recommended Movies for You:")

        st.markdown('<div class="scrolling-container">', unsafe_allow_html=True)

        for movie in movies:
            poster_url = get_movie_poster(movie)
            trailer_url = get_youtube_trailer(movie)

            # Build each card
            card_html = f"""
            <div class="movie-card">
                <img src="{poster_url}" width="200" style="border-radius:10px;">
                <div class="movie-title">{movie}</div>
                <div class="movie-synopsis">A must-watch film picked just for you!</div>
            """
            if trailer_url:
                card_html += f"""
                <iframe width="200" height="120" src="{trailer_url}" frameborder="0" allowfullscreen></iframe>
                """
            else:
                card_html += "<p style='color:grey;font-size:12px;'>Trailer not found</p>"

            card_html += "</div>"  # close card

            st.markdown(card_html, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.error("❌ No movies found. Try another query!")
else:
    st.info("🔎 Start by entering a movie name or description above.")
