import streamlit as st
import cv2
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components
from PIL import Image

from spotify_client import get_playlists_for_mood
from emotion_detector import detect_emotion_live

# -----------------------------------
# PAGE CONFIG
# -----------------------------------

st.set_page_config(
    page_title="🎵 EmoSonic",
    page_icon="🎧",
    layout="wide"
)

# -----------------------------------
# SESSION STATE
# -----------------------------------

if "mood" not in st.session_state:
    st.session_state["mood"] = None

if "scores" not in st.session_state:
    st.session_state["scores"] = None

if "latest_mood" not in st.session_state:
    st.session_state["latest_mood"] = None

# -----------------------------------
# CUSTOM CSS
# -----------------------------------

st.markdown("""
<style>

.main {
    background-color: #0E1117;
}

h1, h2, h3 {
    color: white;
}

.stButton>button {
    width: 100%;
    border-radius: 15px;
    background: linear-gradient(90deg, #ff4b4b, #ff6b6b);
    color: white;
    border: none;
    padding: 0.6rem;
    font-weight: bold;
}

.stButton>button:hover {
    color: white;
}

div[data-testid="stImage"] img {
    border-radius: 15px;
}

.mood-box {
    background: #1f2937;
    padding: 20px;
    border-radius: 20px;
    text-align: center;
    color: white;
    font-size: 30px;
    font-weight: bold;
    margin-bottom: 20px;
}

.mood-badge {
    display: inline-block;
    padding: 15px 30px;
    border-radius: 50px;
    font-size: 28px;
    font-weight: bold;
    color: white;

    background: linear-gradient(
        135deg,
        #ff4b4b,
        #ff7b54,
        #ff4b4b
    );

    background-size: 200% 200%;

    animation:
        gradientMove 4s ease infinite,
        pulse 2s infinite;

    box-shadow:
        0 0 20px rgba(255,75,75,.5);
}

@keyframes pulse {

    0% {
        transform: scale(1);
    }

    50% {
        transform: scale(1.06);
    }

    100% {
        transform: scale(1);
    }
}

@keyframes gradientMove {

    0% {
        background-position: 0% 50%;
    }

    50% {
        background-position: 100% 50%;
    }

    100% {
        background-position: 0% 50%;
    }
}

@media (max-width: 768px) {

    h1 {
        font-size: 1.8rem !important;
        text-align: center;
    }

    .mood-box {
        font-size: 22px;
    }

    iframe {
        width: 100% !important;
    }

    .stButton>button {
        font-size: 14px;
    }
}

</style>
""", unsafe_allow_html=True)

# -----------------------------------
# HEADER
# -----------------------------------

col1, col2 = st.columns([1, 6])

with col1:
    st.image("img/logo.png", width=90)

with col2:
    st.markdown("""
    <h1 style='padding-top:10px;'>
    🎵 EmoSonic – AI Mood Music Recommender
    </h1>
    """, unsafe_allow_html=True)

st.markdown("---")

MOOD_EMOJIS = {
    "happy": "😊",
    "sad": "😢",
    "angry": "😡",
    "relax": "😌",
    "party": "🥳",
    "focus": "🎯",
    "romantic": "❤️",
    "energetic": "⚡",
    "chill": "🌙",
    "rock": "🎸"
}

# -----------------------------------
# SIDEBAR
# -----------------------------------

with st.sidebar:

    st.header("⚙ Controls")

    input_mode = st.radio(
        "Choose Input Method",
        [
            "🎥 Live Camera",
            "📸 Upload Selfie",
            "🎭 Enter Mood Manually"
        ]
    )

    if st.button("🔄 Reset App"):
        st.session_state["mood"] = None
        st.session_state["scores"] = None
        st.session_state["latest_mood"] = None
        st.rerun()

# -----------------------------------
# LIVE CAMERA MODE
# -----------------------------------

