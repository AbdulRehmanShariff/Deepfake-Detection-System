import tensorflow as tf
import numpy as np
import cv2
import subprocess
import os
from tensorflow.keras.applications.efficientnet_v2 import preprocess_input
from tensorflow.keras.models import load_model # The only function we need

# --- MODEL PARAMETERS ---
# Make sure this points to your NEW, MODERN model file
VIDEO_MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models', 'video_model_v3.keras')
TARGET_SIZE = (224, 224)
SEQUENCE_LENGTH = 20
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# The model will be loaded on the first request
video_model = None

# --- UTILITY FUNCTION (This is correct) ---
def extract_faces_from_video(video_path):
    frames_list = []
    converted_video_path = "temp_converted_video.mp4"
    subprocess.run(['ffmpeg', '-i', video_path, '-y', converted_video_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    cap = cv2.VideoCapture(converted_video_path)
    while len(frames_list) < SEQUENCE_LENGTH:
        ret, frame = cap.read()
        if not ret: break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 5)
        if len(faces) > 0:
            (x, y, w, h) = faces[0]
            face_crop = frame[y:y+h, x:x+w]
            resized_face = cv2.resize(face_crop, TARGET_SIZE)
            resized_face = cv2.cvtColor(resized_face, cv2.COLOR_BGR2RGB)
            frames_list.append(resized_face)
    cap.release()
    if os.path.exists(converted_video_path):
        os.remove(converted_video_path)
    return frames_list

# --- PREDICTION FUNCTION (Final Version) ---
def predict_video(file_path):
    global video_model

    # 1. Load the modern model file if it's not already loaded
    if video_model is None:
        try:
            video_model = load_model(VIDEO_MODEL_PATH, compile=False)
            print("Video Model (loaded on first request).")
        except Exception as e:
            return {"result": "Error: Model not loaded.", "confidence": 0.0, "reason": str(e)}

    # 2. Proceed with prediction
    try:
        faces = extract_faces_from_video(file_path)
        if len(faces) < 5:
            return {"result": "Prediction failed", "confidence": 0.0, "reason": "Could not detect enough faces in the video."}
            
        faces_np = np.array(faces).astype('float32')
        faces_preprocessed = preprocess_input(faces_np)
        predictions = video_model.predict(faces_preprocessed)
        avg_prediction = np.mean(predictions)
        label = "DEEPFAKE" if avg_prediction < 0.5 else "REAL"
        return {"result": label, "confidence": float(avg_prediction)}
    except Exception as e:
        return {"result": "Prediction failed", "confidence": 0.0, "reason": str(e)}