import streamlit as st

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Hype Drop Club", page_icon="🩸", layout="wide")

# --- CUSTOM CSS FOR BRANDING ---
st.markdown("""
    <style>
    .main {
        background-color: #000000;
        color: #ffffff;
    }
    .stAlert {
        background-color: #2b2b2b;
        color: #ffffff;
        border: 1px solid #ee631d;
    }
    h1, h2, h3 {
        color: #ee631d !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- MAINTENANCE HEADER ---
st.title("Hype Drop Club 🩸")
st.divider()

st.header("🛠️ Systems Update in Progress")
st.info("""
**We are currently upgrading the Hype Drop Club engine.**

To ensure we provide the most accurate algorithmic data following recent platform shifts, the Bulk Popularity Checker is temporarily offline for maintenance. 

**What's happening:**
* Migrating to a new high-speed data architecture.
* Enhancing security for bulk catalog uploads.
* Integrating deeper algorithmic trend insights.

Check back soon—we are working to bring the new and improved toolkit live for all subscribers shortly.
""")

# --- FOOTER ---
st.divider()
st.caption("©️ 2026 Hype Drop Club. All systems currently being optimized.")
