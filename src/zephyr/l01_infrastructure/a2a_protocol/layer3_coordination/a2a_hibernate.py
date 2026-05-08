"""P2: Agent休眠管理"""

class A2AHibernate:
    def __init__(self):
        self._sleeping: set = set()

    def sleep(self, agent_id: str, reason: str) -> dict:
        self._sleeping.add(agent_id)
        return {"agent": agent_id, "status": "sleeping", "reason": reason}

    def wake(self, agent_id: str) -> dict:
        self._sleeping.discard(agent_id)
        return {"agent": agent_id, "status": "awake"}

    def is_sleeping(self, agent_id: str) -> bool:
        return agent_id in self._sleeping
