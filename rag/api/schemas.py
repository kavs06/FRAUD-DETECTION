"""
API Schemas

Defines request and response models for the Healthcare
Fraud RAG Chatbot API.
"""

from pydantic import BaseModel


class ChatRequest(BaseModel):
    """
    Incoming chat request.
    """

    question: str


class ChatResponse(BaseModel):
    """
    Chat response returned to frontend.
    """

    answer: str