"use client";

import { useState } from "react";
import Link from "next/link";

export default function ChatPage() {
  const [pergunta, setPergunta] = useState("");
  const [mensagem, setMensagem] = useState("");
  const [carregando, setCarregando] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMensagem("");
    setCarregando(true);
    try {
      const resposta = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model: "default",
          messages: [{ role: "user", content: pergunta }],
        }),
      });
      const data = await resposta.json();
      if (data.erro) {
        setMensagem(data.erro);
      } else {
        setMensagem(data.message.content || "Pergunta enviada!");
      }
    } catch {
      setMensagem("Erro ao enviar a pergunta.");
    } finally {
      setCarregando(false);
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

      <h1>Chat with Knowledge Base</h1>

      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={pergunta}
          onChange={(e) => setPergunta(e.target.value)}
          placeholder="Digite sua pergunta"
          style={{ width: "80%", padding: "0.5rem" }}
          disabled={carregando}
        />
        <br />
        <button
          type="submit"
          style={{ marginTop: "1rem", padding: "0.5rem 1rem" }}
          disabled={carregando}
        >
          {carregando ? "Enviando..." : "Enviar"}
        </button>
      </form>

      {mensagem && <p>{mensagem}</p>}
    </div>
  );
}
