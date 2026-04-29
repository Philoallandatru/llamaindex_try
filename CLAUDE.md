# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LlamaIndex Chat Interface - A ChatGPT-style application for querying multiple data sources (PDF, Office documents, Jira, Confluence) using LlamaIndex with local LLM support via LM Studio. Features hybrid search (BM25 + vector similarity), conversation history, and source citations.

## Development Commands

### Backend

```bash
# Install dependencies (from project root)
pip install -e ".[dev]"

# Run backend server
cd backend
python main.py
# Or with uvicorn directly:
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest

# Code formatting
black backend/
ruff check backend/
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Development server
npm run dev

# Build for production
npm run build

# Linting
npm run lint

# E2E tests (requires backend running)
npm run test:e2e           # Headless
npm run test:e2e:ui        # UI mode
npm run test:e2e:headed    # Show browser
npm run test:e2e:debug     # Debug mode
```

### Prerequisites

- **LM Studio** must be running on port 1234 with a model loaded (recommended: qwen2.5-coder-7b-instruct)
- Backend runs on port 8000, frontend on port 5173
- Environment variables configured in `.env` (see `.env.example`)

## Architecture

### High-Level Flow

```
Frontend (React) ←→ FastAPI Backend ←→ LlamaIndex ←→ ChromaDB
                           ↓
                    LM Studio (Local LLM)
                           ↓
                    HuggingFace Embeddings (Local)
```

### Backend Structure

**Core Services** (backend/services/):
- `ingestion/` - Document parsing (MinerU for PDF/Office, Jira/Confluence connectors)
- `indexing/` - LlamaIndex integration with 3 retrieval modes:
  - `vector` - Semantic similarity only
  - `bm25` - Keyword matching only (good for IDs, technical terms)
  - `hybrid` - Combined approach (default, 50/50 weight)
- `chat/` - Conversation engine with context window (default 10 messages), session persistence, citation extraction
- `analysis/` - Jira issue deep analysis
- `knowledge/` - Knowledge base management (workspace/knowledge/)
- `reports/` - Daily report generation

**API Routes** (backend/api/):
- `chat_routes.py` - Session CRUD, send message, history
- `websocket_routes.py` - Streaming chat at `/ws/chat/{session_id}`
- `index_routes.py` - Index stats, build, clear, status
- `source_routes.py` - File upload, Jira/Confluence sync
- `analysis_routes.py` - Issue analysis endpoints
- `report_routes.py` - Report generation endpoints

**Models** (backend/models/):
- `chat.py` - ChatMessage, ChatSession, Citation
- `api.py` - Request/response schemas for all endpoints
- `analysis.py` - Issue analysis models
- `report.py` - Report models

**Configuration** (backend/config/settings.py):
- Pydantic Settings with environment variable loading
- Auto-creates required directories (data/, vector_store/, uploads/, chat_history/)

### Frontend Structure

**Pages** (frontend/src/pages/):
- `ChatPage.tsx` - Main chat interface with sidebar
- Additional pages for Issues, Reports, Knowledge Base

**API Client** (frontend/src/utils/api.ts):
- Axios-based TypeScript client
- Type-safe API calls matching backend schemas

**State Management**:
- TanStack Query for server state
- React hooks for local state

### Data Storage

All data stored in `data/` directory:
- `uploads/` - Uploaded PDF/Office files
- `vector_store/` - ChromaDB persistent storage
- `chat_history/` - JSON session files
- `workspace/knowledge/` - Knowledge base files

## Key Technical Details

### Retrieval Modes

The system supports three retrieval strategies (configured in `index_manager.py`):

1. **Vector** - Pure semantic similarity using embeddings (good for conceptual queries)
2. **BM25** - Keyword-based probabilistic ranking (good for exact matches like "PROJ-123")
3. **Hybrid** - Combines both with configurable weights (default: 50/50)

Use hybrid mode for most queries. Switch to BM25 when searching for specific IDs or technical terms.

### Chat Context

The chat engine uses `CondensePlusContextChatEngine` with:
- Configurable context window (default: 10 messages via `CHAT_CONTEXT_WINDOW`)
- Automatic context condensation for long conversations
- Source citation extraction from retrieved nodes
- Session persistence to `data/chat_history/`

### Document Processing

Documents are processed through this pipeline:
1. **Parse** - MinerU (primary) or pypdf (fallback) for PDF/Office
2. **Normalize** - Convert to LlamaIndex Document format with metadata
3. **Chunk** - Smart chunking based on document structure
4. **Embed** - HuggingFace embeddings (BAAI/bge-small-zh-v1.5 supports Chinese/English)
5. **Index** - Store in ChromaDB with BM25 index

### Global Service Instances

The FastAPI app initializes these global instances in `lifespan`:
- `index_manager` - Manages vector store and retrievers
- `session_manager` - Handles chat session persistence
- `chat_engine` - Main conversation engine
- `kb_manager` - Knowledge base operations
- `issue_analyzer` - Jira issue analysis (lazy init)

Routes receive these via `init_*_routes()` functions.

## Common Patterns

### Adding a New API Endpoint

1. Define request/response models in `backend/models/api.py`
2. Create route in appropriate `backend/api/*_routes.py` file
3. Initialize route dependencies in `backend/main.py` lifespan
4. Add TypeScript types and API function in `frontend/src/utils/api.ts`

### Adding a New Data Source

1. Create connector in `backend/services/ingestion/`
2. Implement document fetching and conversion to LlamaIndex Document
3. Add sync endpoint in `backend/api/source_routes.py`
4. Update `index_manager` to handle new source type

### Modifying Retrieval Behavior

Edit `backend/services/indexing/index_manager.py`:
- Adjust `bm25_weight` and `vector_weight` for hybrid mode
- Modify `similarity_top_k` for number of results
- Configure BM25 parameters (k1, b) in `bm25_retriever.py`

## Testing

- **Backend tests**: `tests/test_*.py` - Unit tests for ingestion, indexing, chat
- **Frontend E2E**: `frontend/e2e/*.spec.ts` - Playwright tests (see `frontend/E2E_TESTING.md`)
- E2E tests require backend running on port 8000

### Testing Requirements

**IMPORTANT**: When completing any new feature or significant functionality:

1. **Run Playwright E2E tests** to verify the feature works end-to-end:
   ```bash
   cd frontend
   npm run test:e2e
   ```
   
2. **Record progress in memory**: Document the completed work in the memory system at `C:\Users\10259\.claude\projects\C--Users-10259-Documents-code-codex-llamaindex-try\memory\`:
   - Save as `project` type memory for feature completion milestones
   - Include what was built, why it was needed, and how it should inform future work
   - Use the format specified in the memory system documentation

## Environment Configuration

Critical environment variables (see `.env.example`):
- `LM_STUDIO_BASE_URL` - Must point to running LM Studio instance
- `LM_STUDIO_MODEL` - Model name loaded in LM Studio
- `EMBEDDING_MODEL` - HuggingFace model for embeddings
- `JIRA_*` / `CONFLUENCE_*` - Optional Atlassian credentials
- `CHAT_CONTEXT_WINDOW` - Number of messages to maintain in context

## Troubleshooting

**LM Studio connection errors**: Verify LM Studio is running with `curl http://localhost:1234/v1/models`

**ChromaDB errors**: Clear and rebuild with `rm -rf data/vector_store/*` then restart backend

**Import errors**: Ensure you're running from project root and virtual environment is activated

**E2E test failures**: Backend must be running on port 8000 before running frontend tests
