import uvicorn
import os
import sys

# Add the backend directory to sys.path so we can import 'app'
sys.path.append(os.path.join(os.getcwd(), "backend"))

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
