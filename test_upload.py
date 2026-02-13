import requests
import os

# Test health endpoint
try:
    response = requests.get("http://localhost:8000/health")
    print(f"Health check: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Health check failed: {e}")

# Test upload endpoint with an existing PDF
pdf_path = r"e:\GoogleNoteboolm\backend\data\uploads\knowledge.pdf"
if os.path.exists(pdf_path):
    try:
        with open(pdf_path, 'rb') as f:
            files = {'file': ('knowledge.pdf', f, 'application/pdf')}
            response = requests.post("http://localhost:8000/upload", files=files)
            print(f"\nUpload test: {response.status_code}")
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Upload test failed: {e}")
else:
    print(f"PDF not found at {pdf_path}")
