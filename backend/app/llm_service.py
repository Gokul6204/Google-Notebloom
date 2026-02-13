from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from typing import List, Dict

class LLMService:
    def __init__(self, model_name: str = "llama3"):
        self.llm = OllamaLLM(
            model=model_name,
            num_predict=500,
            temperature=0.1
        )
        self.prompt_template = ChatPromptTemplate.from_template("""
        You are an AI research assistant, inspired by NotebookLM.
        Your goal is to provide accurate, comprehensive answers based ONLY on the provided context.
        
        Instructions:
        1. Answer the question using only the Context below.
        2. If the context doesn't contain the answer, say "I cannot find the answer in the provided documents."
        3. Cite your sources inline where possible, e.g. [Source: file.pdf].
        4. Be concise but detailed.

        Context:
        {context}

        Question:
        {question}

        Answer:""")

    async def generate_response(self, question: str, context: str) -> str:
        chain = self.prompt_template | self.llm
        response = await chain.ainvoke({"question": question, "context": context})
        return response
