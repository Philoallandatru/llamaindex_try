# Chat Services

This module handles conversational chat with context, session management, and source citations.

## Components

### 1. Chat Engine (`chat_engine.py`)
- LlamaIndex CondensePlusContextChatEngine integration
- Conversation context maintenance (configurable window)
- Streaming response support
- Automatic source citation extraction
- Session persistence

### 2. Session Manager (`session_manager.py`)
- Create, load, save, delete chat sessions
- Message history management
- Session listing and filtering
- JSON-based persistent storage
- Conversation history retrieval

### 3. Citation Handler (`citation_handler.py`)
- Extract citations from source nodes
- Format citations (Markdown, HTML, dict)
- Deduplicate citations
- Create text snippets
- Relevance score ranking

### 4. Message Handler (`message_handler.py`)
- Input validation (length, content)
- Message sanitization
- Suspicious content detection
- Source filter extraction
- Error response formatting

### 5. Chat Models (`backend/models/chat.py`)
- ChatMessage - Individual message
- ChatSession - Session with history
- SendMessageRequest - API request
- ChatResponse - API response
- Citation - Source citation

## Features

### Conversation Context
- Maintains last N messages in context (default: 10)
- Uses ChatMemoryBuffer for efficient context management
- Automatic context pruning based on token limit

### Source Citations
- Every response includes source documents
- Relevance scores for each source
- Automatic deduplication
- Formatted snippets with metadata

### Session Persistence
- JSON-based storage in `data/chat_history/`
- Automatic save on message add
- Session metadata support
- Efficient session listing

### Streaming Support
- Real-time response generation
- Chunk-by-chunk delivery
- Citations added after streaming completes

## Usage Examples

### Initialize Components

```python
from backend.services.indexing.index_manager import create_index_manager
from backend.services.chat.session_manager import create_session_manager
from backend.services.chat.chat_engine import create_chat_engine

# Create index manager (with documents)
index_manager = create_index_manager(use_hybrid=True)
await index_manager.add_documents(documents)

# Create session manager
session_manager = create_session_manager()

# Create chat engine
chat_engine = create_chat_engine(
    index_manager=index_manager,
    session_manager=session_manager,
    context_window=10,
)
```

### Create Session and Chat

```python
# Create new session
session = session_manager.create_session(name="My Chat")

# Send message
response = await chat_engine.send_message(
    session_id=session.session_id,
    message="What is Python?",
    retrieval_mode="hybrid",
    similarity_top_k=5,
)

print(response.content)
for source in response.sources:
    print(f"- {source['title']} (score: {source['relevance_score']:.2f})")
```

### Streaming Response

```python
async for chunk in chat_engine.stream_message(
    session_id=session.session_id,
    message="Tell me more about Python",
    retrieval_mode="hybrid",
):
    print(chunk, end="", flush=True)
```

### Session Management

```python
# List all sessions
sessions = session_manager.list_sessions(limit=10)
for s in sessions:
    print(f"{s['name']}: {s['message_count']} messages")

# Load session
session = session_manager.load_session(session_id)

# Get conversation history
history = session_manager.get_conversation_history(
    session_id=session_id,
    max_messages=10,
)

# Delete session
session_manager.delete_session(session_id)
```

### Citation Handling

```python
from backend.services.chat.citation_handler import CitationHandler

# Extract citations from source nodes
citations = CitationHandler.extract_citations(
    source_nodes=response.source_nodes,
    max_citations=5,
)

# Deduplicate
citations = CitationHandler.deduplicate_citations(citations)

# Format as markdown
markdown = CitationHandler.format_citations_markdown(citations)
print(markdown)

# Format as HTML
html = CitationHandler.format_citations_html(citations)
```

### Message Validation

```python
from backend.services.chat.message_handler import MessageHandler

# Validate message
is_valid, error = MessageHandler.validate_message(user_input)
if not is_valid:
    print(f"Invalid message: {error}")
    return

# Sanitize message
clean_message = MessageHandler.sanitize_message(user_input)

# Extract filters
filters = MessageHandler.extract_filters_from_message(user_input)
# Example: "Show me recent Jira issues"
# Returns: {"source_type": "jira", "sort_by": "updated_at"}
```

## Architecture

```
User Message
    ↓
MessageHandler (validate, sanitize)
    ↓
SessionManager (load session, add user message)
    ↓
ChatEngine (create chat engine with context)
    ↓
IndexManager (retrieve relevant documents)
    ↓
LlamaIndex CondensePlusContextChatEngine
    ↓
LLM (generate response with context)
    ↓
CitationHandler (extract and format citations)
    ↓
SessionManager (save assistant message)
    ↓
ChatResponse (return to user)
```

## Configuration

### Context Window
- Default: 10 messages
- Configurable via `context_window` parameter
- Affects memory usage and response quality

### Retrieval Modes
- `hybrid`: BM25 + Vector (recommended)
- `vector`: Semantic similarity only
- `bm25`: Keyword matching only

### Citation Limits
- Default: 5 sources per response
- Configurable via `similarity_top_k`
- Automatically deduplicated

## Best Practices

1. **Session Management**
   - Create new session for each conversation
   - Use descriptive session names
   - Clean up old sessions periodically

2. **Context Window**
   - Larger window = more context, slower responses
   - Smaller window = faster, less context
   - 10 messages is a good default

3. **Retrieval Mode**
   - Use `hybrid` for most queries
   - Use `bm25` for exact keyword matching
   - Use `vector` for conceptual queries

4. **Error Handling**
   - Always validate messages before processing
   - Handle session not found errors
   - Provide user-friendly error messages

5. **Performance**
   - Use streaming for long responses
   - Limit citation count appropriately
   - Clean up old sessions regularly

## Dependencies

- `llama-index` - Chat engine and memory
- `pydantic` - Data models
- Backend services: indexing, config

## Testing

Run tests:
```bash
pytest tests/test_chat.py -v
```

Test coverage:
- Session creation and management
- Message validation and sanitization
- Citation extraction and formatting
- Conversation context handling
