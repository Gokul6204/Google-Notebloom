import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import shutil
import logging

from app.llm_service import LLMService
from app.rag_service import RAGService
from app.document_service import DocumentService

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Google Noteboolm API")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
llm_service = LLMService()
rag_service = RAGService()
doc_service = DocumentService()

# Use absolute path for uploads
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "data", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
logger.info(f"Upload directory: {UPLOAD_DIR}")

class QueryRequest(BaseModel):
    prompt: str

class QueryResponse(BaseModel):
    answer: str
    sources: List[str]

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    logger.info(f"Received upload request for file: {file.filename}")
    
    try:
        # Save file
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        logger.info(f"Saving file to: {file_path}")
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"File saved successfully: {file_path}")
        
        # Process document
        if file.filename.endswith(".pdf"):
            logger.info(f"Processing PDF: {file.filename}")
            docs = doc_service.process_pdf(file_path)
        elif file.filename.endswith(".txt"):
            logger.info(f"Processing TXT: {file.filename}")
            docs = doc_service.process_text(file_path)
        else:
            logger.error(f"Unsupported file type: {file.filename}")
            raise HTTPException(status_code=400, detail="Unsupported file type. Please upload PDF or TXT files.")
        
        logger.info(f"Document processed into {len(docs)} chunks")
        
        # Add to RAG system
        rag_service.add_documents(docs)
        logger.info(f"Documents added to RAG system successfully")
        
        return {
            "message": f"Successfully uploaded and indexed {file.filename}", 
            "chunks": len(docs),
            "file_path": file_path
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing upload: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.post("/query", response_model=QueryResponse)
async def query_notebook(request: QueryRequest):
    # Retrieve relevant context
    docs = rag_service.query(request.prompt)
    context = "\n\n".join([doc.page_content for doc in docs])
    sources = list(set([doc.metadata.get("source", "unknown") for doc in docs]))
    
    # Generate response
    answer = await llm_service.generate_response(request.prompt, context)
    
    return QueryResponse(answer=answer, sources=sources)

@app.post("/summary")
async def summarize_document(file_name: str):
    # This is a placeholder for real summarization logic
    # In a real app, we would query the LLM with all chunks or a map-reduce approach
    prompt = f"Summarize the document: {file_name}"
    docs = rag_service.query(prompt, k=10)
    context = "\n\n".join([doc.page_content for doc in docs])
    summary = await llm_service.generate_response(f"Provide a 3 paragraph summary of this document.", context)
    return {"summary": summary}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
