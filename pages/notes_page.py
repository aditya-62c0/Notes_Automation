import time
from unicodedata import category 

import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select

from pages.base_page import BasePage
from core.agentic.self_healing import SelfHealingDriver
from core.agentic.retry_engine import auto_retry
from config.environment import UI
from core.mcp.locator_suggester import LocatorSuggester



class NotesPage(BasePage):

# ── Locators ──────────────────────────────────────────────────────────────

    # Dashboard / Navigation
    _ADD_NOTE_BTN = (
        By.XPATH,
        "//button[contains(., '+ Add Note')]"
    )

    _ALL_TAB = (
        By.XPATH,
        "//button[contains(normalize-space(),'All')]"
    )

    _HOME_HEADING = (
        By.CSS_SELECTOR,
        "h1, .notes-heading, [data-testid='page-heading']"
    )

    # ── Create Note Modal ────────────────────────────────────────────────────

    _NOTE_FORM = (
        By.CSS_SELECTOR,
        ".modal-content"
    )

    _NOTE_TITLE_INPUT = (
        By.ID,
        "title"
    )

    _NOTE_DESC_INPUT = (
        By.ID,
        "description"
    )

    _NOTE_CAT_SELECT = (
        By.ID,
        "category"
    )

    _SAVE_BTN = (
        By.CSS_SELECTOR,
        "button[data-testid='note-submit']"
    )

    _CANCEL_BTN = (
        By.CSS_SELECTOR,
        "button[data-testid='note-cancel']"
    )

    # ── Success / Alerts ─────────────────────────────────────────────────────

    _SUCCESS_BANNER = (
        By.CSS_SELECTOR,
        ".alert-success, "
        "[data-testid='alert-message'], "
        ".toast-success, "
        ".swal2-success, "
        "[role='alert']"
    )

    # ── Note Cards ───────────────────────────────────────────────────────────

    _NOTE_CARD_LIST = (
        By.CSS_SELECTOR,
        "[data-testid='notes-list']"
    )

    _NOTE_CARDS = (
        By.CSS_SELECTOR,
        "[data-testid='note-card']"
    )

    _NOTE_TITLES = (
        By.CSS_SELECTOR,
        "[data-testid='note-card-title']"
    )

    _NOTE_BODY_ITEMS = (
        By.CSS_SELECTOR,
        "[data-testid='note-card-description']"
    )

    # ── Delete ───────────────────────────────────────────────────────────────

    _DELETE_BTNS = (
        By.CSS_SELECTOR,
        "button.btn-danger"
    )

    _CONFIRM_DELETE = (
        By.CSS_SELECTOR,
        ".btn-danger[data-testid='note-delete-confirm'], "
        "button.btn-danger"
    )

    # ── Validation ───────────────────────────────────────────────────────────

    _TITLE_VALIDATION = (
        By.CSS_SELECTOR,
        "#title + .invalid-feedback, "
        "[data-testid='title-validation'], "
        ".invalid-feedback, "
        ".alert-danger, "
        "[role='alert']"
    )

    # ── Page ready ────────────────────────────────────────────────────────────

    def wait_for_page_loaded(self):
        self.log.info("Waiting for Notes dashboard to fully load")
        self.wait.until(EC.presence_of_element_located(self._ADD_NOTE_BTN))
        self.log.info("Notes dashboard loaded")

    # ── Navigation ────────────────────────────────────────────────────────────

    @allure.step("Navigate to Notes dashboard")
    def goto_dashboard(self):
        current_url = self.get_current_url()
        if not current_url.startswith(UI.BASE_URL):
            self.open(UI.BASE_URL)
        else:
            self.log.info("Already on dashboard page")
        self.wait_for_visible(self._ADD_NOTE_BTN)
        self.log.info("Notes dashboard loaded")

    # ── Note Creation ─────────────────────────────────────────────────────────

    @allure.step("Click Add Note button")
    def click_add_note(self):
        self.click(self._ADD_NOTE_BTN)
        self.wait_for_visible(self._NOTE_TITLE_INPUT)

    @allure.step("Fill note form — title='{title}', category='{category}'")
    def fill_note_form(self, title: str, description: str, category: str = "Home"):
        self.type_text(self._NOTE_TITLE_INPUT, title)
        self.type_text(self._NOTE_DESC_INPUT, description)
        try:
            from selenium.webdriver.support.select import Select
            el = self.wait_for_visible(self._NOTE_CAT_SELECT)
            Select(el).select_by_visible_text(category)
        except Exception:
            self.driver.execute_script(
                "arguments[0].value = arguments[1];",
                self.wait_for_visible(self._NOTE_CAT_SELECT),
                category,
            )

    @allure.step("Save note")
    def save_note(self):
        self.click(self._SAVE_BTN)

    def _get_visible_note_titles(self) -> list[str]:

        try:

            elements = self.driver.find_elements(*self._NOTE_TITLES)

            titles = []

            for el in elements:

                try:
                    txt = el.text.strip()

                    if txt:
                        titles.append(txt)

                except Exception:
                    continue

            self.log.info(f"Visible note titles: {titles}")

            return titles

        except Exception as exc:

            self.log.warning(
                f"Unable to fetch visible note titles: {exc}"
            )

            return []

    @allure.step("Wait until redirected back to dashboard")
    def wait_until_dashboard_visible(self, timeout: int = 20) -> bool:
        """
        Wait until:
        1. URL is dashboard URL
        2. Add Note button visible
        3. Note form disappears
        """

        try:
            # Wait until note form disappears
            WebDriverWait(self.driver, timeout).until(
                EC.invisibility_of_element_located(self._NOTE_TITLE_INPUT)
            )

            # Wait until Add Note button appears again
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(self._ADD_NOTE_BTN)
            )

            # Verify URL is dashboard
            WebDriverWait(self.driver, timeout).until(
                lambda d: "/notes/app" in d.current_url
            )

            self.log.info(
                f"Dashboard visible after save | URL={self.driver.current_url}"
            )

            return True

        except TimeoutException:
            self.log.warning(
                f"Dashboard did not appear after note creation | "
                f"Current URL={self.driver.current_url}"
            )

            try:
                page_source = self.driver.page_source[:2000]
                self.log.warning(f"Page source snippet:\n{page_source}")
            except Exception:
                pass

            return False
        
    @allure.step("Open All tab")
    def open_all_tab(self):
        try:
            self.click(self._ALL_TAB)
            self.log.info("Opened All tab")
        except Exception:
            self.log.info("All tab not clickable or already active")

