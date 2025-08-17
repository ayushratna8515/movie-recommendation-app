import streamlit as st
import recommendation_app as ra  # Import the whole module

# App title
st.set_page_config(page_title="🎬 Movie Recommender", layout="wide")
st.title("🍿AI Movie Recommender")

# Input bar
query = st.text_input("🎯 Enter a movie name or VIbe:", "")

if query:
    st.write(f"🔍 Your Query: {query}")

    with st.spinner("Fetching recommendations..."):
        try:
            # Call backend logic
            movies = ra.recommend_movies(query)
        except Exception as e:
            st.error(f"Error fetching recommendations: {e}")
            movies = []

    if movies:
        st.subheader("✨ Recommended Movies")

        # Display as horizontal scroll cards
        cols = st.columns(len(movies))
        for idx, col in enumerate(cols):
            with col:
                movie = movies[idx]

                # Poster
                poster_url = ra.get_movie_poster(movie)
                st.image(poster_url, caption=movie, use_column_width=True)

                # OTT info (placeholder for now)
                st.markdown("**Available on:** Netflix / Prime (sample)")

                # Trailer
                trailer_url = ra.get_youtube_trailer(movie)
                if trailer_url:
                    st.markdown(
                        f'<iframe width="100%" height="200" src="{trailer_url}" frameborder="0" allowfullscreen></iframe>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.write("🎥 Trailer not found")
    else:
        st.warning("No recommendations found. Try another query!")

# Footer with a movie quote
st.markdown("---")
st.markdown(
    "<p style='text-align: center; font-style: italic; color: gray;'>"
    "🎥 'Movies touch our hearts and awaken our vision.' – Martin Scorsese"
    "</p>",
    unsafe_allow_html=True,
)
