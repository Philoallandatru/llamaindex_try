"""Test extended Jira issue type support."""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from services.cli.jira_profiles import (
    ISSUE_TYPE_ROUTING,
    ANALYSIS_PROFILES,
    route_issue_type,
    build_analysis_prompt
)


def test_issue_type_routing():
    """Test that all issue types are properly routed."""

    print("Testing Issue Type Routing\n" + "=" * 60)

    # Test all defined issue types
    test_cases = [
        # Defect types
        ("Bug", "rca"),
        ("FW Bug", "rca"),
        ("HW Bug", "rca"),
        ("Test Bug", "rca"),
        ("Defect", "rca"),

        # Requirement types
        ("DAS", "requirement_trace"),
        ("PRD", "requirement_trace"),
        ("Feature", "requirement_trace"),
        ("User Story", "requirement_trace"),

        # Change types
        ("Requirement Change", "change_impact"),
        ("Change Request", "change_impact"),
        ("CR", "change_impact"),
        ("ECO", "change_impact"),

        # Delivery types
        ("Epic", "delivery_summary"),
        ("Task", "delivery_summary"),
        ("Sub-task", "delivery_summary"),

        # Release types
        ("Release", "release_summary"),
        ("Version", "release_summary"),

        # Improvement types
        ("Improvement", "improvement_analysis"),
        ("Enhancement", "improvement_analysis"),
        ("Optimization", "improvement_analysis"),

        # Tech debt types
        ("Tech Debt", "tech_debt_analysis"),
        ("Technical Debt", "tech_debt_analysis"),
        ("Refactoring", "tech_debt_analysis"),

        # Test types
        ("Test Case", "test_analysis"),
        ("Test", "test_analysis"),

        # Unknown type (should use default)
        ("Unknown Type", "rca"),
    ]

    passed = 0
    failed = 0

    for issue_type, expected_route in test_cases:
        route = route_issue_type(issue_type)
        status = "PASS" if route == expected_route else "FAIL"

        if route == expected_route:
            passed += 1
        else:
            failed += 1

        print(f"[{status}] {issue_type:25s} -> {route:25s} (expected: {expected_route})")

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")

    return failed == 0


def test_profile_availability():
    """Test that profiles exist for all routes."""

    print("\n\nTesting Profile Availability\n" + "=" * 60)

    routes = [
        "rca",
        "requirement_trace",
        "change_impact",
        "delivery_summary",
        "release_summary",
        "improvement_analysis",
        "tech_debt_analysis",
        "test_analysis"
    ]

    passed = 0
    failed = 0

    for route in routes:
        if route in ANALYSIS_PROFILES:
            profile = ANALYSIS_PROFILES[route]
            if "label" in profile and "assistant_intro" in profile and "task_instruction" in profile:
                print(f"[PASS] {route:25s} - Profile complete")
                passed += 1
            else:
                print(f"[FAIL] {route:25s} - Profile missing required fields")
                failed += 1
        else:
            print(f"[FAIL] {route:25s} - Profile not found")
            failed += 1

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")

    return failed == 0


def test_profile_content():
    """Test that profiles contain Chinese content and proper structure."""

    print("\n\nTesting Profile Content\n" + "=" * 60)

    test_routes = ["rca", "requirement_trace", "improvement_analysis", "tech_debt_analysis"]

    passed = 0
    failed = 0

    for route in test_routes:
        profile = ANALYSIS_PROFILES[route]

        # Check for Chinese characters
        has_chinese = any('\u4e00' <= c <= '\u9fff' for c in profile["task_instruction"])

        # Check for required keywords
        required_keywords = ["分析要求", "建议"]
        has_keywords = all(keyword in profile["task_instruction"] for keyword in required_keywords)

        if has_chinese and has_keywords:
            print(f"[PASS] {route:25s} - Contains Chinese and required keywords")
            passed += 1
        else:
            print(f"[FAIL] {route:25s} - Missing Chinese: {not has_chinese}, Missing keywords: {not has_keywords}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")

    return failed == 0


def test_prompt_building():
    """Test that prompts can be built successfully."""

    print("\n\nTesting Prompt Building\n" + "=" * 60)

    test_cases = [
        ("Bug", "rca"),
        ("Improvement", "improvement_analysis"),
        ("Tech Debt", "tech_debt_analysis"),
    ]

    passed = 0
    failed = 0

    for issue_type, expected_route in test_cases:
        try:
            prompt = build_analysis_prompt(
                issue_type=issue_type,
                issue_content="Test issue content",
                similar_issues=[],
                relevant_docs=[],
                mode="strict"
            )

            if prompt and len(prompt) > 100:
                print(f"[PASS] {issue_type:25s} - Prompt built successfully ({len(prompt)} chars)")
                passed += 1
            else:
                print(f"[FAIL] {issue_type:25s} - Prompt too short")
                failed += 1
        except Exception as e:
            print(f"[FAIL] {issue_type:25s} - Error: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")

    return failed == 0


if __name__ == "__main__":
    success1 = test_issue_type_routing()
    success2 = test_profile_availability()
    success3 = test_profile_content()
    success4 = test_prompt_building()

    print("\n\n" + "=" * 60)
    print("OVERALL RESULTS")
    print("=" * 60)

    if success1 and success2 and success3 and success4:
        print("All tests passed!")
        sys.exit(0)
    else:
        print("Some tests failed!")
        sys.exit(1)
