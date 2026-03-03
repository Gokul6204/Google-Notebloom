import requests
import os
import time

BASE_URL = "http://localhost:8000"

def test_health():
    print("Testing health...")
    try:
        resp = requests.get(f"{BASE_URL}/health")
        if resp.status_code == 200:
            print("✓ Backend is healthy")
            return True
        else:
            print(f"✗ Backend returned {resp.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to backend. Is it running?")
        return False

def test_upload_and_query():
    print("\nTesting upload and query...")
    filename = "test_doc_chroma.txt"
    content = "ChromaDB is a vector database that is open-source. It is used for building AI applications with embeddings."
    
    # Create dummy file
    with open(filename, "w") as f:
        f.write(content)
        
    try:
        # Upload
        print(f"Uploading {filename}...")
        with open(filename, "rb") as f:
            files = {"file": f}
            resp = requests.post(f"{BASE_URL}/upload", files=files)
            
        if resp.status_code != 200:
            print(f"✗ Upload failed: {resp.text}")
            return False
            
        print("✓ Upload successful")
        print(resp.json())
        
        # Wait a bit for indexing
        time.sleep(2)
        
        # Query
        print("Querying...")
        query = {"prompt": "What is ChromaDB?"}
        resp = requests.post(f"{BASE_URL}/query", json=query)
        
        if resp.status_code != 200:
            print(f"✗ Query failed: {resp.text}")
            return False
            
        print("✓ Query successful")
        result = resp.json()
        print(f"Answer: {result['answer']}")
        print(f"Sources: {result['sources']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    finally:
        if os.path.exists(filename):
            os.remove(filename)

if __name__ == "__main__":
    if test_health():
        test_upload_and_query()
