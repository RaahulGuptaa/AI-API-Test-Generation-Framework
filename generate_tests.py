#!/usr/bin/env python3
"""
AI Test Case Generator
======================
Give it an endpoint spec on the command line.
It probes the live API, asks Claude to write 2 test cases (positive + negative),
then appends them straight to test_cases/test_case_definitions.py.

Usage
-----
    python generate_tests.py \\
        --api_name "DummyJSON" \\
        --base_url "https://dummyjson.com" \\
        --endpoint "/products/1" \\
        --method GET

    python generate_tests.py \\
        --api_name "PokeAPI" \\
        --base_url "https://pokeapi.co" \\
        --endpoint "/api/v2/berry/1"

    # Preview only — nothing written to disk
    python generate_tests.py --api_name MyAPI --base_url https://... --endpoint /foo --dry-run

Requirements
------------
    ANTHROPIC_API_KEY environment variable must be set.
"""

import argparse
import json
import os
import re
import subprocess
import sys

import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


# ─────────────────────────────────────────────────────────────────────────────
#  Step 1 — probe the live endpoint
# ─────────────────────────────────────────────────────────────────────────────

def probe_endpoint(base_url: str, endpoint: str, method: str) -> dict:
    """Hit the real endpoint and return {status_code, body, error}."""
    url = base_url + endpoint
    try:
        resp = requests.request(method.upper(), url, timeout=10)
        try:
            body = resp.json()
        except Exception:
            body = {"_raw": resp.text[:400]}
        return {"status_code": resp.status_code, "body": body, "error": None}
    except Exception as exc:
        return {"status_code": None, "body": {}, "error": str(exc)}


# ─────────────────────────────────────────────────────────────────────────────
#  Step 2 — ask Claude to write the test cases
# ─────────────────────────────────────────────────────────────────────────────

