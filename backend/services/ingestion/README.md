# Document Ingestion Services

This module handles document parsing and normalization from multiple sources.

## Components

### 1. MinerU Parser (`mineru_parser.py`)
- Parses PDF and Office documents using MinerU
- Extracts text, tables, images with layout preservation
- Supports both Python API and CLI fallback
- Graceful degradation if MinerU not available

### 2. Document Parser (`document_parser.py`)
- Multi-format document parser
- Supports: PDF, DOCX, XLSX, PPTX
- Uses MinerU as primary parser
- Falls back to pypdf for PDFs if MinerU unavailable

### 3. Jira Connector (`jira_connector.py`)
- Fetches Jira issues via atlassian-python-api
- Supports JQL queries, project fetching, status filtering
- Converts issues to LlamaIndex Document format

### 4. Confluence Connector (`confluence_connector.py`)
- Fetches Confluence pages and spaces
- Supports CQL queries, label filtering, date filtering
- Converts pages to LlamaIndex Document format

### 5. Document Normalizer (`normalizer.py`)
- Normalizes documents from all sources to LlamaIndex format
- Adds metadata (source_type, timestamps, etc.)
- Supports document chunking for long texts

## Usage Examples

### Parse a PDF
```python
from backend.services.ingestion.document_parser import DocumentParser

parser = DocumentParser(use_mineru=True)
documents = await parser.parse_file(Path("document.pdf"))
```

### Fetch Jira Issues
```python
from backend.services.ingestion.jira_connector import JiraConnector

connector = JiraConnector(
    base_url="https://your-domain.atlassian.net",
    email="your-email@example.com",
    api_token="your-api-token"
)

# Test connection
result = await connector.test_connection()

# Fetch project issues
documents = await connector.fetch_project("PROJ")

# Fetch with JQL
documents = await connector.fetch_issues("project = PROJ AND status = Open")
```

### Fetch Confluence Pages
```python
from backend.services.ingestion.confluence_connector import ConfluenceConnector

connector = ConfluenceConnector(
    base_url="https://your-domain.atlassian.net/wiki",
    email="your-email@example.com",
    api_token="your-api-token"
)

# Fetch entire space
documents = await connector.fetch_space("SPACE")

# Fetch single page
document = await connector.fetch_page("12345")
```

## Dependencies

- `magic-pdf` - MinerU for document parsing
- `pypdf` - Fallback PDF parser
- `atlassian-python-api` - Jira/Confluence API client
- `llama-index` - Document format
