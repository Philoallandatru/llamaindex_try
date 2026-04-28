"""
Test DocumentParser with pypdf fallback
"""
import asyncio
from pathlib import Path
from backend.services.ingestion.document_parser import DocumentParser

async def test_document_parser():
    """Test DocumentParser with automatic fallback to pypdf"""

    # Use small test PDF
    test_pdf = Path("documents/fms-08-09-2023-ssds-201-1-ozturk-final.pdf")
    if not test_pdf.exists():
        print(f"[ERROR] Test PDF not found: {test_pdf}")
        return False

    print("=" * 60)
    print("DocumentParser Test (with pypdf fallback)")
    print("=" * 60)
    print(f"[FILE] Test file: {test_pdf}")
    print()

    try:
        # Initialize parser (will auto-detect MinerU availability)
        print("[INIT] Initializing DocumentParser...")
        parser = DocumentParser(use_mineru=True)

        # Parse PDF (will fallback to pypdf if MinerU fails)
        print("[START] Parsing PDF...")
        documents = await parser.parse_pdf(test_pdf)

        print(f"[SUCCESS] Parsed {len(documents)} pages")

        if documents:
            print(f"\n[PREVIEW] First page (200 chars):")
            # Use ASCII-safe output for Windows console
            preview = documents[0].text[:200].encode('ascii', 'ignore').decode('ascii')
            print(f"   {preview}...")
            print(f"\n[METADATA]")
            for key, value in documents[0].metadata.items():
                print(f"   {key}: {value}")

        return True

    except Exception as e:
        print(f"[ERROR] Parsing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print()
    success = asyncio.run(test_document_parser())
    print()
    print("=" * 60)
    if success:
        print("[PASS] DocumentParser test passed")
    else:
        print("[FAIL] DocumentParser test failed")
    print("=" * 60)