def generate_with_claude(
    api_name: str,
    base_url: str,
    endpoint: str,
    method: str,
    probe: dict,
    start_id: int,
) -> list:
    """Call Claude and parse the returned JSON array of 2 test case dicts."""
    import anthropic

    client = anthropic.Anthropic()

    prompt = f"""You are a senior API test engineer.
Generate exactly 2 API test cases for the endpoint spec below.

Return ONLY a valid JSON array with 2 objects — no explanation, no markdown, just raw JSON.

## Endpoint spec
api_name : {api_name}
base_url : {base_url}
endpoint : {endpoint}
method   : {method}

## Live probe result (what the real endpoint returned right now)
{json.dumps(probe, indent=2)}

## Rules
1. Test case 1 must be POSITIVE (test_type: "positive")
   - Use the endpoint exactly as given above.
   - expected_status: use the status_code from the probe (fall back to 200 if probe failed).
   - expected_keys: pick up to 4 important top-level keys from the probe body.

2. Test case 2 must be NEGATIVE (test_type: "negative")
   - Modify the endpoint to make it fail:
       * If the endpoint ends with a numeric ID  → replace that number with 99999
         Example: /products/1  becomes /products/99999
       * If the endpoint has no numeric ID       → append /99999
         Example: /api/v2/berry/slim            becomes /api/v2/berry/slim/99999
   - expected_status: 404
   - expected_keys: []

3. Required dict keys — use EXACTLY these names (no extras, no renames):
   id, name, description, api_name, base_url, endpoint, method,
   headers, payload, params, expected_status, expected_keys, test_type

4. id values:
   - Positive case: "TC{start_id:03d}"
   - Negative case: "TC{start_id + 1:03d}"

5. headers: {{"Content-Type": "application/json"}} for both cases.
6. payload: null for GET/DELETE; a minimal realistic JSON body for POST/PUT/PATCH.
7. params: null for both.

Return the raw JSON array now:"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()
    # Strip accidental markdown fences Claude might add
    raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.MULTILINE)
    raw = re.sub(r"```\s*$", "", raw, flags=re.MULTILINE)
    return json.loads(raw.strip())


# ─────────────────────────────────────────────────────────────────────────────
#  Step 3 — write the new cases into test_case_definitions.py
# ─────────────────────────────────────────────────────────────────────────────

def _to_python_value(v) -> str:
    """Convert a Python value to its source-code representation."""
    if v is None:
        return "None"
    if isinstance(v, bool):
        return str(v)
    if isinstance(v, str):
        return repr(v)
    if isinstance(v, list):
        if not v:
            return "[]"
        return "[" + ", ".join(repr(i) for i in v) + "]"
    if isinstance(v, dict):
        if not v:
            return "{}"
        items = ", ".join(f"{repr(k)}: {repr(val)}" for k, val in v.items())
        return "{" + items + "}"
    return repr(v)


def dict_to_python_literal(d: dict) -> str:
    """
    Format a dict as a Python source literal that matches the style
    already used in test_case_definitions.py (4-space inner indent).
    """
    lines = ["{"]
    for k, v in d.items():
        lines.append(f'        "{k}": {_to_python_value(v)},')
    lines.append("    }")
    return "\n".join(lines)


def append_to_definitions(new_cases: list) -> None:
    """Append new dicts into TEST_CASES inside test_case_definitions.py."""
    filepath = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "test_cases",
        "test_case_definitions.py",
    )

    section_header = f"\n    # ── AI-generated: {new_cases[0]['api_name']} {new_cases[0]['method']} {new_cases[0]['endpoint']} ─\n"
    block = section_header
    for tc in new_cases:
        block += f"    {dict_to_python_literal(tc)},\n"

    with open(filepath, "r", encoding="utf-8") as fh:
        content = fh.read()

    # Insert right before the final closing `]` of TEST_CASES
    insert_at = content.rfind("]")
    new_content = content[:insert_at] + block + "\n" + content[insert_at:]

    with open(filepath, "w", encoding="utf-8") as fh:
        fh.write(new_content)


# ─────────────────────────────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────────────────────────────

def next_start_id() -> int:
    from test_cases.test_case_definitions import TEST_CASES
    if not TEST_CASES:
        return 1
    return max(int(tc["id"].replace("TC", "")) for tc in TEST_CASES) + 1


# ─────────────────────────────────────────────────────────────────────────────
#  Demo stub (no API key needed)
# ─────────────────────────────────────────────────────────────────────────────

def _demo_cases(api_name, base_url, endpoint, method, probe, start_id) -> list:
    """
    Build realistic-looking test cases from the live probe data alone.
    Used when --demo flag is passed; identical shape to what Claude returns.
    """
    # Derive a "negative" endpoint by replacing the trailing number with 99999
    neg_endpoint = re.sub(r"/(\d+)$", "/99999", endpoint)
    if neg_endpoint == endpoint:           # no trailing number found
        neg_endpoint = endpoint + "/99999"

    top_keys = list(probe["body"].keys())[:4] if probe.get("body") else []
    pos_status = probe["status_code"] if probe["status_code"] else 200
    name_slug = endpoint.strip("/").replace("/", " ").title()

    return [
        {
            "id": f"TC{start_id:03d}",
            "name": f"Get {name_slug} – Valid ID",
            "description": f"Fetch {endpoint}; expect {pos_status} with key fields present",
            "api_name": api_name,
            "base_url": base_url,
            "endpoint": endpoint,
            "method": method.upper(),
            "headers": {"Content-Type": "application/json"},
            "payload": None,
            "params": None,
            "expected_status": pos_status,
            "expected_keys": top_keys,
            "test_type": "positive",
        },
        {
            "id": f"TC{start_id + 1:03d}",
            "name": f"Get {name_slug} – Non-Existent ID",
            "description": f"Fetch {neg_endpoint} (does not exist); expect 404",
            "api_name": api_name,
            "base_url": base_url,
            "endpoint": neg_endpoint,
            "method": method.upper(),
            "headers": {"Content-Type": "application/json"},
            "payload": None,
            "params": None,
            "expected_status": 404,
            "expected_keys": [],
            "test_type": "negative",
        },
    ]


# ─────────────────────────────────────────────────────────────────────────────
#  CLI
# ─────────────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate AI-written test cases and append them to the framework.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python generate_tests.py --api_name DummyJSON --base_url https://dummyjson.com --endpoint /products/1
  python generate_tests.py --api_name PokeAPI   --base_url https://pokeapi.co    --endpoint /api/v2/berry/1
  python generate_tests.py --api_name MyAPI     --base_url https://myapi.com     --endpoint /orders/5 --method GET --dry-run
""",
    )
    parser.add_argument("--api_name", required=True, help='Provider name, e.g. "DummyJSON"')
    parser.add_argument("--base_url", required=True, help="Root URL, e.g. https://dummyjson.com")
    parser.add_argument("--endpoint", required=True, help="Path, e.g. /products/1")
    parser.add_argument("--method", default="GET", help="HTTP verb (default: GET)")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the generated cases without writing to disk",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Skip Claude call; generate realistic stub cases to preview the flow",
    )
    args = parser.parse_args()

    if not args.dry_run and not args.demo and not os.getenv("ANTHROPIC_API_KEY"):
        print("\nError: ANTHROPIC_API_KEY is not set.")
        print("  export ANTHROPIC_API_KEY=sk-ant-...")
        print("\nTip: use --demo to preview the full flow without an API key.")
        return 1

    divider = "=" * 55

    print(f"\n{divider}")
    print("  AI Test Case Generator")
    print(divider)
    print(f"\n  Endpoint : {args.method.upper()} {args.base_url}{args.endpoint}\n")

    # ── 1. Probe ──────────────────────────────────────────
    print("  [1/3] Probing live endpoint ...")
    probe = probe_endpoint(args.base_url, args.endpoint, args.method)
    if probe["error"]:
        print(f"        Warning: {probe['error']}")
        print("        Proceeding without live response data.")
    else:
        top_keys = list(probe["body"].keys())[:5]
        print(f"        Status : {probe['status_code']}")
        print(f"        Keys   : {top_keys}")

    # ── 2. Claude (or demo stub) ───────────────────────────
    start_id = next_start_id()

    if args.demo:
        print(f"\n  [2/3] Demo mode — generating stub cases TC{start_id:03d} + TC{start_id + 1:03d} ...")
        cases = _demo_cases(args.api_name, args.base_url, args.endpoint, args.method, probe, start_id)
    else:
        print(f"\n  [2/3] Asking Claude to write TC{start_id:03d} + TC{start_id + 1:03d} ...")
        try:
            cases = generate_with_claude(
                api_name=args.api_name,
                base_url=args.base_url,
                endpoint=args.endpoint,
                method=args.method,
                probe=probe,
                start_id=start_id,
            )
        except Exception as exc:
            print(f"\n  Error calling Claude: {exc}")
            return 1

    # ── 3. Display ────────────────────────────────────────
    print(f"\n  [3/3] Claude generated {len(cases)} test case(s):\n")
    for tc in cases:
        icon = "+" if tc.get("test_type") == "positive" else "-"
        print(f"  [{icon}] {tc['id']}  {tc['name']}")
        print(f"       {tc['method']} {tc['endpoint']}")
        print(f"       Expected status : {tc['expected_status']}")
        if tc.get("expected_keys"):
            print(f"       Expected keys   : {tc['expected_keys']}")
        print()

    if args.dry_run:
        print("  --dry-run: nothing written, nothing executed.")
        print("\n  Full JSON output:")
        print(json.dumps(cases, indent=2))
        print()
        return 0

    # ── 4. Write ──────────────────────────────────────────
    append_to_definitions(cases)
    print(f"  Appended to test_cases/test_case_definitions.py")

    # ── 5. Run tests automatically ────────────────────────
    print(f"\n{divider}")
    print("  Executing tests ...")
    print(f"{divider}\n")

    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short", "-s"],
        cwd=os.path.dirname(os.path.abspath(__file__)),
    )
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
