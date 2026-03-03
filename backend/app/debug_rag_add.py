import sys
import os
import logging
from langchain_core.documents import Document

# Setup logging
logging.basicConfig(level=logging.INFO)

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    print("Importing RAGService...")
    from app.rag_service import RAGService
    
    print("Initializing RAGService...")
    rag = RAGService()
    
    if not rag.vector_db:
        print("ERROR: Vector DB not initialized")
        sys.exit(1)
        
    print("Creating dummy document...")
    doc = Document(
        page_content="This is a manual test document for ChromaDB persistence.",
        metadata={"source": "manual_test.txt"}
    )
    
    print("Adding document...")
    rag.add_documents([doc])
    
    print("Done adding. Checking count...")
    count = rag.vector_db._collection.count()
    print(f"Count after add: {count}")
    
    if count > 0:
        print("SUCCESS: Document added and persisted.")
        
        print("Querying...")
        results = rag.query("manual test")
        print(f"Found {len(results)} results")
        print(results[0].page_content if results else "No content")
        
        # Cleanup
        print("Cleaning up...")
        rag.delete_document("manual_test.txt")
        print("Cleanup done.")
    else:
        print("FAILURE: Document was NOT added (count is 0).")

except Exception as e:
    print(f"CRITICAL ERROR: {e}")
    import traceback
    traceback.print_exc()
