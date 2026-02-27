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
# We removed the columns here so the text box takes up the full width for a cleaner look
user_input = st.text_area("📋 Paste Spotify URLs here:", height=300, placeholder="https://open.spotify.com/track/...")

if st.button("🚀 Fetch Popularity Scores"):
    if user_input:
        # Extract Track IDs using Regular Expressions
        links = user_input.split('\n')
        track_ids = [re.search(r"track/([a-zA-Z0-9]+)", l).group(1) for l in links if re.search(r"track/([a-zA-Z0-9]+)", l)]
        
        # --- THE 500 LIMIT HARD STOP ---
        if len(track_ids) > 500:
            st.error(f"❌ **Too many tracks!** You pasted {len(track_ids)} links. Please limit your search to **500 tracks** at a time.")
            st.stop()
        
        if track_ids:
            with st.spinner('🔍 Analyzing tracks... this usually takes 2-5 seconds...'):
                results = []
                
                # BATCHING
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
                    except Exception as e:
                        st.error(f"Error fetching batch: {e}")

                if results:
                    df = pd.DataFrame(results)
                    
                    # --- SUMMARY METRICS ---
                    st.divider()
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Total Tracks Found", len(df))
                    m2.metric("Average Popularity", f"{int(df['Rank'].mean())}/100")
                    m3.metric("Highest Rank", df['Rank'].max())

                    # --- DATA TABLE ---
                    st.dataframe(df.sort_values(by="Rank", ascending=False), use_container_width=True)
                    
                    # --- DOWNLOAD BUTTON ---
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📩 Download Results as CSV",
                        data=csv,
                        file_name="spotify_track_analysis.csv",
                        mime="text/csv"
                    )
                else:
                    st.error("Could not find data for these tracks.")
        else:
            st.error("❌ No valid Spotify track links detected. Make sure the URLs contain 'track/'.")
    else:
        st.warning("⚠️ Please paste some links first!")

# --- FOOTER ---
st.divider()
st.caption("©️ 2026 Developed for subscribers. Data provided by Spotify Web API. Not affiliated with Spotify AB.")
