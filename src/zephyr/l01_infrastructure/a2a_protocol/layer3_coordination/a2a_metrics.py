"""A2A 指标收集"""

class A2AMetrics:
    def __init__(self):
        self._metrics: dict = {}

    def record(self, name: str, value: float, tags: dict = None) -> None:
        self._metrics[name] = {"value": value, "tags": tags or {}}

    def get(self, name: str) -> dict:
        return self._metrics.get(name, {})
