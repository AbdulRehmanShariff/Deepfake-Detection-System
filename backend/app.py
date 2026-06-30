import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
import traceback

from image_utils import predict_image
from video_utils import predict_video
from audio_utils import predict_audio
from api_utils import check_misinformation, get_chatbot_response

app = Flask(__name__)

# Correct CORS setup for your Vercel frontend
CORS(
    app,
    resources={
        r"/*": {
            "origins": [
                "https://deepfake-detection-system-sandy.vercel.app"
            ]
        }
    },
    methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    supports_credentials=False
)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/", methods=["GET"])
def home():
    return "Deepfake Detection API is running!"


def handle_file_upload(request, predictor_func, allowed_extensions):
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    if "file" not in request.files:
        return jsonify({"result": "error", "message": "No file part in the request"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"result": "error", "message": "No selected file"}), 400

    filename = file.filename
    if "." not in filename or filename.split(".")[-1].lower() not in allowed_extensions:
        return jsonify({
            "result": "error",
            "message": f"File type not supported. Use: {', '.join(allowed_extensions)}"
        }), 400

    file_extension = filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)

    try:
        file.save(file_path)
        prediction_result = predictor_func(file_path)
        if os.path.exists(file_path):
            os.remove(file_path)
        return jsonify(prediction_result)

    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({
            "result": "error",
            "message": f"Server error: {str(e)}",
            "trace": traceback.format_exc()
        }), 500


@app.route("/predict/image", methods=["POST", "OPTIONS"])
def predict_image_route():
    return handle_file_upload(request, predict_image, ["jpg", "jpeg", "png"])


@app.route("/predict/video", methods=["POST", "OPTIONS"])
def predict_video_route():
    return handle_file_upload(request, predict_video, ["mp4", "mov", "avi"])


@app.route("/predict/audio", methods=["POST", "OPTIONS"])
def predict_audio_route():
    return handle_file_upload(request, predict_audio, ["wav", "mp3", "flac"])


@app.route("/predict/misinformation", methods=["POST", "OPTIONS"])
def check_misinformation_route():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    data = request.get_json(silent=True) or {}
    text = data.get("text", "")

    if not text or len(text) < 10:
        return jsonify({"result": "error", "message": "Text input is too short."}), 400

    result = check_misinformation(text)
    return jsonify(result)


@app.route("/chat", methods=["POST", "OPTIONS"])
def chatbot_route():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    data = request.get_json(silent=True) or {}
    message = data.get("message", "")

    if not message:
        return jsonify({"result": "error", "message": "No message provided."}), 400

    response = get_chatbot_response(message)
    return jsonify(response)


@app.route("/debug/versions", methods=["GET"])
def debug_versions():
    import keras
    import sys
    import tensorflow as tf

    return jsonify({
        "tensorflow": tf.__version__,
        "keras": keras.__version__,
        "python": sys.version,
        "keras_path": keras.__file__,
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)