"""
Embedding model.

Responsibilities:
- Load all-MiniLM-L6-v2
- Generate embeddings
"""

"""
Embeddings Module

Initializes the embedding model used for converting
documents into vector embeddings.
"""

from langchain_huggingface import HuggingFaceEmbeddings

from config import EMBEDDING_MODEL
from utils.logger import setup_logger

logger = setup_logger()


class EmbeddingManager:
    """
    Loads and provides the embedding model.
    """

    def __init__(self):

        self.embedding_model = None

    def load_model(self):
        """
        Load the HuggingFace embedding model.
        """

        logger.info(
            f"Loading embedding model: {EMBEDDING_MODEL}"
        )

        self.embedding_model = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={
                "device": "cpu"
            },
            encode_kwargs={
                "normalize_embeddings": True
            }
        )

        logger.info("Embedding model loaded successfully.")

        return self.embedding_model

    def get_model(self):
        """
        Return loaded embedding model.
        """

        if self.embedding_model is None:
            self.load_model()

        return self.embedding_model


if __name__ == "__main__":

    manager = EmbeddingManager()

    embeddings = manager.load_model()

    print("\n==============================")
    print("Embedding Model Summary")
    print("==============================")

    print(f"\nModel : {EMBEDDING_MODEL}")

    sample = embeddings.embed_query(
        "What is healthcare fraud?"
    )

    print(f"Embedding Dimension : {len(sample)}")

    print("\nFirst 10 Values:\n")

    print(sample[:10])