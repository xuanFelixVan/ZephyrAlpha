# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer1_discovery.identity_verifier
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_identity_verifier | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Identity Verifier — JWT 身份验证器"""

import hashlib
import hmac


class IdentityVerifier:
    """A2A 身份验证器"""

    def __init__(self, shared_secret: bytes | None = None):
        self._secret = shared_secret or b"zephyr-alpha-a2a-secret"

    # 5.110.9 修复: 显式 __repr__ 排除 _secret, 防止调试/日志泄露
    def __repr__(self) -> str:
        return f"IdentityVerifier(secret_configured={self._secret is not None})"

    def sign(self, agent_id: str, payload: dict) -> str:
        message = f"{agent_id}:{payload}".encode()
        return hmac.new(self._secret, message, hashlib.sha256).hexdigest()

    def verify(self, agent_id: str, payload: dict, signature: str) -> bool:
        expected = self.sign(agent_id, payload)
        return hmac.compare_digest(expected, signature)

    def generate_challenge(self) -> str:
        import secrets

        return secrets.token_hex(32)
