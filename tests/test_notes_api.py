"""
TC-API-01  GET /notes returns list with valid auth token
TC-API-02  GET /notes validates response time < 2s
TC-API-03  Delete note via API DELETE /notes/{id}
TC-API-04  Delete non-existent note via API → 404
TC-NEG-03  GET /notes without auth token → 401
TC-NEG-04  POST /notes with invalid payload → 400
TC-NEG-05  GET /notes with expired/invalid token → 401
"""
import allure
import pytest
import time

from api.api_client import NotesAPIClient
from config.environment import API


@allure.feature("FR-04: API GET /notes | FR-06: Delete via API | FR-08: Response Time | FR-09: Negative API")
@allure.story("Notes API Automation")
class TestNotesAPI:

    @allure.title("TC-API-01 | GET /notes returns 200 with note list")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.api
    def test_get_notes_returns_list(self, api_client: NotesAPIClient):

        with allure.step("Send GET /notes with valid token"):
            resp = api_client.get_notes()

        with allure.step("Assert status 200"):
            assert resp["_status_code"] == 200, \
                f"Expected 200, got {resp['_status_code']}"

        with allure.step("Assert response contains 'data' list"):
            assert "data" in resp, "Response should have 'data' key"
            assert isinstance(resp["data"], list), "data should be a list"

        with allure.step("Assert success flag"):
            assert resp.get("success") is True, "API 'success' field should be True"

    @allure.title("TC-API-02 | GET /notes response time < 2000ms")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    def test_get_notes_response_time(self, api_client: NotesAPIClient):

        with allure.step("Send GET /notes and record elapsed time"):
            resp = api_client.get_notes()
            elapsed = resp["_elapsed_ms"]

        with allure.step(f"Assert elapsed {elapsed:.0f}ms < {API.MAX_RESPONSE_MS}ms"):
            allure.attach(
                f"Response time: {elapsed:.0f} ms\nThreshold: {API.MAX_RESPONSE_MS} ms",
                name="Response Time",
                attachment_type=allure.attachment_type.TEXT,
            )
            assert elapsed < API.MAX_RESPONSE_MS, \
                f"Response took {elapsed:.0f}ms — exceeds {API.MAX_RESPONSE_MS}ms threshold"

    @allure.title("TC-API-03 | DELETE /notes/{id} removes a note")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.api
    def test_delete_note_valid(self, api_client: NotesAPIClient):
        ts = int(time.time())

        with allure.step("Create a note via API to delete"):
            create_resp = api_client.create_note(
                title=f"To Delete {ts}",
                description="This note will be deleted",
            )
            assert create_resp["_status_code"] == 200, "Note creation should succeed"
            note_id = create_resp["data"]["id"]

        with allure.step(f"DELETE /notes/{note_id}"):
            del_resp = api_client.delete_note(note_id)

        with allure.step("Assert status 200 and success message"):
            assert del_resp["_status_code"] == 200, \
                f"Expected 200, got {del_resp['_status_code']}"
            assert del_resp.get("success") is True

        with allure.step("Confirm note no longer in GET /notes"):
            notes_resp = api_client.get_notes()
            ids = [n["id"] for n in notes_resp.get("data", [])]
            assert note_id not in ids, f"Deleted note {note_id} still returned by GET /notes"

    @allure.title("TC-API-04 | DELETE non-existent note → 404")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    @pytest.mark.negative
    def test_delete_nonexistent_note(self, api_client: NotesAPIClient):

        with allure.step("DELETE /notes with fake ID"):
            resp = api_client.delete_note("000000000000000000000000")

        with allure.step("Assert status 400 or 404"):
            assert resp["_status_code"] in (400, 404), \
                f"Expected 400/404 for non-existent note, got {resp['_status_code']}"

    @allure.title("TC-NEG-03 | GET /notes without auth token → 401")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.negative
    @pytest.mark.api
    def test_get_notes_no_token(self, anon_api_client: NotesAPIClient):

        with allure.step("Send GET /notes with NO token"):
            resp = anon_api_client.get_notes()

        with allure.step("Assert status 401 Unauthorized"):
            assert resp["_status_code"] == 401, \
                f"Expected 401, got {resp['_status_code']}"

    @allure.title("TC-NEG-04 | POST /notes with empty payload → 400")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.negative
    @pytest.mark.api
    def test_post_note_invalid_payload(self, api_client: NotesAPIClient):

        with allure.step("POST /notes with empty body"):
            resp = api_client._post("/notes", {})

        with allure.step("Assert status 400"):
            assert resp["_status_code"] == 400, \
                f"Expected 400 for empty payload, got {resp['_status_code']}"

    @allure.title("TC-NEG-05 | GET /notes with invalid/expired token → 401")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.negative
    @pytest.mark.api
    def test_get_notes_invalid_token(self):
        bad_client = NotesAPIClient(token="invalid_token_xyz_12345")

        with allure.step("Send GET /notes with bad token"):
            resp = bad_client.get_notes()

        with allure.step("Assert status 401"):
            assert resp["_status_code"] == 401, \
                f"Expected 401 for invalid token, got {resp['_status_code']}"
