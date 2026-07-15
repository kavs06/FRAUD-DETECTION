"""
Split documents into smaller chunks.

Responsibilities:
- Chunk provider reports
- Chunk CMS guidelines
- Preserve metadata
"""

"""
Chunking Module

Combines provider investigation reports and healthcare knowledge
documents, then splits them into chunks for embedding.
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import CHUNK_SIZE, CHUNK_OVERLAP
from rag.document_builder import DocumentBuilder
from rag.knowledge_loader import KnowledgeLoader
from utils.logger import setup_logger

logger = setup_logger()


class ChunkBuilder:
    """
    Creates chunks from all project documents.
    """

    def __init__(self):

        self.documents = []

        self.chunks = []

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )

    def load_documents(self):
        """
        Load provider reports and knowledge documents.
        """

        logger.info("Loading provider investigation reports...")

        builder = DocumentBuilder()

        builder.load_data()
        builder.prepare_claims()
        builder.merge_provider_labels()
        builder.calculate_provider_statistics()
        builder.build_provider_documents()

        provider_docs = builder.get_documents()

        logger.info(
            f"Loaded {len(provider_docs)} provider documents."
        )

        logger.info("Loading healthcare knowledge documents...")

        knowledge_loader = KnowledgeLoader()

        knowledge_docs = knowledge_loader.load_markdown_files()

        logger.info(
            f"Loaded {len(knowledge_docs)} knowledge documents."
        )

        self.documents = provider_docs + knowledge_docs

        logger.info(
            f"Total documents loaded: {len(self.documents)}"
        )

    def split_documents(self):
        """
        Split documents into chunks.
        """

        logger.info("Splitting documents into chunks...")

        self.chunks = self.splitter.split_documents(
            self.documents
        )

        logger.info(
            f"Generated {len(self.chunks)} chunks."
        )

    def get_chunks(self):
        """
        Return generated chunks.
        """

        return self.chunks


if __name__ == "__main__":

    chunk_builder = ChunkBuilder()

    chunk_builder.load_documents()

    chunk_builder.split_documents()

    chunks = chunk_builder.get_chunks()

    print("\n==============================")
    print("Chunking Summary")
    print("==============================")

    print(f"\nTotal Documents : {len(chunk_builder.documents)}")
    print(f"Total Chunks    : {len(chunks)}")

    if chunks:

        print("\nFirst Chunk Metadata\n")
        print(chunks[0].metadata)

        print("\nFirst Chunk Preview\n")
        print(chunks[0].page_content[:600])