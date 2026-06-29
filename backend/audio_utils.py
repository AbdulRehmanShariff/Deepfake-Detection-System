import tensorflow as tf
import numpy as np
import librosa
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import load_model # The only function we need

# --- MODEL PARAMETERS ---
# Make sure this points to your NEW, MODERN model file
import os
AUDIO_MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models', 'audio_model_v3.keras') 
MAX_PAD_LEN = 216
N_MFCC = 40
DURATION = 5

# The model will be loaded on the first request
audio_model = None

# --- UTILITY FUNCTION ---
def extract_mfcc(filepath, duration=DURATION, n_mfcc=N_MFCC):
    try:
        y, sr = librosa.load(filepath, duration=duration)
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
        return mfccs.T
    except Exception as e:
        print(f"Error during MFCC extraction: {e}")
        return None

# --- PREDICTION FUNCTION (Final Version) ---
def predict_audio(file_path):
    global audio_model

    # 1. Load the modern model file if it's not already loaded
    if audio_model is None:
        try:
            # This is the simplest and most reliable way
            audio_model = load_model(AUDIO_MODEL_PATH, compile=False)
            print("Audio Model (loaded on first request).")
        except Exception as e:
            return {"result": "Error: Model not loaded.", "confidence": 0.0, "reason": str(e)}

    # 2. Proceed with prediction
    try:
        new_audio_mfcc = extract_mfcc(file_path)
        if new_audio_mfcc is None:
            return {"result": "Prediction failed", "confidence": 0.0, "reason": "Audio file is corrupt or has an unsupported format."}

        padded_mfcc = pad_sequences(
            [new_audio_mfcc], maxlen=MAX_PAD_LEN, padding='post', truncating='post', dtype='float32'
        )[0]
        
        model_input = np.expand_dims(padded_mfcc, axis=0)
        prediction_score = audio_model.predict(model_input)[0][0]

        # Use a standard 0.5 threshold for now
        label = "DEEPFAKE" if prediction_score < 0.5 else "REAL"

        return { "result": label, "confidence": float(prediction_score) }
    except Exception as e:
        return {"result": "Prediction failed", "confidence": 0.0, "reason": str(e)}