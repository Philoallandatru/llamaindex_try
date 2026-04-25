"""Tests for document ingestion services."""

import pytest
from pathlib import Path

from backend.services.ingestion.document_parser import DocumentParser
from backend.services.ingestion.normalizer import DocumentNormalizer


class TestDocumentParser:
    """Test document parser."""

    def test_is_supported(self):
        """Test file format detection."""
        assert DocumentParser.is_supported(Path("test.pdf"))
        assert DocumentParser.is_supported(Path("test.docx"))
        assert DocumentParser.is_supported(Path("test.xlsx"))
        assert DocumentParser.is_supported(Path("test.pptx"))
        assert not DocumentParser.is_supported(Path("test.txt"))
        assert not DocumentParser.is_supported(Path("test.jpg"))


class TestDocumentNormalizer:
    """Test document normalizer."""

    def test_normalize_jira_issue(self):
        """Test Jira issue normalization."""
        issue_data = {
            "key": "TEST-123",
            "self": "https://jira.example.com/rest/api/2/issue/12345",
            "fields": {
                "summary": "Test issue",
                "description": "Test description",
                "issuetype": {"name": "Bug"},
                "status": {"name": "Open"},
                "priority": {"name": "High"},
                "created": "2024-01-01T00:00:00.000+0000",
                "updated": "2024-01-02T00:00:00.000+0000",
                "assignee": {"displayName": "John Doe"},
                "reporter": {"displayName": "Jane Smith"},
            },
        }

        doc = DocumentNormalizer.normalize_jira_issue(issue_data)

        assert doc.text is not None
        assert "TEST-123" in doc.text
        assert "Test issue" in doc.text
        assert doc.metadata["source_type"] == "jira"
        assert doc.metadata["source_id"] == "TEST-123"
        assert doc.metadata["status"] == "Open"

    def test_normalize_confluence_page(self):
        """Test Confluence page normalization."""
        page_data = {
            "id": "12345",
            "title": "Test Page",
            "body": {
                "storage": {
                    "value": "<p>Test content</p>",
                },
            },
            "space": {
                "key": "TEST",
                "name": "Test Space",
            },
            "_links": {
                "self": "https://confluence.example.com/rest/api/content/12345",
                "webui": "/display/TEST/Test+Page",
            },
            "history": {
                "createdDate": "2024-01-01T00:00:00.000Z",
                "createdBy": {"displayName": "John Doe"},
            },
            "version": {
                "when": "2024-01-02T00:00:00.000Z",
            },
        }

        doc = DocumentNormalizer.normalize_confluence_page(page_data)

        assert doc.text is not None
        assert "Test Page" in doc.text
        assert "Test content" in doc.text
        assert doc.metadata["source_type"] == "confluence"
        assert doc.metadata["source_id"] == "12345"
        assert doc.metadata["space_key"] == "TEST"

    def test_add_timestamp(self):
        """Test timestamp addition."""
        from llama_index.core import Document

        doc = Document(text="Test", metadata={"source": "test"})
        doc_with_ts = DocumentNormalizer.add_timestamp(doc)

        assert "ingested_at" in doc_with_ts.metadata
        assert doc_with_ts.metadata["ingested_at"] is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
