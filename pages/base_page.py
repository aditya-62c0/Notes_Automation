import allure
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
)

from config.environment import UI
from utils.logger import get_logger
from utils.screenshot import capture
from utils.retry import retry
from core.agentic.self_healing import SelfHealingDriver
from core.agentic.intelligent_waits import IntelligentWait


class BasePage:
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.wait = WebDriverWait(driver, UI.EXPLICIT_WAIT)
        self.log = get_logger(self.__class__.__name__)
        self.healer = SelfHealingDriver(driver)
        self.smart_wait = IntelligentWait(driver, UI.EXPLICIT_WAIT)


    # ── Navigation ────────────────────────────────────────────────────────────

    def open(self, url: str = None):
        target = url or UI.BASE_URL
        self.log.info(f"Navigating to {target}")
        self.driver.get(target)
        self.smart_wait.page_ready()

    def refresh(self):
        self.log.info("Refreshing page")
        self.driver.refresh()

    def get_title(self) -> str:
        return self.driver.title

    def get_current_url(self) -> str:
        return self.driver.current_url

    # ── Wait helpers ──────────────────────────────────────────────────────────

    def wait_for_visible(self, locator: tuple, timeout: int = None) -> WebElement:
        if timeout:
            return WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
        return self.smart_wait.visible(locator)

    def wait_for_clickable(self, locator: tuple, timeout: int = None) -> WebElement:
        if timeout:
            return WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(locator)
            )
        return self.smart_wait.clickable(locator)

    def wait_for_present(self, locator: tuple, timeout: int = None) -> WebElement:
        if timeout:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
        return self.smart_wait.present(locator)

    def wait_for_text(self, locator: tuple, text: str, timeout: int = None) -> WebElement:
        _wait = WebDriverWait(self.driver, timeout or UI.EXPLICIT_WAIT)
        return _wait.until(EC.text_to_be_present_in_element(locator, text))

    def wait_for_invisible(self, locator: tuple, timeout: int = None) -> bool:
        _wait = WebDriverWait(self.driver, timeout or UI.EXPLICIT_WAIT)
        return _wait.until(EC.invisibility_of_element_located(locator))

    def wait_for_url_contains(self, text: str, timeout: int = None):
        _wait = WebDriverWait(self.driver, timeout or UI.EXPLICIT_WAIT)
        _wait.until(EC.url_contains(text))

    # ── Element interactions ──────────────────────────────────────────────────

    @retry(exceptions=(StaleElementReferenceException, TimeoutException), tries=3, delay=0.5)
    def click(self, locator: tuple):
        from selenium.common.exceptions import ElementClickInterceptedException
        el = self.wait_for_clickable(locator)
        self.log.debug(f"Clicking {locator}")
        try:
            el.click()
        except ElementClickInterceptedException:
            self.log.warning(f"Click intercepted on {locator} — falling back to JS click")
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
            self.driver.execute_script("arguments[0].click();", el)

    @retry(exceptions=(StaleElementReferenceException,), tries=3, delay=0.5)
    def type_text(self, locator: tuple, text: str, clear: bool = True):
        el = self.wait_for_visible(locator)
        if clear:
            el.clear()
        self.log.debug(f"Typing '{text}' into {locator}")
        el.send_keys(text)

    def get_text(self, locator: tuple) -> str:
        return self.wait_for_visible(locator).text.strip()

    def get_attribute(self, locator: tuple, attr: str) -> str:
        return self.wait_for_visible(locator).get_attribute(attr)

    def is_visible(self, locator: tuple, timeout: int = 5) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(locator))
            return True
        except TimeoutException:
            return False

    def is_present(self, locator: tuple, timeout: int = 5) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located(locator))
            return True
        except TimeoutException:
            return False

    def find_elements(self, locator: tuple) -> list:
        return self.driver.find_elements(*locator)

    # ── JavaScript helpers ────────────────────────────────────────────────────

    def js_click(self, locator: tuple):
        el = self.wait_for_present(locator)
        self.log.debug(f"JS click on {locator}")
        self.driver.execute_script("arguments[0].click();", el)

    def js_scroll_to(self, locator: tuple):
        el = self.wait_for_present(locator)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", el)

    def js_get_text(self, locator: tuple) -> str:
        el = self.wait_for_present(locator)
        return self.driver.execute_script("return arguments[0].innerText;", el)

    def js_reload(self):
        self.log.info("JS window.location.reload()")
        self.driver.execute_script("window.location.reload();")

    # ── Allure + screenshot ───────────────────────────────────────────────────

    def take_screenshot(self, name: str = "step"):
        return capture(self.driver, name)
