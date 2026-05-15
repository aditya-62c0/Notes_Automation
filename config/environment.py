import os
import yaml
from pathlib import Path


_ROOT = Path(__file__).parent.parent
_CONFIG_PATH = _ROOT / "config" / "config.yaml"


def _load() -> dict:
    with open(_CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)


_cfg = _load()


class UI:
    BASE_URL: str = _cfg["ui"]["base_url"]
    LOGIN_URL: str = _cfg["ui"]["login_url"]

    IMPLICIT_WAIT: int = _cfg["ui"]["implicit_wait"]
    EXPLICIT_WAIT: int = _cfg["ui"]["explicit_wait"]
    PAGE_LOAD_TIMEOUT: int = _cfg["ui"]["page_load_timeout"]

    BROWSER: str = os.getenv(
        "BROWSER",
        _cfg["ui"]["browser"]
    )

    HEADLESS: bool = (
        os.getenv(
            "HEADLESS",
            str(_cfg["ui"]["headless"])
        ).lower() == "true"
    )

    EXECUTION: str = os.getenv(
        "EXECUTION",
        _cfg["ui"].get("execution", "local")
    )

    GRID_URL: str = os.getenv(
        "GRID_URL",
        _cfg["ui"].get("grid_url", "http://localhost:4444")
    )

class API:
    BASE_URL: str = _cfg["api"]["base_url"]

    TIMEOUT: int = _cfg["api"]["timeout"]

    MAX_RESPONSE_MS: int = _cfg["api"]["max_response_time_ms"]


class Credentials:
    EMAIL: str = os.getenv(
        "TEST_EMAIL",
        _cfg["credentials"]["email"]
    )

    PASSWORD: str = os.getenv(
        "TEST_PASSWORD",
        _cfg["credentials"]["password"]
    )

    NAME: str = _cfg["credentials"]["name"]


class Note:
    TITLE: str = _cfg["note"]["title"]

    DESCRIPTION: str = _cfg["note"]["description"]

    CATEGORY: str = _cfg["note"]["category"]


class Reporting:
    ALLURE_DIR: str = str(
        _ROOT / _cfg["reporting"]["allure_results_dir"]
    )

    HTML_REPORT: str = str(
        _ROOT / _cfg["reporting"]["html_report"]
    )

    SCREENSHOT_DIR: str = str(
        _ROOT / _cfg["reporting"]["screenshot_dir"]
    )

    LOG_DIR: str = str(
        _ROOT / _cfg["reporting"]["log_dir"]
    )