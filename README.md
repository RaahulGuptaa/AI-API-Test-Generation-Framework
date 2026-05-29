# AI-Assisted API Test Generation & Execution Framework

A beginner-friendly Python framework that automatically generates and executes positive and negative API test cases against public dummy APIs, then produces colour-coded HTML and Excel reports.

---

## Project Objective

This project demonstrates how a Test Engineer can build a **data-driven API testing framework** from scratch. All test cases are defined as plain Python dictionaries — no hard-coded `assert` calls scattered across dozens of files. The framework:

- Reads endpoint definitions from a central config
- Executes each test case via a reusable HTTP client
- Validates status codes **and** response body keys
- Generates a professional HTML report and a styled Excel report automatically after every run

---

## Project Structure

```
api_test_framework/
├── config/
│   └── api_config.py              # Base URLs and global settings
├── test_cases/
│   └── test_case_definitions.py   # All 14 test cases (data-driven)
├── tests/
│   ├── test_jsonplaceholder.py    # JSONPlaceholder endpoint tests
│   ├── test_reqres.py             # ReqRes endpoint tests
│   └── test_dummyjson.py          # DummyJSON endpoint tests
├── utils/
│   ├── api_client.py              # HTTP client with response-time capture
│   ├── test_runner.py             # Executes one test case, returns result dict
│   └── report_generator.py        # Generates HTML + Excel reports
├── reports/                       # Auto-created; output files land here
├── conftest.py                    # pytest fixtures + session-finish hook
├── pytest.ini                     # pytest configuration
├── main.py                        # One-command entry point
├── requirements.txt
└── README.md
```

---

## APIs Under Test

| Provider | Base URL | Endpoints tested |
|---|---|---|
| JSONPlaceholder | `https://jsonplaceholder.typicode.com` | `/posts/{id}`, `/users/{id}`, `/posts` (POST), `/todos/{id}` |
| PokeAPI | `https://pokeapi.co` | `/api/v2/pokemon/{id}`, `/api/v2/move/{id}` |
| DummyJSON | `https://dummyjson.com` | `/products/{id}`, `/users/{id}` |

---

## Test Cases Summary

| ID | Name | API | Method | Endpoint | Type | Expected |
|---|---|---|---|---|---|---|
| TC001 | Get Post – Valid ID | JSONPlaceholder | GET | /posts/1 | Positive | 200 |
| TC002 | Get Post – Non-Existent ID | JSONPlaceholder | GET | /posts/99999 | Negative | 404 |
| TC003 | Get User – Valid ID | JSONPlaceholder | GET | /users/1 | Positive | 200 |
| TC004 | Get User – Non-Existent ID | JSONPlaceholder | GET | /users/99999 | Negative | 404 |
| TC005 | Create Post – Valid Payload | JSONPlaceholder | POST | /posts | Positive | 201 |
| TC006 | Get Todo – Non-Existent ID | JSONPlaceholder | GET | /todos/99999 | Negative | 404 |
| TC007 | Get Pokémon – Valid ID | PokeAPI | GET | /api/v2/pokemon/1 | Positive | 200 |
| TC008 | Get Pokémon – Non-Existent ID | PokeAPI | GET | /api/v2/pokemon/99999 | Negative | 404 |
| TC009 | Get Move – Valid ID | PokeAPI | GET | /api/v2/move/1 | Positive | 200 |
| TC010 | Get Move – Non-Existent ID | PokeAPI | GET | /api/v2/move/99999 | Negative | 404 |
| TC011 | Get Product – Valid ID | DummyJSON | GET | /products/1 | Positive | 200 |
| TC012 | Get Product – Non-Existent ID | DummyJSON | GET | /products/99999 | Negative | 404 |
| TC013 | Get DummyJSON User – Valid ID | DummyJSON | GET | /users/1 | Positive | 200 |
| TC014 | Get DummyJSON User – Non-Existent ID | DummyJSON | GET | /users/99999 | Negative | 404 |

---

## Setup Steps

### 1. Prerequisites

- Python 3.9 or higher
- pip (comes with Python)

### 2. Clone / Download the project

```bash
cd ~/Desktop
# The folder api_test_framework/ should already be present
cd api_test_framework
```

### 3. Create a virtual environment (recommended)

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

## How to Run Tests

### Option A — Single command (recommended)

```bash
python main.py
```

### Option B — Using pytest directly

```bash
# Run all tests
pytest tests/ -v

# Run only one API's tests
pytest tests/test_reqres.py -v

# Run a specific test case by ID
pytest tests/ -k TC009 -v

# Run only positive tests
pytest tests/ -k "TC001 or TC003 or TC005 or TC007 or TC009 or TC011 or TC013" -v
```

---

## How to View Reports

After each run, two report files are created inside the `reports/` folder:

| Format | File | How to open |
|---|---|---|
| HTML | `reports/test_report_YYYYMMDD_HHMMSS.html` | Double-click or open in any browser |
| Excel | `reports/test_report_YYYYMMDD_HHMMSS.xlsx` | Open with Excel or LibreOffice Calc |

The terminal output also prints the absolute paths:

