# LlamaIndex Chat Interface

A ChatGPT-style interface for querying multiple data sources (PDF, Office documents, Jira, Confluence) using LlamaIndex + MinerU with local LLM support.

## Features

- 🤖 **Local LLM** - Uses LM Studio (OpenAI-compatible API)
- 📄 **Multi-format Support** - PDF, DOCX, XLSX, PPTX via MinerU
- 🔗 **Atlassian Integration** - Jira Issues and Confluence Pages
- 💬 **ChatGPT-style UI** - Conversation history with source citations
- 🔍 **Hybrid Search** - Vector similarity + BM25 keyword search
- ⚡ **Streaming Responses** - Real-time message generation
- 🎯 **Source Citations** - Every answer includes references

## Architecture

```
Frontend (React + Vite) ←→ Backend (FastAPI) ←→ LlamaIndex ←→ ChromaDB
                                    ↓
                            LM Studio (Local LLM)
```

## Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **LM Studio** - Download from [lmstudio.ai](https://lmstudio.ai/)
  - Download a model (recommended: `qwen2.5-coder-7b-instruct`)
  - Start local server on port 1234

## Quick Start

### 1. Backend Setup

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.\.venv\Scripts\Activate.ps1

# Activate (Linux/Mac)
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Copy environment template
cp .env.example .env

# Edit .env with your settings (LM Studio URL, Jira/Confluence credentials)

# Run backend server
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will start at `http://localhost:8000`

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will start at `http://localhost:5173`

### 3. Verify LM Studio

```bash
# Check if LM Studio is running
curl http://localhost:1234/v1/models
```

## Usage

### Upload Documents

1. Navigate to "Sources" page
2. Click "Upload File"
3. Select PDF or Office document
4. Wait for indexing to complete

### Connect Jira/Confluence

1. Navigate to "Sources" page
2. Click "Add Jira" or "Add Confluence"
3. Enter credentials (base URL, email, API token)
4. Test connection
5. Sync data

### Chat

1. Click "New Chat" in sidebar
2. Type your question
3. Get answers with source citations
4. Continue multi-turn conversation

## Project Structure

```
llamaindex_try/
├── backend/
│   ├── api/              # FastAPI routes
│   ├── services/         # Business logic
│   │   ├── ingestion/    # Document parsing (MinerU)
│   │   ├── indexing/     # LlamaIndex integration
│   │   └── chat/         # Chat engine
│   ├── models/           # Pydantic schemas
│   ├── config/           # Configuration
│   └── main.py           # FastAPI app entry
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   ├── hooks/        # Custom hooks
│   │   └── utils/        # Utilities
│   └── package.json
├── data/                 # Local data storage
│   ├── uploads/          # Uploaded files
│   ├── vector_store/     # ChromaDB data
│   └── chat_history/     # Session storage
├── tests/
└── pyproject.toml
```

## API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Development

### Run Tests

```bash
# Backend tests
pytest

# Frontend tests
cd frontend
npm test
```

### Code Formatting

```bash
# Python
black backend/
ruff check backend/

# TypeScript
cd frontend
npm run lint
```

## Configuration

### Environment Variables

See `.env.example` for all available configuration options.

Key settings:
- `LM_STUDIO_BASE_URL` - LM Studio API endpoint
- `LM_STUDIO_MODEL` - Model name to use
- `EMBEDDING_MODEL` - HuggingFace embedding model
- `JIRA_BASE_URL` / `CONFLUENCE_BASE_URL` - Atlassian URLs
- `DATA_DIR` - Local data storage path

### LM Studio Models

Recommended models:
- **qwen2.5-coder-7b-instruct** - Best for code/technical docs
- **llama-3.1-8b-instruct** - General purpose
- **deepseek-coder-6.7b** - Code generation

## Troubleshooting

### LM Studio Connection Failed

```bash
# Check if LM Studio is running
curl http://localhost:1234/v1/models

# Verify model is loaded in LM Studio UI
# Check .env has correct LM_STUDIO_BASE_URL
```

### MinerU Parsing Errors

```bash
# Install MinerU separately if needed
pip install magic-pdf[full]

# Check file permissions in data/uploads/
```

### ChromaDB Errors

```bash
# Clear vector store and rebuild
rm -rf data/vector_store/*
# Restart backend to rebuild index
```

## License

Internal project for SSD team use.

## Support

- Documentation: `docs/`
- Issues: Create GitHub issue
- Help: Check API docs at `/docs`
