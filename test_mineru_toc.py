"""Test MinerU TOC filtering."""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from services.ingestion.document_parser import DocumentParser


async def test_mineru_toc_filtering():
    """Test that MinerU path also filters TOC pages."""

    # Find a PDF file in documents/
    docs_dir = Path(__file__).parent / "documents"
    pdf_files = list(docs_dir.glob("*.pdf"))

    if not pdf_files:
        print("No PDF files found in documents/ directory")
        return

    test_file = pdf_files[0]
    print(f"Testing with: {test_file.name}\n")

    # Test with TOC filtering enabled (default)
    print("=" * 60)
    print("Test 1: With TOC filtering (filter_toc=True)")
    print("=" * 60)

    parser_with_filter = DocumentParser(use_mineru=True, filter_toc=True)
    docs_filtered = await parser_with_filter.parse_file(test_file)

    print(f"Documents created: {len(docs_filtered)}")
    if docs_filtered:
        print(f"First doc length: {len(docs_filtered[0].text)} chars")
        print(f"Parser used: {docs_filtered[0].metadata.get('parser', 'unknown')}")

    # Test with TOC filtering disabled
    print("\n" + "=" * 60)
    print("Test 2: Without TOC filtering (filter_toc=False)")
    print("=" * 60)

    parser_no_filter = DocumentParser(use_mineru=True, filter_toc=False)
    docs_unfiltered = await parser_no_filter.parse_file(test_file)

    print(f"Documents created: {len(docs_unfiltered)}")
    if docs_unfiltered:
        print(f"First doc length: {len(docs_unfiltered[0].text)} chars")
        print(f"Parser used: {docs_unfiltered[0].metadata.get('parser', 'unknown')}")

    # Compare
    print("\n" + "=" * 60)
    print("Comparison")
    print("=" * 60)

    if docs_filtered and docs_unfiltered:
        filtered_len = len(docs_filtered[0].text)
        unfiltered_len = len(docs_unfiltered[0].text)
        diff = unfiltered_len - filtered_len

        print(f"Text length difference: {diff} chars ({diff/unfiltered_len*100:.1f}%)")

        if diff > 0:
            print("✓ TOC filtering is working!")
        else:
            print("✗ TOC filtering may not be working")


if __name__ == "__main__":
    asyncio.run(test_mineru_toc_filtering())
