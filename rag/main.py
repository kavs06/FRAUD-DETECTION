"""
Main FastAPI Application

Starts the Healthcare Fraud RAG Chatbot API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router

app = FastAPI(
    title="Healthcare Fraud RAG Chatbot",
    description="AI-powered Healthcare Fraud Investigation Assistant",
    version="1.0.0",
)

# Enable CORS (needed for React frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Later, replace "*" with your React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(router)


@app.get("/")
def root():
    return {
        "message": "Healthcare Fraud RAG Chatbot API is running!"
    }