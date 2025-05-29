"use client";

import Link from "next/link";

export default function Home() {
  return (
    <div style={{ maxWidth: "800px", margin: "2rem auto", padding: "1rem" }}>
      <h1 style={{ marginBottom: "2rem", textAlign: "center" }}>
        Local RAG System
      </h1>

      <div style={{ display: "flex", gap: "1rem", justifyContent: "center" }}>
        <Link
          href="/chat"
          style={{
            padding: "1rem 2rem",
            backgroundColor: "#0070f3",
            color: "white",
            textDecoration: "none",
            borderRadius: "4px",
            textAlign: "center",
          }}
        >
          Chat with Knowledge Base
        </Link>

        <Link
          href="/embed"
          style={{
            padding: "1rem 2rem",
            backgroundColor: "#0070f3",
            color: "white",
            textDecoration: "none",
            borderRadius: "4px",
            textAlign: "center",
          }}
        >
          Add to Knowledge Base
        </Link>
      </div>
    </div>
  );
}
