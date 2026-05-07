import allure
from pathlib import Path
from datetime import datetime

from config.environment import Reporting
from utils.logger import get_logger

log = get_logger(__name__)


def capture(driver, name: str = "screenshot") -> str:
    """Take a screenshot, save to disk, and attach to Allure report."""
    scr_dir = Path(Reporting.SCREENSHOT_DIR)
    scr_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = scr_dir / f"{name}_{ts}.png"

    try:
        driver.save_screenshot(str(filename))
        log.info(f"Screenshot saved → {filename}")

        with open(filename, "rb") as img:
            allure.attach(
                img.read(),
                name=name,
                attachment_type=allure.attachment_type.PNG,
            )
    except Exception as e:
        log.error(f"Screenshot failed: {e}")

    return str(filename)
