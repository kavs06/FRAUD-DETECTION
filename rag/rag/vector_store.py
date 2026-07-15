"""
FAISS Vector Store.

Responsibilities:
- Build vector database
- Save index
- Load existing index
- Rebuild index
"""

"""
Vector Store Module

Builds and saves a FAISS vector database using
all document chunks.
"""

from langchain_community.vectorstores import FAISS

from config import (
    FAISS_INDEX_DIR,
    FAISS_INDEX_FILE,
    FAISS_METADATA_FILE,
)

from rag.chunking import ChunkBuilder
from rag.embeddings import EmbeddingManager
from utils.logger import setup_logger

logger = setup_logger()


class VectorStoreManager:
    """
    Creates and manages the FAISS vector database.
    """

    def __init__(self):

        self.vector_store = None

    def build_vector_store(self):
        """
        Build FAISS vector database.
        """

        logger.info("Loading chunks...")

        chunk_builder = ChunkBuilder()

        chunk_builder.load_documents()

        chunk_builder.split_documents()

        chunks = chunk_builder.get_chunks()

        logger.info(f"Loaded {len(chunks)} chunks.")

        logger.info("Loading embedding model...")

        embedding_model = EmbeddingManager().get_model()

        logger.info("Building FAISS index...")

        self.vector_store = FAISS.from_documents(
            documents=chunks,
            embedding=embedding_model
        )

        logger.info("FAISS index created successfully.")

        return self.vector_store

    def save_vector_store(self):
        """
        Save FAISS index to disk.
        """

        if self.vector_store is None:
            raise ValueError(
                "Vector store has not been created."
            )

        FAISS_INDEX_DIR.mkdir(exist_ok=True)

        self.vector_store.save_local(
            str(FAISS_INDEX_DIR)
        )

        logger.info(
            f"Vector database saved to {FAISS_INDEX_DIR}"
        )

    def load_vector_store(self):
        """
        Load saved FAISS index.
        """

        embedding_model = EmbeddingManager().get_model()

        self.vector_store = FAISS.load_local(
            folder_path=str(FAISS_INDEX_DIR),
            embeddings=embedding_model,
            allow_dangerous_deserialization=True
        )

        logger.info("FAISS database loaded successfully.")

        return self.vector_store


if __name__ == "__main__":

    manager = VectorStoreManager()

    manager.build_vector_store()

    manager.save_vector_store()

    print("\n==============================")
    print("FAISS Summary")
    print("==============================")

    print("\nVector database created successfully.")

    print(f"\nLocation : {FAISS_INDEX_DIR}")

    print(f"\nIndex File : {FAISS_INDEX_FILE}")

    print(f"\nMetadata File : {FAISS_METADATA_FILE}")