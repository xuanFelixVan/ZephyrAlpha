"""Identity Verifier — JWT 身份验证器"""

import hashlib
import hmac
from typing import Dict, Optional


class IdentityVerifier:
    """A2A 身份验证器"""

    def __init__(self, shared_secret: Optional[bytes] = None):
        self._secret = shared_secret or b"zephyr-alpha-a2a-secret"

    def sign(self, agent_id: str, payload: Dict) -> str:
        message = f"{agent_id}:{payload}".encode("utf-8")
        return hmac.new(self._secret, message, hashlib.sha256).hexdigest()

    def verify(self, agent_id: str, payload: Dict, signature: str) -> bool:
        expected = self.sign(agent_id, payload)
        return hmac.compare_digest(expected, signature)

    def generate_challenge(self) -> str:
        import secrets
        return secrets.token_hex(32)
