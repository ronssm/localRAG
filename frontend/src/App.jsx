import React, { useState } from "react";

export default function App() {
  const [input, setInput] = useState("");
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResponse(null);
    try {
      const res = await fetch("/api-rag/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: input, n_results: 3 }),
      });
      const data = await res.json();
      setResponse(data);
    } catch (err) {
      setResponse({ answer: "Erro ao consultar a API." });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{ maxWidth: 600, margin: "2rem auto", fontFamily: "sans-serif" }}
    >
      <h1>Frontend RAG</h1>
      <form onSubmit={handleSubmit}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Digite sua pergunta..."
          style={{ width: "80%", padding: 8 }}
        />
        <button
          type="submit"
          style={{ padding: 8, marginLeft: 8 }}
          disabled={loading}
        >
          {loading ? "Consultando..." : "Enviar"}
        </button>
      </form>
      {response && (
        <div style={{ marginTop: 24 }}>
          <strong>Resposta:</strong>
          <div style={{ marginTop: 8 }}>{response.answer}</div>
          {response.documents && response.documents.length > 0 && (
            <>
              <hr />
              <strong>Documentos relevantes:</strong>
              <ul>
                {response.documents.map((doc, i) => (
                  <li key={i} style={{ marginBottom: 8 }}>
                    {doc}
                  </li>
                ))}
              </ul>
            </>
          )}
        </div>
      )}
    </div>
  );
}
