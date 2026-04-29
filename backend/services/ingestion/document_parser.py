"""Multi-format document parser with MinerU and fallback support."""

import logging
import re
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
        ".txt": "text",
        ".md": "text",
        ".json": "text",
    }

    def __init__(self, use_mineru: bool = True, filter_toc: bool = True):
        """Initialize document parser.

        Args:
            use_mineru: Whether to use MinerU for parsing (default: True)
            filter_toc: Whether to filter out table of contents pages (default: True)
        """
        self.use_mineru = use_mineru
        self.filter_toc = filter_toc
        self.mineru_parser: Optional[MinerUParser] = None

        if use_mineru:
            self.mineru_parser = MinerUParser()
            if not self.mineru_parser.is_available():
                logger.warning("MinerU not available, will use fallback parsers")
                self.mineru_parser = None

    def _is_toc_page(self, text: str, page_num: int = 0) -> bool:
        """Detect if a page is a table of contents page.

        Args:
            text: Page text content
            page_num: Page number (1-indexed, optional)

        Returns:
            True if page appears to be a TOC page
        """
        if not text or len(text.strip()) < 50:
            return False

        text_lower = text.lower()

        # TOC keywords in multiple languages
        toc_keywords = [
            "table of contents",
            "contents",
            "目录",
            "目　录",
            "table des matières",
            "inhaltsverzeichnis",
        ]

        # Check for TOC keywords at the beginning
        first_100_chars = text_lower[:100]
        has_toc_keyword = any(keyword in first_100_chars for keyword in toc_keywords)

        # Pattern 1: Multiple lines with page numbers at the end
        # Example: "Chapter 1 .................. 5"
        page_number_pattern = r'\.{3,}\s*\d+\s*$'
        dotted_lines = len(re.findall(page_number_pattern, text, re.MULTILINE))

        # Pattern 2: Lines with chapter/section numbers followed by page numbers
        # Example: "1.1 Introduction .......... 10"
        section_pattern = r'^\s*\d+\.[\d\.]*\s+.+\s+\d+\s*$'
        section_lines = len(re.findall(section_pattern, text, re.MULTILINE))

        # Pattern 3: High ratio of numbers (page references)
        numbers = re.findall(r'\b\d+\b', text)
        number_ratio = len(numbers) / max(len(text.split()), 1)

        # Decision logic
        if has_toc_keyword and (dotted_lines >= 3 or section_lines >= 3):
            return True

        if dotted_lines >= 5 or section_lines >= 5:
            return True

        # Only check page_num if provided (for pypdf path)
        if page_num > 0 and has_toc_keyword and number_ratio > 0.05 and page_num < 20:
            return True

        return False

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
        elif format_type == "text":
            return await self.parse_text(file_path)
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
            filtered_count = 0

            for page_num, page in enumerate(reader.pages, start=1):
                text = page.extract_text()
                if text.strip():
                    # Filter TOC pages if enabled
                    if self.filter_toc and self._is_toc_page(text, page_num):
                        logger.info(f"Filtered TOC page {page_num} from {file_path.name}")
                        filtered_count += 1
                        continue

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

            if filtered_count > 0:
                logger.info(f"Filtered {filtered_count} TOC pages from {file_path.name}")

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

    async def parse_text(self, file_path: Path) -> list[Document]:
        """Parse plain text file.

        Args:
            file_path: Path to text file

        Returns:
            List of Document objects
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()

            if not text.strip():
                logger.warning(f"Empty text file: {file_path}")
                return []

            doc = Document(
                text=text,
                metadata={
                    "source": str(file_path),
                    "source_type": "text",
                    "file_name": file_path.name,
                    "parser": "text",
                },
            )
            return [doc]

        except Exception as e:
            logger.error(f"Text parsing failed: {e}")
            raise RuntimeError(f"Failed to parse text file: {e}")

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
            text = parsed_data["text"]

            # Apply TOC filtering if enabled and source is PDF
            if self.filter_toc and source_type == "pdf":
                # Split by page breaks (MinerU uses form feed character)
                pages = text.split('\f')
                filtered_pages = []

                for page_text in pages:
                    if page_text.strip() and not self._is_toc_page(page_text):
                        filtered_pages.append(page_text)

                text = '\f'.join(filtered_pages)

                if len(filtered_pages) < len(pages):
                    print(f"[INFO] Filtered {len(pages) - len(filtered_pages)} TOC pages from {file_path.name}")

            doc = Document(
                text=text,
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
