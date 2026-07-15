"""
API Routes

Defines all REST API endpoints for the
Healthcare Fraud RAG Chatbot.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from api.schemas import ChatRequest, ChatResponse
from rag.rag_pipeline import RAGPipeline

router = APIRouter()

# Load RAG Pipeline only once
pipeline = RAGPipeline()


@router.get("/")
def home():
    return {
        "message": "Healthcare Fraud RAG Chatbot API is running."
    }


@router.get("/health")
def health():
    return {
        "status": "healthy"
    }


# -----------------------------
# Normal Chat API
# -----------------------------
@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    try:

        answer = pipeline.ask(request.question)

        return ChatResponse(
            answer=answer
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# -----------------------------
# Streaming Chat API
# -----------------------------
@router.post("/chat-stream")
def chat_stream(request: ChatRequest):

    try:

        return StreamingResponse(
            pipeline.stream_answer(request.question),
            media_type="text/plain"
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )