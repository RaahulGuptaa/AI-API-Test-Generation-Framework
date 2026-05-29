"""
Single dynamic test file — runs every case in TEST_CASES regardless of API.
New cases added by generate_tests.py are automatically picked up here.
"""
import pytest

from test_cases.test_case_definitions import TEST_CASES
from utils.test_runner import execute_test_case

if not TEST_CASES:
    pytest.skip(
        "No test cases yet. Run: python generate_tests.py --api_name ... --endpoint ... --demo",
        allow_module_level=True,
    )


@pytest.mark.parametrize("test_case", TEST_CASES, ids=[tc["id"] for tc in TEST_CASES])
def test_api(test_case, api_client, test_results):
    record = execute_test_case(test_case, api_client)
    test_results.append(record)
    assert record["result"] == "PASS", record["failure_reason"]
