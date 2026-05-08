"""向量化信誉系统"""

class A2AVectorReputation:
    def __init__(self):
        self._scores: dict = {}

    def rate(self, agent_id: str, dimension: str, score: float) -> None:
        self._scores.setdefault(agent_id, {})
        self._scores[agent_id][dimension] = score

    def reputation(self, agent_id: str) -> dict:
        return self._scores.get(agent_id, {})
