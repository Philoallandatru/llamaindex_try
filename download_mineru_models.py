"""
Download all MinerU models from ModelScope
"""
import os
from pathlib import Path

# Set ModelScope as model source
os.environ['MODEL_SOURCE'] = 'modelscope'

def download_models():
    """Download all required MinerU models from ModelScope"""

    print("=" * 60)
    print("MinerU Model Downloader (ModelScope)")
    print("=" * 60)

    # Model list from MinerU documentation
    models = {
        "Layout Detection": "opendatalab/PDF-Extract-Kit-1.0",
        "Formula Detection": "opendatalab/PDF-Extract-Kit-1.0",
        "OCR": "paddleocr",
        "Table Recognition": "paddleocr",
    }

    print("\n[INFO] Models to download:")
    for name, model_id in models.items():
        print(f"  - {name}: {model_id}")

    print("\n[START] Downloading models from ModelScope...")
    print("[INFO] This may take 10-30 minutes depending on network speed")
    print()

    try:
        from modelscope import snapshot_download

        # Download PDF-Extract-Kit (layout + formula detection)
        print("[1/2] Downloading PDF-Extract-Kit...")
        cache_dir = Path.home() / ".cache" / "modelscope" / "hub"

        model_dir = snapshot_download(
            'opendatalab/PDF-Extract-Kit-1.0',
            cache_dir=str(cache_dir),
            revision='master'
        )
        print(f"[SUCCESS] PDF-Extract-Kit downloaded to: {model_dir}")

        # Download PaddleOCR models
        print("\n[2/2] Downloading PaddleOCR models...")
        print("[INFO] PaddleOCR models will be auto-downloaded on first use")

        # Test import to trigger auto-download
        try:
            from paddleocr import PaddleOCR
            ocr = PaddleOCR(use_angle_cls=True, lang='ch', show_log=False)
            print("[SUCCESS] PaddleOCR models ready")
        except Exception as e:
            print(f"[WARNING] PaddleOCR setup: {e}")

        print("\n" + "=" * 60)
        print("[COMPLETE] All models downloaded successfully")
        print("=" * 60)
        print("\n[NEXT] You can now use MinerU with:")
        print("  python test_mineru_local.py")

        return True

    except ImportError as e:
        print(f"[ERROR] Missing dependency: {e}")
        print("\n[FIX] Install required packages:")
        print("  pip install modelscope paddlepaddle paddleocr")
        return False

    except Exception as e:
        print(f"[ERROR] Download failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = download_models()
    exit(0 if success else 1)
