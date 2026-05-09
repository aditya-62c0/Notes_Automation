import pytest
import allure

from core.mcp.llm_testdata_generator import LLMTestDataGenerator
from core.performance.ui_performance import UIPerformance
from core.performance.trend_logger import TrendLogger


@allure.feature("Agentic + MCP + Performance")
@pytest.mark.smoke
def test_agentic_mcp_note_creation(notes_page):
    data = LLMTestDataGenerator().generate_note_data()

    notes_page.create_note(
        data["title"],
        data["description"],
        data["category"]
    )

    assert notes_page.is_success_banner_visible()
    assert notes_page.is_note_visible_in_list(data["title"])


@allure.feature("UI Performance")
def test_ui_navigation_timing(notes_page):
    timing = UIPerformance().collect_navigation_timing(notes_page.driver)

    TrendLogger().log(
        "test_ui_navigation_timing",
        "dom_content_loaded_ms",
        timing["domContentLoaded"]
    )

    assert timing["domContentLoaded"] < 5000
