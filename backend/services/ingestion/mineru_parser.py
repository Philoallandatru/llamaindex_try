"""MinerU parser for PDF and Office documents."""

import json
import logging
import subprocess
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class MinerUParser:
    """Wrapper for MinerU document parsing."""

    def __init__(self, output_dir: Optional[Path] = None):
        """Initialize MinerU parser.

        Args:
            output_dir: Directory for MinerU output (default: temp directory)
        """
        self.output_dir = output_dir or Path("./data/mineru_output")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def parse_pdf(self, file_path: Path) -> dict[str, any]:
        """Parse PDF using MinerU.

        Args:
            file_path: Path to PDF file

        Returns:
            Dictionary with parsed content:
            {
                "text": str,
                "markdown": str,
                "tables": list[dict],
                "images": list[dict],
                "metadata": dict
            }

        Raises:
            RuntimeError: If MinerU parsing fails
        """
        try:
            # Try to import magic_pdf (MinerU)
            try:
                from magic_pdf.pipe.UNIPipe import UNIPipe
                from magic_pdf.rw.DiskReaderWriter import DiskReaderWriter

                return self._parse_with_magic_pdf(file_path)
            except ImportError:
                logger.warning("magic-pdf not installed, trying CLI method")
                return self._parse_with_cli(file_path)

        except Exception as e:
            logger.error(f"MinerU parsing failed for {file_path}: {e}")
            raise RuntimeError(f"Failed to parse PDF: {e}")

    def _parse_with_magic_pdf(self, file_path: Path) -> dict[str, any]:
        """Parse using magic_pdf Python API."""
        from magic_pdf.pipe.UNIPipe import UNIPipe
        from magic_pdf.rw.DiskReaderWriter import DiskReaderWriter

        # Read PDF bytes
        pdf_bytes = file_path.read_bytes()

        # Create output directory for this file
        output_path = self.output_dir / file_path.stem
        output_path.mkdir(parents=True, exist_ok=True)

        # Initialize reader/writer
        reader_writer = DiskReaderWriter(str(output_path))

        # Parse PDF
        pipe = UNIPipe(pdf_bytes, {"_pdf_type": ""}, reader_writer)
        pipe.pipe_classify()
        pipe.pipe_parse()

        # Get markdown output
        markdown_path = output_path / f"{file_path.stem}.md"
        markdown_text = ""
        if markdown_path.exists():
            markdown_text = markdown_path.read_text(encoding="utf-8")

        # Get middle JSON (structured data)
        middle_json_path = output_path / f"{file_path.stem}_middle.json"
        metadata = {}
        tables = []
        images = []

        if middle_json_path.exists():
            with open(middle_json_path, "r", encoding="utf-8") as f:
                middle_data = json.load(f)
                metadata = middle_data.get("metadata", {})

                # Extract tables
                for page in middle_data.get("pdf_info", []):
                    for table in page.get("tables", []):
                        tables.append({
                            "page": page.get("page_no", 0),
                            "content": table.get("text", ""),
                            "bbox": table.get("bbox", []),
                        })

                # Extract images
                for page in middle_data.get("pdf_info", []):
                    for img in page.get("images", []):
                        images.append({
                            "page": page.get("page_no", 0),
                            "path": img.get("path", ""),
                            "bbox": img.get("bbox", []),
                        })

        return {
            "text": markdown_text,
            "markdown": markdown_text,
            "tables": tables,
            "images": images,
            "metadata": metadata,
        }

    def _parse_with_cli(self, file_path: Path) -> dict[str, any]:
        """Parse using MinerU CLI (fallback method)."""
        output_path = self.output_dir / file_path.stem
        output_path.mkdir(parents=True, exist_ok=True)

        # Run MinerU CLI
        cmd = [
            "magic-pdf",
            "-p", str(file_path),
            "-o", str(output_path),
            "-m", "auto",
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutes timeout
        )

        if result.returncode != 0:
            raise RuntimeError(f"MinerU CLI failed: {result.stderr}")

        # Read output
        markdown_path = output_path / f"{file_path.stem}.md"
        markdown_text = ""
        if markdown_path.exists():
            markdown_text = markdown_path.read_text(encoding="utf-8")

        return {
            "text": markdown_text,
            "markdown": markdown_text,
            "tables": [],
            "images": [],
            "metadata": {},
        }

    def parse_office(self, file_path: Path) -> dict[str, any]:
        """Parse Office document (DOCX, XLSX, PPTX) using MinerU.

        Args:
            file_path: Path to Office file

        Returns:
            Dictionary with parsed content

        Raises:
            RuntimeError: If parsing fails
        """
        # MinerU supports Office formats through the same pipeline
        try:
            return self.parse_pdf(file_path)  # Same API for Office files
        except Exception as e:
            logger.error(f"Office parsing failed for {file_path}: {e}")
            raise RuntimeError(f"Failed to parse Office document: {e}")

    def is_available(self) -> bool:
        """Check if MinerU is available.

        Returns:
            True if MinerU can be used
        """
        try:
            import magic_pdf
            return True
        except ImportError:
            # Try CLI
            try:
                result = subprocess.run(
                    ["magic-pdf", "--version"],
                    capture_output=True,
                    timeout=5,
                )
                return result.returncode == 0
            except (subprocess.SubprocessError, FileNotFoundError):
                return False