```
══════════════════════════════════════════════════════════════
  TEST EXECUTION SUMMARY
  Total : 14  |  Passed : 14  |  Failed : 0
  HTML  : /Users/.../api_test_framework/reports/test_report_20260101_120000.html
  Excel : /Users/.../api_test_framework/reports/test_report_20260101_120000.xlsx
══════════════════════════════════════════════════════════════
```

### Sample HTML Report

```
┌─────────────────────────────────────────────────────┐
│  AI-Assisted API Test Report                        │
│  Generated May 29, 2026 at 12:00:00                 │
├────────┬────────┬────────┬──────────┬───────────────┤
│ Total  │ Passed │ Failed │ Pass Rate │ Avg Resp (ms) │
│  14    │  14    │   0    │  100.0%  │     212 ms    │
└────────┴────────┴────────┴──────────┴───────────────┘

┌──────┬──────────────────────────┬─────────┬────────┬──────┬──────┬────────┐
│ ID   │ Test Name                │ API     │ Method │ Exp  │ Act  │ Result │
├──────┼──────────────────────────┼─────────┼────────┼──────┼──────┼────────┤
│ TC001│ Get Post – Valid ID      │ JPH     │ GET    │ 200  │ 200  │ ✅ PASS│
│ TC002│ Get Post – Non-Existent  │ JPH     │ GET    │ 404  │ 404  │ ✅ PASS│
│ TC009│ Login – Valid Creds      │ ReqRes  │ POST   │ 200  │ 200  │ ✅ PASS│
│ TC010│ Login – Missing Password │ ReqRes  │ POST   │ 400  │ 400  │ ✅ PASS│
└──────┴──────────────────────────┴─────────┴────────┴──────┴──────┴────────┘
```

---

## How This Framework Works — Architecture

```
main.py
  └─ runs pytest
       └─ conftest.py (fixtures: api_client, test_results)
            ├─ tests/test_jsonplaceholder.py  ─┐
            ├─ tests/test_reqres.py            ├─ parametrize from TEST_CASES
            └─ tests/test_dummyjson.py         ┘
                 └─ utils/test_runner.py
                      └─ utils/api_client.py  (HTTP + timing)
                 └─ conftest.pytest_sessionfinish
                      └─ utils/report_generator.py (HTML + Excel)
```

**Data flow for each test:**

1. pytest parametrizes the test with one dict from `TEST_CASES`
2. `execute_test_case()` sends the HTTP request and measures response time
3. Validates: `actual_status == expected_status`, then checks `expected_keys` in body
4. Appends a result record (`PASS`/`FAIL` + reason) to the session list
5. After all tests finish, `pytest_sessionfinish` generates both reports

---

## Adding a New Test Case

Open `test_cases/test_case_definitions.py` and append a new dict to `TEST_CASES`:

```python
{
    "id": "TC015",
    "name": "Get Comment – Valid ID",
    "description": "Fetch comment #1; expect 200 with id/email/body",
    "api_name": "JSONPlaceholder",          # must match a test file's filter
    "base_url": "https://jsonplaceholder.typicode.com",
    "endpoint": "/comments/1",
    "method": "GET",
    "headers": {"Content-Type": "application/json"},
    "payload": None,
    "params": None,
    "expected_status": 200,
    "expected_keys": ["id", "email", "body"],
    "test_type": "positive",
},
```

No other file needs to change — the parametrize decorator picks it up automatically.

---

## Future Enhancements with AI Integration

This project is designed to grow into a fully AI-assisted testing platform:

### Phase 1 (Current) — Manual test case authoring
- Data-driven test cases defined by the engineer
- Automated execution and reporting

### Phase 2 — AI-assisted test case generation
- Feed an OpenAPI / Swagger spec to Claude (Anthropic API) or GPT
- AI suggests additional edge cases, boundary values, and security-oriented tests
- Engineer reviews and approves before adding to `TEST_CASES`

```python
# Pseudocode — Phase 2
import anthropic

client = anthropic.Anthropic()
message = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": f"Generate 5 negative test cases for this endpoint: {endpoint_spec}"
    }]
)
suggested_cases = parse_ai_response(message.content)
```

### Phase 3 — AI-powered failure analysis
- When a test fails, send the response body + expected behaviour to Claude
- AI explains the root cause and suggests a fix
- Automatically adds a Jira ticket via API

### Phase 4 — Self-healing tests
- AI detects schema changes in API responses
- Automatically updates `expected_keys` when a new field appears
- Sends a Slack/email notification with a diff of what changed

---

## How to Present This as a Milestone Project

When presenting this to your team or in an interview, highlight these points:

1. **Data-driven design** — adding a test takes one dict, not a new function
2. **Separation of concerns** — config, test data, execution logic, and reporting are all independent layers
3. **Dual reporting** — both HTML (for stakeholders) and Excel (for test management tools)
4. **Extensibility** — the three-phase AI roadmap shows strategic thinking
5. **Real API coverage** — three production-like APIs, seven endpoints, 14 test cases across positive and negative scenarios
6. **Zero flakiness** — all tests hit stable public APIs with deterministic responses

---

## Dependencies

| Package | Version | Purpose |
|---|---|---|
| `requests` | ≥ 2.31 | HTTP client |
| `pytest` | ≥ 7.4 | Test runner and parametrization |
| `pandas` | ≥ 2.0 | DataFrame for Excel export |
| `openpyxl` | ≥ 3.1 | Excel file writing with styles |
