from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import ollama
import chromadb
from chromadb.utils import embedding_functions
import os

app = FastAPI()

# 🔗 Conexão com o ChromaDB
chroma_client = chromadb.HttpClient(
    host=os.getenv("CHROMA_DB", "http://localhost:8000")
)
collection = chroma_client.get_or_create_collection(name="rag-collection")

# 🔧 Configuração dos modelos
EMBEDDING_MODEL = "nomic-embed-text"
LLM_MODEL = "gemma:2b"  # ✅ Modelo mais leve para CPU


# 📦 Modelo de entrada para /index
class IndexItem(BaseModel):
    ids: List[str]
    documents: List[str]
    metadatas: List[dict]


# 📦 Modelo de entrada para /query
class QueryItem(BaseModel):
    query: str
    n_results: int = 3


# 🚀 Rota para indexar documentos
@app.post("/index")
def index_documents(item: IndexItem):
    try:
        embeddings = []

        for doc in item.documents:
            response = ollama.embeddings(model=EMBEDDING_MODEL, prompt=doc)
            embeddings.append(response["embedding"])

        collection.add(
            ids=item.ids,
            documents=item.documents,
            metadatas=item.metadatas,
            embeddings=embeddings,
        )

        return {"message": "Documentos indexados com sucesso."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao indexar: {str(e)}")


# 🔍 Rota para consulta (RAG)
@app.post("/query")
def query_rag(item: QueryItem):
    try:
        # 🔹 Gera embedding da pergunta
        query_embedding = ollama.embeddings(model=EMBEDDING_MODEL, prompt=item.query)[
            "embedding"
        ]

        # 🔍 Busca nos vetores
        results = collection.query(
            query_embeddings=[query_embedding], n_results=item.n_results
        )

        documents = results["documents"][0] if results["documents"] else []
        context = "\n".join(documents)

        if not context:
            return {"answer": "Nenhum documento relevante encontrado."}

        # 🧠 Gera a resposta com o modelo LLM
        prompt = f"""Use os seguintes documentos para responder a pergunta:\n{context}\n\nPergunta: {item.query}\nResposta:"""

        response = ollama.generate(model=LLM_MODEL, prompt=prompt)

        answer = response["response"]

        return {"answer": answer, "documents": documents}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na consulta: {str(e)}")


# 🏠 Rota de teste
@app.get("/")
def read_root():
    return {"message": "API RAG está rodando."}
