"""Load data from Jira, Confluence, and local documents"""

from pathlib import Path
from typing import List
from llama_index.core import Document
from backend.services.ingestion.document_parser import DocumentParser
from backend.services.cli.index_tracker import IndexTracker
from backend.services.cli.mock_jira import MockJiraLoader

class DataLoader:
    def __init__(self, config, tracker: IndexTracker, use_mock_jira: bool = False):
        self.config = config
        self.tracker = tracker
        self.doc_parser = DocumentParser()
        self.use_mock_jira = use_mock_jira

        if use_mock_jira:
            self.mock_jira = MockJiraLoader()

    def load_jira_issues(self, force_refresh: bool = False) -> List[Document]:
        """Load Jira issues incrementally"""
        if self.use_mock_jira:
            # Use mock data
            docs = []
            for project_key in self.config.jira.project_keys:
                issues = self.mock_jira.load_issues(project_key)
                for doc in issues:
                    issue_key = doc.metadata.get("key")
                    if force_refresh or not self.tracker.is_indexed("jira_issues", issue_key):
                        docs.append(doc)
                        self.tracker.mark_indexed("jira_issues", issue_key, {"project": project_key})
            return docs

        # Real Jira API (original code)
        try:
            from llama_index.readers.jira import JiraReader

            print(f"\n=== Connecting to Jira Server ===")
            print(f"Server URL: {self.config.jira.server_url}")
            print(f"Email: {self.config.jira.email}")
            print(f"Project Keys: {self.config.jira.project_keys}")
            print(f"Token: {'*' * 10 if self.config.jira.token else 'NOT SET'}")

            reader = JiraReader(
                server_url=self.config.jira.server_url,
                email=self.config.jira.email,
                api_token=self.config.jira.token
            )

            docs = []
            for project_key in self.config.jira.project_keys:
                jql = f"project = {project_key}"
                print(f"\nQuerying Jira: {jql}")
                issues = reader.load_data(query=jql)
                print(f"Found {len(issues)} issues in {project_key}")

                for doc in issues:
                    issue_key = doc.metadata.get("key")
                    if force_refresh or not self.tracker.is_indexed("jira_issues", issue_key):
                        docs.append(doc)
                        self.tracker.mark_indexed("jira_issues", issue_key, {"project": project_key})

            print(f"\n[SUCCESS] Successfully loaded {len(docs)} new/updated issues from Jira")
            return docs

        except ImportError as e:
            print(f"\n✗ Jira Reader Import Error:")
            print(f"  Error: {e}")
            print(f"  Solution: Install llama-index-readers-jira")
            print(f"  Command: pip install llama-index-readers-jira")
            print(f"\n→ Falling back to mock data...")
            self.use_mock_jira = True
            self.mock_jira = MockJiraLoader()
            return self.load_jira_issues(force_refresh)

        except Exception as e:
            import traceback
            print(f"\n✗ Jira API Connection Failed:")
            print(f"  Error Type: {type(e).__name__}")
            print(f"  Error Message: {str(e)}")
            print(f"\n  Configuration Check:")
            print(f"    - Server URL format: Should be 'https://your-domain.atlassian.net' or 'http://localhost:8080'")
            print(f"    - Current URL: {self.config.jira.server_url}")
            print(f"    - Email: {self.config.jira.email}")
            print(f"    - Token: {'Set' if self.config.jira.token else 'NOT SET'}")
            print(f"\n  Common Issues:")
            print(f"    1. Invalid server URL format")
            print(f"    2. Incorrect API token or expired token")
            print(f"    3. Network connectivity issues")
            print(f"    4. Firewall blocking the connection")
            print(f"    5. Project key doesn't exist or no access")
            print(f"\n  Full Traceback:")
            traceback.print_exc()
            print(f"\n→ Falling back to mock data...")
            self.use_mock_jira = True
            self.mock_jira = MockJiraLoader()
            return self.load_jira_issues(force_refresh)

    def load_confluence_pages(self, force_refresh: bool = False) -> List[Document]:
        """Load Confluence pages incrementally"""
        if not self.config.confluence:
            print("\n[INFO] Confluence not configured, skipping...")
            return []

        try:
            from llama_index.readers.confluence import ConfluenceReader

            print(f"\n=== Connecting to Confluence ===")
            print(f"Server URL: {self.config.confluence.server_url}")
            print(f"Space Keys: {self.config.confluence.space_keys}")
            print(f"Token: {'*' * 10 if self.config.confluence.token else 'NOT SET'}")

            reader = ConfluenceReader(
                base_url=self.config.confluence.server_url,
                cloud=True,
                oauth2={"token": self.config.confluence.token}
            )

            docs = []
            for space_key in self.config.confluence.space_keys:
                print(f"\nLoading pages from space: {space_key}")
                pages = reader.load_data(space_key=space_key, include_attachments=True)
                print(f"Found {len(pages)} pages in {space_key}")

                for doc in pages:
                    page_id = doc.metadata.get("page_id")
                    if force_refresh or not self.tracker.is_indexed("confluence_pages", page_id):
                        docs.append(doc)
                        self.tracker.mark_indexed("confluence_pages", page_id, {"space": space_key})

            print(f"\n[SUCCESS] Successfully loaded {len(docs)} new/updated pages from Confluence")
            return docs

        except ImportError as e:
            print(f"\n[ERROR] Confluence Reader Import Error:")
            print(f"  Error: {e}")
            print(f"  Solution: Install llama-index-readers-confluence")
            print(f"  Command: pip install llama-index-readers-confluence")
            return []

        except Exception as e:
            import traceback
            print(f"\n[ERROR] Confluence API Connection Failed:")
            print(f"  Error Type: {type(e).__name__}")
            print(f"  Error Message: {str(e)}")
            print(f"\n  Configuration Check:")
            print(f"    - Server URL: {self.config.confluence.server_url}")
            print(f"    - Token: {'Set' if self.config.confluence.token else 'NOT SET'}")
            print(f"    - Space Keys: {self.config.confluence.space_keys}")
            print(f"\n  Common Issues:")
            print(f"    1. Invalid server URL or token")
            print(f"    2. Space key doesn't exist or no access")
            print(f"    3. Network connectivity issues")
            print(f"\n  Full Traceback:")
            traceback.print_exc()
            return []

    def load_documents(self, force_refresh: bool = False) -> List[Document]:
        """Load local documents with MinerU"""
        folder = Path(self.config.documents.folder)
        if not folder.exists():
            return []

        docs = []
        supported_exts = [".pdf", ".docx", ".doc", ".pptx", ".xlsx", ".txt", ".md"]

        for file_path in folder.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in supported_exts:
                file_id = str(file_path.relative_to(folder))

                if force_refresh or not self.tracker.is_indexed("documents", file_id):
                    try:
                        # Sync wrapper for async parse_file
                        import asyncio
                        parsed_docs = asyncio.run(self.doc_parser.parse_file(file_path))
                        docs.extend(parsed_docs)
                        self.tracker.mark_indexed("documents", file_id, {"path": str(file_path)})
                    except Exception as e:
                        print(f"Warning: Failed to parse {file_path}: {e}")

        return docs
