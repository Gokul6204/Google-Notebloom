import sys
import os
import logging
import traceback

# Setup logging
logging.basicConfig(level=logging.ERROR)

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

print("Starting test...")

try:
    print("Attempting to import Chroma...")
    import langchain_chroma
    import chromadb
    print("SUCCESS: Imported Chroma libraries.")
except ImportError as e:
    print(f"ERROR: Failed to import Chroma libraries: {e}")
    sys.exit(1)

try:
    print("Attempting to import RAGService...")
    from app.rag_service import RAGService
    print("SUCCESS: Imported RAGService")
    
    print("Attempting to initialize RAGService...")
    rag = RAGService()
    
    if rag.vector_db:
        print("SUCCESS: Vector DB initialized correctly.")
    else:
        print("ERROR: Vector DB failed to initialize.")
        # Try to manually init to catch exception
        rag._init_vector_db()
        
except Exception as e:
    print(f"CRITICAL ERROR: {e}")
    traceback.print_exc()
