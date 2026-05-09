from selenium.common.exceptions import NoSuchElementException
from utils.logger import get_logger

log = get_logger(__name__)


class SelfHealingDriver:

    def __init__(self, driver):
        self.driver = driver

    def find(self, primary_locator, fallback_locators=None):
        fallback_locators = fallback_locators or []
        locators = [primary_locator] + fallback_locators

        for locator in locators:
            try:
                element = self.driver.find_element(*locator)
                log.info(f"Locator worked: {locator}")
                return element
            except NoSuchElementException:
                log.warning(f"Locator failed: {locator}")

        raise NoSuchElementException(
            f"All locators failed. Tried: {locators}"
        )
