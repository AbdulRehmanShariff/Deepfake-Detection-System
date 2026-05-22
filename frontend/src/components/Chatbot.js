import React, { useState, useRef, useEffect } from "react";
import axios from "axios";

const API_URL = "http://127.0.0.1:5000";
// const API_URL = "https://unarbitrarily-impostrous-dino.ngrok-free.dev";

function Chatbot() {
  const [messages, setMessages] = useState([
    {
      sender: "bot",
      text: "Hello! I am the project's AI assistant. Ask me anything about the technology used, the models, or the project's goals.",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;
    const userMessage = input;
    setMessages((prev) => [...prev, { sender: "user", text: userMessage }]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await axios.post(`${API_URL}/chat`, {
        message: userMessage,
      });
      // const response = await axios.post(
      //   `${API_URL}/chat`,
      //   { message: userMessage },
      //   {
      //     headers: {
      //       "Content-Type": "application/json",
      //       "ngrok-skip-browser-warning": "true",
      //     },
      //   }
      // );
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: response.data.response },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: "Error: Could not connect to the chatbot API." },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="detector-container" style={{ maxWidth: "800px" }}>
      <h2 style={{ textAlign: "center" }}>🤖 Project AI Assistant</h2>
      <div className="chat-window">
        <div className="messages-area">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`message-bubble ${
                msg.sender === "user" ? "user-message" : "bot-message"
              }`}
            >
              {msg.text}
            </div>
          ))}
          {isLoading && (
            <div className="message-bubble bot-message">
              <div
                className="spinner"
                style={{ width: "20px", height: "20px" }}
              ></div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
        <div className="chat-input-area">
          <input
            type="text"
            className="chat-input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && sendMessage()}
            placeholder="Ask a question..."
            disabled={isLoading}
          />
          <button
            onClick={sendMessage}
            className="btn"
            disabled={isLoading || !input.trim()}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}

export default Chatbot;
