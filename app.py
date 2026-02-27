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
    st.error("Setup error: Please check your Streamlit Secrets.")
    st.stop()

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Hype Drop Club", page_icon="🩸", layout="wide")

# --- HEADER & BRANDING ---
st.title("Hype Drop Club 🩸")
st.markdown("### Bulk Spotify Popularity Score Checker")

# --- ABOUT THE TOOL ---
with st.container():
    st.markdown("#### The tool")
    st.write("This is a bulk spotify popularity checker. It pulls the internal popularity score for up to 500 track links at once. This score is a 0 to 100 metric that spotify uses to rank every song on the platform relative to everything else.")
    
    st.markdown("#### Why i built it")
    st.write("""
    I made this because checking tracks one by one is a headache for marketing teams and managers working across different projects. Most tools are too slow for professional use. If you are working on a catalog marketing plan for a client or analyzing an entire album to see which tracks are moving the needle, you need to see the data in aggregate. 

    As editorial playlists phase out and become more of a "stamp of approval" rather than a primary traffic driver, triggering the algorithm is where the real scale happens. Spotify needs to see specific momentum before it starts pushing your music into discover weekly or radio. 

    Using this tool lets you monitor a whole project in seconds to find the tracks hitting the 20-30 popularity threshold. These are the songs the algorithm is actually watching, so you can stop wasting budget on tracks that aren't sticking and focus your energy where you have the best chance of triggering an algorithmic surge.
    """)

st.divider()

# --- SIDEBAR / INFO ---
with st.expander("ℹ️ How to use & Limits", expanded=True):
    st.write("""
    1. **Paste** Spotify track URLs into the box (one per line).
    2. **Limit:** This tool is strictly limited to **500 tracks per search**.
    3. **Accuracy:** Scores (0-100) are updated by Spotify daily.
    """)

# --- MAIN INTERFACE ---
user_input = st.text_area("📋 Paste Spotify URLs here:", height=300, placeholder="http://open.spotify.com/track/...")

if st.button("🚀 Fetch Popularity Scores"):
    if user_input:
        raw_links = user_input.split('\n')
        track_ids = []
        for l in raw_links:
            clean_link = l.strip()
            match = re.search(r"track/([a-zA-Z0-9]+)", clean_link)
            if match:
                track_ids.append(match.group(1))
        
        if len(track_ids) > 500:
            st.error("❌ Too many tracks! Please limit your search to 500 tracks.")
            st.stop()
        
        if track_ids:
            results = []
            # Added progress bar because single-fetching takes longer
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for index, tid in enumerate(track_ids):
                try:
                    # Single track fetch to avoid 2026 403 batch errors
                    track = sp.track(tid)
                    if track:
                        results.append({
                            "Rank": track['popularity'],
                            "Song Name": track['name'],
                            "Artist": track['artists'][0]['name'],
                            "Spotify ID": track['id']
                        })
                    time.sleep(0.02) # Gentle pacing
                except Exception as e:
                    pass
                
                # Update progress
                perc = (index + 1) / len(track_ids)
                progress_bar.progress(perc)
                status_text.text(f"Processing {index + 1} of {len(track_ids)}")

            if results:
                status_text.empty()
                progress_bar.empty()
                df = pd.DataFrame(results)
                st.divider()
                
                m1, m2, m3 = st.columns(3)
                m1.metric("Total Tracks Found", len(df))
                m2.metric("Average Popularity", f"{int(df['Rank'].mean())}/100")
                m3.metric("Highest Rank", df['Rank'].max())

                st.dataframe(df.sort_values(by="Rank", ascending=False), use_container_width=True)
                
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📩 Download Results as CSV",
                    data=csv,
                    file_name="spotify_track_analysis.csv",
                    mime="text/csv"
                )
            else:
                st.error("No data found. Check your 'Users and Access' list in Spotify Dashboard.")
        else:
            st.error("❌ No valid links detected.")
    else:
        st.warning("⚠️ Paste links first.")

# --- FOOTER ---
st.divider()
st.caption("©️ 2026 Developed for Hype Drop Club subscribers. Data provided by Spotify Web API.")
