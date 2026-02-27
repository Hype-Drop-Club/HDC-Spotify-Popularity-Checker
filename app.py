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

# --- HEADER & BRANDING ---
st.title("Hype Drop Club 🩸")
st.markdown("### Bulk Spotify Popularity Score Checker")

# --- SIDEBAR / INFO ---
with st.expander("ℹ️ How to use & Limits", expanded=True):
    st.write("""
    1. **Paste** Spotify track URLs into the box (one per line).
    2. **Limit:** 500 tracks per search.
    3. **Note:** Due to Feb 2026 API changes, tracks are processed individually.
    """)

# --- MAIN INTERFACE ---
user_input = st.text_area("📋 Paste Spotify URLs here:", height=300, placeholder="https://open.spotify.com/track/...")

if st.button("🚀 Fetch Popularity Scores"):
    if user_input:
        links = user_input.split('\n')
        track_ids = []
        for l in links:
            match = re.search(r"track/([a-zA-Z0-9]+)", l.strip())
            if match:
                track_ids.append(match.group(1))
        
        if track_ids:
            results = []
            # We use a spinner here instead of a progress bar to keep it clean
            with st.spinner(f'Processing {len(track_ids)} tracks... please wait...'):
                for tid in track_ids:
                    try:
                        # 2026 Strategy: Single track fetch only
                        track = sp.track(tid)
                        if track:
                            results.append({
                                "Rank": track.get('popularity', 0),
                                "Song Name": track.get('name', 'Unknown'),
                                "Artist": track['artists'][0]['name'] if track['artists'] else 'Unknown',
                                "Spotify ID": track.get('id', tid)
                            })
                        time.sleep(0.1) # Required to avoid 2026 rate limits
                    except Exception:
                        continue

                if results:
                    df = pd.DataFrame(results)
                    st.divider()
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Tracks Found", len(df))
                    m2.metric("Avg Popularity", f"{int(df['Rank'].mean())}/100")
                    m3.metric("Max Rank", df['Rank'].max())

                    st.dataframe(df.sort_values(by="Rank", ascending=False), use_container_width=True)
                    
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button("📩 Download Results as CSV", csv, "results.csv", "text/csv")
                else:
                    st.error("Spotify API returned no data. Your account may be restricted under the new Feb 2026 rules.")
        else:
            st.error("No valid track links found.")
    else:
        st.warning("Please paste links first.")

# --- FOOTER ---
st.divider()
st.caption("©️ 2026 Hype Drop Club. Data provided by Spotify Web API.")
