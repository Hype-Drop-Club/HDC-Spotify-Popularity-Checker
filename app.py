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
st.markdown("""
    <style>
    .stApp {
        background-color: #2B2B2B;
        color: #F9F7EE;
    }
    h1 {
        color: #EE631D !important;
    }
    h2, h3, p, span, label, .stMetric {
        color: #F9F7EE !important;
    }
    hr {
        border: 1px solid #EE631D !important;
        margin: 2em 0 !important;
    }
    .stMarkdown p {
        color: #F9F7EE !important;
    }
    .stTextArea textarea {
        color: #F9F7EE !important;
        background-color: #3D3D3D !important;
    }
    /* Unified Button Styling */
    button, [data-testid="stBaseButton-primary"], [data-testid="stBaseButton-secondary"] {
        background-color: #EE631D !important;
        color: #F9F7EE !important;
        border: none !important;
        border-radius: 4px !important;
    }
    button:hover {
        background-color: #d1561a !important;
        color: #F9F7EE !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER & BRANDING ---
st.title("Hype Drop Club 🩸")
st.markdown("### Bulk Spotify Popularity Score Checker")

# --- SIDEBAR / INFO ---
with st.expander("ℹ️ How to use & Limits", expanded=True):
    st.write("""
    1. **Paste** Spotify track URLs
