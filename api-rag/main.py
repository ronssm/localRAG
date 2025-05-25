from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import ollama
import chromadb
from chromadb.utils import embedding_functions
import os
import logging

app = FastAPI()

# 🔗 Conexão com o ChromaDB
chroma_client = chromadb.HttpClient(
    host=os.getenv("CHROMA_DB", "http://localhost:8000")
)
collection = chroma_client.get_or_create_collection(name="rag-collection")

# 🔧 Configuração dos modelos
EMBEDDING_MODEL = "nomic-embed-text"
LLM_MODEL = "gemma:2b"  # ✅ Modelo mais leve para CPU

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api-rag")


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
@app.post("/embeddings")
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
        logger.info(f"[API-RAG] Recebido /query: {item}")
        # 🔹 Gera embedding da pergunta
        query_embedding = ollama.embeddings(model=EMBEDDING_MODEL, prompt=item.query)[
            "embedding"
        ]
        logger.debug(f"[API-RAG] Embedding gerado: {query_embedding[:5]}... (tamanho={len(query_embedding)})")
        # 🔍 Busca nos vetores
        results = collection.query(
            query_embeddings=[query_embedding], n_results=item.n_results
        )
        logger.info(f"[API-RAG] Resultados da busca: {results}")
        documents = []
        if results["documents"]:
            # Junta todos os documentos relevantes encontrados
            for doclist in results["documents"]:
                documents.extend(doclist)
        context = "\n".join(documents)
        logger.debug(f"[API-RAG] Contexto encontrado: {context}")
        if not context:
            logger.warning("[API-RAG] Nenhum documento relevante encontrado.")
            return {"answer": "Nenhum documento relevante encontrado.", "documents": []}
        # 🧠 Gera a resposta com o modelo LLM
        prompt = f"""DOCUMENTOS RELEVANTES:\n{context}\n\nPergunta: {item.query}\nResposta:"""
        logger.debug(f"[API-RAG] Prompt para LLM: {prompt}")
        try:
            response = ollama.generate(model=LLM_MODEL, prompt=prompt)
            logger.info(f"[API-RAG] Resposta do modelo: {response}")
            answer = response["response"]
        except Exception as ollama_error:
            logger.error(f"[API-RAG] Erro ao chamar ollama.generate: {ollama_error}")
            answer = "O modelo não conseguiu gerar uma resposta para a pergunta."
        return {"answer": answer, "documents": documents}
    except Exception as e:
        import traceback
        logger.error(f"[API-RAG] Erro inesperado: {e}")
        logger.debug(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erro na consulta: {str(e)}")


# 🏠 Rota de teste
@app.get("/")
def read_root():
    return {"message": "API RAG está rodando."}
