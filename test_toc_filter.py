"""Test PDF Table of Contents filtering."""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from services.ingestion.document_parser import DocumentParser


def test_toc_detection():
    """Test TOC page detection with various examples."""

    parser = DocumentParser(use_mineru=False, filter_toc=True)

    # Test case 1: English TOC with dotted lines
    toc_text_1 = """
    Table of Contents

    Chapter 1: Introduction .................. 5
    Chapter 2: Getting Started ............... 12
    Chapter 3: Advanced Topics ............... 28
    Chapter 4: Troubleshooting ............... 45
    Chapter 5: Conclusion .................... 67
    """

    # Test case 2: Chinese TOC
    toc_text_2 = """
    目录

    第一章 概述 ............................ 1
    第二章 系统架构 ........................ 15
    第三章 功能说明 ........................ 32
    第四章 性能优化 ........................ 58
    第五章 故障排查 ........................ 89
    """

    # Test case 3: Section-style TOC
    toc_text_3 = """
    Contents

    1. Introduction                          1
    1.1 Background                           2
    1.2 Objectives                           5
    2. System Design                         10
    2.1 Architecture                         11
    2.2 Components                           18
    3. Implementation                        25
    """

    # Test case 4: Normal content (should NOT be detected as TOC)
    normal_text = """
    Chapter 1: Introduction

    This chapter provides an overview of the system architecture.
    The system consists of multiple components that work together
    to provide a comprehensive solution for data processing.

    The main components include:
    - Data ingestion layer
    - Processing engine
    - Storage backend
    - API gateway
    """

    # Test case 5: Content with numbers (should NOT be detected as TOC)
    normal_with_numbers = """
    Performance Results

    The system achieved the following performance metrics:
    - Throughput: 1000 requests per second
    - Latency: 50ms at p99
    - CPU usage: 45% average
    - Memory usage: 2GB

    These results were obtained using 10 concurrent clients
    over a period of 5 minutes.
    """

    test_cases = [
        ("English TOC with dots", toc_text_1, True, 1),
        ("Chinese TOC", toc_text_2, True, 2),
        ("Section-style TOC", toc_text_3, True, 3),
        ("Normal content", normal_text, False, 10),
        ("Normal with numbers", normal_with_numbers, False, 15),
    ]

    print("Testing TOC Detection\n" + "=" * 60)

    passed = 0
    failed = 0

    for name, text, expected_is_toc, page_num in test_cases:
        result = parser._is_toc_page(text, page_num)
        status = "PASS" if result == expected_is_toc else "FAIL"

        if result == expected_is_toc:
            passed += 1
        else:
            failed += 1

        print(f"\n[{status}] {name}")
        print(f"  Expected: {expected_is_toc}, Got: {result}")
        if result != expected_is_toc:
            print(f"  Text preview: {text[:100]}...")

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")

    return failed == 0


if __name__ == "__main__":
    success = test_toc_detection()
    sys.exit(0 if success else 1)
