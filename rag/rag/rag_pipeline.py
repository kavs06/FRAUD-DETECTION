"""
Complete Retrieval-Augmented Generation pipeline.

Flow:
User Question
    ↓
Retriever
    ↓
Retrieved Context
    ↓
Prompt
    ↓
Gemini
    ↓
Answer
"""

from rag.retriever import Retriever
from rag.prompt_template import PromptBuilder
from rag.gemini_chat import GeminiChat
from utils.logger import setup_logger

logger = setup_logger()


class RAGPipeline:
    """
    Complete Retrieval-Augmented Generation pipeline.
    """

    def __init__(self):

        logger.info("Initializing RAG Pipeline...")

        self.retriever = Retriever()
        self.prompt_builder = PromptBuilder()
        self.chatbot = GeminiChat()

        logger.info("RAG Pipeline initialized successfully.")

    def ask(self, question: str) -> str:
        """
        Normal (non-streaming) answer.
        """

        logger.info(f"User Question: {question}")

        documents = self.retriever.search(question)

        if not documents:

            logger.warning("No documents found.")
            logger.info("Using Gemini general chat...")

            return self.chatbot.general_chat(question)

        logger.info(f"Retrieved {len(documents)} documents.")

        context = "\n\n".join(
            doc.page_content
            for doc in documents
        )

        logger.info("Context created successfully.")

        prompt = self.prompt_builder.build_prompt(
            context=context,
            question=question
        )

        logger.info("Prompt generated successfully.")

        answer = self.chatbot.ask(prompt)

        logger.info("Answer generated successfully.")

        if "I could not find enough information" in answer:

            logger.info("Falling back to Gemini General Chat...")

            answer = self.chatbot.general_chat(question)

        return answer

    def stream_answer(self, question: str):
        """
        Stream answer token-by-token.
        """

        logger.info(f"Streaming Question: {question}")

        documents = self.retriever.search(question)

        # No documents → General Gemini
        if not documents:

            logger.warning("No documents found.")

            response = self.chatbot.general_chat(question)

            yield response

            return

        logger.info(f"Retrieved {len(documents)} documents.")

        context = "\n\n".join(
            doc.page_content
            for doc in documents
        )

        prompt = self.prompt_builder.build_prompt(
            context=context,
            question=question
        )

        logger.info("Streaming answer...")

        full_answer = ""

        for chunk in self.chatbot.stream(prompt):

            full_answer += chunk

            yield chunk

        if "I could not find enough information" in full_answer:

            logger.info("Falling back to General Gemini...")

            response = self.chatbot.general_chat(question)

            yield "\n\n"
            yield response


if __name__ == "__main__":

    pipeline = RAGPipeline()

    print("=" * 50)
    print("Healthcare Fraud RAG Chatbot")
    print("=" * 50)

    while True:

        question = input("\nAsk a question: ")

        if question.lower() in ["exit", "quit"]:

            break

        print()

        for chunk in pipeline.stream_answer(question):
            print(chunk, end="", flush=True)

        print("\n")