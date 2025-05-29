"use client";

import { useState } from "react";
import Link from "next/link";

export default function EmbedPage() {
  const [text, setText] = useState("");
  const [status, setStatus] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsProcessing(true);
    setStatus("");

    try {
      const response = await fetch("/api/embeddings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: text.trim() }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Failed to process text");
      }

      setStatus(data.message || "Text processed successfully");
      setText(""); // Clear the input after successful processing
    } catch (error) {
      setStatus(`Error: ${error.message}`);
      console.error("Embedding error:", error);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div style={{ maxWidth: "800px", margin: "2rem auto", padding: "1rem" }}>
      <div style={{ marginBottom: "2rem" }}>
        <Link
          href="/"
          style={{
            color: "#0070f3",
            textDecoration: "none",
          }}
        >
          ← Back to Home
        </Link>
      </div>

      <h1>Add to Knowledge Base</h1>

      <form onSubmit={handleSubmit}>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Enter your text here..."
          style={{
            width: "100%",
            minHeight: "200px",
            marginBottom: "1rem",
            padding: "0.5rem",
            border: "1px solid #ccc",
          }}
          disabled={isProcessing}
        />

        <button
          type="submit"
          disabled={isProcessing || !text.trim()}
          style={{
            padding: "0.5rem 1rem",
            backgroundColor: isProcessing ? "#ccc" : "#0070f3",
            color: "white",
            border: "none",
            borderRadius: "4px",
            cursor: isProcessing ? "not-allowed" : "pointer",
          }}
        >
          {isProcessing ? "Processing..." : "Process Text"}
        </button>
      </form>

      {status && (
        <p
          style={{
            marginTop: "1rem",
            color: status.includes("Error") ? "red" : "green",
          }}
        >
          {status}
        </p>
      )}
    </div>
  );
}
