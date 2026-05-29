#!/usr/bin/env python3
"""
Entry point for the AI-Assisted API Test Generation & Execution Framework.
Run this file to execute all tests and generate HTML + Excel reports.

    python main.py

Or use pytest directly for more control:

    pytest tests/ -v
    pytest tests/test_reqres.py -v
    pytest tests/ -k TC005
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))


def main() -> int:
    banner = "  AI-Assisted API Test Generation & Execution Framework  "
    print("\n" + "=" * len(banner))
    print(banner)
    print("=" * len(banner))
    print(f"\n  Running tests from: {ROOT}")
    print(f"  APIs under test  : JSONPlaceholder, PokeAPI, DummyJSON")
    print(f"  Total test cases : 14  (7 positive + 7 negative)\n")

    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short", "-s"],
        cwd=ROOT,
    )
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
