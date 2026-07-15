"""
Load external healthcare fraud knowledge.

Responsibilities:
- Read Markdown files
- Read TXT files
- Read PDFs (optional)
- Convert into LangChain Documents
"""

"""
Knowledge Loader

Loads all Markdown knowledge files and converts them into
LangChain Documents for the RAG pipeline.
"""

from pathlib import Path

from langchain_core.documents import Document

from config import KNOWLEDGE_DIR
from utils.logger import setup_logger

logger = setup_logger()


class KnowledgeLoader:
    """
    Loads healthcare knowledge documents.
    """

    def __init__(self):

        self.knowledge_dir = Path(KNOWLEDGE_DIR)

        self.documents = []

    def load_markdown_files(self):
        """
        Load every Markdown file from the knowledge folder.
        """

        logger.info("Loading knowledge files...")

        md_files = sorted(self.knowledge_dir.glob("*.md"))

        if not md_files:
            logger.warning("No Markdown files found.")
            return []

        for file_path in md_files:

            logger.info(f"Reading {file_path.name}")

            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()

            document = Document(
                page_content=content,
                metadata={
                    "source": file_path.name,
                    "document_type": "knowledge_base",
                    "path": str(file_path)
                }
            )

            self.documents.append(document)

        logger.info(
            f"Loaded {len(self.documents)} knowledge documents."
        )

        return self.documents

    def get_documents(self):
        """
        Return loaded documents.
        """

        return self.documents


if __name__ == "__main__":

    loader = KnowledgeLoader()

    documents = loader.load_markdown_files()

    print("\n==============================")
    print("Knowledge Loader Summary")
    print("==============================")

    print(f"\nTotal Documents : {len(documents)}")

    if documents:

        print("\nFirst Document Metadata\n")

        print(documents[0].metadata)

        print("\nPreview\n")

        preview = documents[0].page_content[:500]

        print(preview)

        if len(documents[0].page_content) > 500:
            print("...")