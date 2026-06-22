# [A_module] module_id=MOD-SEC_payloads | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
class Payload:
    def __init__(self, payload_type="", content="", metadata=None):
        self.payload_type = payload_type
        self.content = content
        self.metadata = metadata or {}


class MaliciousPayload(Payload):
    def __init__(self, payload_type="unknown", content="", threat_level="medium", detection_method=""):
        super().__init__(payload_type=payload_type, content=content)
        self.threat_level = threat_level
        self.detection_method = detection_method


def load_red_team_payloads(category=None):
    return []


__all__ = ["MaliciousPayload", "Payload", "load_red_team_payloads"]
