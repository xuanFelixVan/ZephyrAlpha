"""P2: 宪法性Agent管理"""

class A2AConstitutional:
    VETOABLE = ["delete", "drop_table", "mass_update", "rm_rf", "shutdown"]

    def __init__(self):
        self._articles: dict = {}

    def can_veto(self, action: str) -> bool:
        return action in self.VETOABLE

    def veto(self, action: str, reason: str) -> dict:
        return {"action": action, "vetoed": self.can_veto(action), "reason": reason}
