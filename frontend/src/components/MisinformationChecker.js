import React, { useState } from "react";
import axios from "axios";

const API_URL = "http://127.0.0.1:5000";
// const API_URL = "https://unarbitrarily-impostrous-dino.ngrok-free.dev";

function MisinformationChecker() {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleClear = () => {
    setText("");
    setResult(null);
    setError("");
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (text.length < 50) {
      setError("Please enter at least 50 characters for a reliable analysis.");
      return;
    }
    setIsLoading(true);
    setError("");
    setResult(null);
    try {
      // const response = await axios.post(`${API_URL}/predict/misinformation`, {
      //   text,
      // });
      const response = await axios.post(
        `${API_URL}/predict/misinformation`,
        { text },
        {
          headers: {
            "Content-Type": "application/json",
            "ngrok-skip-browser-warning": "true",
          },
        }
      );
      if (response.data.result === "error") {
        setError(response.data.message);
      } else {
        setResult(response.data);
      }
    } catch (err) {
      setError(
        "API Error. Please check your Gemini API key and backend server."
      );
    } finally {
      setIsLoading(false);
    }
  };

  const renderHighlightedText = () => {
    if (!result || !result.analysis_points) return <p>{text}</p>;

    let highlightedHtml = text;
    const sortedPoints = [...result.analysis_points].sort(
      (a, b) => b.text_fragment.length - a.text_fragment.length
    );

    sortedPoints.forEach((point) => {
      if (point.fragment_verdict !== "FACT") {
        const verdictClass =
          point.fragment_verdict.toLowerCase() === "fake"
            ? "highlight-fake"
            : "highlight-misleading";

        const highlightedFragment = `
                    <span class="highlight ${verdictClass}">
                        ${point.text_fragment}
                        <span class="tooltip">${point.reason}</span>
                    </span>`;
        highlightedHtml = highlightedHtml.replace(
          new RegExp(escapeRegExp(point.text_fragment), "g"),
          highlightedFragment
        );
      }
    });

    return (
      <div
        className="highlighted-text"
        dangerouslySetInnerHTML={{ __html: highlightedHtml }}
      />
    );
  };

  const escapeRegExp = (string) =>
    string.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

  return (
    <div className="detector-container">
      <h2 style={{ textAlign: "center" }}>📰 Misinformation Analyzer</h2>

      {!result ? (
        <form
          onSubmit={handleSubmit}
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: "1.5rem",
          }}
        >
          <textarea
            className="text-input-area"
            rows="15"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Paste a news article or block of text here for a detailed forensic breakdown..."
          />
          <div className="button-group">
            <button
              type="submit"
              className="btn"
              disabled={isLoading || text.length < 50}
            >
              {isLoading ? "Analyzing..." : "Run Forensic Analysis"}
            </button>
          </div>
        </form>
      ) : (
        <div>
          <div className={`verdict-card verdict-${result.overall_verdict}`}>
            <h4>OVERALL VERDICT: {result.overall_verdict.replace("_", " ")}</h4>
          </div>
          <div className="highlighted-text-container">
            <h3>Analysis Breakdown (Hover for details)</h3>
            {renderHighlightedText()}
          </div>
          <div className="button-group">
            <button
              type="button"
              className="btn btn-clear"
              onClick={handleClear}
            >
              Analyze New Text
            </button>
          </div>
        </div>
      )}

      {isLoading && (
        <div className="spinner-container">
          <div className="spinner"></div>
        </div>
      )}
      {error && <p className="error-message">{error}</p>}
    </div>
  );
}

export default MisinformationChecker;
