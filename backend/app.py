# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import os
# import uuid

# # Import the prediction functions from our utility files
# from image_utils import predict_image
# from video_utils import predict_video
# from audio_utils import predict_audio
# from api_utils import check_misinformation, get_chatbot_response

# # --- FLASK SETUP ---
# app = Flask(__name__)
# CORS(app)

# UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
# if not os.path.exists(UPLOAD_FOLDER):
#     os.makedirs(UPLOAD_FOLDER)
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# @app.route('/', methods=['GET'])
# def home():
#     return "Deepfake Detection API is running!"

# def handle_file_upload(request, predictor_func, allowed_extensions):
#     if 'file' not in request.files:
#         return jsonify({"result": "error", "message": "No file part in the request"}), 400
    
#     file = request.files['file']
#     if file.filename == '':
#         return jsonify({"result": "error", "message": "No selected file"}), 400

#     filename = file.filename
#     if '.' not in filename or filename.split('.')[-1].lower() not in allowed_extensions:
#         return jsonify({"result": "error", "message": f"File type not supported. Use: {', '.join(allowed_extensions)}"}), 400

#     file_extension = filename.split('.')[-1]
#     unique_filename = str(uuid.uuid4()) + '.' + file_extension
#     file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    
#     try:
#         file.save(file_path)
#         prediction_result = predictor_func(file_path)
#         os.remove(file_path) # Cleanup
#         return jsonify(prediction_result)
#     except Exception as e:
#         if os.path.exists(file_path):
#             os.remove(file_path)
#         return jsonify({"result": "error", "message": f"Server processing error: {e}"}), 500

# # --- IMAGE DETECTION ENDPOINT ---
# @app.route('/predict/image', methods=['POST'])
# def predict_image_route():
#     return handle_file_upload(request, predict_image, ['jpg', 'jpeg', 'png'])

# # --- VIDEO DETECTION ENDPOINT ---
# @app.route('/predict/video', methods=['POST'])
# def predict_video_route():
#     return handle_file_upload(request, predict_video, ['mp4', 'mov', 'avi'])

# # --- AUDIO DETECTION ENDPOINT ---
# @app.route('/predict/audio', methods=['POST'])
# def predict_audio_route():
#     return handle_file_upload(request, predict_audio, ['wav', 'mp3', 'flac'])

# # --- MISINFORMATION DETECTION ENDPOINT ---
# @app.route('/predict/misinformation', methods=['POST'])
# def check_misinformation_route():
#     data = request.get_json()
#     text = data.get('text', '')
#     if not text or len(text) < 10:
#         return jsonify({"result": "error", "message": "Text input is too short."}), 400
#     result = check_misinformation(text) 
#     return jsonify(result)

# # --- CHATBOT ASSISTANCE ENDPOINT ---
# @app.route('/chat', methods=['POST'])
# def chatbot_route():
#     data = request.get_json()
#     message = data.get('message', '')
#     if not message:
#         return jsonify({"result": "error", "message": "No message provided."}), 400
#     response = get_chatbot_response(message)
#     return jsonify(response)

# @app.route("/debug/versions")
# def debug_versions():
#     import tensorflow as tf
#     import keras
#     import sys

#     return jsonify({
#         "tensorflow": tf.__version__,
#         "keras": keras.__version__,
#         "python": sys.version,
#         "keras_path": keras.__file__,
#     })
# # --- START THE SERVER ---
# if __name__ == '__main__':
#     app.run(debug=True, port=5000)


from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid

from image_utils import predict_image
from video_utils import predict_video
from audio_utils import predict_audio
from api_utils import check_misinformation, get_chatbot_response

app = Flask(__name__)

# FIX: explicitly cover all origins and include error responses
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=False)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# FIX: attach CORS headers even on error responses
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/', methods=['GET'])
def home():
    return "Deepfake Detection API is running!"

def handle_file_upload(request, predictor_func, allowed_extensions):
    if 'file' not in request.files:
        return jsonify({"result": "error", "message": "No file part in the request"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"result": "error", "message": "No selected file"}), 400
    filename = file.filename
    if '.' not in filename or filename.split('.')[-1].lower() not in allowed_extensions:
        return jsonify({"result": "error", "message": f"File type not supported. Use: {', '.join(allowed_extensions)}"}), 400
    file_extension = filename.split('.')[-1]
    unique_filename = str(uuid.uuid4()) + '.' + file_extension
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    try:
        file.save(file_path)
        prediction_result = predictor_func(file_path)
        os.remove(file_path)
        return jsonify(prediction_result)
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        import traceback
        return jsonify({"result": "error", "message": f"Server error: {str(e)}", "trace": traceback.format_exc()}), 500

@app.route('/predict/image', methods=['POST'])
def predict_image_route():
    return handle_file_upload(request, predict_image, ['jpg', 'jpeg', 'png'])

@app.route('/predict/video', methods=['POST'])
def predict_video_route():
    return handle_file_upload(request, predict_video, ['mp4', 'mov', 'avi'])

@app.route('/predict/audio', methods=['POST'])
def predict_audio_route():
    return handle_file_upload(request, predict_audio, ['wav', 'mp3', 'flac'])

@app.route('/predict/misinformation', methods=['POST'])
def check_misinformation_route():
    data = request.get_json()
    text = data.get('text', '')
    if not text or len(text) < 10:
        return jsonify({"result": "error", "message": "Text input is too short."}), 400
    result = check_misinformation(text)
    return jsonify(result)

@app.route('/chat', methods=['POST'])
def chatbot_route():
    data = request.get_json()
    message = data.get('message', '')
    if not message:
        return jsonify({"result": "error", "message": "No message provided."}), 400
    response = get_chatbot_response(message)
    return jsonify(response)

@app.route("/debug/versions")
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

if __name__ == '__main__':
    app.run(debug=True, port=5000)