# PDF Upload and RAG Processing Flow

## Complete System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React)                         │
│                                                                  │
│  1. User clicks "+" button                                      │
│  2. Selects PDF file                                            │
│  3. handleFileUpload() creates FormData                         │
│  4. POST to http://localhost:8000/upload                        │
│  5. Shows progress bar (0% → 90% → 100%)                        │
│  6. Displays success/error message in chat                      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    HTTP POST /upload
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI) - main.py                   │
│                                                                  │
│  1. Receive UploadFile                                          │
│     LOG: "Received upload request for file: {filename}"         │
│                                                                  │
│  2. Save to disk                                                │
│     Path: E:\GoogleNoteboolm\backend\data\uploads\{filename}    │
│     LOG: "Saving file to: {file_path}"                          │
│     LOG: "File saved successfully"                              │
│                                                                  │
│  3. Process document (DocumentService)                          │
│     LOG: "Processing PDF: {filename}"                           │
│     ↓                                                            │
│     ┌─────────────────────────────────────────────────┐        │
│     │      DocumentService.process_pdf()              │        │
│     │                                                  │        │
│     │  - PyMuPDFLoader loads PDF                      │        │
│     │  - RecursiveCharacterTextSplitter splits text   │        │
│     │    • chunk_size: 1000 chars                     │        │
│     │    • chunk_overlap: 100 chars                   │        │
│     │  - Returns List[Document]                       │        │
│     └─────────────────────────────────────────────────┘        │
│     ↓                                                            │
│     LOG: "Document processed into {N} chunks"                   │
│                                                                  │
│  4. Add to RAG system (RAGService)                              │
│     LOG: "Documents added to RAG system successfully"           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   RAGService.add_documents()                     │
│                                                                  │
│  LOG: "Adding {N} documents to vector database"                 │
│                                                                  │
│  1. Generate embeddings (Ollama)                                │
│     ┌─────────────────────────────────────────────────┐        │
│     │      OllamaEmbeddings                            │        │
│     │      model: "nomic-embed-text"                   │        │
│     │                                                  │        │
│     │  For each chunk:                                │        │
│     │    text → embedding vector (768 dimensions)     │        │
│     └─────────────────────────────────────────────────┘        │
│                                                                  │
│  2. Store in FAISS vector database                              │
│     LOG: "Creating new FAISS index" (first time)                │
│     OR                                                           │
│     LOG: "Adding to existing FAISS index"                       │
│                                                                  │
│  3. Persist to disk                                             │
│     Path: E:\GoogleNoteboolm\backend\faiss_index\               │
│     LOG: "Saving FAISS index to {path}"                         │
│     LOG: "FAISS index saved successfully"                       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    Return success response
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React)                         │
│                                                                  │
│  1. Receives response:                                          │
│     {                                                            │
│       "message": "Successfully uploaded and indexed...",        │
│       "chunks": 45,                                             │
│       "file_path": "E:\GoogleNoteboolm\backend\..."            │
│     }                                                            │
│                                                                  │
│  2. Updates UI:                                                 │
│     - Progress bar → 100%                                       │
│     - Adds to sources list                                      │
│     - Shows success message in chat                             │
│       "✅ Successfully uploaded and indexed knowledge.pdf       │
│        (45 chunks created)"                                     │
└─────────────────────────────────────────────────────────────────┘
```

## Query Flow (After Upload)

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React)                         │
│                                                                  │
│  1. User types question                                         │
│  2. handleSend() sends POST to /query                           │
│     Body: { "prompt": "What is...?" }                           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND - main.py /query                      │
│                                                                  │
│  1. RAGService.query(prompt)                                    │
│     ┌─────────────────────────────────────────────────┐        │
│     │  FAISS similarity search                         │        │
│     │  - Convert query to embedding                    │        │
│     │  - Find top 7 most similar chunks                │        │
│     │  - Return List[Document]                         │        │
│     └─────────────────────────────────────────────────┘        │
│                                                                  │
│  2. Build context from retrieved documents                      │
│     context = "\n\n".join([doc.page_content for doc in docs])   │
│                                                                  │
│  3. LLMService.generate_response(prompt, context)               │
│     ┌─────────────────────────────────────────────────┐        │
│     │  Ollama LLM (llama3)                             │        │
│     │                                                  │        │
│     │  Prompt Template:                                │        │
│     │  "You are an AI research assistant...           │        │
│     │   Context: {context}                             │        │
│     │   Question: {question}                           │        │
│     │   Answer:"                                       │        │
│     │                                                  │        │
│     │  → Generated answer                              │        │
│     └─────────────────────────────────────────────────┘        │
│                                                                  │
│  4. Return QueryResponse                                        │
│     {                                                            │
│       "answer": "Based on the documents...",                    │
│       "sources": ["knowledge.pdf"]                              │
│     }                                                            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React)                         │
│                                                                  │
│  1. Displays AI response in chat                                │
│  2. Shows source badges below answer                            │
└─────────────────────────────────────────────────────────────────┘
```

## Key Components

### 1. Document Processing
- **PyMuPDFLoader**: Extracts text from PDF pages
- **RecursiveCharacterTextSplitter**: Splits into manageable chunks
  - Preserves context with overlap
  - Ensures chunks fit in embedding model

### 2. Embeddings
- **Model**: nomic-embed-text (via Ollama)
- **Purpose**: Convert text to vector representations
- **Dimension**: 768-dimensional vectors
- **Usage**: Both for indexing and querying

### 3. Vector Storage
- **FAISS**: Facebook AI Similarity Search
- **Type**: In-memory with disk persistence
- **Index Type**: Flat (exact search)
- **Persistence**: Saved to `backend/faiss_index/`

### 4. LLM
- **Model**: llama3 (via Ollama)
- **Temperature**: 0.1 (low for factual responses)
- **Max tokens**: 500
- **Purpose**: Generate answers based on context

## Error Handling

### Upload Errors
1. **File save fails** → HTTP 500 with detailed error
2. **Unsupported file type** → HTTP 400 "Please upload PDF or TXT"
3. **PDF processing fails** → HTTP 500 with PyMuPDF error
4. **Embedding fails** → HTTP 500 with Ollama error
5. **FAISS save fails** → HTTP 500 with file system error

All errors are:
- Logged to backend console with stack traces
- Returned to frontend with detailed messages
- Displayed in chat UI with ❌ emoji

### Query Errors
1. **No documents indexed** → Returns empty context
2. **Ollama not running** → Connection error
3. **Model not found** → Model loading error

## Logging Levels

### INFO logs show:
- Upload directory path
- FAISS index directory path
- File received and saved
- Processing steps
- Chunk counts
- FAISS operations
- HTTP requests

### ERROR logs show:
- Exception details
- Stack traces
- Failed operations

## File Structure

```
E:\GoogleNoteboolm\
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI endpoints
│   │   ├── document_service.py  # PDF/text processing
│   │   ├── rag_service.py       # Vector DB operations
│   │   └── llm_service.py       # LLM interactions
│   ├── data/
│   │   └── uploads/             # Uploaded PDFs stored here
│   │       ├── knowledge.pdf
│   │       └── ...
│   ├── faiss_index/             # Vector DB persisted here
│   │   ├── index.faiss
│   │   └── index.pkl
│   └── requirements.txt
├── frontend/
│   └── src/
│       └── App.jsx              # React UI
└── run_backend.py               # Server launcher
```
