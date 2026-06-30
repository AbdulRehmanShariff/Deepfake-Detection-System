import os
import traceback

import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image

# -----------------------------
# MODEL CONFIGURATION
# -----------------------------
IMAGE_MODEL_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "models",
    "image_model_v3.keras"
)

TARGET_SIZE = (224, 224)
PREDICTION_THRESHOLD = 0.35

# Load model only once
image_model = None


def predict_image(file_path):
    global image_model

    # -----------------------------
    # Load model (first request only)
    # -----------------------------
    if image_model is None:
        try:
            print("=" * 60)
            print("Loading Image Model...")
            print("Model Path:", IMAGE_MODEL_PATH)

            image_model = tf.keras.models.load_model(
                IMAGE_MODEL_PATH,
                compile=False
            )

            print("Image model loaded successfully.")
            print("=" * 60)

        except Exception:
            import traceback

            print("=" * 60)
            print("IMAGE MODEL LOAD ERROR")
            traceback.print_exc()
            print("=" * 60)

            raise
    # if image_model is None:
    #     try:
    #         print("=" * 60)
    #         print("Loading Image Model...")
    #         print("Model Path:", IMAGE_MODEL_PATH)

    #         image_model = tf.keras.models.load_model(
    #             IMAGE_MODEL_PATH,
    #             compile=False
    #         )

    #         print("Image model loaded successfully.")
    #         print("=" * 60)

    #     except Exception:
    #         print("=" * 60)
    #         print("IMAGE MODEL LOAD ERROR")
    #         traceback.print_exc()
    #         print("=" * 60)

    #         return {
    #             "result": "Error: Model not loaded.",
    #             "confidence": 0.0,
    #             "reason": traceback.format_exc()
    #         }

    # -----------------------------
    # Prediction
    # -----------------------------
    try:
        test_image = image.load_img(
            file_path,
            target_size=TARGET_SIZE
        )

        image_array = image.img_to_array(test_image)
        image_array = np.expand_dims(image_array, axis=0)
        image_array = image_array / 255.0

        prediction = image_model.predict(
            image_array,
            verbose=0
        )

        prediction_value = float(prediction[0][0])

        if prediction_value < PREDICTION_THRESHOLD:
            label = "DEEPFAKE"
        else:
            label = "REAL"

        return {
            "result": label,
            "confidence": prediction_value
        }

    except Exception:
        print("=" * 60)
        print("IMAGE PREDICTION ERROR")
        traceback.print_exc()
        print("=" * 60)

        return {
            "result": "Prediction failed",
            "confidence": 0.0,
            "reason": traceback.format_exc()
        }