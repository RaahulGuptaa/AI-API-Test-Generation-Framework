from typing import Dict
from utils.api_client import APIClient


def execute_test_case(test_case: Dict, api_client: APIClient) -> Dict:
    """Run one test case dict and return a result record."""
    url = test_case["base_url"] + test_case["endpoint"]
    response = api_client.execute(
        method=test_case["method"],
        url=url,
        headers=test_case.get("headers"),
        payload=test_case.get("payload"),
        params=test_case.get("params"),
    )

    failures = []

    if response["error"]:
        failures.append(f"Request error: {response['error']}")
    else:
        if response["status_code"] != test_case["expected_status"]:
            failures.append(
                f"Expected HTTP {test_case['expected_status']}, got {response['status_code']}"
            )
        # Validate body keys only on successful responses
        if (
            not failures
            and test_case.get("expected_keys")
            and response["status_code"] in (200, 201)
        ):
            missing = [k for k in test_case["expected_keys"] if k not in response["body"]]
            if missing:
                failures.append(f"Missing keys in response body: {missing}")

    return {
        **test_case,
        "actual_status": response["status_code"],
        "response_time_ms": response["response_time_ms"],
        "result": "FAIL" if failures else "PASS",
        "failure_reason": "; ".join(failures) if failures else "",
    }
