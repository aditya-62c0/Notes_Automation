from selenium.webdriver.common.by import By

from core.mcp.llm_client import MCPClient


class LocatorSuggester:

    BY_MAP = {
        "id": By.ID,
        "name": By.NAME,
        "css": By.CSS_SELECTOR,
        "css_selector": By.CSS_SELECTOR,
        "xpath": By.XPATH,
        "tag_name": By.TAG_NAME,
        "class_name": By.CLASS_NAME,
        "link_text": By.LINK_TEXT,
        "partial_link_text": By.PARTIAL_LINK_TEXT,
    }

    def __init__(self):
        self.client = MCPClient()

    def suggest_for_notes_app(self, element_name):
        llm_suggestions = self.client.ask_json(
            system_prompt=(
                "You suggest stable Selenium locators for the ExpandTesting "
                "Notes app. Return only JSON."
            ),
            user_prompt=(
                f"Suggest fallback Selenium locators for element '{element_name}'. "
                "Return JSON like: {\"locators\": [{\"by\": \"css\", "
                "\"value\": \"selector\"}]}. Prefer data-testid, id, name, "
                "and stable XPath with normalize-space."
            ),
        )

        converted = self._convert_llm_locators(llm_suggestions)
        if converted:
            return converted

        suggestions = {
            "add_note_button": [
                (By.CSS_SELECTOR, "button[data-testid='add-new-note']"),
                (By.XPATH, "//button[contains(normalize-space(), 'Add Note')]"),
                (By.CSS_SELECTOR, "button.btn-primary")
            ],
            "note_title": [
                (By.ID, "title"),
                (By.NAME, "title"),
                (By.CSS_SELECTOR, "input[placeholder*='title' i]")
            ],
            "save_button": [
                (By.CSS_SELECTOR, "button[data-testid='note-submit']"),
                (By.XPATH, "//button[contains(normalize-space(), 'Create')]"),
                (By.XPATH, "//button[contains(normalize-space(), 'Save')]")
            ]
        }

        return suggestions.get(element_name, [])

    def _convert_llm_locators(self, llm_suggestions):
        if not llm_suggestions:
            return []

        converted = []
        for item in llm_suggestions.get("locators", []):
            by = self.BY_MAP.get(str(item.get("by", "")).lower())
            value = item.get("value")
            if by and value:
                converted.append((by, value))

        return converted
