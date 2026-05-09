class APIPerformance:

    def assert_response_time(self, response, max_ms):
        elapsed = response.get("_elapsed_ms", 0)
        assert elapsed < max_ms, f"API response time {elapsed:.0f}ms exceeded {max_ms}ms"
        return elapsed
