
# 🎬 Movie Recommendation App

This is a **Streamlit-based Movie Recommendation Web App** that recommends movies based on either:
- Exact movie title matches (via IMDb/TMDB API)
- AI-generated "movie vibe" recommendations (via Cohere API)

The app also displays:
- 🎭 Movie Posters (via TMDB API)
- ▶ YouTube Trailers (via YouTube Data API)

## 🚀 Features
- Search movies by name or vibe.
- AI-based recommendations when an exact match is not found.
- Movie posters and YouTube trailers embedded.
- Responsive UI with horizontally scrollable movie cards.
- Mobile-friendly design.

## 🛠️ Tech Stack
- **Frontend**: Streamlit
- **Backend**: Python
- **APIs Used**:
  - [TMDB API](https://www.themoviedb.org/documentation/api) - for posters & movie data
  - [YouTube Data API](https://developers.google.com/youtube/v3) - for trailers
  - [Cohere API](https://cohere.ai/) - for AI vibe-based recommendations
  - [RapidAPI IMDb API](https://rapidapi.com) - for movie metadata

## 📦 Installation

1. Clone the repository:
```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory and add your API keys:
```env
RAPIDAPI_KEY=your_rapidapi_key
COHERE_API_KEY=your_cohere_api_key
TMDB_API_KEY=your_tmdb_api_key
YOUTUBE_API_KEY=your_youtube_api_key
```

4. Run the app locally:
```bash
streamlit run app.py
```

## 🌍 Deployment (Streamlit Cloud)
1. Push your code to a **GitHub repository**.
2. Go to [Streamlit Cloud](https://share.streamlit.io/).
3. Sign in with GitHub.
4. Click **"New App"**, select your repo, branch, and `app.py` file.
5. Add your API keys as **secrets** in Streamlit Cloud settings.
6. Deploy 🎉

## 📷 Screenshot
![App Screenshot](screenshot.png)

---
**Author**: Ayush Ratna  
**License**: MIT
