import os
import logging
from app.rag_service import RAGService
from app.document_service import DocumentService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def reindex():
    rag = RAGService()
    doc_service = DocumentService()
    
    upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "uploads")
    
    if not os.path.exists(upload_dir):
        logger.error(f"Upload directory not found: {upload_dir}")
        return

    files = os.listdir(upload_dir)
    if not files:
        logger.info("No files found to index.")
        return

    for filename in files:
        file_path = os.path.join(upload_dir, filename)
        logger.info(f"Indexing {filename}...")
        
        try:
            if filename.lower().endswith(".pdf"):
                docs = doc_service.process_pdf(file_path)
            elif filename.lower().endswith(".txt"):
                docs = doc_service.process_text(file_path)
            else:
                continue
                
            logger.info(f"Generated {len(docs)} chunks. Adding to Supabase...")
            rag.add_documents(docs)
            logger.info(f"Successfully indexed {filename}")
        except Exception as e:
            logger.error(f"Failed to index {filename}: {e}")

if __name__ == "__main__":
    reindex()
