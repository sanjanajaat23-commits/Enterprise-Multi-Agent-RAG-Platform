# Enterprise Multi-Agent RAG Platform

End-to-end document intelligence platform combining **multi-agent routing, Retrieval-Augmented Generation (RAG), persistent vector search, conversation memory, and a full-stack web application**.

Built to demonstrate practical **AI engineering, Python backend, API design, retrieval systems, and full-stack development**.

## What it does

Users can create isolated chat sessions, upload multiple PDFs, ask questions about their documents, and request deeper document analysis.

A router automatically selects the appropriate workflow:

```text
User Query
    ↓
Router Agent
    ├── GENERAL → General response
    ├── RAG → Retrieve document context → Answer
    └── ANALYSIS → Retrieve context → Analyze
```

## Key Engineering Features

- Multi-agent architecture with General, RAG, Analysis, and Router agents
- Session-isolated document retrieval
- Multiple PDF uploads per session
- Semantic embeddings with `all-MiniLM-L6-v2`
- Persistent FAISS vector indexes
- Persistent SQLite conversation memory
- Local LLM inference with Ollama / Llama 3.2
- FastAPI REST backend
- Next.js + React + TypeScript frontend
- Document listing and clearing APIs
- Conversation/session reset APIs
- Health and system-status endpoints
- Environment-based configuration and Git hygiene

## Architecture

```text
┌─────────────────────────────────────────────────────┐
│              Next.js / React / TypeScript            │
│              Chat UI · Upload · Sessions             │
└─────────────────────────┬───────────────────────────┘
                          │ REST / JSON
                          ▼
┌─────────────────────────────────────────────────────┐
│                     FastAPI                          │
│            API Routes · Agent Orchestration          │
└─────────────────────────┬───────────────────────────┘
                          ▼
                    Router Agent
                  /       |        \
                 /        |         \
          GENERAL         RAG      ANALYSIS
                            │          │
                            ▼          ▼
                    Session FAISS Retriever
                            │
                            ▼
                     Retrieved Context
                            │
                            ▼
                     Ollama / Llama 3.2
                            │
                            ▼
                         Answer

Conversation Memory ─────────────→ SQLite
PDF Embeddings ─────────────────→ Sentence Transformers
Vector Indexes ─────────────────→ Persistent FAISS
```

## Retrieval Design

Each session receives its own vector-store namespace:

```text
Session A → PDF A → Embeddings → FAISS Index A
Session B → PDF B → Embeddings → FAISS Index B
```

This prevents document context from being shared between independent sessions.

When a PDF is uploaded, the application loads the document, splits it into chunks, creates embeddings, adds them to the session-specific FAISS index, and persists the index.

## Conversation Memory

Conversation messages are persisted in SQLite and associated with the session ID. Memory can be cleared independently from uploaded document storage, while a complete session reset can clear both.

## API Surface

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/v1/health` | Backend health check |
| GET | `/api/v1/status` | System status |
| POST | `/api/v1/chat` | Process a chat query |
| POST | `/api/v1/upload` | Upload a PDF to a session |
| GET | `/api/v1/documents/{session_id}` | List session documents |
| DELETE | `/api/v1/documents/{session_id}` | Clear session documents |
| DELETE | `/api/v1/chat/memory/{session_id}` | Clear conversation memory |
| DELETE | `/api/v1/chat/session/{session_id}` | Clear complete session |

## Technology Stack

**Backend**
- Python
- FastAPI
- Uvicorn
- Pydantic
- SQLAlchemy

**AI / RAG**
- Ollama
- Llama 3.2
- Sentence Transformers
- FAISS
- Semantic embeddings
- Vector similarity search

**Frontend**
- Next.js
- React
- TypeScript
- Tailwind CSS

**Persistence**
- SQLite
- Persistent FAISS indexes

## Repository Structure

```text
NovaRAG/
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

## Run Locally

### Backend

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Install Ollama and pull the local model:

```powershell
ollama pull llama3.2
```

Create `.env` from `.env.example`, then start FastAPI:

```powershell
$env:OPENBLAS_NUM_THREADS="1"
$env:OMP_NUM_THREADS="1"
$env:MKL_NUM_THREADS="1"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8002
```

API documentation:

`http://127.0.0.1:8002/docs`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend:

`http://localhost:3000`

## Example Workflow

```text
Start application
      ↓
Create chat session
      ↓
Upload one or more PDFs
      ↓
Documents are chunked + embedded
      ↓
Session FAISS index is persisted
      ↓
Ask a question
      ↓
Router selects General / RAG / Analysis
      ↓
Relevant context is retrieved
      ↓
Llama 3.2 generates the response
      ↓
Conversation is persisted in SQLite
```

## Security Notes

The project excludes local secrets and generated data such as `.env`, virtual environments, uploaded files, databases, and generated vector stores from Git.

Session isolation protects document context at the application level. A production deployment would additionally require authentication, authorization, secure secret management, HTTPS/TLS, rate limiting, monitoring, and stronger access controls.

## Production Roadmap

- Authentication and authorization
- PostgreSQL
- Redis caching
- Background document processing
- Streaming responses
- Hybrid retrieval and reranking
- Metadata filtering
- Docker / Docker Compose
- Cloud deployment
- Automated tests
- CI/CD
- Observability and structured logging
- Role-based access control

## Portfolio Value

This project demonstrates hands-on experience with **AI application architecture, multi-agent systems, RAG pipelines, embeddings, vector search, local LLM inference, FastAPI REST APIs, Next.js, persistent application state, session isolation, and end-to-end full-stack development**.

> Portfolio project — production deployment would require additional security, testing, monitoring, and infrastructure hardening.
