"""A2A 经济学——Token/API成本追踪"""

class A2AEconomics:
    def __init__(self):
        self._costs: dict = {}

    def track(self, task_id: str, tokens_in: int, tokens_out: int, model: str) -> dict:
        rates = {"deepseek": 0.000001, "claude": 0.000015}
        cost = (tokens_in + tokens_out) * rates.get(model, 0.000001)
        self._costs[task_id] = cost
        return {"task_id": task_id, "cost_usd": cost}
