"""
TC-E2E-01  UI → API: Create via UI, validate in API
TC-E2E-02  API → UI: Delete via API, confirm absent from UI
"""
import allure
import pytest
import time

from api.api_client import NotesAPIClient
from config.environment import API
from pages.notes_page import NotesPage


@allure.feature("FR-05: UI→API Sync | FR-07: API→UI Sync")
@allure.story("Hybrid E2E: UI + API")
class TestE2EHybrid:

    @allure.title("TC-E2E-01 | Create note via UI → validate in API response")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.e2e
    @pytest.mark.smoke
    def test_ui_create_note_visible_in_api(self, notes_page: NotesPage, api_client: NotesAPIClient):
        ts = int(time.time())
        title = f"E2E Note {ts}"
        description = f"E2E description {ts}"
        category = "Home"

        # ── Step 1: Create note via UI first (before any API cleanup) ──────────
        with allure.step("Step 1 — Create note via UI"):
            notes_page.create_note(title, description, category)

        with allure.step("Step 1a — Verify redirected to My Notes dashboard"):
            assert notes_page.wait_until_dashboard_visible(), \
                "User was not redirected back to My Notes dashboard"
            notes_page.open_all_tab()
            appeared = notes_page.wait_for_note_in_list(title)
            notes_page.take_screenshot("E2E-01-UI-success")
            assert appeared, \
                f"Note '{title}' not visible in All tab after creation"

        # ── Step 2: Confirm via API (retry loop) ───────────────────────────────
        with allure.step("Step 2 — Confirm note exists in API (with retry)"):
            api_note = None
            api_notes = []
            for attempt in range(8):
                notes_resp = api_client.get_notes()
                api_notes = notes_resp.get("data", [])
                # Log what API actually returns each attempt
                titles_in_api = [n.get("title") for n in api_notes]
                allure.attach(
                    f"Attempt {attempt+1}: {titles_in_api}",
                    name=f"API titles attempt {attempt+1}",
                    attachment_type=allure.attachment_type.TEXT,
                )
                api_note = next(
                    (n for n in api_notes if n.get("title", "").strip() == title.strip()),
                    None,
                )
                if api_note:
                    break
                time.sleep(3)

            assert api_note is not None, (
                f"Note '{title}' not found in API after 8 retries.\n"
                f"Last API titles: {[n.get('title') for n in api_notes]}\n"
                f"This likely means the UI and API are authenticated to different accounts.\n"
                f"Check that Credentials.EMAIL/PASSWORD in config.yaml match your UI login."
            )

        with allure.step("Step 2a — Assert GET /notes status 200"):
            assert notes_resp["_status_code"] == 200

        with allure.step("Step 2b — Assert response time < threshold"):
            assert notes_resp["_elapsed_ms"] < API.MAX_RESPONSE_MS, \
                f"API response {notes_resp['_elapsed_ms']:.0f}ms exceeds threshold"

        # ── Step 3: Verify note visible in UI list ─────────────────────────────
        with allure.step("Step 3 — Verify note visible in UI list"):
            appeared = notes_page.note_exists_on_page(title)
            notes_page.take_screenshot("E2E-01-UI-note-visible")
            assert appeared, f"Note '{title}' NOT visible in UI after creation"

        # ── Step 4: Compare fields ─────────────────────────────────────────────
        with allure.step("Step 4a — Compare Title: UI vs API"):
            assert api_note["title"] == title

        with allure.step("Step 4b — Compare Description: UI vs API"):
            assert api_note["description"] == description

        with allure.step("Step 4c — Compare Category: UI vs API"):
            assert api_note.get("category", "").lower() == category.lower()

        allure.attach(
            f"Title:       {api_note['title']}\n"
            f"Description: {api_note['description']}\n"
            f"Category:    {api_note.get('category')}\n"
            f"Note ID:     {api_note.get('id')}\n",
            name="UI → API Field Comparison",
            attachment_type=allure.attachment_type.TEXT,
        )

        # ── Cleanup ───────────────────────────────────────────────────────────
        with allure.step("Cleanup — delete test note via API"):
            api_client.delete_note(api_note["id"])

    @allure.title("TC-E2E-02 | Delete note via API → Confirm absent from UI")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.e2e
    @pytest.mark.smoke
    def test_api_delete_note_disappears_from_ui(
        self,
        notes_page: NotesPage,
        api_client: NotesAPIClient,
    ):
        ts = int(time.time())
        title = f"To Be Deleted {ts}"
        description = "Will be removed via API"

        with allure.step("Step 1 — Create note via API"):
            create_resp = api_client.create_note(title, description)
            assert create_resp["_status_code"] == 200, "Note creation via API failed"
            note_id = create_resp["data"]["id"]

        with allure.step("Step 2 — Reload UI and confirm note is visible"):
            notes_page.reload_and_wait()
            assert notes_page.is_note_visible_in_list(title), \
                f"Note '{title}' should be visible in UI before deletion"
            notes_page.take_screenshot("E2E-02-before-delete")

        with allure.step("Step 3 — DELETE via API"):
            del_resp = api_client.delete_note(note_id)
            assert del_resp["_status_code"] == 200
            assert del_resp.get("success") is True

        with allure.step("Step 4 — Confirm note absent in GET /notes"):
            notes_resp = api_client.get_notes()
            ids_in_api = [n["id"] for n in notes_resp.get("data", [])]
            assert note_id not in ids_in_api

        with allure.step("Step 5 — Reload UI and confirm note is gone"):
            notes_page.reload_and_wait()
            notes_page.take_screenshot("E2E-02-after-delete")
            assert notes_page.is_note_absent_from_list(title), \
                f"Deleted note '{title}' still visible in UI"

        with allure.step("Step 6 — Verify UI renders cleanly after deletion"):
            assert notes_page.is_visible(notes_page._ADD_NOTE_BTN), \
                "UI broken after deletion"
            notes_page.take_screenshot("E2E-02-UI-clean")