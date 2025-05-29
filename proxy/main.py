from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, timezone
import httpx
import os
import logging

app = FastAPI()

# 🔧 Configurações
RAG_API_URL = os.getenv("RAG_API_URL", "http://api-rag:8080")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("proxy")


# 🔸 Modelos de entrada


class GenerateRequest(BaseModel):
    model: str
    prompt: str
    stream: bool = False


class EmbeddingRequest(BaseModel):
    ids: list[str]
    documents: list[str]
    metadatas: list[dict]


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str
    messages: list[ChatMessage]
    stream: bool = False


# 🔹 /api/generate → via RAG


@app.post("/api/generate")
async def generate(request: GenerateRequest):
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{RAG_API_URL}/query", json={"query": request.prompt, "n_results": 3}
            )
            if resp.status_code != 200:
                raise HTTPException(status_code=resp.status_code, detail=resp.text)

            result = resp.json()

        return {
            "model": request.model,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "response": result["answer"],
            "done": True,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 🔹 /api/chat → via RAG (simula chat com contexto)


@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        logger.info(f"[PROXY] Recebido /api/chat: {request}")
        messages = request.messages
        user_message = messages[-1].content if messages else ""

        history = "\n".join(
            [f"{m.role.capitalize()}: {m.content}" for m in messages[:-1]]
        )

        prompt = f"""
Você está participando de um chat. Aqui está o histórico anterior:
{history}

Agora, responda à última pergunta:
{user_message}
"""
        logger.debug(f"[PROXY] Prompt gerado: {prompt}")
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{RAG_API_URL}/query", json={"query": prompt, "n_results": 3}
            )
            logger.info(f"[PROXY] Resposta da api-rag: status={resp.status_code}")
            logger.debug(f"[PROXY] Body da resposta da api-rag: {resp.text}")
            if resp.status_code != 200:
                logger.warning(f"[PROXY] Erro ao chamar api-rag: {resp.text}")
                raise HTTPException(status_code=resp.status_code, detail=resp.text)
            result = resp.json()
        return {
            "model": request.model,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "message": {
                "role": "assistant",
                "content": result["answer"],
            },
            "done": True,
        }
    except Exception as e:
        import traceback
        logger.error(f"[PROXY] Erro inesperado: {e}")
        logger.debug(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


# 🔹 /api/embeddings → via API de RAG customizada


@app.post("/api/embeddings")
async def embeddings(request: EmbeddingRequest):
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{RAG_API_URL}/embeddings",
                json={
                    "ids": request.ids,
                    "documents": request.documents,
                    "metadatas": request.metadatas
                }
            )
            if resp.status_code != 200:
                raise HTTPException(status_code=resp.status_code, detail=resp.text)

            return resp.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 🔹 /api/tags → lista de modelos no Ollama


@app.get("/api/tags")
async def tags():
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{OLLAMA_URL}/api/tags")
            return resp.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 🔹 /api/show → detalhes de um modelo


@app.post("/api/show")
async def show(request: dict):
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{OLLAMA_URL}/api/show", json=request)
            return resp.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 🔹 /api/pull → baixar modelo do Ollama


@app.post("/api/pull")
async def pull(request: dict):
    try:
        async with httpx.AsyncClient(timeout=None) as client:
            resp = await client.post(f"{OLLAMA_URL}/api/pull", json=request)
            return resp.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 🔹 /api/push → subir modelo para o Ollama


@app.post("/api/push")
async def push(request: dict):
    try:
        async with httpx.AsyncClient(timeout=None) as client:
            resp = await client.post(f"{OLLAMA_URL}/api/push", json=request)
            return resp.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 🔹 /api/delete → remover modelo do Ollama


@app.post("/api/delete")
async def delete(request: dict):
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{OLLAMA_URL}/api/delete", json=request)
            return resp.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 🔹 /api/version → obter versão do Ollama


@app.get("/api/version")
async def version():
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{OLLAMA_URL}/api/version")
            logger.info(f"[PROXY] /api/version chamada, status={resp.status_code}")
            if resp.status_code != 200:
                logger.warning(f"[PROXY] Erro ao obter versão do Ollama: {resp.text}")
                raise HTTPException(status_code=resp.status_code, detail=resp.text)
            return resp.json()
    except Exception as e:
        import traceback
        logger.error(f"[PROXY] Erro inesperado em /api/version: {e}")
        logger.debug(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
