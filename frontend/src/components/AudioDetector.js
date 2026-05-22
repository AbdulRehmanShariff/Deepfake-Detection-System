import React, { useState } from "react";
import axios from "axios";

const API_URL = "http://127.0.0.1:5000";
// const API_URL = "https://unarbitrarily-impostrous-dino.ngrok-free.dev";

function AudioDetector() {
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
      const response = await axios.post(`${API_URL}/predict/audio`, formData);
      // const response = await axios.post(`${API_URL}/predict/audio`, formData, {
      //   headers: {
      //     "Content-Type": "multipart/form-data",
      //     "ngrok-skip-browser-warning": "true",
      //   },
      // });
      setResult(response.data);
    } catch (err) {
      setError(
        "Analysis failed. Please ensure the backend is running and the file is valid."
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
      (droppedFile.type === "audio/wav" || droppedFile.type === "audio/mpeg")
    ) {
      handleFileChange(droppedFile);
    }
  };

  return (
    <div className="detector-container">
      <h2>🎤 Audio Deepfake Detector</h2>

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
            accept="audio/wav,audio/mpeg"
          />
          <p>Drag & Drop an Audio File Here</p>
          <small>or click to select (WAV, MP3)</small>
        </div>
      )}

      {preview && (
        <div className="preview-container">
          <audio src={preview} controls />
        </div>
      )}

      <div className="button-group">
        {file && !isLoading && !result && (
          <button type="button" className="btn" onClick={handleSubmit}>
            Analyze Audio
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

export default AudioDetector;
