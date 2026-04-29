"""Check page 2 content."""

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
reader = PdfReader(pdf_path)

# Get page 2 (index 1)
page = reader.pages[1]
text = page.extract_text()

print("=== Page 2 Full Content ===")
print(text)
print("\n=== Analysis ===")

parser = DocumentParser(filter_toc=True)
is_toc = parser._is_toc_page(text, 2)
print(f"TOC detected: {is_toc}")

# Check patterns
lines = text.split('\n')
print(f"Total lines: {len(lines)}")

# Check for dotted lines
dotted = sum(1 for line in lines if '...' in line or '…' in line)
print(f"Dotted lines: {dotted}")

# Check for numbered sections
import re
numbered = sum(1 for line in lines if re.match(r'^\s*\d+\.', line))
print(f"Numbered sections: {numbered}")

# Check for page numbers
page_nums = sum(1 for line in lines if re.search(r'\b\d{1,3}\b\s*$', line))
print(f"Lines ending with numbers: {page_nums}")
