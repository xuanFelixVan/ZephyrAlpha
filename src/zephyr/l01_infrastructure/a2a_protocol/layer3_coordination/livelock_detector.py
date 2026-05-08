"""P2: 活锁检测器"""

class LivelockDetector:
    def __init__(self, cycle_limit: int = 10):
        self._state_history: dict = {}
        self.cycle_limit = cycle_limit

    def check_cycle(self, agent_id: str, state_hash: str) -> bool:
        history = self._state_history.setdefault(agent_id, [])
        count = history.count(state_hash)
        return count >= self.cycle_limit

    def record_state(self, agent_id: str, state_hash: str) -> None:
        self._state_history.setdefault(agent_id, []).append(state_hash)
