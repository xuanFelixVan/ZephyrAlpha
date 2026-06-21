# [A_module] module_id=MOD-INF_identity_verifier | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md

# [MODULE] zephyr.infrastructure.a2a_protocol.layer1_discovery.identity_verifier

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] stable

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

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
