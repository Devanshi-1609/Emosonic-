import cv2
import numpy as np
from fer import FER

# -----------------------------------
# EMOTION TO MUSIC MOOD MAPPING
# -----------------------------------

EMOTION_TO_MOOD = {
    "happy": "happy",
    "sad": "sad",
    "angry": "energetic",
    "fear": "chill",
    "surprise": "party",
    "disgust": "rock",
    "neutral": "relax"
}

# -----------------------------------
# INITIALIZE DETECTOR
# -----------------------------------

# mtcnn=False makes detection MUCH faster
# Better for deployment + mobile devices

detector = FER(mtcnn=False)

# -----------------------------------
# MAIN DETECTION FUNCTION
# -----------------------------------

def detect_emotion_live(frame: np.ndarray):

    """
    Detect emotion from image frame
    Returns:
        mood (str)
        emotions (dict)
    """

    try:

        # -----------------------------------
        # VALIDATION
        # -----------------------------------

        if frame is None:
            return "relax", {"neutral": 1.0}

        if not isinstance(frame, np.ndarray):
            return "relax", {"neutral": 1.0}

        # -----------------------------------
        # HANDLE RGBA IMAGES
        # -----------------------------------

        if len(frame.shape) == 3 and frame.shape[2] == 4:
            frame = frame[:, :, :3]

        # -----------------------------------
        # RESIZE FOR PERFORMANCE
        # -----------------------------------

        height, width = frame.shape[:2]

        if width > 640:
            scale = 640 / width
            frame = cv2.resize(
                frame,
                (
                    int(width * scale),
                    int(height * scale)
                )
            )

        # -----------------------------------
        # ENSURE RGB FORMAT
        # -----------------------------------

        if frame.shape[2] == 3:
            rgb_frame = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )
        else:
            rgb_frame = frame

        # -----------------------------------
        # DETECT EMOTIONS
        # -----------------------------------

        results = detector.detect_emotions(rgb_frame)

        # -----------------------------------
        # NO FACE DETECTED
        # -----------------------------------

        if not results:

            emotions = {
                "neutral": 1.0
            }

            return "relax", emotions

        # -----------------------------------
        # GET TOP FACE
        # -----------------------------------

        emotions = results[0]["emotions"]

        # -----------------------------------
        # DETECT STRONGEST EMOTION
        # -----------------------------------

        detected_emotion = max(
            emotions,
            key=emotions.get
        )

        # -----------------------------------
        # MAP TO MUSIC MOOD
        # -----------------------------------

        mood = EMOTION_TO_MOOD.get(
            detected_emotion,
            "relax"
        )

        return mood, emotions

    except Exception as e:

        print(f"Emotion Detection Error: {e}")

        return "relax", {"neutral": 1.0}