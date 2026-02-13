from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from typing import List
import os
import logging

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self, persist_directory: str = None):
        if persist_directory is None:
            # Use absolute path
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            persist_directory = os.path.join(base_dir, "faiss_index")
        
        self.embedding_model = OllamaEmbeddings(
            model="nomic-embed-text"
        )
        self.persist_directory = persist_directory
        logger.info(f"FAISS index directory: {self.persist_directory}")
        
        if os.path.exists(self.persist_directory):
            logger.info("Loading existing FAISS index...")
            self.vector_db = FAISS.load_local(
                self.persist_directory, 
                self.embedding_model,
                allow_dangerous_deserialization=True
            )
            logger.info("FAISS index loaded successfully")
        else:
            logger.info("No existing FAISS index found. Will create on first document upload.")
            self.vector_db = None

    def add_documents(self, documents: List[Document]):
        if not documents:
            logger.warning("No documents to add")
            return
        
        logger.info(f"Adding {len(documents)} documents to vector database")
        
        if self.vector_db:
            logger.info("Adding to existing FAISS index")
            self.vector_db.add_documents(documents)
        else:
            logger.info("Creating new FAISS index")
            self.vector_db = FAISS.from_documents(
                documents=documents,
                embedding=self.embedding_model
            )
        
        logger.info(f"Saving FAISS index to {self.persist_directory}")
        self.vector_db.save_local(self.persist_directory)
        logger.info("FAISS index saved successfully")

    def query(self, query_text: str, k: int = 7) -> List[Document]:
        if not self.vector_db:
             return []
        
        # Simple similarity search
        return self.vector_db.similarity_search(query_text, k=k)

    def get_retriever(self, k: int = 7):
        if not self.vector_db:
             # Return a dummy retriever if DB is empty
             from langchain_core.retrievers import BaseRetriever
             class DummyRetriever(BaseRetriever):
                 def _get_relevant_documents(self, query: str, *, run_manager=None) -> List[Document]:
                     return []
             return DummyRetriever()

        return self.vector_db.as_retriever(search_kwargs={"k": k})
