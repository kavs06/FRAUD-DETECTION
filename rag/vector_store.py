import os
import pickle
from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from typing import List, Dict
from .config import Config

class VectorStoreManager:
    def __init__(self, embeddings):
        self.embeddings = embeddings
        self.store_dir = Path(Config.VECTOR_STORE_DIR)
        self.index_path = self.store_dir / "index.faiss"
        self.docs_path = self.store_dir / "documents.pkl"
        
        if not self.store_dir.exists():
            self.store_dir.mkdir(parents=True, exist_ok=True)
            
    def store_exists(self) -> bool:
        return self.index_path.exists() and self.docs_path.exists()

    def build_store(self, documents: List[Dict]):
        print("Building FAISS vector store...")
        langchain_docs = [
            Document(page_content=doc['text'], metadata={"provider_id": doc['provider_id']})
            for doc in documents
        ]
        
        vector_store = FAISS.from_documents(langchain_docs, self.embeddings)
        vector_store.save_local(str(self.store_dir))
        
        # Save raw documents for reference if needed
        with open(self.docs_path, 'wb') as f:
            pickle.dump(documents, f)
            
        print(f"Vector store saved to {self.store_dir}")
        return vector_store

    def load_store(self):
        print("Loading FAISS vector store from disk...")
        vector_store = FAISS.load_local(str(self.store_dir), self.embeddings, allow_dangerous_deserialization=True)
        return vector_store
