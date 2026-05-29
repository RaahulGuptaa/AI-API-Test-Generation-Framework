import time
import requests
from typing import Any, Dict, Optional


class APIClient:
    """Thin wrapper around requests.Session that captures response time."""

    def __init__(self, timeout: int = 10) -> None:
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})

    def execute(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        payload: Optional[Any] = None,
        params: Optional[Dict] = None,
    ) -> Dict:
        start = time.perf_counter()
        try:
            resp = self.session.request(
                method=method.upper(),
                url=url,
                headers=headers or {},
                json=payload,
                params=params,
                timeout=self.timeout,
            )
            ms = round((time.perf_counter() - start) * 1000, 2)
            try:
                body = resp.json()
            except ValueError:
                body = {"_raw": resp.text[:500]}
            return {
                "status_code": resp.status_code,
                "body": body,
                "response_time_ms": ms,
                "error": None,
            }
        except requests.exceptions.Timeout:
            return _err(start, "Request timed out")
        except requests.exceptions.ConnectionError as exc:
            return _err(start, f"Connection error: {exc}")
        except Exception as exc:
            return _err(start, f"Unexpected error: {exc}")


def _err(start: float, msg: str) -> Dict:
    return {
        "status_code": None,
        "body": {},
        "response_time_ms": round((time.perf_counter() - start) * 1000, 2),
        "error": msg,
    }
