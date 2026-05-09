# ExpandTesting Notes App — Selenium Python Capstone

## Quick Start (3 steps)

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set your credentials
Open `config/config.yaml` and update:
```yaml
credentials:
  email: "your_registered_email@example.com"
  password: "your_password"
```
Or export as environment variables:
```bash
export TEST_EMAIL="your@email.com"
export TEST_PASSWORD="yourpassword"
```
> **Register** a free account at https://practice.expandtesting.com/notes/app

### 3. Run tests
```bash
# All tests
pytest

# Only smoke tests
pytest -m smoke

# Only API tests (no browser needed)
pytest -m api

# Only E2E hybrid tests
pytest -m e2e

# Only negative tests
pytest -m negative

# Parallel (4 workers)
pytest -n 4

# Headless browser
HEADLESS=true pytest

# Specific test file
pytest tests/test_login.py
pytest tests/test_notes_api.py
pytest tests/test_e2e_hybrid.py
```

### View Allure Report
```bash
# Install Allure CLI first: https://docs.qameta.io/allure/#_installing_a_commandline
allure serve reports/allure-results
```

HTML report is auto-generated at: `reports/html/report.html`

---

## Project Structure
```
notes_automation/
├── tests/
│   ├── test_login.py          # TC-UI-01 to TC-UI-03, TC-NEG-01
│   ├── test_notes_ui.py       # TC-UI-04 to TC-UI-06, TC-NEG-02
│   ├── test_notes_api.py      # TC-API-01 to TC-API-04, TC-NEG-03 to TC-NEG-05
│   └── test_e2e_hybrid.py     # TC-E2E-01, TC-E2E-02
├── pages/
│   ├── base_page.py           # Core POM: waits, clicks, JS, retry
│   ├── login_page.py          # Login page object
│   └── notes_page.py          # Notes dashboard page object
├── api/
│   └── api_client.py          # Reusable Notes API client
├── config/
│   ├── config.yaml            # All settings (URL, credentials, timeouts)
│   └── environment.py         # Typed config loader
├── utils/
│   ├── logger.py              # File + console logging
│   ├── screenshot.py          # Auto-screenshot + Allure attach
│   └── retry.py               # Retry decorator for flaky actions
├── reports/
│   ├── allure-results/        # Allure raw data
│   ├── html/                  # pytest-html report
│   └── screenshots/           # Failure screenshots
├── logs/                      # Daily log files
├── conftest.py                # All pytest fixtures
├── pytest.ini                 # pytest config + markers
└── requirements.txt
```

## Test Case → File Mapping
| Test Case ID | File | Description |
|---|---|---|
| TC-UI-01 | test_login.py | Valid login |
| TC-UI-02 | test_login.py | Invalid password |
| TC-UI-03 | test_login.py | Empty credentials |
| TC-UI-04 | test_notes_ui.py | Create note via UI |
| TC-UI-05 | test_notes_ui.py | Missing title validation |
| TC-UI-06 | test_notes_ui.py | Instant visibility (no refresh) |
| TC-API-01 | test_notes_api.py | GET /notes → 200 + list |
| TC-API-02 | test_notes_api.py | Response time < 2s |
| TC-API-03 | test_notes_api.py | DELETE /notes/{id} |
| TC-API-04 | test_notes_api.py | DELETE non-existent → 404 |
| TC-E2E-01 | test_e2e_hybrid.py | UI create → API validate |
| TC-E2E-02 | test_e2e_hybrid.py | API delete → UI absent |
| TC-NEG-01 | test_login.py | Empty email field |
| TC-NEG-02 | test_notes_ui.py | All fields empty |
| TC-NEG-03 | test_notes_api.py | No auth token → 401 |
| TC-NEG-04 | test_notes_api.py | Invalid payload → 400 |
| TC-NEG-05 | test_notes_api.py | Bad token → 401 |

## Agentic Automation

Implemented:
- Self-healing locators
- Auto-retry for flaky UI actions
- Intelligent waits
- Decision-based rerun logic

## MCP Layer

Implemented:
- LLM-style test data generation
- Failure analysis helper
- Locator suggestion helper

## Performance Engineering

Implemented:
- API response time validation
- UI navigation timing
- JSONL trend logging in reports/performance_trends.jsonl
