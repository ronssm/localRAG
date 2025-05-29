"use client";

import Link from "next/link";

export default function Home() {
  return (
    <div className="container">
      <h1 className="title">Local RAG System</h1>

      <div className="flex-center">
        <Link href="/chat" className="button">
          Chat with Knowledge Base
        </Link>

        <Link href="/embed" className="button">
          Add to Knowledge Base
        </Link>
      </div>
    </div>
  );
}
