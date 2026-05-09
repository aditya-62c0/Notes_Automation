import pytest
import allure
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

from config.environment import UI, Credentials
from api.api_client import NotesAPIClient
from pages.login_page import LoginPage
from pages.notes_page import NotesPage
from utils.screenshot import capture
from utils.logger import get_logger
from core.mcp.llm_failure_analysis import LLMFailureAnalyzer
import time

log = get_logger("conftest")


# ── Browser fixture ────────────────────────────────────────────────────────────

@pytest.fixture(scope="function")
def driver(request):

    browser = UI.BROWSER.lower()
    execution = UI.EXECUTION.lower()

    log.info(f"Browser={browser} | Execution={execution}")

    if browser == "firefox":

        options = webdriver.FirefoxOptions()

        if UI.HEADLESS:
            options.add_argument("--headless")

    else:

        options = webdriver.ChromeOptions()

        if UI.HEADLESS:
            options.add_argument("--headless=new")

        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1920,1080")

    options.page_load_strategy = "eager"

    # ---------------- LOCAL ----------------

    if execution == "local":

        if browser == "firefox":

            _driver = webdriver.Firefox(
                service=FirefoxService(
                    GeckoDriverManager().install()
                ),
                options=options
            )

        else:

            import glob, os

            raw_path = ChromeDriverManager().install()
            driver_dir = os.path.dirname(raw_path)

            candidates = glob.glob(
                os.path.join(driver_dir, "chromedriver")
            )

            chromedriver_path = candidates[0] if candidates else raw_path

            os.chmod(chromedriver_path, 0o755)

            _driver = webdriver.Chrome(
                service=ChromeService(chromedriver_path),
                options=options
            )

    # ---------------- REMOTE GRID ----------------

    else:

        _driver = webdriver.Remote(
            command_executor=UI.GRID_URL,
            options=options
        )

    _driver.implicitly_wait(UI.IMPLICIT_WAIT)
    _driver.set_page_load_timeout(UI.PAGE_LOAD_TIMEOUT)

    yield _driver

    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        capture(_driver, f"FAIL_{request.node.name}")

    _driver.quit()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Make test result available and attach MCP failure analysis."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)

    if rep.when == "call" and rep.failed:
        current_url = None

        driver = item.funcargs.get("driver") or item.funcargs.get("authenticated_driver")

        if driver:
            try:
                current_url = driver.current_url
            except Exception:
                current_url = "Unable to capture current URL"

        analysis = LLMFailureAnalyzer().analyze(
            test_name=item.name,
            error_message=rep.longreprtext,
            current_url=current_url,
        )

        allure.attach(
            json.dumps(analysis, indent=2),
            name="MCP Failure Analysis",
            attachment_type=allure.attachment_type.JSON,
        )

        log.error(f"MCP failure analysis attached for test: {item.name}")



# ── Authenticated UI session ───────────────────────────────────────────────────

@pytest.fixture(scope="function")
def authenticated_driver(driver):
    login = LoginPage(driver)
    login.open_login()
    login.login_valid(Credentials.EMAIL, Credentials.PASSWORD)
    log.info("UI login complete")
    return driver


# ── API client fixtures ────────────────────────────────────────────────────────

@pytest.fixture(scope="function")
def api_client() -> NotesAPIClient:
    client = NotesAPIClient()
    client.login()
    return client


@pytest.fixture(scope="function")
def anon_api_client() -> NotesAPIClient:
    """Unauthenticated client for negative tests."""
    return NotesAPIClient()


# ── Page Object fixtures ───────────────────────────────────────────────────────

@pytest.fixture(scope="function")
def login_page(driver) -> LoginPage:
    return LoginPage(driver)


@pytest.fixture(scope="function")
def notes_page(authenticated_driver) -> NotesPage:
    page = NotesPage(authenticated_driver)
    page.goto_dashboard()

    # Wait for page to be ready before returning
    page.wait_for_page_loaded()

    return page


# ── Shared note fixture (creates via API, yields id+data, cleans up) ───────────

@pytest.fixture(scope="function")
def existing_note(api_client) -> dict:
    """Creates a note via API before test; deletes it after (if still exists)."""
    ts = int(time.time())
    resp = api_client.create_note(
        title=f"Fixture Note {ts}",
        description="Created by fixture for test",
        category="Home",
    )
    note = resp.get("data", {})
    note_id = note.get("id")
    log.info(f"Fixture note created: id={note_id}, title={note.get('title')}")
    yield note

    # Teardown
    if note_id:
        try:
            api_client.delete_note(note_id)
            log.info(f"Fixture note deleted: id={note_id}")
        except Exception:
            pass


# ── Allure environment info ────────────────────────────────────────────────────

def pytest_configure(config):
    import os
    from pathlib import Path
    allure_dir = Path("reports/allure-results")
    allure_dir.mkdir(parents=True, exist_ok=True)
    env_file = allure_dir / "environment.properties"
    env_file.write_text(
        f"Browser={UI.BROWSER}\n"
        f"BaseURL={UI.BASE_URL}\n"
        f"API_BaseURL=https://practice.expandtesting.com/notes/api\n"
        f"Environment=QA\n"
        f"Framework=Selenium+Pytest\n"
    )
