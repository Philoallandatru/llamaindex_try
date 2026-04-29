"""Test complete TOC filtering workflow."""

import sys
import io
import asyncio
from pathlib import Path

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from services.ingestion.document_parser import DocumentParser


async def test_filtering():
    """Test TOC filtering on NVMe spec."""

    pdf_path = Path(__file__).parent / "documents" / "NVM-Express-Base-Specification-Revision-2.1-2024.08.05-Ratified.pdf"

    print("=== Test 1: With TOC filtering (filter_toc=True) ===")
    parser_filtered = DocumentParser(use_mineru=False, filter_toc=True)
    docs_filtered = await parser_filtered.parse_file(pdf_path)

    print(f"Documents created: {len(docs_filtered)}")
    print(f"First doc page: {docs_filtered[0].metadata.get('page', 'N/A')}")
    print(f"First doc preview: {docs_filtered[0].text[:100]}")

    print("\n=== Test 2: Without TOC filtering (filter_toc=False) ===")
    parser_unfiltered = DocumentParser(use_mineru=False, filter_toc=False)
    docs_unfiltered = await parser_unfiltered.parse_file(pdf_path)

    print(f"Documents created: {len(docs_unfiltered)}")
    print(f"First doc page: {docs_unfiltered[0].metadata.get('page', 'N/A')}")
    print(f"First doc preview: {docs_unfiltered[0].text[:100]}")

    print("\n=== Comparison ===")
    filtered_count = len(docs_unfiltered) - len(docs_filtered)
    print(f"Pages filtered: {filtered_count}")
    print(f"Percentage filtered: {filtered_count / len(docs_unfiltered) * 100:.1f}%")

    if filtered_count > 0:
        print("\n[SUCCESS] TOC filtering is working!")
    else:
        print("\n[ERROR] TOC filtering did not remove any pages")


if __name__ == "__main__":
    asyncio.run(test_filtering())
