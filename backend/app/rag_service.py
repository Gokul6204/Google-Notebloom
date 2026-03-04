from langchain_postgres import PGVector
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from typing import List
import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()

class RAGService:
    def __init__(self):
        logger.info("Initializing HuggingFace embeddings...")
        
        # Use a high-quality, lightweight embedding model
        # self.embeddings = HuggingFaceEmbeddings(
        #     model_name="sentence-transformers/all-MiniLM-L6-v2",
        #     model_kwargs={"device": "cpu"},
        #     encode_kwargs={"normalize_embeddings": True},
        # )

        self.embeddings = HuggingFaceEmbeddings(
            model_name="BAAI/bge-small-en-v1.5",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )

        # Supabase connection string
        self.connection_string = os.getenv("DATABASE_URL")
        
        # Clean the connection string if it has the +psycopg prefix which some drivers don't like
        # but langchain-postgres (which uses sqlalchemy) usually likes it.
        # However, let's ensure it's valid.
        if not self.connection_string:
            logger.error("DATABASE_URL not found in environment variables!")
            self.vector_db = None
            return

        logger.info(f"Connecting to Supabase (Production Mode)...")
        
        try:
            # Initialize PGVector
            # collection_name will be the table name prefix in Supabase
            self.vector_db = PGVector(
                connection=self.connection_string,
                collection_name="noteboolm_v1",
                embeddings=self.embeddings,
                use_jsonb=True
            )
            logger.info("PGVector connected and initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize PGVector: {str(e)}", exc_info=True)
            self.vector_db = None

    def add_documents(self, documents: List[Document]):
        """Add documents to the vector store with error handling"""
        if not documents:
            logger.warning("No documents to add.")
            return
        
        if self.vector_db is None:
            logger.error("Cannot add documents: Vector DB is not initialized.")
            return

        logger.info(f"Adding {len(documents)} chunks to Supabase...")
        try:
            # PGVector's add_documents correctly handles table creation and insertion
            self.vector_db.add_documents(documents)
            logger.info("Successfully added documents to Supabase.")
        except Exception as e:
            logger.error(f"Error adding documents to Supabase: {str(e)}", exc_info=True)

    def delete_document(self, file_path: str):
        """Delete all vectors associated with a specific file path from Supabase"""
        if self.vector_db is None:
            return False
            
        try:
            logger.info(f"Cleaning up vector store for: {file_path}")
            
            # Use .get() to find IDs by metadata and delete them
            # This is the most reliable way in modern langchain-vectorstores
            try:
                # Search for documents with the given source
                results = self.vector_db.get(where={"source": file_path})
                if results and results.get('ids'):
                    ids_to_delete = results['ids']
                    logger.info(f"Deleting {len(ids_to_delete)} chunks from Supabase.")
                    self.vector_db.delete(ids=ids_to_delete)
                    return True
                else:
                    logger.warning(f"No documents found for source: {file_path}")
            except Exception as e:
                logger.error(f"Error during .get() and delete: {e}")
                
            return False
        except Exception as e:
            logger.error(f"Error during deletion from Supabase: {str(e)}")
            return False

    def query(self, query_text: str, k: int = 5) -> List[Document]:
        """Query the vector store for relevant chunks"""
        if self.vector_db is None:
            logger.warning("Query attempted but vector_db is not initialized.")
            return []
            
        try:
            return self.vector_db.similarity_search(query_text, k=k)
        except Exception as e:
            logger.error(f"Error during Supabase query: {str(e)}")
            return []

    def get_retriever(self, k: int = 5):
        if self.vector_db is None:
            return None
        return self.vector_db.as_retriever(search_kwargs={"k": k})