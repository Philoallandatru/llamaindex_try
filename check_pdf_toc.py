"""Check PDF content for TOC pages."""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from services.ingestion.document_parser import DocumentParser


async def check_pdf_content():
    """Check if PDF has TOC pages."""

    docs_dir = Path(__file__).parent / "documents"
    pdf_files = list(docs_dir.glob("*.pdf"))

    if not pdf_files:
        print("No PDF files found")
        return

    test_file = pdf_files[0]
    print(f"Analyzing: {test_file.name}\n")

    parser = DocumentParser(use_mineru=False, filter_toc=False)
    docs = await parser.parse_file(test_file)

    print(f"Total pages: {len(docs)}\n")

    # Check first 5 pages for TOC patterns
    for i, doc in enumerate(docs[:5], 1):
        text = doc.text[:500]  # First 500 chars
        is_toc = parser._is_toc_page(doc.text, i)

        print(f"Page {i} - TOC detected: {is_toc}")
        print(f"Preview: {text[:200]}...")
        print("-" * 60)


if __name__ == "__main__":
    asyncio.run(check_pdf_content())
