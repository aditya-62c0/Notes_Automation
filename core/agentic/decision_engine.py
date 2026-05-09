from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
    ElementClickInterceptedException,
    WebDriverException,
)


class DecisionEngine:

    RERUNNABLE_ERRORS = (
        TimeoutException,
        StaleElementReferenceException,
        ElementClickInterceptedException,
        WebDriverException,
    )

    NON_RERUNNABLE_KEYWORDS = [
        "AssertionError",
        "expected",
        "invalid credentials",
        "validation",
        "401",
        "404",
    ]

    def should_rerun(self, error: Exception) -> bool:
        error_text = str(error).lower()

        for keyword in self.NON_RERUNNABLE_KEYWORDS:
            if keyword.lower() in error_text:
                return False

        return isinstance(error, self.RERUNNABLE_ERRORS)

    def reason(self, error: Exception) -> str:
        if self.should_rerun(error):
            return f"Rerun allowed because this looks like flaky UI/infrastructure failure: {error}"
        return f"Rerun skipped because this looks like an application/assertion failure: {error}"
