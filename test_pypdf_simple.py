"""
测试pypdf解析（简化版，不依赖MinerU）
"""
from pathlib import Path
from llama_index.core import Document
from pypdf import PdfReader

def test_pypdf_simple():
    """测试pypdf直接解析PDF"""

    # 查找测试PDF
    test_pdf = Path("test_upload.pdf")
    if not test_pdf.exists():
        docs_dir = Path("documents")
        if docs_dir.exists():
            pdf_files = list(docs_dir.glob("*.pdf"))
            if pdf_files:
                test_pdf = pdf_files[0]
            else:
                print("[ERROR] No PDF files found")
                return False
        else:
            print("[ERROR] No test PDF found")
            return False

    print("=" * 60)
    print("pypdf Simple Test")
    print("=" * 60)
    print(f"[FILE] Test file: {test_pdf}")
    print()

    try:
        print("[START] Parsing with pypdf...")
        reader = PdfReader(str(test_pdf))

        print(f"[INFO] Total pages: {len(reader.pages)}")

        documents = []
        for page_num, page in enumerate(reader.pages, start=1):
            text = page.extract_text()
            if text.strip():
                doc = Document(
                    text=text,
                    metadata={
                        "source": str(test_pdf),
                        "source_type": "pdf",
                        "page": page_num,
                        "total_pages": len(reader.pages),
                        "parser": "pypdf",
                    },
                )
                documents.append(doc)

        print(f"[SUCCESS] Extracted {len(documents)} pages")

        if documents:
            print(f"\n[PREVIEW] First page (200 chars):")
            print(f"   {documents[0].text[:200]}...")
            print(f"\n[METADATA] {documents[0].metadata}")

        return True

    except Exception as e:
        print(f"[ERROR] Parsing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_pypdf_simple()
    print()
    print("=" * 60)
    if success:
        print("[PASS] pypdf test passed")
    else:
        print("[FAIL] pypdf test failed")
    print("=" * 60)
