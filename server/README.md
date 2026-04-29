# TypeScript Server

This directory contains the LlamaIndex TypeScript server that provides a modern chat interface.

## Architecture

- **TypeScript Layer**: Uses `@llamaindex/server` for chat UI and streaming
- **Python Backend**: Existing FastAPI server with RAG capabilities
- **Communication**: TypeScript workflow calls Python API via HTTP

## Setup

1. Install dependencies:
```bash
cd server
npm install
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your OpenAI API key and settings
```

3. Start the Python backend first:
```bash
cd ..
python backend/main.py
```

4. Start the TypeScript server:
```bash
npm run dev
```

5. Open browser:
```
http://localhost:3000
```

## Project Structure

```
server/
├── src/
│   ├── index.ts       # Server entry point
│   └── workflow.ts    # Workflow that calls Python API
├── package.json
├── tsconfig.json
└── .env.example
```

## How It Works

1. User sends message via chat UI (port 3000)
2. TypeScript workflow receives the message
3. Workflow calls Python FastAPI endpoint (port 8000)
4. Python backend performs RAG retrieval and generates response
5. Response flows back through workflow to chat UI
6. User sees the response with streaming support

## Development

- `npm run dev` - Start with hot reload
- `npm run build` - Build TypeScript
- `npm start` - Run production build
