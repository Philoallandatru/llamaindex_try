"""File data source implementation."""

import os
from pathlib import Path
from typing import List, Tuple

from llama_index.core import Document

from backend.services.datasource.base_datasource import BaseDataSource
from backend.services.ingestion.document_parser import DocumentParser


class FileDataSource(BaseDataSource):
    """File-based data source using MinerU for parsing."""

    def __init__(self, file_paths: List[str]):
        """Initialize file data source.

        Args:
            file_paths: List of absolute file paths
        """
        self.file_paths = file_paths
        self.parser = DocumentParser()

    async def validate_config(self) -> Tuple[bool, str]:
        """Validate that all files exist and are readable."""
        if not self.file_paths:
            return False, "No files specified"

        missing_files = []
        for file_path in self.file_paths:
            if not os.path.exists(file_path):
                missing_files.append(file_path)

        if missing_files:
            return False, f"Files not found: {', '.join(missing_files)}"

        return True, ""

    async def fetch_documents(self) -> List[Document]:
        """Fetch and parse documents from files."""
        documents = []

        for file_path in self.file_paths:
            try:
                # Use DocumentParser to parse the file
                file_docs = await self.parser.parse_file(Path(file_path))
                documents.extend(file_docs)
            except Exception as e:
                # Log error but continue with other files
                print(f"Error processing {file_path}: {str(e)}")
                continue

        return documents

    async def get_document_count(self) -> int:
        """Get the number of files."""
        return len(self.file_paths)
