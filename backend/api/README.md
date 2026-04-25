# API Routes

FastAPI backend routes for the LlamaIndex Chat application.

## Running the Server

```bash
# Development mode
cd backend
python main.py

# Or with uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Server will start at: http://localhost:8000

## Interactive Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Main Endpoints

### Health & Info
- `GET /` - Root endpoint
- `GET /health` - Health check

### Chat Routes (`/api/chat`)
- `POST /api/chat/sessions` - Create session
- `GET /api/chat/sessions` - List sessions
- `GET /api/chat/sessions/{id}` - Get session details
- `DELETE /api/chat/sessions/{id}` - Delete session
- `POST /api/chat/message` - Send message (non-streaming)
- `GET /api/chat/sessions/{id}/history` - Get conversation history

### WebSocket Routes (`/ws`)
- `WS /ws/chat/{session_id}` - Streaming chat

### Index Routes (`/api/index`)
- `GET /api/index/stats` - Get index statistics
- `POST /api/index/build` - Build/rebuild index
- `DELETE /api/index/clear` - Clear index
- `GET /api/index/status` - Get index status

### Source Routes (`/api/sources`)
- `POST /api/sources/upload` - Upload file
- `POST /api/sources/jira/test` - Test Jira connection
- `POST /api/sources/jira/sync` - Sync Jira issues
- `POST /api/sources/confluence/test` - Test Confluence connection
- `POST /api/sources/confluence/sync` - Sync Confluence pages
- `GET /api/sources/list` - List sources

## Example Usage

### Create Session and Chat

```python
import httpx

# Create session
response = httpx.post(
    "http://localhost:8000/api/chat/sessions",
    json={"name": "My Chat"}
)
session = response.json()

# Send message
response = httpx.post(
    "http://localhost:8000/api/chat/message",
    json={
        "session_id": session["session_id"],
        "message": "What is Python?",
        "retrieval_mode": "hybrid"
    }
)
result = response.json()
print(result["content"])
```

### WebSocket Streaming

```javascript
const ws = new WebSocket(`ws://localhost:8000/ws/chat/${sessionId}`);

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'chunk') {
    console.log(data.content);
  } else if (data.type === 'complete') {
    console.log('Sources:', data.sources);
  }
};

ws.send(JSON.stringify({
  message: 'What is Python?',
  retrieval_mode: 'hybrid'
}));
```

See full API documentation at `/docs` when server is running.
