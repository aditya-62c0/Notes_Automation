import time
import functools
from typing import Callable, Type, Tuple

from utils.logger import get_logger

log = get_logger(__name__)


def retry(
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    tries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
):
    """Decorator: retry a function on specified exceptions with exponential backoff."""

    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            _delay = delay
            for attempt in range(1, tries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == tries:
                        log.error(f"[retry] '{func.__name__}' failed after {tries} attempts → {e}")
                        raise
                    log.warning(
                        f"[retry] '{func.__name__}' attempt {attempt}/{tries} failed: {e}. "
                        f"Retrying in {_delay:.1f}s…"
                    )
                    time.sleep(_delay)
                    _delay *= backoff

        return wrapper

    return decorator