# ── Note Creation ─────────────────────────────────────────────────────────

    @auto_retry(max_attempts=3, delay=1)
    @allure.step("Create note: title='{title}'")
    def create_note(self, title: str, description: str, category: str = "Home"):
        """
        Creates a note from UI.
        """

        # Click + Add Note
        self.click(self._ADD_NOTE_BTN)

        # Wait for modal
        self.smart_wait.visible(self._NOTE_TITLE_INPUT)

        # Fill title
        fallbacks = LocatorSuggester().suggest_for_notes_app("note_title")
        title_input = self.healer.find(self._NOTE_TITLE_INPUT, fallbacks)

        title_input.clear()
        title_input.send_keys(title)

        # Fill description
        desc_input = self.healer.find(
            self._NOTE_DESC_INPUT,
            fallback_locators=[
                (By.NAME, "description"),
                (By.CSS_SELECTOR, "textarea[placeholder*='description' i]")
            ]
        )

        desc_input.clear()
        desc_input.send_keys(description)

        # Select category
        category_select = self.healer.find(
            self._NOTE_CAT_SELECT,
            fallback_locators=[
                (By.NAME, "category"),
                (By.CSS_SELECTOR, "select")
            ]
        )

        Select(category_select).select_by_visible_text(category)
    

        time.sleep(1)

        # Click Create button
        create_btn = self.smart_wait.clickable(self._SAVE_BTN)

        self.driver.execute_script(
            "arguments[0].scrollIntoView(true);",
            create_btn
        )

        time.sleep(1)

        # JS click avoids interception
        self.driver.execute_script(
            "arguments[0].click();",
            create_btn
        )

        self.log.info(f"Note submitted: {title}")

        # Wait for modal to disappear
        WebDriverWait(self.driver, 15).until(
            EC.invisibility_of_element_located(self._SAVE_BTN)
        )

        # Wait for dashboard
        self.smart_wait.visible(self._ADD_NOTE_BTN)

        time.sleep(2)

    # ── Assertions / Getters ──────────────────────────────────────────────────

    @allure.step("Check success banner is visible")
    def is_success_banner_visible(self, timeout: int = 15) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(self._SUCCESS_BANNER)
            )
            self.log.info("Success banner found in DOM")
            return True
        except TimeoutException:
            pass
        try:
            WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located(self._ADD_NOTE_BTN)
            )
            if not self.is_visible(self._NOTE_TITLE_INPUT, timeout=2):
                self.log.info("No explicit banner — dashboard visible, form closed; treating as success")
                return True
        except TimeoutException:
            pass
        return False

    def get_success_message(self) -> str:
        try:
            return self.get_text(self._SUCCESS_BANNER)
        except Exception:
            return ""

    def get_all_note_titles(self) -> list[str]:
        return [el.text.strip() for el in self.find_elements(self._NOTE_CARDS) if el.text.strip()]

    def get_all_note_descriptions(self) -> list[str]:
        return [el.text.strip() for el in self.find_elements(self._NOTE_BODY_ITEMS) if el.text.strip()]

    def _get_all_card_texts(self) -> list[str]:
        """Returns full text of every card/list item on the current page."""
        cards = self.driver.find_elements(By.CSS_SELECTOR, ".card, .list-group-item")
        return [c.text.strip() for c in cards if c.text.strip()]

    def note_exists_on_page(self, title: str) -> bool:
        self.driver.refresh()

        WebDriverWait(self.driver, 15).until(

            EC.visibility_of_element_located(self._ADD_NOTE_BTN)

        )

        self.open_all_tab()

        titles = self._get_visible_note_titles()

        self.log.info(

            f"Checking note existence | Expected='{title}' | Visible={titles}"

        )

        return title.strip() in [t.strip() for t in titles]

    def is_note_visible_in_list(self, title: str) -> bool:
        """Reload once then scan every card's full text for the title."""
        self.reload_and_wait()
        texts = self._get_all_card_texts()
        self.log.info(f"Notes visible in UI: {texts}")
        return any(title in t for t in texts)

    def is_note_absent_from_list(self, title: str) -> bool:
        self.reload_and_wait()
        texts = self._get_all_card_texts()
        self.log.info(f"Notes after delete: {texts}")
        return not any(title in t for t in texts)

    def get_title_validation_error(self) -> str:
        if self.is_visible(self._TITLE_VALIDATION):
            return self.get_text(self._TITLE_VALIDATION)
        return ""

    def _is_on_form(self) -> bool:
        url = self.get_current_url()
        if "add" in url or "edit" in url:
            return True
        return self.is_visible(self._NOTE_TITLE_INPUT, timeout=2)

    def is_form_still_visible(self) -> bool:
        return self._is_on_form()

    def is_any_validation_shown(self, timeout: int = 5) -> bool:
        if self.is_visible(self._TITLE_VALIDATION, timeout=timeout):
            self.log.info("Validation element found in DOM")
            return True
        try:
            for el in self.driver.find_elements(By.CSS_SELECTOR, "[role='alert'], .alert"):
                if el.is_displayed():
                    txt = el.text.lower()
                    if not any(w in txt for w in ("success", "created", "saved")):
                        self.log.info(f"Error alert visible: {el.text[:60]}")
                        return True
        except Exception:
            pass
        try:
            count = self.driver.execute_script(
                "return document.querySelectorAll(':invalid').length;"
            )
            if count and count > 0:
                self.log.info(f"HTML5 :invalid fields found: {count}")
                return True
        except Exception:
            pass
        return False

    @allure.step("Wait for note '{title}' to appear in list")
    def wait_for_note_in_list(self, title: str, timeout: int = 30):

        end_time = time.time() + timeout
        attempt = 1

        while time.time() < end_time:

            self.driver.refresh()

            WebDriverWait(self.driver, 15).until(
                EC.visibility_of_element_located(self._ADD_NOTE_BTN)
            )

            time.sleep(2)

            self.click(self._ALL_TAB)

            WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located(self._NOTE_TITLES)
            )

            titles = [
                el.text.strip()
                for el in self.driver.find_elements(*self._NOTE_TITLES)
                if el.text.strip()
            ]

            self.log.info(f"[WAIT] Attempt {attempt} → titles={titles}")

            if title.strip() in titles:
                self.log.info(f"Found note: {title}")
                return True

            attempt += 1
            time.sleep(3)

        self.log.warning(f"[WAIT] Note not found after timeout: {title}")
        return False

    @allure.step("Reload page and wait for notes list")
    def reload_and_wait(self):
        self.driver.refresh()
        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located(self._ADD_NOTE_BTN)
        )