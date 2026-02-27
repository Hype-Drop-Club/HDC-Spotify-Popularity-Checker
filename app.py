import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import re

# SECURE SETUP: This pulls from the hidden Streamlit Secrets vault
try:
    CLIENT_ID = st.secrets["SPOTIFY_CLIENT_ID"]
    CLIENT_SECRET = st.secrets["SPOTIFY_CLIENT_SECRET"]
    
    auth_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    sp = spotipy.Spotify(auth_manager=auth_manager)
except Exception as e:
    st.error("Secrets not configured. Please add SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in the Streamlit Settings.")
    st.stop()

# PAGE CONFIG
st.set_page_config(page_title="Bulk Popularity Checker", page_icon="🎵")
st.title("🎵 Bulk Spotify Popularity Checker")
st.write("Paste your Spotify track URLs below (one per line).")

# INPUT BOX
user_input = st.text_area("Spotify URLs", height=200, placeholder="https://open.spotify.com/track/...")

if st.button("Get Popularity Scores"):
    if user_input:
        # Extract Track IDs using Regular Expressions
        links = user_input.split('\n')
        track_ids = []
        for link in links:
            # Matches the ID part of the URL
            match = re.search(r"track/([a-zA-Z0-9]+)", link)
            if match:
                track_ids.append(match.group(1))
        
        if track_ids:
            with st.spinner(f'Fetching data for {len(track_ids)} tracks...'):
                results = []
                
                # BATCHING: Spotify allows 50 tracks per request
                # This is the "guidance" part: we don't spam the API!
                for i in range(0, len(track_ids), 50):
                    batch = track_ids[i:i+50]
                    try:
                        tracks_data = sp.tracks(batch)
                        
                        for track in tracks_data['tracks']:
                            if track: # Ensure track exists
                                results.append({
                                    "Song": track['name'],
                                    "Artist": track['artists'][0]['name'],
                                    "Popularity": track['popularity'],
                                    "Link": f"https://open.spotify.com/track/{track['id']}"
                                })
                    except Exception as e:
                        st.error(f"Error fetching batch: {e}")
                
                # DISPLAY RESULTS
                if results:
                    df = pd.DataFrame(results)
                    st.success(f"Successfully fetched {len(results)} tracks!")
                    st.dataframe(df, use_container_width=True)
                    
                    # DOWNLOAD OPTION
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button("Download results as CSV", csv, "spotify_popularity.csv", "text/csv")
        else:
            st.error("No valid Spotify track URLs found. Make sure they include 'track/ID'.")
    else:
        st.warning("Please paste some links first!")
