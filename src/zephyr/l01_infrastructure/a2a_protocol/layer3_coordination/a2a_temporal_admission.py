"""时序准入控制"""

class A2ATemporalAdmission:
    def __init__(self, max_concurrent: int = 10):
        self.max_concurrent = max_concurrent
        self._active: set = set()

    def admit(self, agent_id: str) -> bool:
        return len(self._active) < self.max_concurrent

    def enter(self, agent_id: str) -> None:
        self._active.add(agent_id)

    def leave(self, agent_id: str) -> None:
        self._active.discard(agent_id)