if input_mode == "🎥 Live Camera":

    st.subheader("🎥 Real-Time Emotion Detection")

    run_camera = st.checkbox("Start Camera")

    frame_placeholder = st.empty()
    mood_placeholder = st.empty()
    chart_placeholder = st.empty()

    if run_camera:

        cap = cv2.VideoCapture(0)

        while run_camera:

            success, frame = cap.read()

            if not success:
                st.error("Unable to access camera.")
                break

            frame_rgb = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            frame_placeholder.image(
                frame_rgb,
                channels="RGB",
                width=800,
            )

            try:

                mood, scores = detect_emotion_live(
                    frame_rgb
                )

                st.session_state["mood"] = mood
                st.session_state["latest_mood"] = mood

                emoji = MOOD_EMOJIS.get(
                mood,
                "🎵"
                )

                mood_placeholder.markdown(
                f"""
                <div style="text-align:center;">
                <div class="mood-badge">
                {emoji} {mood.upper()}
                </div>
                </div>
                """,
                unsafe_allow_html=True
                )

                st.session_state["latest_mood"] = mood

            except Exception as e:
                st.error(str(e))

        cap.release()
        st.info("📷 Click START to begin")

# -----------------------------------
# UPLOAD SELFIE MODE
# -----------------------------------

elif input_mode == "📸 Upload Selfie":

    st.subheader("📸 Upload Your Selfie")

    uploaded_file = st.file_uploader(
        "Choose an Image",
        type=["png", "jpg", "jpeg"]
    )

    if uploaded_file:

        image = Image.open(uploaded_file)

        frame = np.array(image)[:, :, :3]

        col1, col2 = st.columns([1, 1])

        with col1:

            st.image(
                frame,
                caption="Uploaded Image",
                use_column_width=True
            )

        try:

            mood, scores = detect_emotion_live(
                frame
            )

            st.session_state["mood"] = mood
            st.session_state["latest_mood"] = mood
            st.session_state["scores"] = scores

            with col2:

                st.markdown(
                    f"""
                    <div class="mood-box">
                    {mood.upper()}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                df_scores = pd.DataFrame(
                    list(scores.items()),
                    columns=["Emotion", "Score"]
                )

                fig = px.line_polar(
                    df_scores,
                    r="Score",
                    theta="Emotion",
                    line_close=True
                )

                fig.update_layout(
                    template="plotly_dark"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

        except Exception as e:
            st.error(f"Error: {e}")

# -----------------------------------
# MANUAL MODE
# -----------------------------------

elif input_mode == "🎭 Enter Mood Manually":

    st.subheader("🎭 Select Your Mood")

    manual_mood = st.selectbox(
        "Choose Your Vibe",
        [
            "happy",
            "sad",
            "angry",
            "relax",
            "party",
            "focus",
            "romantic",
            "energetic"
        ]
    )

    if st.button("🎵 Recommend Music"):

        st.session_state["mood"] = manual_mood

# -----------------------------------
# PLAYLIST SECTION
# -----------------------------------

current_mood = (
    st.session_state.get("latest_mood")
    or st.session_state.get("mood")
)

if current_mood:

    st.markdown("---")

    st.subheader(
        f"🎧 Recommended Playlists for '{current_mood}'"
    )

    playlists = get_playlists_for_mood(
        current_mood
    )

    if not playlists:

        st.warning("No playlists found.")

    else:

        cols = st.columns(2)

        for idx, playlist in enumerate(playlists):

            with cols[idx % 2]:

                playlist_id = playlist.get("id")

                st.markdown(
                    "### 🎵 Spotify Playlist"
                )

                if playlist_id:

                    components.iframe(
                        f"https://open.spotify.com/embed/playlist/{playlist_id}",
                        height=400
                    )

                else:

                    if playlist.get("image"):
                        st.image(
                            playlist["image"]
                        )

                    st.write(
                        f"### {playlist['name']}"
                    )

                    st.markdown(
                        f"[Open in Spotify]({playlist['url']})"
                    )
                    st.markdown("---")

                    st.markdown("""
                    <div style="
                    text-align:center;
                    padding:20px;
                    color:#94a3b8;
                    ">

                    Made with ❤️ using
                    Python • Streamlit • FER • Spotify API

                    </div>
                    """, unsafe_allow_html=True)