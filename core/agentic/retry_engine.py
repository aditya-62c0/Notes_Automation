import time
import functools
from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
    ElementClickInterceptedException,
    NoSuchElementException,
)
from utils.logger import get_logger

log = get_logger(__name__)


FLAKY_UI_EXCEPTIONS = (
    TimeoutException,
    StaleElementReferenceException,
    ElementClickInterceptedException,
    NoSuchElementException,
)


def auto_retry(max_attempts=3, delay=1):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None

            for attempt in range(1, max_attempts + 1):
                try:
                    log.info(f"Running step: {func.__name__}, attempt {attempt}")
                    return func(*args, **kwargs)
                except FLAKY_UI_EXCEPTIONS as error:
                    last_error = error
                    log.warning(
                        f"Step failed: {func.__name__}, attempt {attempt}/{max_attempts}, error={error}"
                    )
                    time.sleep(delay)

            raise last_error

        return wrapper

    return decorator
