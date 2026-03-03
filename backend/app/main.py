import os
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
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

def process_and_index(file_path: str, filename: str):
    """Background task to process and index document"""
    try:
        logger.info(f"Starting background processing for {filename}")
        
        filename_lower = filename.lower()
        if filename_lower.endswith(".pdf"):
            docs = doc_service.process_pdf(file_path)
        elif filename_lower.endswith(".txt"):
            docs = doc_service.process_text(file_path)
        else:
            logger.error(f"Unsupported file type for processing: {filename}")
            return
            
        num_chunks = len(docs)
        logger.info(f"Document {filename} processed into {num_chunks} chunks.")
        
        # Add to vector store
        rag_service.add_documents(docs)
        logger.info(f"Completed processing and indexing for {filename}")
        
    except Exception as e:
        logger.error(f"Error in background processing for {filename}: {str(e)}", exc_info=True)

@app.post("/upload")
async def upload_document(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    logger.info(f"Received upload request for file: {file.filename}")
    
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        
        # Check if file already exists (Deduplication)
        if os.path.exists(file_path):
            logger.info(f"File {file.filename} already exists. Skipping re-processing.")
            return {
                "message": f"File {file.filename} already exists.", 
                "file_path": file_path,
                "status": "already_exists",
                "chunks": 0 # We don't know the exact count without checking DB, but that's fine
            }

        # Save file (Non-blocking for large files)
        def save_file():
            logger.info(f"Saving file to: {file_path}")
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            logger.info(f"File saved successfully: {file_path}")
            
        from fastapi.concurrency import run_in_threadpool
        await run_in_threadpool(save_file)
        
        # Add processing to background tasks
        # This prevents timeout on large files (e.g. 3000 pages)
        background_tasks.add_task(process_and_index, file_path, file.filename)
        
        return {
            "message": f"Successfully uploaded {file.filename}. Processing started in background.", 
            "file_path": file_path,
            "status": "processing_started",
            "chunks": -1 # Indicates processing is ongoing
        }
        
    except Exception as e:
        logger.error(f"Error during upload: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error during upload: {str(e)}")

@app.get("/documents")
async def list_documents():
    """List all uploaded documents"""
    files = []
    if os.path.exists(UPLOAD_DIR):
        for f in os.listdir(UPLOAD_DIR):
            if os.path.isfile(os.path.join(UPLOAD_DIR, f)):
                files.append({
                    "name": f,
                    "type": f.split('.')[-1].upper() if '.' in f else "FILE"
                })
    return {"documents": files}

@app.delete("/documents/{filename}")
async def delete_document(filename: str):
    """Delete a document from filesystem and vector store"""
    try:
        # Calculate file path first
        file_path = os.path.join(UPLOAD_DIR, filename)

        # 1. Delete from vector store using full path
        db_deleted = rag_service.delete_document(file_path)
        
        # 2. Delete from filesystem
        fs_deleted = False
        if os.path.exists(file_path):
            os.remove(file_path)
            fs_deleted = True
            logger.info(f"Deleted file from filesystem: {file_path}")
        
        if db_deleted or fs_deleted:
            return {"message": f"Successfully deleted {filename} from the system."}
        else:
            raise HTTPException(status_code=404, detail=f"Document {filename} not found.")
            
    except Exception as e:
        logger.error(f"Error during deletion: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error during deletion: {str(e)}")



@app.post("/query", response_model=QueryResponse)
async def query_notebook(request: QueryRequest):
    logger.info(f"Processing query: {request.prompt}")
    
    # Retrieve relevant context
    logger.info("Retrieving context from RAG service...")
    try:
        # Use run_in_threadpool to avoid blocking the event loop
        from fastapi.concurrency import run_in_threadpool
        docs = await run_in_threadpool(rag_service.query, request.prompt)
        logger.info(f"Retrieved {len(docs)} relevant chunks.")
    except Exception as e:
        logger.error(f"Error in RAG query: {str(e)}")
        return QueryResponse(answer=f"Error retrieving context: {str(e)}", sources=[])
    
    if not docs:
        logger.info("No relevant context found.")
        return QueryResponse(
            answer="I'm sorry, but I don't have any documents in my memory to answer that. Please upload a document first.",
            sources=[]
        )

    context = "\n\n".join([doc.page_content for doc in docs])
    sources = list(set([doc.metadata.get("source", "unknown") for doc in docs]))
    
    # Generate response
    logger.info("Generating response from LLM service...")
    try:
        answer = await llm_service.generate_response(request.prompt, context)
        logger.info("Response generated successfully.")
    except Exception as e:
        logger.error(f"Error in LLM generation: {str(e)}")
        return QueryResponse(answer=f"Error generating response: {str(e)}", sources=sources)
    
    return QueryResponse(answer=answer, sources=sources)


@app.post("/summary")
async def summarize_document(file_name: str):
    # This is a placeholder for real summarization logic
    # In a real app, we would query the LLM with all chunks or a map-reduce approach
    prompt = f"Summarize the document: {file_name}"
    docs = rag_service.query(prompt, k=5)
    context = "\n\n".join([doc.page_content for doc in docs])
    summary = await llm_service.generate_response(f"Provide a 3 paragraph summary of this document.", context)
    return {"summary": summary}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
