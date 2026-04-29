"""
测试MinerU本地模型
"""
import os
from pathlib import Path
from backend.services.ingestion.mineru_parser import MinerUParser

# 设置环境变量使用ModelScope
os.environ['MODEL_SOURCE'] = 'modelscope'

def test_mineru_local():
    """测试MinerU本地模型解析PDF"""

    # 使用小的测试PDF
    test_pdf = Path("documents/fms-08-09-2023-ssds-201-1-ozturk-final.pdf")
    if not test_pdf.exists():
        print(f"❌ 未找到测试PDF文件: {test_pdf}")
        return

    print(f"[FILE] Test file: {test_pdf}")
    print(f"[MODEL] Model source: {os.environ.get('MODEL_SOURCE', 'huggingface')}")
    print()

    # 创建输出目录
    output_dir = Path("mineru_test_output")
    output_dir.mkdir(exist_ok=True)

    # 初始化MinerU解析器
    print("[INIT] Initializing MinerU parser...")
    parser = MinerUParser(output_dir=output_dir)

    # 解析PDF
    print("[START] Parsing PDF...")
    print("=" * 60)

    try:
        result = parser.parse_pdf(test_pdf)

        print("=" * 60)
        print(f"[SUCCESS] Parsing completed!")
        print(f"[RESULT] Text length: {len(result.get('text', ''))} chars")
        print(f"[RESULT] Markdown length: {len(result.get('markdown', ''))} chars")
        print(f"[RESULT] Tables: {len(result.get('tables', []))}")
        print(f"[RESULT] Images: {len(result.get('images', []))}")

        if result.get('text'):
            print(f"\n[PREVIEW] First 200 chars:")
            print(f"   {result['text'][:200]}...")

        if result.get('metadata'):
            print(f"\n[METADATA] {result['metadata']}")

        # 检查输出目录
        output_files = list(output_dir.glob("*"))
        if output_files:
            print(f"\n[OUTPUT] Output files:")
            for f in output_files[:5]:  # 只显示前5个
                print(f"   - {f.name}")

        return True

    except Exception as e:
        print("=" * 60)
        print(f"[ERROR] Parsing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("MinerU Local Model Test")
    print("=" * 60)
    print()

    success = test_mineru_local()

    print()
    print("=" * 60)
    if success:
        print("[PASS] Test passed")
    else:
        print("[FAIL] Test failed")
    print("=" * 60)
