import React, { useState } from "react";
import axios from "axios";

// const API_URL = "http://127.0.0.1:5000";
const API_URL = "https://deepfake-detection-system-bwn3.onrender.com";

function ImageDetector() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [preview, setPreview] = useState(null);
  const [isDragOver, setIsDragOver] = useState(false);

  const handleFileChange = (selectedFile) => {
    if (!selectedFile) return;
    setFile(selectedFile);
    setResult(null);
    setError("");
    setPreview(URL.createObjectURL(selectedFile));
  };

  const handleClear = () => {
    setFile(null);
    setResult(null);
    setError("");
    setPreview(null);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);
    setIsLoading(true);
    try {
      const response = await axios.post(`${API_URL}/predict/image`, formData);
      // const response = await axios.post(`${API_URL}/predict/image`, formData, {
      //   headers: {
      //     "Content-Type": "multipart/form-data",
      //     "ngrok-skip-browser-warning": "true", // <--- THIS IS THE KEY FIX
      //   },
      // });
      setResult(response.data);
    } catch (err) {
      setError(
        "Analysis failed. Please ensure the backend is running and the file is valid.",
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };
  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };
  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    const droppedFile = e.dataTransfer.files[0];
    if (
      droppedFile &&
      (droppedFile.type === "image/jpeg" || droppedFile.type === "image/png")
    ) {
      handleFileChange(droppedFile);
    }
  };

  return (
    <div className="detector-container">
      <h2>🖼️ Image Deepfake Detector</h2>

      {!preview && (
        <div
          className={`drop-zone ${isDragOver ? "drag-over" : ""}`}
          onClick={() => document.getElementById("file-upload").click()}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <input
            id="file-upload"
            type="file"
            onChange={(e) => handleFileChange(e.target.files[0])}
            accept="image/jpeg,image/png"
          />
          <p>Drag & Drop an Image Here</p>
          <small>or click to select (JPG, PNG)</small>
        </div>
      )}

      {preview && (
        <div className="preview-container">
          <img src={preview} alt="Selected Preview" />
        </div>
      )}

      <div className="button-group">
        {file && !isLoading && !result && (
          <button type="button" className="btn" onClick={handleSubmit}>
            Analyze Image
          </button>
        )}
        {preview && (
          <button type="button" className="btn btn-clear" onClick={handleClear}>
            Clear
          </button>
        )}
      </div>

      {isLoading && (
        <div className="spinner-container">
          <div className="spinner"></div>
        </div>
      )}
      {error && (
        <p style={{ color: "var(--danger-color)", textAlign: "center" }}>
          {error}
        </p>
      )}

      {result && (
        <div
          className={`result-card ${
            result.result === "REAL" ? "result-real" : "result-deepfake"
          }`}
        >
          <h4>{result.result}</h4>
          <p>
            The model's confidence score is **
            {(result.confidence * 100).toFixed(2)}%**.
          </p>
        </div>
      )}
    </div>
  );
}

export default ImageDetector;
