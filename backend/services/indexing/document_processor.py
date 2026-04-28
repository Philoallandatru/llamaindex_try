"""Document processor using MinerU."""

import os
from pathlib import Path
from typing import List

from llama_index.core import Document


class DocumentProcessor:
    """Process documents using MinerU for parsing."""

    SUPPORTED_EXTENSIONS = {
        '.pdf', '.doc', '.docx', '.ppt', '.pptx',
        '.xls', '.xlsx', '.md', '.txt', '.json'
    }

    def __init__(self):
        """Initialize document processor."""
        self.upload_dir = Path("data/uploads")
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def process_file(self, file_path: str) -> List[Document]:
        """Process a single file and return LlamaIndex documents.

        Args:
            file_path: Path to the file

        Returns:
            List of Document objects
        """
        file_path = Path(file_path)
        extension = file_path.suffix.lower()

        if extension not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {extension}")

        # For now, use simple text extraction
        # TODO: Integrate MinerU for advanced parsing
        if extension == '.txt':
            return await self._process_text(file_path)
        elif extension == '.md':
            return await self._process_markdown(file_path)
        elif extension == '.json':
            return await self._process_json(file_path)
        elif extension == '.pdf':
            return await self._process_pdf(file_path)
        else:
            # For office files, we'll need MinerU integration
            return await self._process_with_mineru(file_path)

    async def _process_text(self, file_path: Path) -> List[Document]:
        """Process plain text file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return [Document(
            text=content,
            metadata={
                'file_path': str(file_path),
                'file_name': file_path.name,
                'file_type': 'text'
            }
        )]

    async def _process_markdown(self, file_path: Path) -> List[Document]:
        """Process markdown file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return [Document(
            text=content,
            metadata={
                'file_path': str(file_path),
                'file_name': file_path.name,
                'file_type': 'markdown'
            }
        )]

    async def _process_json(self, file_path: Path) -> List[Document]:
        """Process JSON file."""
        import json

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Convert JSON to text representation
        content = json.dumps(data, indent=2, ensure_ascii=False)

        return [Document(
            text=content,
            metadata={
                'file_path': str(file_path),
                'file_name': file_path.name,
                'file_type': 'json'
            }
        )]

    async def _process_pdf(self, file_path: Path) -> List[Document]:
        """Process PDF file using PyPDF2."""
        try:
            import PyPDF2

            documents = []
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page_num, page in enumerate(pdf_reader.pages):
                    text = page.extract_text()
                    if text.strip():
                        documents.append(Document(
                            text=text,
                            metadata={
                                'file_path': str(file_path),
                                'file_name': file_path.name,
                                'file_type': 'pdf',
                                'page_number': page_num + 1
                            }
                        ))

            return documents
        except ImportError:
            raise ImportError("PyPDF2 is required for PDF processing. Install with: pip install PyPDF2")

    async def _process_with_mineru(self, file_path: Path) -> List[Document]:
        """Process office files with MinerU.

        TODO: Implement MinerU integration for:
        - .doc, .docx
        - .ppt, .pptx
        - .xls, .xlsx
        """
        raise NotImplementedError(
            f"MinerU integration for {file_path.suffix} files is not yet implemented. "
            "This will be added in a future update."
        )

    def is_supported(self, file_path: str) -> bool:
        """Check if file type is supported."""
        extension = Path(file_path).suffix.lower()
        return extension in self.SUPPORTED_EXTENSIONS
