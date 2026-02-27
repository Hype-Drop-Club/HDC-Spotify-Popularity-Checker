import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import re

# --- SECURE SETUP ---
try:
    CLIENT_ID = st.secrets["SPOTIFY_CLIENT_ID"]
    CLIENT_SECRET = st.secrets["SPOTIFY_CLIENT_SECRET"]
    auth_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    sp = spotipy.Spotify(auth_manager=auth_manager)
except Exception as e:
    st.error("Setup Error: Please check your Streamlit Secrets.")
    st.stop()

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Hype Drop Club", page_icon="🩸", layout="wide")

# --- CUSTOM THEMEING ---
st.markdown(f"""
    <style>
    .stApp {{
        background-color: #2B2B2B;
        color: #F9F7EE;
    }}
    h1 {{
        color: #EE631D !important;
    }}
    h2, h3, p, span, label, .stMetric {{
        color: #F9F7EE !important;
    }}
    hr {{
        border: 1px solid #EE631D !important;
    }}
    .stMarkdown p {{
        color: #F9F7EE !important;
    }}
    /* Input box text color */
    .stTextArea textarea {{
        color: #F9F7EE !important;
        background-color: #3D3D3D !important;
    }}
    /* Button Styles */
    div.stButton > button {{
        background-color: #EE631D !important;
        color: #F9F7EE !important;
        border: none !important;
    }}
    div.stButton > button:hover {{
        background-color: #d1561a !important;
        color: #F9F7EE !important;
    }}
    /* Download link button specific styling */
    div.stDownloadButton > button {{
        background-color: #EE631D !important;
        color: #F9F7EE !important;
        border: none !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- HEADER & BRANDING ---
st.title("Hype Drop Club 🩸")
st.markdown("### Bulk Spotify Popularity Score Checker")

# --- SIDEBAR / INFO ---
with st.expander("ℹ️ How to use & Limits", expanded=True):
    st.write("""
    1. **Paste** Spotify track URLs into the box (one per line).
    2. **Limit:** This tool is strictly limited to **500 tracks per search** to ensure speed and stability.
    3. **Accuracy:** Scores (0-100) are updated by Spotify daily.
    """)

# --- MAIN INTERFACE ---
user_input = st.text_area("📋 Paste Spotify URLs here:", height=300, placeholder="https://open.spotify.com/track/...")

if st.button("🚀 Fetch Popularity Scores"):
    if user_input:
        links = user_input.split('\n')
        track_ids = [re.search(r"track/([a-zA-Z0-9]+)", l).group(1) for l in links if re.search(r"track/([a-zA-Z0-9]+)", l)]
        
        if len(track_ids) > 500:
            st.error(f"❌ **Too many tracks!** You pasted {len(track_ids)} links. Please limit your search to **500 tracks** at a time.")
            st.stop()
        
        if track_ids:
            with st.spinner('🔍 Analyzing tracks...'):
                results = []
                for i in range(0, len(track_ids), 50):
                    batch = track_ids[i:i+50]
                    try:
                        tracks_data = sp.tracks(batch)
                        for track in tracks_data['tracks']:
                            if track:
                                results.append({
                                    "Rank": track['popularity'],
                                    "Song Name": track['name'],
                                    "Artist": track['artists'][0]['name'],
                                    "Spotify ID": track['id']
                                })
