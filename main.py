#!/usr/bin/env python3
"""
Run all generated tests and produce HTML + Excel reports.

    python main.py

To generate new test cases first:
    python generate_tests.py --api_name NAME --base_url URL --endpoint PATH --demo
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))


def main() -> int:
    from test_cases.test_case_definitions import TEST_CASES

    banner = "  AI-API-Test-Generation-Framework  "
    print("\n" + "=" * len(banner))
    print(banner)
    print("=" * len(banner))

    if not TEST_CASES:
        print("\n  No test cases yet.")
        print("  Generate some first:\n")
        print("  python generate_tests.py \\")
        print('    --api_name "DummyJSON" \\')
        print('    --base_url "https://dummyjson.com" \\')
        print('    --endpoint "/products/1" \\')
        print("    --demo\n")
        return 0

    total = len(TEST_CASES)
    positive = sum(1 for tc in TEST_CASES if tc["test_type"] == "positive")
    negative = total - positive
    apis = sorted({tc["api_name"] for tc in TEST_CASES})

    print(f"\n  APIs         : {', '.join(apis)}")
    print(f"  Test cases   : {total}  ({positive} positive, {negative} negative)\n")

    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short", "-s"],
        cwd=ROOT,
    )
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
