# Jira Deep Analysis CLI

Minimal CLI tool for deep Jira issue analysis using LlamaIndex.

## Quick Start

1. **Install dependencies**
   ```bash
   pip install -e .
   # Or install required packages:
   pip install llama-index-readers-jira llama-index-readers-confluence pyyaml
   ```

2. **Configure**
   ```bash
   cp config.yaml.example config.yaml
   # Edit config.yaml with your Jira/Confluence credentials
   ```

3. **Run analysis**
   ```bash
   python cli.py PROJ-123
   ```

## Tested Components

✓ CLI argument parsing  
✓ Config loading (YAML)  
✓ IndexTracker (incremental indexing)  
✓ OutputFormatter (markdown/HTML generation)

## Usage

```bash
# Basic analysis
python cli.py PROJ-123

# Force refresh all data sources
python cli.py PROJ-123 --refresh

# Custom config file
python cli.py PROJ-123 -c my-config.yaml

# Custom output directory
python cli.py PROJ-123 -o ./reports
```

## Configuration

Edit `config.yaml`:

```yaml
jira:
  server_url: "https://your-domain.atlassian.net"
  token: "your-api-token"
  email: "your-email@example.com"
  project_keys: ["PROJ"]

confluence:  # Optional
  server_url: "https://your-domain.atlassian.net/wiki"
  token: "your-api-token"
  email: "your-email@example.com"
  space_keys: ["TECH"]

documents:
  folder: "./documents"  # Local PDF/Office files

llm:
  base_url: "http://localhost:1234/v1"
  model: "qwen2.5-coder-7b-instruct"
  embedding_model: "BAAI/bge-small-zh-v1.5"

storage:
  vector_store: "./data/cli_vector_store"
  index_cache: "./data/cli_index_cache.json"
  output: "./output"
```

## Analysis Pipeline

1. **Fetch** - Retrieve Jira issue with comments/attachments
2. **Extract** - Structure issue data
3. **Retrieve Similar** - Find related Jira issues via vector search
4. **Retrieve Docs** - Find relevant Wiki/Spec/Case documents
5. **Aggregate** - Combine evidence
6. **Generate RCA** - LLM-powered root cause analysis
7. **Output** - Save as markdown and HTML

## Incremental Indexing

- First run: Full sync of all data sources
- Subsequent runs: Only index new/changed items
- Use `--refresh` to force full re-index
- Index state tracked in `data/cli_index_cache.json`

## Output

Analysis saved to `output/` directory:
- `{JIRA_KEY}_{timestamp}.md` - Markdown report
- `{JIRA_KEY}_{timestamp}.html` - HTML report

## Requirements

- Python 3.11+
- LM Studio running on port 1234 (or configure custom LLM endpoint)
- Jira/Confluence API tokens
