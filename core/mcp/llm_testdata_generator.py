from faker import Faker

from core.mcp.llm_client import MCPClient

fake = Faker()


class LLMTestDataGenerator:

    def __init__(self):
        self.client = MCPClient()

    def generate_note_data(self):
        llm_data = self.client.ask_json(
            system_prompt=(
                "You generate realistic Selenium test data for the ExpandTesting "
                "Notes app. Return only JSON."
            ),
            user_prompt=(
                "Generate one valid note object with keys: title, description, "
                "category. The category must be one of: Home, Work, Personal."
            ),
        )

        if llm_data:
            return {
                "title": llm_data.get("title", f"LLM Note {fake.unique.random_number(digits=5)}"),
                "description": llm_data.get("description", fake.sentence(nb_words=10)),
                "category": llm_data.get("category", "Home"),
            }

        return {
            "title": f"LLM Note {fake.unique.random_number(digits=5)}",
            "description": fake.sentence(nb_words=10),
            "category": fake.random_element(elements=["Home", "Work", "Personal"])
        }

    def generate_negative_note_data(self):
        llm_data = self.client.ask_json(
            system_prompt=(
                "You generate negative Selenium test data for the ExpandTesting "
                "Notes app. Return only JSON."
            ),
            user_prompt=(
                "Generate one invalid note object for missing-title validation "
                "with keys: title, description, category."
            ),
        )

        if llm_data:
            return {
                "title": "",
                "description": llm_data.get("description", fake.sentence(nb_words=6)),
                "category": llm_data.get("category", "Home"),
            }

        return {
            "title": "",
            "description": fake.sentence(nb_words=6),
            "category": "Home"
        }
