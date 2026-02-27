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

# --- ABOUT ---
with st.expander("📖 The tool & Why i built it"):
    st.write("""
    **The tool:** This pulls the internal popularity score (0-100) for your tracks.
    
    **Why i built it:** Most tools are too slow for professional use. As editorial playlists phase out, 
    triggering the algorithm is where the real scale happens. This tool helps you find the tracks 
    hitting the 20-30 popularity threshold so you can focus your energy where it moves the needle.
    """)

# --- MAIN INTERFACE ---
user_input = st.text_area("📋 Paste Spotify URLs here:", height=250, placeholder="https://open.spotify.com/track/...")

if st.button("🚀 Fetch Popularity Scores"):
    if user_input:
        raw_links = user_input.split('\n')
        track_ids = []
        for l in raw_links:
            match = re.search(r"track/([a-zA-Z0-9]+)", l.strip())
            if match:
                track_ids.append(match.group(1))
        
        if len(track_ids) > 500:
            st.error("❌ Limit: 500 tracks per search.")
            st.stop()
        
        if track_ids:
            results = []
            progress_text = "🔍 Analyzing tracks one by one (New 2026 API Rules)..."
            my_bar = st.progress(0, text=progress_text)
            
            for index, tid in enumerate(track_ids):
                try:
                    # New 2026 requirement: Single track fetch only for Dev Mode
                    track = sp.track(tid)
                    if track:
                        results.append({
                            "Rank": track['popularity'],
                            "Song Name": track['name'],
                            "Artist": track['artists'][0]['name'],
                            "Spotify ID": track['id']
                        })
                    # Tiny sleep to prevent rate limiting
                    time.sleep(0.05) 
                except Exception as e:
                    # If it's a 403, it's usually a private/invalid track
                    pass
                
                # Update progress bar
                progress = (index + 1) / len(track_ids)
                my_bar.progress(progress, text=f"Processed {index + 1} of {len(track_ids)} tracks")

            if results:
                df = pd.DataFrame(results)
                st.divider()
                
                m1, m2, m3 = st.columns(3)
                m1.metric("Total Tracks Found", len(df))
                m2.metric("Average Popularity", f"{int(df['Rank'].mean())}/100")
                m3.metric("Highest Rank", df['Rank'].max())

                st.dataframe(df.sort_values(by="Rank", ascending=False), use_container_width=True)
                
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("📩 Download Results as CSV", csv, "spotify_analysis.csv", "text/csv")
            else:
                st.error("No data found. Ensure your email is added to 'Users and Access' in Spotify Dashboard.")
        else:
            st.error("❌ No valid links detected.")
    else:
        st.warning("⚠️ Paste links first.")

st.divider()
st.caption("©️ 2026 Developed for Hype Drop Club. Data provided by Spotify.")
