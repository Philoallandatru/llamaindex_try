"""Test TOC filtering with NVMe Spec."""

import sys
import io
from pathlib import Path

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from pypdf import PdfReader
from services.ingestion.document_parser import DocumentParser

# Use NVMe spec
pdf_path = Path(__file__).parent / "documents" / "NVM-Express-Base-Specification-Revision-2.1-2024.08.05-Ratified.pdf"

if not pdf_path.exists():
    print(f"File not found: {pdf_path}")
    sys.exit(1)

print(f"Testing: {pdf_path.name}")
reader = PdfReader(pdf_path)
print(f"Total pages: {len(reader.pages)}")

parser = DocumentParser(filter_toc=True)

# Check first 20 pages for TOC
print("\n=== Checking first 20 pages for TOC ===")
for i in range(min(20, len(reader.pages))):
    page = reader.pages[i]
    text = page.extract_text()

    # Get first line as title
    lines = text.split('\n')
    title = lines[0][:60] if lines else ""

    is_toc = parser._is_toc_page(text, i + 1)

    if is_toc or 'table of contents' in text.lower() or 'contents' in title.lower():
        print(f"\nPage {i+1}: {title}")
        print(f"  TOC detected: {is_toc}")
        if i < 15:  # Show content for first few pages
            print(f"  First 500 chars:\n{text[:500]}")
