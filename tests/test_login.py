"""
TC-UI-01  Login with valid credentials
TC-UI-02  Login with invalid password
TC-UI-03  Login with empty credentials
TC-NEG-01 UI login with empty email
"""
import allure
import pytest

from config.environment import Credentials, UI
from pages.login_page import LoginPage


@allure.feature("FR-01: UI Login")
@allure.story("User Authentication")
class TestLogin:

    @allure.title("TC-UI-01 | Login with valid credentials")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_login_valid(self, driver):
        login = LoginPage(driver)

        with allure.step("Open login page"):
            login.open_login()

        with allure.step("Enter valid credentials and submit"):
            login.login_valid(Credentials.EMAIL, Credentials.PASSWORD)

        with allure.step("Verify redirect to dashboard"):
            assert "notes/app" in driver.current_url, (
                f"Expected dashboard URL, got: {driver.current_url}"
            )
            login.take_screenshot("TC-UI-01-PASS")

    @allure.title("TC-UI-02 | Login with invalid password")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.negative
    def test_login_invalid_password(self, driver):
        login = LoginPage(driver)

        with allure.step("Open login page"):
            login.open_login()

        with allure.step("Enter valid email with wrong password"):
            login.login(Credentials.EMAIL, "WrongPassword@999")

        with allure.step("Verify error message is displayed"):
            assert login.is_login_error_shown(), "Error message should be displayed for invalid password"
            err = login.get_error_message()
            assert err != "", f"Error text should not be empty, got: '{err}'"
            login.take_screenshot("TC-UI-02-PASS")

        with allure.step("Verify user stays on login page"):
            assert "login" in driver.current_url.lower() or "notes/app" not in driver.current_url, \
                "User should NOT be redirected on invalid login"

    @allure.title("TC-UI-03 | Login with empty email and password")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_login_empty_credentials(self, driver):
        login = LoginPage(driver)

        with allure.step("Open login page"):
            login.open_login()

        with allure.step("Click login without entering any credentials"):
            login.click(login._LOGIN_BTN)

        with allure.step("Verify form validation prevents submission"):
            # Either field-level HTML5 validation or app-level error
            still_on_login = (
                "login" in driver.current_url.lower()
                or "notes/app" not in driver.current_url
            )
            assert still_on_login, "User should remain on login page when credentials are empty"
            login.take_screenshot("TC-UI-03-PASS")

    @allure.title("TC-NEG-01 | Login with empty email field only")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_login_empty_email(self, driver):
        login = LoginPage(driver)

        with allure.step("Open login page"):
            login.open_login()

        with allure.step("Enter password only, leave email blank"):
            login.type_text(login._PASSWORD, Credentials.PASSWORD)
            login.click(login._LOGIN_BTN)

        with allure.step("Verify user is not logged in"):
            assert "notes/app" not in driver.current_url or "login" in driver.current_url.lower(), \
                "Should NOT log in with empty email"
            login.take_screenshot("TC-NEG-01-PASS")
