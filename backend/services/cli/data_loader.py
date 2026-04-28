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
            reader = JiraReader(
                server_url=self.config.jira.server_url,
                email=self.config.jira.email,
                api_token=self.config.jira.token
            )

            docs = []
            for project_key in self.config.jira.project_keys:
                jql = f"project = {project_key}"
                issues = reader.load_data(query=jql)

                for doc in issues:
                    issue_key = doc.metadata.get("key")
                    if force_refresh or not self.tracker.is_indexed("jira_issues", issue_key):
                        docs.append(doc)
                        self.tracker.mark_indexed("jira_issues", issue_key, {"project": project_key})

            return docs
        except Exception as e:
            print(f"Warning: Jira API failed, using mock data: {e}")
            self.use_mock_jira = True
            return self.load_jira_issues(force_refresh)

    def load_confluence_pages(self, force_refresh: bool = False) -> List[Document]:
        """Load Confluence pages incrementally"""
        if not self.config.confluence:
            return []

        try:
            from llama_index.readers.confluence import ConfluenceReader
            reader = ConfluenceReader(
                base_url=self.config.confluence.server_url,
                cloud=True,
                oauth2={"token": self.config.confluence.token}
            )

            docs = []
            for space_key in self.config.confluence.space_keys:
                pages = reader.load_data(space_key=space_key, include_attachments=True)

                for doc in pages:
                    page_id = doc.metadata.get("page_id")
                    if force_refresh or not self.tracker.is_indexed("confluence_pages", page_id):
                        docs.append(doc)
                        self.tracker.mark_indexed("confluence_pages", page_id, {"space": space_key})

            return docs
        except Exception as e:
            print(f"Warning: Confluence API failed: {e}")
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
