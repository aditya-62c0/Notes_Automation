from time import time

import allure
from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from config.environment import UI


class LoginPage(BasePage):

    # Locators
    _EMAIL = (By.ID, "email")
    _PASSWORD = (By.ID, "password")
    _LOGIN_BTN = (By.CSS_SELECTOR, "button[type='submit']")
    _ERROR_MSG = (By.CSS_SELECTOR, ".alert-danger, [data-testid='alert-message']")
    _EMAIL_ERROR = (By.CSS_SELECTOR, "#email + .invalid-feedback, [data-testid='email-validation']")
    _PASSWORD_ERROR = (By.CSS_SELECTOR, "#password + .invalid-feedback, [data-testid='password-validation']")

    @allure.step("Open login page")
    def open_login(self):
        self.open(UI.LOGIN_URL)
        self.wait_for_visible(self._EMAIL)
        self.log.info("Login page loaded")

    @allure.step("Login with email={email}")
    def login(self, email: str, password: str):
        self.type_text(self._EMAIL, email)
        self.type_text(self._PASSWORD, password)
        # Submit the form instead of clicking the button
        form = self.driver.find_element(By.TAG_NAME, "form")
        form.submit()
        self.log.info(f"Login attempted for {email}")

    @allure.step("Login with valid credentials")
    def login_valid(self, email: str, password: str):
        self.login(email, password)

        try:
            # Wait until we leave login page
            self.wait.until(lambda d: "/login" not in d.current_url)
            self.log.info(f"Redirected to: {self.get_current_url()}")
        except:
            self.log.error(f"Login failed, current URL: {self.get_current_url()}")
            error = self.get_error_message()
            if error:
                raise ValueError(f"Login failed: {error}")
            else:
                raise

        # Wait for correct page
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.by import By

        self.wait.until(lambda d: "/notes/app" in d.current_url)
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        import time
        time.sleep(2)

    def get_error_message(self) -> str:
        if self.is_visible(self._ERROR_MSG):
            return self.get_text(self._ERROR_MSG)
        return ""

    def get_email_validation_error(self) -> str:
        if self.is_visible(self._EMAIL_ERROR):
            return self.get_text(self._EMAIL_ERROR)
        return ""

    def get_password_validation_error(self) -> str:
        if self.is_visible(self._PASSWORD_ERROR):
            return self.get_text(self._PASSWORD_ERROR)
        return ""

    def is_login_error_shown(self) -> bool:
        return self.is_visible(self._ERROR_MSG)
