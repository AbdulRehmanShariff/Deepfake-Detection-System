# import tensorflow as tf
# import numpy as np
# from tensorflow.keras.preprocessing import image
# from tensorflow.keras.models import Model

# # --- IMPORTS FOR YOUR EXACT XCEPTION MODEL ---
# from tensorflow.keras.applications import Xception
# from tensorflow.keras.layers import GlobalAveragePooling2D, Dense
# # --- END IMPORTS ---

# # --- MODEL PARAMETERS ---
# IMAGE_MODEL_PATH = 'models/image_model_v3.keras' # Using the modern file
# TARGET_SIZE = (224, 224)
# PREDICTION_THRESHOLD = 0.35
# image_model = None

# # --- PREDICTION FUNCTION ---
# def predict_image(file_path):
#     global image_model
    
#     # 1. Load model only if it's not already loaded
#     if image_model is None:
#         try:
#             # Step A: Rebuild the exact Xception architecture
#             base_model = Xception(weights=None, include_top=False, input_shape=(224, 224, 3))
#             x = base_model.output
#             x = GlobalAveragePooling2D()(x)
#             x = Dense(512, activation='relu')(x)
#             predictions = Dense(1, activation='sigmoid')(x)
#             image_model = Model(inputs=base_model.input, outputs=predictions)

#             # Step B: Load your trained weights into this perfect blueprint
#             image_model.load_weights(IMAGE_MODEL_PATH)
            
#             print("✅ Image Model loaded successfully using Xception blueprint.")
#         except Exception as e:
#             return {"result": "Error: Model not loaded.", "confidence": 0.0, "reason": str(e)}
    
#     # 2. Proceed with prediction
#     try:
#         test_image = image.load_img(file_path, target_size=TARGET_SIZE)
#         image_array = image.img_to_array(test_image)
#         image_array = np.expand_dims(image_array, axis=0)
#         image_array /= 255.0

#         prediction = image_model.predict(image_array)
#         prediction_value = prediction[0][0]

#         label = "DEEPFAKE" if prediction_value < PREDICTION_THRESHOLD else "REAL"

#         return { "result": label, "confidence": float(prediction_value) }
#     except Exception as e:
#         return {"result": "Prediction failed", "confidence": 0.0, "reason": str(e)}

import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image

# --- MODEL PARAMETERS ---
import os
IMAGE_MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models', 'image_model_v3.keras')
TARGET_SIZE = (224, 224)
PREDICTION_THRESHOLD = 0.35

# Load only once
image_model = None


def predict_image(file_path):
    global image_model

    # Load model only on the first request
    if image_model is None:
        try:
            image_model = tf.keras.models.load_model(
                IMAGE_MODEL_PATH,
                compile=False
            )

            print("Image model loaded successfully.")

        except Exception as e:
            return {
                "result": "Error: Model not loaded.",
                "confidence": 0.0,
                "reason": str(e)
            }

    try:
        # Load image
        test_image = image.load_img(file_path, target_size=TARGET_SIZE)
        image_array = image.img_to_array(test_image)
        image_array = np.expand_dims(image_array, axis=0)
        image_array = image_array / 255.0

        # Predict
        prediction = image_model.predict(image_array, verbose=0)
        prediction_value = float(prediction[0][0])

        # Classification
        if prediction_value < PREDICTION_THRESHOLD:
            label = "DEEPFAKE"
        else:
            label = "REAL"

        return {
            "result": label,
            "confidence": prediction_value
        }

    except Exception as e:
        return {
            "result": "Prediction failed",
            "confidence": 0.0,
            "reason": str(e)
        }