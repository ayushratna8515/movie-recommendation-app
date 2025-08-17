import streamlit as st
import recommendation_app as ra

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="AI Movie Recommender",
    page_icon="🎬",
    layout="wide",
)

# -----------------------------
# Header
# -----------------------------
st.markdown(
    """
    <h1 style="text-align: center;">🍿 AI Movie Recommender</h1>
    <p style="text-align: center; font-size:18px; color:gray;">
    "Movies touch our hearts and awaken our vision." – Martin Scorsese
    </p>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Input box
# -----------------------------
query = st.text_input("🎯 Enter a movie name or Vibe:", "")

if query:
    st.write(f"🔎 Your Query: **{query}**")

    try:
        movies = ra.recommend_movies(query)

        if movies:
            st.markdown("## ✨ Recommended Movies")

            # Horizontal Scrollable CSS
            st.markdown(
                """
                <style>
                .scroll-container {
                    display: flex;
                    overflow-x: auto;
                    gap: 16px;
                    padding: 10px;
                }
                .movie-card {
                    flex: 0 0 auto;
                    background: #1e1e1e;
                    border-radius: 12px;
                    padding: 12px;
                    width: 250px;
                    color: white;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.3);
                }
                .movie-poster {
                    border-radius: 10px;
                    width: 100%;
                }
                .movie-title {
                    font-size: 18px;
                    font-weight: bold;
                    margin-top: 10px;
                }
                .movie-overview {
                    font-size: 14px;
                    margin: 6px 0;
                }
                .ott {
                    font-size: 13px;
                    color: #aaa;
                }
                </style>
                """,
                unsafe_allow_html=True,
            )

            # Horizontal Scroll Wrapper
            st.markdown('<div class="scroll-container">', unsafe_allow_html=True)

            for movie in movies:
                trailer_embed = f'<iframe width="100%" height="160" src="{movie["trailer"].replace("watch?v=", "embed/")}" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>' if movie["trailer"] else "<p>Trailer not found</p>"

                st.markdown(
                    f"""
                    <div class="movie-card">
                        <img src="{movie['poster']}" class="movie-poster" alt="Poster"/>
                        <div class="movie-title">{movie['title']}</div>
                        <div class="movie-overview">{movie['overview'][:120]}...</div>
                        <div class="ott"><b>Available on:</b> {movie['ott']}</div>
                        {trailer_embed}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.markdown("</div>", unsafe_allow_html=True)

        else:
            st.error("😔 No movies found. Try another vibe or movie name.")

    except Exception as e:
        st.error(f"Error fetching recommendations: {e}")
