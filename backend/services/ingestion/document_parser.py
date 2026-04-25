"""Multi-format document parser with MinerU and fallback support."""

import logging
from pathlib import Path
from typing import Optional

from llama_index.core import Document

from .mineru_parser import MinerUParser

logger = logging.getLogger(__name__)


class DocumentParser:
    """Parse documents in multiple formats."""

    SUPPORTED_FORMATS = {
        ".pdf": "pdf",
        ".docx": "office",
        ".doc": "office",
        ".xlsx": "office",
        ".xls": "office",
        ".pptx": "office",
        ".ppt": "office",
    }

    def __init__(self, use_mineru: bool = True):
        """Initialize document parser.

        Args:
            use_mineru: Whether to use MinerU for parsing (default: True)
        """
        self.use_mineru = use_mineru
        self.mineru_parser: Optional[MinerUParser] = None

        if use_mineru:
            self.mineru_parser = MinerUParser()
            if not self.mineru_parser.is_available():
                logger.warning("MinerU not available, will use fallback parsers")
                self.mineru_parser = None

    async def parse_file(self, file_path: Path) -> list[Document]:
        """Parse a file and return LlamaIndex Documents.

        Args:
            file_path: Path to file

        Returns:
            List of LlamaIndex Document objects

        Raises:
            ValueError: If file format is not supported
            RuntimeError: If parsing fails
        """
        suffix = file_path.suffix.lower()

        if suffix not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported file format: {suffix}")

        format_type = self.SUPPORTED_FORMATS[suffix]

        if format_type == "pdf":
            return await self.parse_pdf(file_path)
        elif format_type == "office":
            return await self.parse_office(file_path)
        else:
            raise ValueError(f"Unknown format type: {format_type}")

    async def parse_pdf(self, file_path: Path) -> list[Document]:
        """Parse PDF file.

        Args:
            file_path: Path to PDF

        Returns:
            List of Document objects
        """
        # Try MinerU first
        if self.mineru_parser:
            try:
                parsed = self.mineru_parser.parse_pdf(file_path)
                return self._convert_to_documents(parsed, file_path, "pdf")
            except Exception as e:
                logger.warning(f"MinerU failed, falling back to pypdf: {e}")

        # Fallback to pypdf
        return await self._parse_pdf_fallback(file_path)

    async def _parse_pdf_fallback(self, file_path: Path) -> list[Document]:
        """Parse PDF using pypdf as fallback.

        Args:
            file_path: Path to PDF

        Returns:
            List of Document objects
        """
        try:
            from pypdf import PdfReader

            reader = PdfReader(str(file_path))
            documents = []

            for page_num, page in enumerate(reader.pages, start=1):
                text = page.extract_text()
                if text.strip():
                    doc = Document(
                        text=text,
                        metadata={
                            "source": str(file_path),
                            "source_type": "pdf",
                            "page": page_num,
                            "total_pages": len(reader.pages),
                            "parser": "pypdf",
                        },
                    )
                    documents.append(doc)

            return documents

        except Exception as e:
            logger.error(f"pypdf parsing failed: {e}")
            raise RuntimeError(f"Failed to parse PDF with fallback: {e}")

    async def parse_office(self, file_path: Path) -> list[Document]:
        """Parse Office document.

        Args:
            file_path: Path to Office file

        Returns:
            List of Document objects
        """
        # Try MinerU
        if self.mineru_parser:
            try:
                parsed = self.mineru_parser.parse_office(file_path)
                return self._convert_to_documents(parsed, file_path, "office")
            except Exception as e:
                logger.error(f"MinerU Office parsing failed: {e}")
                raise RuntimeError(f"Failed to parse Office document: {e}")
        else:
            raise RuntimeError("MinerU not available for Office document parsing")

    def _convert_to_documents(
        self,
        parsed_data: dict[str, any],
        file_path: Path,
        source_type: str,
    ) -> list[Document]:
        """Convert parsed data to LlamaIndex Documents.

        Args:
            parsed_data: Parsed data from MinerU
            file_path: Original file path
            source_type: Type of source (pdf, office)

        Returns:
            List of Document objects
        """
        documents = []

        # Main text document
        if parsed_data.get("text"):
            doc = Document(
                text=parsed_data["text"],
                metadata={
                    "source": str(file_path),
                    "source_type": source_type,
                    "parser": "mineru",
                    "has_tables": len(parsed_data.get("tables", [])) > 0,
                    "has_images": len(parsed_data.get("images", [])) > 0,
                    **parsed_data.get("metadata", {}),
                },
            )
            documents.append(doc)

        # Table documents (separate for better retrieval)
        for idx, table in enumerate(parsed_data.get("tables", [])):
            table_doc = Document(
                text=f"Table {idx + 1}:\n{table.get('content', '')}",
                metadata={
                    "source": str(file_path),
                    "source_type": f"{source_type}_table",
                    "table_index": idx,
                    "page": table.get("page", 0),
                    "parser": "mineru",
                },
            )
            documents.append(table_doc)

        return documents

    @classmethod
    def is_supported(cls, file_path: Path) -> bool:
        """Check if file format is supported.

        Args:
            file_path: Path to file

        Returns:
            True if format is supported
        """
        return file_path.suffix.lower() in cls.SUPPORTED_FORMATS
