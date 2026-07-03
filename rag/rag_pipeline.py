import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from rag.config import Config
from rag.data_loader import DataLoader
from rag.document_builder import DocumentBuilder
from rag.embeddings import EmbeddingGenerator
from rag.vector_store import VectorStoreManager
from rag.retriever import Retriever
from rag.prompt_template import get_prompt_template
from rag.gemini_chat import GeminiChat

class RAGPipeline:
    def __init__(self):
        # 1. Embeddings & Vector Store
        self.embedding_gen = EmbeddingGenerator()
        self.vsm = VectorStoreManager(self.embedding_gen.get_embeddings())
        
        if not self.vsm.store_exists():
            print("Vector store not found. Building from datasets...")
            # Load Data
            loader = DataLoader()
            train_df, bene_df, inpatient_df, outpatient_df = loader.load_data()
            
            # Build Documents
            builder = DocumentBuilder(train_df, bene_df, inpatient_df, outpatient_df)
            documents = builder.build_documents()
            
            # Store in FAISS
            self.vector_store = self.vsm.build_store(documents)
        else:
            self.vector_store = self.vsm.load_store()
            
        # 2. Retriever
        self.retriever = Retriever(self.vector_store, top_k=Config.TOP_K)
        
        # 3. Gemini LLM
        self.llm = GeminiChat()

    def chat(self, question: str) -> str:
        # Retrieve Context
        context = self.retriever.retrieve(question)
        
        # Build Prompt
        prompt = get_prompt_template().format(context=context, question=question)
        
        # Generate Answer
        print("Generating response with Gemini...")
        response = self.llm.generate_response(prompt)
        
        return response

# Single accessible function as requested
def rag_chat(question: str) -> str:
    pipeline = RAGPipeline()
    return pipeline.chat(question)

if __name__ == "__main__":
    # Example usage
    question = "Why was Provider PRV10001 flagged?"
    print(f"\nQuestion: {question}")
    answer = rag_chat(question)
    print(f"\nAnswer:\n{answer}")
