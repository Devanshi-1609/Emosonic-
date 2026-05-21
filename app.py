import streamlit as st
import cv2
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components
from PIL import Image
from spotify_client import get_playlists_for_mood
from emotion_detector import detect_emotion_live

st.set_page_config(page_title="🎵 EmoSonic – Mood Music", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .stButton>button { width: 100%; border-radius: 20px; }
    div[data-testid="stImage"] img { border-radius: 10px; }
    /* Optional: Fix vertical alignment so logo and text line up nicely */
    div[data-testid="column"] { display: flex; align-items: center; } 
</style>
""", unsafe_allow_html=True)

# Define your logo path
logo_path = "img/logo.png"

# Create two columns: a small one for the logo (width=1), and a wide one for the title (width=5)
col1, col2 = st.columns([0.7, 7]) 

with col1:
    # Display the logo (adjust width if needed)
    st.image("img/logo.png", width=80) 

with col2:
    # Use HTML to vertically center the text with the logo and tweak margin
    st.markdown("""
        <h1 style='margin-top: -5px; padding-bottom: 30px;'>
            EmoSonic – AI Mood RECOMMENDER
        </h1>
    """, unsafe_allow_html=True)

# ------------------------------
# 💾 Session State Initialization
# ------------------------------
# This ensures variables survive the script re-run when buttons are clicked
if 'mood' not in st.session_state:
    st.session_state['mood'] = None
if 'scores' not in st.session_state:
    st.session_state['scores'] = None

# ------------------------------
# 🎛 Sidebar
# ------------------------------
with st.sidebar:
    st.header("Controls")
    input_mode = st.radio("Input Source:", ["Live Camera", "Upload Selfie", "Enter Mood Manually"])
    
    if st.button("🔄 Reset App"):
        st.session_state['mood'] = None
        st.session_state['scores'] = None
        st.rerun()

# ------------------------------
# 1️⃣ Live Camera Mode
# ------------------------------
if input_mode == "Live Camera":
    col1, col2 = st.columns([3, 1])
    
    with col1:
        run_camera = st.checkbox("Start Live Camera 🎥")
        frame_placeholder = st.empty()

    with col2:
        mood_text_placeholder = st.empty()
        chart_placeholder = st.empty()

    if run_camera:
        cap = cv2.VideoCapture(0)
        
        while run_camera:
            ret, frame = cap.read()
            if not ret:
                st.error("Camera not detected.")
                break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_placeholder.image(frame_rgb, channels="RGB", use_column_width=True, width=850)

            try:
                # Detect
                mood, scores = detect_emotion_live(frame_rgb)
                
                # Update State
                st.session_state['mood'] = mood
                st.session_state['scores'] = scores
                
                # Live Feedback
                mood_text_placeholder.markdown(f"### Detected: **{mood.upper()}**")
                
                # Live Chart
                df_scores = pd.DataFrame(list(scores.items()), columns=['Emotion', 'Score'])
                fig = px.bar(df_scores, x='Score', y='Emotion', orientation='h', color='Score', range_x=[0,1])
                fig.update_layout(height=200, margin=dict(l=0, r=0, t=0, b=0))
                chart_placeholder.plotly_chart(fig, use_container_width=True, key="live_chart")
                
            except Exception:
                pass

        cap.release()

# ------------------------------
# 2️⃣ Upload Selfie Mode
# ------------------------------
elif input_mode == "Upload Selfie":
    uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        frame = np.array(image)[:, :, :3]
        
        col1, col2 = st.columns([1, 1])
        with col1:
            st.image(frame, caption="Your Selfie", use_column_width=True)
        
        try:
            mood, scores = detect_emotion_live(frame)
            st.session_state['mood'] = mood
            st.session_state['scores'] = scores
            
            with col2:
                st.success(f"### Detected Mood: {mood.title()}")
                df_scores = pd.DataFrame(list(scores.items()), columns=['Emotion', 'Score'])
                fig = px.line_polar(df_scores, r='Score', theta='Emotion', line_close=True, title="Emotion Radar")
                st.plotly_chart(fig, use_container_width=True)
                
        except Exception as e:
            st.error(f"Error: {e}")

# ------------------------------
# 3️⃣ Manual Mode
# ------------------------------
elif input_mode == "Enter Mood Manually":
    manual_mood = st.selectbox("Select your vibe:", ["happy", "sad", "energetic", "relax", "party", "focus"])
    if st.button("Get Music"):
        st.session_state['mood'] = manual_mood

# ------------------------------
# 🎵 Playlist Generation (Always Visible if Mood Exists)
# ------------------------------
if st.session_state['mood']:
    st.markdown("---")
    st.subheader(f"🎧 Playlists for '{st.session_state['mood']}'")
    
    playlists = get_playlists_for_mood(st.session_state['mood'])

    if not playlists:
        st.warning("No playlists found.")
    else:
        cols = st.columns(3)
        for idx, playlist in enumerate(playlists):
            with cols[idx % 3]:
                playlist_id = playlist.get('id')
                
                # --- CORRECT EMBED CODE ---
                if playlist_id:
                    components.iframe(f"https://open.spotify.com/embed/playlist/{playlist_id}", height=380)
                else:
                    # Fallback if ID is missing
                    if playlist.get('image'):
                        st.image(playlist['image'])
                    st.write(f"**{playlist['name']}**")
                    st.markdown(f"[Open in Spotify]({playlist['url']})")