"""Simple TOC detection test."""

import sys
import io
from pathlib import Path

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from pypdf import PdfReader
from services.ingestion.document_parser import DocumentParser

# Find PDF file
docs_dir = Path(__file__).parent / "documents"
pdf_files = list(docs_dir.glob("*.pdf"))

if not pdf_files:
    print("No PDF files found")
    sys.exit(1)

pdf_path = pdf_files[0]
print(f"Testing: {pdf_path.name}\n")

# Read PDF
reader = PdfReader(pdf_path)
print(f"Total pages: {len(reader.pages)}\n")

# Create parser
parser = DocumentParser(filter_toc=True)

# Check first 5 pages
for i in range(min(5, len(reader.pages))):
    page = reader.pages[i]
    text = page.extract_text()
    is_toc = parser._is_toc_page(text, i+1)

    print(f"Page {i+1}:")
    print(f"  TOC detected: {is_toc}")
    print(f"  Text length: {len(text)} chars")

    # Show first line
    first_line = text.split('\n')[0] if text else ""
    print(f"  First line: {first_line[:80]}")
    print()
