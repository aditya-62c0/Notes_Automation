class UIPerformance:

    def collect_navigation_timing(self, driver):
        timing = driver.execute_script("""
            const nav = performance.getEntriesByType('navigation')[0];
            return {
                loadTime: nav.loadEventEnd - nav.startTime,
                domContentLoaded: nav.domContentLoadedEventEnd - nav.startTime,
                responseTime: nav.responseEnd - nav.requestStart
            };
        """)
        return timing
