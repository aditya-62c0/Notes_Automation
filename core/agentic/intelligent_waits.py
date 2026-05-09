from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class IntelligentWait:

    def __init__(self, driver, timeout=15):
        self.driver = driver
        self.timeout = timeout

    def visible(self, locator):
        return WebDriverWait(self.driver, self.timeout).until(
            EC.visibility_of_element_located(locator)
        )

    def clickable(self, locator):
        return WebDriverWait(self.driver, self.timeout).until(
            EC.element_to_be_clickable(locator)
        )

    def present(self, locator):
        return WebDriverWait(self.driver, self.timeout).until(
            EC.presence_of_element_located(locator)
        )

    def page_ready(self):
        return WebDriverWait(self.driver, self.timeout).until(
            lambda d: d.execute_script("return document.readyState") in ["interactive", "complete"]
        )

    def url_contains(self, text):
        return WebDriverWait(self.driver, self.timeout).until(
            EC.url_contains(text)
        )

    def angular_or_react_idle(self):
        return WebDriverWait(self.driver, self.timeout).until(
            lambda d: d.execute_script(
                "return document.readyState === 'complete'"
            )
        )
