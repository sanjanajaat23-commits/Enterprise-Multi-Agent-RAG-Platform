<img width="1920" height="1080" alt="Screenshot 2026-08-20 091728" src="https://github.com/user-attachments/assets/fae9cb38-5286-4e23-8f70-d0f641fbc623" />
<img width="1920" height="1080" alt="Screenshot 2026-08-20 194652" src="https://github.com/user-attachments/assets/459b044f-1daa-4b13-afdf-f224aaafe058" />
<img width="1920" height="1080" alt="Screenshot 2026-08-20 194652" src="https://github.com/user-attachments/assets/9f42ebd3-f999-444b-bbc5-d95a335c489b" />
# Enterprise Multi-Agent RAG Platform

An end-to-end Enterprise Multi-Agent Retrieval-Augmented Generation (RAG) Platform built with FastAPI, Next.js, FAISS, Sentence Transformers, SQLite, and Ollama.

The platform combines intelligent agent routing, document-based question answering, document analysis, persistent conversation memory, session-isolated vector storage, and a modern web interface.

## Features

- Multi-agent AI architecture
- General, RAG, and Analysis agents
- Intelligent query routing
- PDF document question answering
- Multiple PDF support per session
- Session-isolated RAG
- Persistent FAISS vector storage
- Persistent SQLite conversation memory
- Local LLM inference with Ollama and Llama 3.2
- Sentence Transformer embeddings using all-MiniLM-L6-v2
- Next.js and TypeScript frontend
- FastAPI REST backend
- Document listing and clearing
- New Chat and Clear Memory functionality
- Backend health and system status endpoints

## Architecture

```text
User
  |
  v
Next.js Frontend
  |
  v
FastAPI Backend
  |
  v
Router Agent
  |
  +----------------+----------------+
  |                |                |
  v                v                v
GENERAL           RAG            ANALYSIS
Agent             Agent           Agent
  |                |                |
  |                v                v
  |        Session-Specific FAISS Store
  |                |
  |                v
  |          Retrieved Context
  |                |
  +----------------+----------------+
                   |
                   v
              Ollama LLM
              Llama 3.2
                   |
                   v
                Answer

Conversation Memory -> SQLite
PDF Embeddings      -> Sentence Transformers
Vector Indexes      -> Persistent FAISS Storage
```

## Multi-Agent System

### General Agent

Handles general questions that do not require uploaded document context.

Example:

```text
Explain machine learning in simple words.
```

### RAG Agent

Retrieves relevant chunks from PDFs uploaded in the current session and generates answers grounded in document context.

Example:

```text
What does the uploaded document say about revenue?
```

### Analysis Agent

Performs detailed analysis using retrieved information from uploaded documents. It can identify important facts, patterns, trends, risks, comparisons, and document-based insights.

Example:

```text
Analyze the main information in the uploaded document.
```

### Router Agent

Automatically routes each query to one of the following:

```text
GENERAL
RAG
ANALYSIS
```

## Session-Isolated RAG

Each chat receives a unique session ID. Documents uploaded in one session are isolated from other sessions.

```text
Session A -> PDF A -> FAISS Index A
Session B -> PDF B -> FAISS Index B
```

This prevents document context from being shared between independent chat sessions.

## Persistent FAISS Storage

FAISS indexes and document metadata are persisted to disk:

```text
data/
└── vector_stores/
    ├── session-a/
    │   ├── index.faiss
    │   └── documents.pkl
    └── session-b/
        ├── index.faiss
        └── documents.pkl
```

After a backend restart, a session's vector store can be loaded again without re-uploading the PDF.

Generated vector-store data is excluded from Git.

## Persistent Conversation Memory

Conversation messages are stored in SQLite and associated with a session ID.

The Clear Memory feature removes conversation history for the current session independently of document storage.

## Multiple Document Support

Users can upload multiple PDFs within the same session. The platform loads each PDF, splits it into chunks, generates embeddings, adds them to the session-specific FAISS index, and persists the updated index.

## Technology Stack

### Backend

- Python
- FastAPI
- Uvicorn
- Pydantic
- SQLAlchemy

### AI and Machine Learning

- Ollama
- Llama 3.2
- Sentence Transformers
- all-MiniLM-L6-v2

### RAG

