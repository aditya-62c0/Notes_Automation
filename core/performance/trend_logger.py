import json
from pathlib import Path
from datetime import datetime


class TrendLogger:

    def __init__(self, path="reports/performance_trends.jsonl"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, test_name, metric_name, value):
        record = {
            "timestamp": datetime.now().isoformat(),
            "test_name": test_name,
            "metric_name": metric_name,
            "value": value
        }

        with self.path.open("a") as file:
            file.write(json.dumps(record) + "\n")
