import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import re
import time

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

# --- HEADER ---
st.title("Hype Drop Club 🩸")
st.markdown("### Bulk Spotify Popularity Score Checker")

# --- SIDEBAR / INFO ---
with st.expander("ℹ️ How to use & Limits", expanded=True):
    st.write("""
    1. **Paste** Spotify track URLs into the box (one per line).
    2. **Limit:** 500 tracks per search.
    3. **Accuracy:** This tool pulls the official 0-100 Spotify Popularity Index.
    """)

# --- MAIN INTERFACE ---
user_input = st.text_area("📋 Paste Spotify URLs here:", height=300, placeholder="http://open.spotify.com/track/...")

if st.button("🚀 Fetch Popularity Scores"):
    if user_input:
        links = user_input.split('\n')
        track_ids = [re.search(r"track/([a-zA-Z0-9]+)", l.strip()).group(1) for l in links if re.search(r"track/([a-zA-Z0-9]+)", l)]
        
        if track_ids:
            results = []
            with st.spinner('🔍 Fetching Official Spotify Scores...'):
                for tid in track_ids:
                    try:
                        # 2026 BYPASS: Get metadata first
                        t_info = sp.track(tid)
                        t_name = t_info['name']
                        a_name = t_info['artists'][0]['name']
                        
                        # SEARCH BYPASS: The only endpoint that still returns Popularity in 2026
                        query = f"track:{t_name} artist:{a_name}"
                        search_res = sp.search(q=query, type='track', limit=1)
                        
                        if search_res['tracks']['items']:
                            # Grab the official score from the search result
                            official_score = search_res['tracks']['items'][0]['popularity']
                            results.append({
                                "Rank": official_score,
                                "Song Name": t_name,
                                "Artist": a_name,
                                "Spotify ID": tid
                            })
                        time.sleep(0.1) 
                    except Exception:
                        continue

                if results:
                    df = pd.DataFrame(results)
                    st.divider()
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Tracks Found", len(df))
                    m2.metric("Avg Popularity", f"{int(df['Rank'].mean())}/100")
                    m3.metric("Highest Rank", df['Rank'].max())

                    st.dataframe(df.sort_values(by="Rank", ascending=False), use_container_width=True)
                    
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button("📩 Download CSV", csv, "spotify_scores.csv", "text/csv")
                else:
                    st.error("Could not retrieve scores. Spotify may have closed the Search Bypass for your account.")
        else:
            st.error("❌ No valid links detected.")
    else:
        st.warning("⚠️ Paste links first.")

st.divider()
st.caption("©️ 2026 Hype Drop Club. Official Spotify Web API Data.")
