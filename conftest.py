import os
import sys

import pytest

# Make project root importable regardless of working directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.api_client import APIClient
from utils.report_generator import generate_excel_report, generate_html_report

# Module-level list shared across the entire test session
_session_results = []


@pytest.fixture(scope="session")
def api_client():
    """Single requests.Session shared by all tests."""
    return APIClient(timeout=10)


@pytest.fixture(scope="session")
def test_results():
    """List that each test appends its result record to."""
    return _session_results


def pytest_sessionfinish(session, exitstatus):
    """Generate HTML + Excel reports after the full test session completes."""
    if not _session_results:
        return

    total = len(_session_results)
    passed = sum(1 for r in _session_results if r.get("result") == "PASS")
    failed = total - passed

    html_path = generate_html_report(_session_results)
    excel_path = generate_excel_report(_session_results)

    print(f"\n{'=' * 62}")
    print(f"  TEST EXECUTION SUMMARY")
    print(f"  Total : {total}  |  Passed : {passed}  |  Failed : {failed}")
    print(f"  HTML  : {os.path.abspath(html_path)}")
    print(f"  Excel : {os.path.abspath(excel_path)}")
    print(f"{'=' * 62}")
