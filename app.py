import streamlit as st
import recommendation_app as ra
import html
from urllib.parse import quote_plus

# ------------------------------------------------
# Page config
# ------------------------------------------------
st.set_page_config(
    page_title="AI Movie Recommender",
    page_icon="🎬",
    layout="wide",
)

# ------------------------------------------------
# Styles (Netflix-like horizontal scroll)
# ------------------------------------------------
st.markdown("""
<style>
body, .stApp { background: #0e0e0f; }
.app-title { text-align:center; margin: 0.5rem 0 0.25rem; }
.app-sub { text-align:center; color:#bdbdbd; margin-bottom: 1.25rem; }
.quote { text-align:center; color:#9aa0a6; font-style: italic; margin-top: 1rem; }

.scroll-wrap {
  overflow-x: auto;
  overflow-y: hidden;
  white-space: nowrap;
  padding: 8px 4px 12px;
  -webkit-overflow-scrolling: touch;
}
.scroll-track {
  display: inline-flex;
  gap: 16px;
}

.card {
  background: #18181b;
  color: #eaeaea;
  border-radius: 14px;
  box-shadow: 0 8px 20px rgba(0,0,0,.35);
  width: 260px;
  min-width: 260px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.poster {
  width: 100%;
  height: 380px;
  object-fit: cover;
  background: #111;
}
.card-body {
  padding: 12px 12px 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.title {
  font-weight: 700;
  font-size: 16px;
  line-height: 1.2;
  min-height: 38px;
}
.overview {
  font-size: 13px;
  color: #cfcfcf;
  min-height: 44px;
}
.badges {
  display: flex; flex-wrap: wrap; gap: 6px; margin-top: 2px;
}
.badge {
  background: #2a2a2e;
  border: 1px solid #34343a;
  border-radius: 999px;
  padding: 3px 10px;
  font-size: 11px;
  color: #d6d6d6;
}
.trailer {
  width: 100%; height: 168px; border: 0; border-radius: 10px; margin-top: 8px;
}
.helper {
  color:#9aa0a6; font-size: 13px; margin: 4px 0 10px;
}
.input-help {
  color:#9aa0a6; font-size: 13px; margin-top:-6px; margin-bottom:10px;
}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------
# Header
# ------------------------------------------------
st.markdown('<h1 class="app-title">🍿 AI Movie Recommender</h1>', unsafe_allow_html=True)
st.markdown('<div class="app-sub">Find posters, synopsis, OTT availability in India, and trailers.</div>', unsafe_allow_html=True)
st.markdown('<div class="quote">"Movies touch our hearts and awaken our vision." – Martin Scorsese</div>', unsafe_allow_html=True)

# ------------------------------------------------
# Input
# ------------------------------------------------
query = st.text_input("🎬 Enter a movie name or a vibe (e.g., “coming-of-age in New York”):", "")
st.markdown('<div class="input-help">Tip: Try a title like <i>Tamasha</i> or a vibe like <i>nostalgic 90s romcom</i>.</div>', unsafe_allow_html=True)

# ✅ Recommend CTA button
if st.button("✨ Recommend") and query.strip():
    st.write(f"🔎 Your Query: **{query.strip()}**")

    try:
        movies = ra.recommend_movies(query.strip())
    except Exception as e:
        st.error(f"Error fetching recommendations: {e}")
        movies = []

    if not movies:
        st.warning("No recommendations found. Try another title or refine your vibe.")
    else:
        # ✅ Build horizontal scroll cards properly
        cards_html = ""
        for m in movies:
            title = html.escape(m.get("title") or "Unknown Title")
            overview = (m.get("overview") or "No overview available").strip()
            overview_short = (overview[:150] + "…") if len(overview) > 150 else overview
            overview_short = html.escape(overview_short)
            poster = m.get("poster") or "https://via.placeholder.com/500x750?text=No+Poster"
            poster = html.escape(poster)

            ott_text = m.get("ott") or "Not available on OTT"
            if isinstance(ott_text, list):
                ott_list = ott_text
            else:
                ott_list = [x.strip() for x in str(ott_text).split(",") if x.strip()]
            if not ott_list:
                ott_list = ["Not available on OTT"]

            badges_html = "".join([f'<span class="badge">{html.escape(x)}</span>' for x in ott_list[:5]])

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

        final_html = f"""
        <div class="helper">Swipe/scroll horizontally to see more →</div>
        <div class="scroll-wrap">
            <div class="scroll-track">
                {cards_html}
            </div>
        </div>
        """

        st.markdown(final_html, unsafe_allow_html=True)
