"""
Gemini Integration.

Responsibilities:
- Connect to Gemini API
- Send prompts to Gemini
- Stream responses
- Receive responses
"""

import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from config import GEMINI_MODEL
from utils.logger import setup_logger

logger = setup_logger()

# Load environment variables
load_dotenv(override=True)

# Read API Key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


class GeminiChat:
    """
    Handles Gemini LLM initialization and response generation.
    """

    def __init__(self):

        if not GOOGLE_API_KEY:
            raise ValueError(
                "GOOGLE_API_KEY not found in .env file."
            )

        logger.info(f"Loading Gemini Model: {GEMINI_MODEL}")

        self.llm = ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            google_api_key=GOOGLE_API_KEY,
            temperature=0.2,
        )

        logger.info("Gemini initialized successfully.")

    def _extract_text(self, response):
        """
        Extract plain text from Gemini response.
        """

        if isinstance(response.content, list):

            answer = ""

            for item in response.content:

                if isinstance(item, dict):

                    if item.get("type") == "text":
                        answer += item.get("text", "")

                else:
                    answer += str(item)

            return answer.strip()

        return str(response.content)

    def ask(self, prompt: str) -> str:
        """
        Used by the RAG pipeline.
        """

        logger.info("Sending RAG prompt to Gemini...")

        try:

            response = self.llm.invoke(prompt)

            logger.info("Response received.")

            return self._extract_text(response)

        except Exception as e:

            logger.exception(
                "Gemini Error while processing RAG prompt."
            )

            raise Exception(str(e))

    def stream(self, prompt: str):
        """
        Stream Gemini response token-by-token.
        """

        logger.info("Streaming response from Gemini...")

        try:

            for chunk in self.llm.stream(prompt):

                if hasattr(chunk, "content"):

                    # Normal string response
                    if isinstance(chunk.content, str):

                        if chunk.content:
                            yield chunk.content

                    # Gemini structured response
                    elif isinstance(chunk.content, list):

                        text = ""

                        for item in chunk.content:

                            if isinstance(item, dict):

                                if item.get("type") == "text":
                                    text += item.get("text", "")

                            else:
                                text += str(item)

                        if text:
                            yield text

        except Exception as e:

            logger.exception(
                "Gemini Error while streaming."
            )

            yield f"\n\nError: {str(e)}"

    def general_chat(self, question: str) -> str:
        """
        Used for general questions outside the healthcare knowledge base.
        """

        logger.info("Sending general question to Gemini...")

        prompt = f"""
You are a helpful AI assistant.

Answer the following question clearly and accurately.

Question:
{question}
"""

        try:

            response = self.llm.invoke(prompt)

            logger.info("General response received.")

            return self._extract_text(response)

        except Exception as e:

            logger.exception(
                "Gemini Error while processing general chat."
            )

            raise Exception(str(e))


if __name__ == "__main__":

    chatbot = GeminiChat()

    question = "What is diabetes?"

    print("\n==============================")
    print("Gemini Streaming Test")
    print("==============================")
    print()

    for chunk in chatbot.stream(question):
        print(chunk, end="", flush=True)