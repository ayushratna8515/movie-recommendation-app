import streamlit as st
import recommendation_app as ra

st.set_page_config(page_title="AI Movie Recommender", layout="wide")

st.title("🍿 AI Movie Recommender")

# 🎬 Inspirational Quote
st.markdown(
    "> *'Movies touch our hearts and awaken our vision.' – Martin Scorsese* 🎥",
    unsafe_allow_html=True,
)

# Input
query = st.text_input("🎬 Enter a movie name or Vibe:", placeholder="e.g. a coming of age teenage movie")

if query:
    st.write(f"🔎 Your Query: **{query}**")

    try:
        movies = ra.recommend_movies(query)

        st.subheader("✨ Recommended Movies")

        # Horizontal scrolling cards
        cols = st.columns(len(movies))

        for i, movie in enumerate(movies):
            with cols[i]:
                # Poster
                poster_url = ra.get_movie_poster(movie)
                st.image(poster_url, use_container_width=True)

                # Title & overview (1-liner)
                st.markdown(f"**{movie['title']}**")
                st.caption(movie.get("overview", "No description available")[:120] + "...")

                # OTT availability
                ott_info = ra.get_ott_availability(movie["title"])
                st.markdown(f"**Available on:** {ott_info}")

                # YouTube trailer
                trailer_url = ra.get_youtube_trailer(movie["title"])
                if trailer_url:
                    st.video(trailer_url)
                else:
                    st.write("🎥 Trailer not found")

    except Exception as e:
        st.error(f"Error fetching recommendations: {e}")
