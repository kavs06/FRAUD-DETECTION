"""
Project Configuration

This file stores all project paths and configurable settings.
Every module should import values from here instead of hardcoding paths.
"""

from pathlib import Path

# -----------------------------
# Base Project Directory
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent

# -----------------------------
# Data Directories
# -----------------------------
DATA_DIR = BASE_DIR / "data"
KNOWLEDGE_DIR = BASE_DIR / "knowledge"
FAISS_INDEX_DIR = BASE_DIR / "faiss_index"
LOG_DIR = BASE_DIR / "logs"

# -----------------------------
# Model Configuration
# -----------------------------
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Gemini Model
GEMINI_MODEL = "gemini-3.5-flash"

# -----------------------------
# RAG Settings
# -----------------------------
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150
TOP_K = 5

# -----------------------------
# FAISS Files
# -----------------------------
FAISS_INDEX_FILE = FAISS_INDEX_DIR / "index.faiss"
FAISS_METADATA_FILE = FAISS_INDEX_DIR / "index.pkl"