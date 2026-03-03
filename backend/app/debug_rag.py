import sys
import os
import logging
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

# Setup logging
logging.basicConfig(level=logging.INFO)

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    print("Initializing RAG Service manually...")
    
    # Path to Chroma DB
    persist_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'chroma_db')
    print(f"Persist directory: {persist_directory}")
    
    if os.path.exists(persist_directory):
        print("✓ Persist directory exists")
    else:
        print("✗ Persist directory does NOT exist")
        sys.exit(1)
        
    embedding_model = OllamaEmbeddings(
        model="nomic-embed-text",
        base_url="http://localhost:11434",
    )
    
    vector_db = Chroma(
        persist_directory=persist_directory,
        embedding_function=embedding_model,
        collection_name="noteboolm_collection"
    )
    
    print("Checking collection count...")
    count = vector_db._collection.count()
    print(f"Total documents in collection: {count}")
    
    if count > 0:
        print("Initial verification successful: Data exists!")
        
        # Try a query
        print("\nAttempting query...")
        results = vector_db.similarity_search("ChromaDB", k=1)
        print(f"Found {len(results)} results")
        for i, doc in enumerate(results):
            print(f"Result {i+1}: {doc.page_content[:100]}...")
            print(f"Metadata: {doc.metadata}")
            
    else:
        print("Verified: Collection is empty. Backend upload failed silently?")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
