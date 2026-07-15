"""
Prompt templates.

Responsibilities:
- Build RAG prompt
- Combine retrieved context + user question
"""

from langchain_core.prompts import PromptTemplate


class PromptBuilder:
    """
    Builds the prompt sent to Gemini.
    """

    def __init__(self):

        self.prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""
You are Healthcare Fraud Investigation Assistant.

You are an intelligent AI investigator that helps users understand healthcare fraud,
provider investigations, billing rules, CMS regulations and medical claims.

You have been given retrieved knowledge from a healthcare database.

==========================
IMPORTANT RULES
==========================

1. Answer ONLY using the provided CONTEXT.

2. If the answer exists in the context,
explain it clearly in simple language.

3. Do NOT invent facts.

4. If the answer is partially available,
say what is available.

5. If the answer is NOT available,
reply exactly:

"I could not find enough information in the healthcare knowledge base."

6. Use bullet points whenever appropriate.

7. If provider statistics are present,
summarize them clearly.

8. If fraud risk is mentioned,
explain WHY the provider is risky.

9. Never mention that you are an AI language model.

10. Keep answers concise but informative.

==========================
CONTEXT
==========================

{context}

==========================
QUESTION
==========================

{question}

==========================
FINAL ANSWER
==========================
"""
        )

    def build_prompt(self, context: str, question: str) -> str:

        return self.prompt.format(
            context=context,
            question=question
        )


if __name__ == "__main__":

    builder = PromptBuilder()

    sample_context = """
Healthcare fraud includes:
- Phantom Billing
- Upcoding
- Duplicate Claims
"""

    sample_question = "What is healthcare fraud?"

    prompt = builder.build_prompt(
        context=sample_context,
        question=sample_question
    )

    print("\n==============================")
    print("Prompt Template Test")
    print("==============================\n")

    print(prompt)