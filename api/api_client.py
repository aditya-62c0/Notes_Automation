import time
import allure
import requests

from config.environment import API, Credentials
from utils.logger import get_logger

log = get_logger(__name__)


class NotesAPIClient:
    """Reusable API client for the ExpandTesting Notes API."""

    def __init__(self, token: str = None):
        self.base_url = API.BASE_URL
        self.token = token
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json", "Accept": "application/json"})
        if token:
            self._set_auth(token)

    # ── Auth ──────────────────────────────────────────────────────────────────

    def _set_auth(self, token: str):
        self.token = token
        self.session.headers.update({"X-Auth-Token": token})

    def login(self, email: str = None, password: str = None) -> dict:
        payload = {
            "email": email or Credentials.EMAIL,
            "password": password or Credentials.PASSWORD,
        }
        resp = self._post("/users/login", payload, auth=False)
        token = resp.get("data", {}).get("token")
        if token:
            self._set_auth(token)
            log.info("API login successful — token acquired")
        return resp

    # ── Notes CRUD ────────────────────────────────────────────────────────────

    def get_notes(self) -> dict:
        return self._get("/notes")

    def create_note(self, title: str, description: str, category: str = "Home") -> dict:
        payload = {"title": title, "description": description, "category": category}
        return self._post("/notes", payload)

    def delete_note(self, note_id: str) -> dict:
        return self._delete(f"/notes/{note_id}")

    def get_note_by_id(self, note_id: str) -> dict:
        return self._get(f"/notes/{note_id}")

    # ── Low-level HTTP with timing ────────────────────────────────────────────

    def _get(self, path: str, **kwargs) -> dict:
        return self._request("GET", path, **kwargs)

    def _post(self, path: str, payload: dict, auth: bool = True, **kwargs) -> dict:
        return self._request("POST", path, json=payload, auth=auth, **kwargs)

    def _delete(self, path: str, **kwargs) -> dict:
        return self._request("DELETE", path, **kwargs)

    def _request(self, method: str, path: str, auth: bool = True, **kwargs) -> dict:
        url = self.base_url + path
        log.debug(f"→ {method} {url}")

        for attempt in range(3):
            start = time.time()
            try:
                if auth:
                    resp = self.session.request(method, url, timeout=API.TIMEOUT, **kwargs)
                else:
                    headers = {"Content-Type": "application/json", "Accept": "application/json"}
                    resp = requests.request(method, url, headers=headers, timeout=API.TIMEOUT, **kwargs)

                elapsed_ms = (time.time() - start) * 1000
                log.info(f"← {method} {path} | status={resp.status_code} | {elapsed_ms:.0f}ms")

                allure.attach(
                    body=f"{method} {url}\nStatus: {resp.status_code}\nTime: {elapsed_ms:.0f}ms\n\nResponse:\n{resp.text}",
                    name=f"API {method} {path}",
                    attachment_type=allure.attachment_type.TEXT,
                )

                result = {}
                try:
                    result = resp.json()
                except Exception:
                    result = {"raw": resp.text}

                result["_status_code"] = resp.status_code
                result["_elapsed_ms"] = elapsed_ms
                return result

            except requests.exceptions.Timeout:
                log.warning(f"Request timed out (attempt {attempt + 1}/3): {method} {path}")
                if attempt == 2:
                    log.error(f"All 3 attempts timed out: {method} {path}")
                    raise
                time.sleep(3)

            except requests.exceptions.RequestException as e:
                log.error(f"Request failed: {e}")
                raise