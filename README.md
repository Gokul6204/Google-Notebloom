# Noteboolm 🚀

A premium AI-powered research assistant inspired by NotebookLM.

## 🌟 Features

- **Document Ingestion**: Upload PDFs and Text files.
- **RAG-based Chat**: Ask questions about your documents and get answers with sources.
- **Ollama Integration**: Powered by local models like `gemma3:4b`.
- **Modern UI**: Sleek, responsive interface built with React and Vite.

## 🛠️ Tech Stack

- **Backend**: FastAPI, LangChain, ChromaDB, Ollama.
- **Frontend**: React, Vite, Vanilla CSS.

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Node.js & npm
- [Ollama](https://ollama.com/) installed and running.

### Installation

1. **Clone the repository** (if applicable).
2. **Setup Backend**:
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate # or .venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```
3. **Setup Frontend**:
   ```bash
   cd frontend
   npm install
   ```

### Running the App

1. **Start Backend**:
   ```bash
   python run_backend.py
   ```
2. **Start Frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

## 📝 License

MIT
