"""P2: Agent同意管理"""

class A2AConsent:
    def __init__(self):
        self._consents: dict = {}

    def grant(self, agent_id: str, scope: str, granted_by: str) -> dict:
        self._consents.setdefault(agent_id, {})
        self._consents[agent_id][scope] = {"granted": True, "by": granted_by}
        return {"agent": agent_id, "scope": scope, "consent": True}

    def revoke(self, agent_id: str, scope: str) -> dict:
        if agent_id in self._consents:
            self._consents[agent_id].pop(scope, None)
        return {"agent": agent_id, "scope": scope, "revoked": True}
