from langchain_huggingface import HuggingFaceEmbeddings
from .config import Config

class EmbeddingGenerator:
    def __init__(self):
        print(f"Initializing embedding model: {Config.EMBEDDING_MODEL_NAME}...")
        self.embeddings = HuggingFaceEmbeddings(model_name=Config.EMBEDDING_MODEL_NAME)
        
    def get_embeddings(self):
        return self.embeddings
