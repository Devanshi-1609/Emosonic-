import streamlit as st
import cv2
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components
from PIL import Image
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import av

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

    mood_placeholder = st.empty()
    chart_placeholder = st.empty()

    class EmotionProcessor(VideoTransformerBase):

        def transform(self, frame):

            img = frame.to_ndarray(format="bgr24")

            img = cv2.resize(img, (640, 480))

            rgb_frame = cv2.cvtColor(
                img,
                cv2.COLOR_BGR2RGB
            )

            try:

                mood, scores = detect_emotion_live(
                    rgb_frame
                )

                # DEBUG
                print("Detected Mood:", mood)

                # SAVE
                st.session_state["latest_mood"] = mood
                st.session_state["scores"] = scores

                # MOOD DISPLAY
                mood_placeholder.success(
                    f"Detected Mood: {mood.upper()}"
                )

                # CHART
                df_scores = pd.DataFrame(
                    list(scores.items()),
                    columns=["Emotion", "Score"]
                )

                fig = px.bar(
                    df_scores,
                    x="Score",
                    y="Emotion",
                    orientation="h",
                    color="Score",
                    range_x=[0, 1]
                )

                fig.update_layout(
                    height=350,
                    template="plotly_dark"
                )

                chart_placeholder.plotly_chart(
                    fig,
                    use_container_width=True
                )

            except Exception as e:
                print(e)

            return av.VideoFrame.from_ndarray(
                img,
                format="bgr24"
            )

    webrtc_ctx = webrtc_streamer(
        key="emotion-detection",
        video_transformer_factory=EmotionProcessor,
        media_stream_constraints={
            "video": {
                "width": {"ideal": 640},
                "height": {"ideal": 480},
                "facingMode": "user"
            },
            "audio": False,
        },
        async_processing=True
    )

    if webrtc_ctx.state.playing:
        st.success("✅ Camera Started Successfully")
    else:
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