- FAISS
- Document chunking
- Semantic embeddings
- Vector similarity search
- Context-grounded generation

### Database

- SQLite

### Frontend

- Next.js
- React
- TypeScript
- Tailwind CSS

## Project Structure

```text
Enterprise-Multi-Agent-RAG-Platform/
├── app/
│   ├── agents/
│   │   ├── analysis_agent.py
│   │   ├── general_agent.py
│   │   ├── memory.py
│   │   ├── rag_agent.py
│   │   └── router_agent.py
│   ├── api/v1/
│   │   ├── chat.py
│   │   ├── routes.py
│   │   └── upload.py
│   ├── config/
│   ├── database/
│   ├── llm/
│   ├── models/
│   ├── rag/
│   │   ├── embeddings.py
│   │   ├── loader.py
│   │   ├── retriever.py
│   │   ├── splitter.py
│   │   └── vectorstore.py
│   └── main.py
├── frontend/
│   ├── app/
│   ├── public/
│   ├── package.json
│   └── tsconfig.json
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## API Endpoints

### Health Check

```http
GET /api/v1/health
```

### System Status

```http
GET /api/v1/status
```

### Chat

```http
POST /api/v1/chat
```

Example:

```json
{
  "session_id": "web-session-1",
  "query": "What does the uploaded document say?"
}
```

### Upload PDF

```http
POST /api/v1/upload
```

Form data:

```text
file: document.pdf
session_id: web-session-1
```

### List Session Documents

```http
GET /api/v1/documents/{session_id}
```

### Clear Session Documents

```http
DELETE /api/v1/documents/{session_id}
```

### Clear Conversation Memory

```http
DELETE /api/v1/chat/memory/{session_id}
```

### Clear Complete Session

```http
DELETE /api/v1/chat/session/{session_id}
```

## Local Setup

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd Enterprise-Multi-Agent-RAG-Platform
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install backend dependencies

```bash
pip install -r requirements.txt
```

### 4. Install and configure Ollama

Install Ollama, then pull Llama 3.2:

```bash
ollama pull llama3.2
```

Verify:

```bash
ollama list
```

### 5. Configure environment variables

Create a local `.env` based on `.env.example`.

Never commit real API keys, credentials, or secrets.

### 6. Start the backend

Windows PowerShell:

```powershell
$env:OPENBLAS_NUM_THREADS="1"
$env:OMP_NUM_THREADS="1"
$env:MKL_NUM_THREADS="1"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8002
```

FastAPI backend:

```text
http://127.0.0.1:8002
```

API documentation:

```text
http://127.0.0.1:8002/docs
```

### 7. Start the frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend:

```text
http://localhost:3000
```

## Example Workflow

```text
Start FastAPI
    |
Start Next.js
    |
Create New Chat
    |
Upload PDF(s)
    |
Ask Question
    |
Router Selects Agent
    |
FAISS Retrieves Context (for RAG/Analysis)
    |
Ollama Generates Answer
    |
Conversation Stored in SQLite
```

## Security and Privacy

Sensitive and generated files should remain excluded from Git, including:

```text
.env
.venv/
uploads/
*.db
data/vector_stores/
data/chroma_db/
frontend/node_modules/
frontend/.next/
```

Never commit real API keys, credentials, uploaded private documents, or production secrets.

Session isolation in this portfolio project separates document context by chat session. A production deployment should additionally implement authentication, authorization, access controls, and secure secret management.

## Future Improvements

- User authentication and authorization
- PostgreSQL
- Redis caching
- Background document processing
- Streaming LLM responses
- Hybrid search
- Reranking
- Metadata filtering
- Individual document deletion
- Docker and Docker Compose
- Cloud deployment
- Automated tests
- CI/CD
- Observability and structured logging
- Role-based access control
- Production-grade vector database

## Portfolio Value

This project demonstrates practical experience with AI engineering, LLM application development, multi-agent systems, Retrieval-Augmented Generation, embeddings, vector search, FAISS, local LLM deployment, FastAPI, Next.js, persistent application state, session isolation, REST API design, and end-to-end AI application architecture.

## Disclaimer

This project is designed as an AI engineering and portfolio project. Before production use with sensitive enterprise data, additional security, authentication, authorization, testing, monitoring, and deployment controls should be implemented.
