# Jira Server & Confluence Server Authentication

## Overview

This CLI tool now supports **Jira Server** and **Confluence Server** authentication using Personal Access Tokens (PAT), without requiring email addresses.

## Changes Made

### 1. Jira Server Authentication

**Before (Jira Cloud):**
```python
reader = JiraReader(
    server_url="https://your-domain.atlassian.net",
    email="your-email@example.com",
    api_token="your-api-token"
)
```

**After (Jira Server):**
```python
from llama_index.readers.jira.base import PATauth

pat_auth = PATauth(
    server_url="http://your-jira-server:8080",
    api_token="your-personal-access-token"
)

reader = JiraReader(PATauth=pat_auth)
```

### 2. Confluence Server Authentication

**Before (Confluence Cloud):**
```python
reader = ConfluenceReader(
    base_url="https://your-domain.atlassian.net/wiki",
    cloud=True,
    oauth2={"token": "your-api-token"}
)
```

**After (Confluence Server):**
```python
reader = ConfluenceReader(
    base_url="http://your-confluence-server:8090",
    cloud=False,
    api_token="your-personal-access-token"
)
```

### 3. Configuration Changes

**config.yaml:**
```yaml
# Jira Configuration (Jira Server with Personal Access Token)
jira:
  server_url: "http://your-jira-server:8080"
  token: "your-personal-access-token"  # No email needed
  project_keys:
    - "PROJECT1"

# Confluence Configuration (optional, for Confluence Server)
confluence:
  server_url: "http://your-confluence-server:8090"
  token: "your-personal-access-token"  # No email needed
  space_keys:
    - "TECH"
```

**Note:** The `email` field is now **optional** and only required for Jira Cloud / Confluence Cloud.

## How to Get Personal Access Token

### Jira Server

1. Log in to your Jira Server instance
2. Go to **Profile** → **Personal Access Tokens**
3. Click **Create token**
4. Give it a name and set expiration (optional)
5. Copy the generated token

### Confluence Server

1. Log in to your Confluence Server instance
2. Go to **Profile** → **Personal Access Tokens**
3. Click **Create token**
4. Give it a name and set expiration (optional)
5. Copy the generated token

## Error Handling

The tool now provides better error diagnostics:

```
[ERROR] Jira API Connection Failed:
  Error Type: HTTPSConnectionPool
  Error Message: Failed to resolve http...

  Configuration Check:
    - Server URL: http://your-jira-server:8080
    - Token: Set
    - Auth Method: PATauth (Personal Access Token for Jira Server)

  Common Issues:
    1. Invalid server URL (should be http://your-jira-server:port)
    2. Incorrect Personal Access Token or expired token
    3. Network connectivity issues (check if server is reachable)
    4. Firewall blocking the connection
    5. Project key doesn't exist or no access permissions
    6. SSL certificate issues (if using https)
```

## Testing

Test your configuration:

```bash
# Test with mock data first
python cli.py TEST-123 --mock --output test_output

# Test with real Jira Server
python cli.py YOUR-ISSUE-KEY --output output
```

## Backward Compatibility

- **Jira Cloud users:** Can still use `email` field in config (it will be ignored for Server)
- **Jira Server users:** Simply omit the `email` field
- The tool automatically detects and uses the correct authentication method

## Files Modified

1. `backend/services/cli/data_loader.py` - Updated authentication logic
2. `backend/services/cli/config.py` - Made `email` field optional
3. `config.yaml` - Updated example configuration
4. `config.yaml.example` - Added Server/Cloud distinction

## References

- [LlamaIndex Jira Reader](https://docs.llamaindex.ai/en/stable/examples/data_connectors/JiraDemo/)
- [LlamaIndex Confluence Reader](https://docs.llamaindex.ai/en/stable/examples/data_connectors/ConfluenceDemo/)
- [Jira Server Personal Access Tokens](https://confluence.atlassian.com/enterprise/using-personal-access-tokens-1026032365.html)
