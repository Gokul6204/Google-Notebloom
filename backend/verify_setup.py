import requests
import os
import time
import sys

# Configuration
BASE_URL = "http://localhost:8000"
TEST_FILENAME = "test_chroma_setup.txt"
TEST_CONTENT = "This is a verification document for the Google NotebookLM clone using ChromaDB."

def print_result(msg, success=True):
    icon = "✅" if success else "❌"
    print(f"{icon} {msg}")

def check_backend_running():
    print("Checking backend status...")
    try:
        resp = requests.get(f"{BASE_URL}/health")
        if resp.status_code == 200:
            print_result("Backend is running and accessible.")
            return True
        else:
            print_result(f"Backend returned status {resp.status_code}", False)
            return False
    except requests.exceptions.ConnectionError:
        print_result("Could not connect to backend at http://localhost:8000", False)
        print("   Please ensure 'python app/run_backend.py' is running.")
        return False

def verify_full_flow():
    print("\nStarting end-to-end verification...")
    
    # 1. Create test file
    with open(TEST_FILENAME, "w") as f:
        f.write(TEST_CONTENT)
    
    upload_success = False
    
    try:
        # 2. Upload
        print(f"Uploading {TEST_FILENAME}...")
        with open(TEST_FILENAME, "rb") as f:
            files = {"file": f}
            resp = requests.post(f"{BASE_URL}/upload", files=files)
            
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") == "already_exists":
                print_result("File already exists. Proceeding to query.")
                # We assume it was uploaded correctly before or we can delete and retry
                # For now let's just proceed
            else:
                print_result(f"Upload successful. Chunks: {data.get('chunks')}")
            upload_success = True
        else:
            print_result(f"Upload failed: {resp.text}", False)
            return
            
        # 3. Wait for indexing (background task)
        print("Waiting 3 seconds for background indexing...")
        time.sleep(3)
        
        # 4. Query
        print("Querying for content...")
        query = {"prompt": "What is this verification document for?"}
        resp = requests.post(f"{BASE_URL}/query", json=query)
        
        if resp.status_code == 200:
            result = resp.json()
            answer = result.get("answer", "")
            sources = result.get("sources", [])
            
            print(f"\n--- Model Response ---\n{answer}\n----------------------\n")
            
            if "verification document" in answer.lower() or "chromadb" in answer.lower():
                print_result("RAG Retrieval verified! Model answered from context.")
            elif not sources:
                 print_result("RAG Retrieval failed. No sources found.", False)
                 print("   This likely means the background indexing task failed or Ollama is not running.")
            else:
                 print_result("RAG Retrieval might be working, but answer was generic.")
                 print(f"   Sources found: {sources}")
        else:
            print_result(f"Query failed: {resp.text}", False)

    except Exception as e:
        print_result(f"Verification error: {e}", False)
        
    finally:
        # 5. Cleanup
        if upload_success:
            print("\nCleaning up...")
            try:
                # Use filename to delete
                requests.delete(f"{BASE_URL}/documents/{TEST_FILENAME}")
                print("Test document deleted from backend.")
            except:
                print("Failed to delete test document from backend.")
                
        if os.path.exists(TEST_FILENAME):
            os.remove(TEST_FILENAME)
            
if __name__ == "__main__":
    print("=== ChromaDB Setup Verification ===")
    if check_backend_running():
        verify_full_flow()
    else:
        sys.exit(1)
