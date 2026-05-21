import cv2
from fer import FER
import numpy as np

# Map detected emotions to playlist-friendly moods
EMOTION_TO_MOOD = {
    "happy": "happy",
    "sad": "sad",
    "angry": "energetic",
    "fear": "chill",
    "surprise": "party",
    "disgust": "rock",
    "neutral": "relax"
}

# Initialize FER detector once (faster if reused)
detector = FER(mtcnn=True)

# emotion_detector.py

def detect_emotion_live(frame: np.ndarray):
    """
    Detects emotion from a frame and returns the mapped mood 
    AND the raw emotion probabilities.
    """
    if frame is None:
        raise ValueError("No image/frame provided")

    # Ensure frame is in RGB format
    if frame.shape[2] == 4:
        frame = frame[:, :, :3]

    result = detector.detect_emotions(frame)

    if result:
        # Get the dictionary of emotions (e.g., {'happy': 0.9, 'sad': 0.02, ...})
        emotions = result[0]["emotions"]
        detected_emotion = max(emotions, key=emotions.get)
    else:
        emotions = {"neutral": 1.0}
        detected_emotion = "neutral"

    mood = EMOTION_TO_MOOD.get(detected_emotion, "relax")
    
    # Return both the mood AND the raw scores dictionary
    return mood, emotions