// import React, { useState } from "react";
// import axios from "axios";

// // const API_URL = "http://127.0.0.1:5000";
// const API_URL = "https://deepfake-detection-system-bwn3.onrender.com";

// function VideoDetector() {
//   const [file, setFile] = useState(null);
//   const [result, setResult] = useState(null);
//   const [error, setError] = useState("");
//   const [isLoading, setIsLoading] = useState(false);
//   const [preview, setPreview] = useState(null);
//   const [isDragOver, setIsDragOver] = useState(false);

//   const handleFileChange = (selectedFile) => {
//     if (!selectedFile) return;
//     setFile(selectedFile);
//     setResult(null);
//     setError("");
//     setPreview(URL.createObjectURL(selectedFile));
//   };

//   const handleClear = () => {
//     setFile(null);
//     setResult(null);
//     setError("");
//     setPreview(null);
//   };

//   const handleSubmit = async (event) => {
//     event.preventDefault();
//     if (!file) return;
//     const formData = new FormData();
//     formData.append("file", file);
//     setIsLoading(true);
//     try {
//       const response = await axios.post(`${API_URL}/predict/video`, formData);
//       // const response = await axios.post(`${API_URL}/predict/video`, formData, {
//       //   headers: {
//       //     "Content-Type": "multipart/form-data",
//       //     "ngrok-skip-browser-warning": "true",
//       //   },
//       // });
//       setResult(response.data);
//     } catch (err) {
//       console.error("Backend Error:", err.response?.data);
//       setError(
//         err.response?.data?.message ||
//         err.response?.data?.reason ||
//         err.message ||
//         "Analysis failed."
//       );
//     } finally {
//       setIsLoading(false);
//     }
//   };

//   const handleDragOver = (e) => {
//     e.preventDefault();
//     setIsDragOver(true);
//   };
//   const handleDragLeave = (e) => {
//     e.preventDefault();
//     setIsDragOver(false);
//   };
//   const handleDrop = (e) => {
//     e.preventDefault();
//     setIsDragOver(false);
//     const droppedFile = e.dataTransfer.files[0];
//     if (
//       droppedFile &&
//       (droppedFile.type === "video/mp4" ||
//         droppedFile.type === "video/quicktime")
//     ) {
//       handleFileChange(droppedFile);
//     }
//   };

//   return (
//     <div className="detector-container">
//       <h2>🎥 Video Deepfake Detector</h2>

//       {!preview && (
//         <div
//           className={`drop-zone ${isDragOver ? "drag-over" : ""}`}
//           onClick={() => document.getElementById("file-upload").click()}
//           onDragOver={handleDragOver}
//           onDragLeave={handleDragLeave}
//           onDrop={handleDrop}
//         >
//           <input
//             id="file-upload"
//             type="file"
//             onChange={(e) => handleFileChange(e.target.files[0])}
//             accept="video/mp4,video/quicktime"
//           />
//           <p>Drag & Drop a Video Here</p>
//           <small>or click to select (MP4, MOV)</small>
//         </div>
//       )}

//       {preview && (
//         <div className="preview-container">
//           <video src={preview} controls />
//         </div>
//       )}

//       <div className="button-group">
//         {file && !isLoading && !result && (
//           <button type="button" className="btn" onClick={handleSubmit}>
//             Analyze Video
//           </button>
//         )}
//         {preview && (
//           <button type="button" className="btn btn-clear" onClick={handleClear}>
//             Clear
//           </button>
//         )}
//       </div>

//       {isLoading && (
//         <div className="spinner-container">
//           <div className="spinner"></div>
//           <p style={{ marginLeft: "1rem" }}>Processing video...</p>
//         </div>
//       )}
//       {error && (
//         <p style={{ color: "var(--danger-color)", textAlign: "center" }}>
//           {error}
//         </p>
//       )}

//       {result && (
//         <div
//           className={`result-card ${
//             result.result === "REAL" ? "result-real" : "result-deepfake"
//           }`}
//         >
//           <h4>{result.result}</h4>
//           <p>
//             The model's confidence score is **
//             {(result.confidence * 100).toFixed(2)}%**.
//           </p>
//         </div>
//       )}
//     </div>
//   );
// }

// export default VideoDetector;

import React, { useState } from "react";
import axios from "axios";

const API_URL = "https://deepfake-detection-system-bwn3.onrender.com";

function VideoDetector() {
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
    setResult(null);
    setError("");

    try {
      const response = await axios.post(`${API_URL}/predict/video`, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
        timeout: 180000,
      });

      setResult(response.data);
    } catch (err) {
      console.error("Backend Error:", err);

      if (err.code === "ECONNABORTED") {
        setError(
          "Request timed out. Video processing may take longer on Render. Please try again.",
        );
      } else {
        setError(
          err.response?.data?.message ||
            err.response?.data?.reason ||
            err.message ||
            "Analysis failed.",
        );
      }
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
      (droppedFile.type === "video/mp4" ||
        droppedFile.type === "video/quicktime" ||
        droppedFile.type === "video/x-msvideo")
    ) {
      handleFileChange(droppedFile);
    } else {
      setError("Please upload an MP4, MOV, or AVI video file.");
    }
  };

  return (
    <div className="detector-container">
      <h2>🎥 Video Deepfake Detector</h2>

      {!preview && (
        <div
          className={`drop-zone ${isDragOver ? "drag-over" : ""}`}
          onClick={() => document.getElementById("video-file-upload").click()}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <input
            id="video-file-upload"
            name="file"
            type="file"
            onChange={(e) => handleFileChange(e.target.files[0])}
            accept="video/mp4,video/quicktime,video/x-msvideo"
          />
          <p>Drag & Drop a Video Here</p>
          <small>or click to select (MP4, MOV, AVI)</small>
        </div>
      )}

      {preview && (
        <div className="preview-container">
          <video src={preview} controls />
        </div>
      )}

      <div className="button-group">
        {file && !result && (
          <button
            type="button"
            className="btn"
            onClick={handleSubmit}
            disabled={isLoading}
          >
            {isLoading ? "Analyzing..." : "Analyze Video"}
          </button>
        )}

        {preview && (
          <button
            type="button"
            className="btn btn-clear"
            onClick={handleClear}
            disabled={isLoading}
          >
            Clear
          </button>
        )}
      </div>

      {isLoading && (
        <div className="spinner-container">
          <div className="spinner"></div>
          <p style={{ marginLeft: "1rem" }}>Processing video...</p>
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
            The model's confidence score is{" "}
            {(result.confidence * 100).toFixed(2)}%.
          </p>
        </div>
      )}
    </div>
  );
}

export default VideoDetector;
