# import tensorflow as tf
# import numpy as np
# import cv2
# import subprocess
# import os
# from tensorflow.keras.applications.efficientnet_v2 import preprocess_input
# from tensorflow.keras.models import load_model # The only function we need

# # --- MODEL PARAMETERS ---
# # Make sure this points to your NEW, MODERN model file
# VIDEO_MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models', 'video_model_v3.keras')
# TARGET_SIZE = (224, 224)
# SEQUENCE_LENGTH = 20
# face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# # The model will be loaded on the first request
# video_model = None

# # --- UTILITY FUNCTION (This is correct) ---
# def extract_faces_from_video(video_path):
#     frames_list = []
#     converted_video_path = "temp_converted_video.mp4"
#     subprocess.run(['ffmpeg', '-i', video_path, '-y', converted_video_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#     cap = cv2.VideoCapture(converted_video_path)
#     while len(frames_list) < SEQUENCE_LENGTH:
#         ret, frame = cap.read()
#         if not ret: break
#         gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#         faces = face_cascade.detectMultiScale(gray, 1.1, 5)
#         if len(faces) > 0:
#             (x, y, w, h) = faces[0]
#             face_crop = frame[y:y+h, x:x+w]
#             resized_face = cv2.resize(face_crop, TARGET_SIZE)
#             resized_face = cv2.cvtColor(resized_face, cv2.COLOR_BGR2RGB)
#             frames_list.append(resized_face)
#     cap.release()
#     if os.path.exists(converted_video_path):
#         os.remove(converted_video_path)
#     return frames_list

# # --- PREDICTION FUNCTION (Final Version) ---
# def predict_video(file_path):
#     global video_model

#     # 1. Load the modern model file if it's not already loaded
#     if video_model is None:
#         try:
#             video_model = load_model(VIDEO_MODEL_PATH, compile=False)
#             print("Video Model (loaded on first request).")
#         except Exception as e:
#             return {"result": "Error: Model not loaded.", "confidence": 0.0, "reason": str(e)}

#     # 2. Proceed with prediction
#     try:
#         faces = extract_faces_from_video(file_path)
#         if len(faces) < 5:
#             return {"result": "Prediction failed", "confidence": 0.0, "reason": "Could not detect enough faces in the video."}
            
#         faces_np = np.array(faces).astype('float32')
#         faces_preprocessed = preprocess_input(faces_np)
#         predictions = video_model.predict(faces_preprocessed)
#         avg_prediction = np.mean(predictions)
#         label = "DEEPFAKE" if avg_prediction < 0.5 else "REAL"
#         return {"result": label, "confidence": float(avg_prediction)}
#     except Exception as e:
#         return {"result": "Prediction failed", "confidence": 0.0, "reason": str(e)}

import os
import numpy as np
import cv2
import subprocess
import keras  # FIX: use keras directly

VIDEO_MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models', 'video_model_v3.keras')
TARGET_SIZE = (224, 224)
SEQUENCE_LENGTH = 20
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
video_model = None

def preprocess_input(x):
    # EfficientNetV2 preprocessing — scale to [-1, 1]
    return (x / 127.5) - 1.0

def extract_faces_from_video(video_path):
    frames_list = []
    converted = "temp_converted_video.mp4"
    subprocess.run(['ffmpeg', '-i', video_path, '-y', converted], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    cap = cv2.VideoCapture(converted)
    while len(frames_list) < SEQUENCE_LENGTH:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 5)
        if len(faces) > 0:
            (x, y, w, h) = faces[0]
            face_crop = cv2.resize(frame[y:y+h, x:x+w], TARGET_SIZE)
            face_crop = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB)
            frames_list.append(face_crop)
    cap.release()
    if os.path.exists(converted):
        os.remove(converted)
    return frames_list

def predict_video(file_path):
    global video_model
    if video_model is None:
        try:
            video_model = keras.models.load_model(VIDEO_MODEL_PATH, compile=False)  # FIX
            print("Video model loaded OK.")
        except Exception as e:
            return {"result": "error", "message": f"Model load failed: {str(e)}"}

    try:
        faces = extract_faces_from_video(file_path)
        if len(faces) < 5:
            return {"result": "Prediction failed", "confidence": 0.0, "reason": "Not enough faces detected."}
        faces_np = preprocess_input(np.array(faces).astype('float32'))
        predictions = video_model.predict(faces_np)
        avg = float(np.mean(predictions))
        label = "DEEPFAKE" if avg < 0.5 else "REAL"
        return {"result": label, "confidence": round(avg, 4)}
    except Exception as e:
        return {"result": "Prediction failed", "confidence": 0.0, "reason": str(e)}