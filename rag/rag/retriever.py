"""
Semantic Retriever.

Responsibilities:
- Receive user query
- Retrieve Top-K relevant documents
- Return retrieved context
"""

import re

from langchain_community.vectorstores import FAISS

from config import FAISS_INDEX_DIR
from rag.embeddings import EmbeddingManager
from rag.provider_lookup import ProviderLookup
from utils.logger import setup_logger

logger = setup_logger()


class Retriever:

    def __init__(self):

        logger.info("Loading embedding model...")

        self.embedding_model = EmbeddingManager().get_model()

        logger.info("Loading FAISS vector database...")

        self.vector_store = FAISS.load_local(
            folder_path=str(FAISS_INDEX_DIR),
            embeddings=self.embedding_model,
            allow_dangerous_deserialization=True
        )

        logger.info("Loading Provider Lookup...")

        self.provider_lookup = ProviderLookup()

        logger.info("Provider Lookup loaded successfully.")

        logger.info("Retriever initialized successfully.")

    def search(self, query, k=3):
        """
        Perform retrieval.

        If the query contains a Provider ID,
        return the provider report directly.

        Otherwise perform semantic search.
        """

        logger.info(f"Searching for: {query}")

        # ---------------------------------
        # Detect Provider ID
        # ---------------------------------

        provider_match = re.search(r"PRV\d+", query.upper())

        if provider_match:

            provider_id = provider_match.group()

            logger.info(
                f"Detected Provider ID: {provider_id}"
            )

            # =====================================
            # Use Provider Lookup (FAST + EXACT)
            # =====================================

            document = self.provider_lookup.get_provider(provider_id)

            if document is not None:

                logger.info(
                    f"Exact provider {provider_id} found using Provider Lookup."
                )

                return [document]

            logger.info(
                "Provider not found in lookup. Falling back to FAISS..."
            )

            # ---------------------------------
            # FAISS fallback
            # ---------------------------------

            documents = self.vector_store.similarity_search(
                query=provider_id,
                k=200
            )

            exact_documents = []

            for doc in documents:

                if doc.metadata.get("provider_id") == provider_id:
                    exact_documents.append(doc)

            if exact_documents:

                logger.info(
                    f"Found {len(exact_documents)} provider documents using FAISS."
                )

                return exact_documents

        # ---------------------------------
        # Normal Semantic Search
        # ---------------------------------

        results = self.vector_store.similarity_search(
            query=query,
            k=k
        )

        logger.info(
            f"Retrieved {len(results)} documents."
        )

        return results


if __name__ == "__main__":

    retriever = Retriever()

    query = "PRV56689"

    documents = retriever.search(query)

    print("\n==============================")
    print("Retriever Summary")
    print("==============================")

    print("\nQuery:")
    print(query)

    print(f"\nRetrieved Documents: {len(documents)}")

    if documents:

        print("\nMetadata:\n")
        print(documents[0].metadata)

        print("\nDocument:\n")
        print(documents[0].page_content)

    else:

        print("\nNo documents found.")