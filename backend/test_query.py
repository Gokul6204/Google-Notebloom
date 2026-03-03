from app.rag_service import RAGService
import logging

logging.basicConfig(level=logging.INFO)

def test_query():
    rag = RAGService()
    query = "What is the employee handbook about?"
    print(f"\nQuerying: {query}")
    results = rag.query(query, k=3)
    
    if not results:
        print("No results found.")
        return
        
    print(f"Found {len(results)} results:")
    for i, res in enumerate(results):
        print(f"\nResult {i+1}:")
        print(f"Content: {res.page_content[:200]}...")
        print(f"Source: {res.metadata.get('source')}")

if __name__ == "__main__":
    test_query()
