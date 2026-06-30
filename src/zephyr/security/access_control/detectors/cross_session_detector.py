# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_rbac/blueprint.md | §3
# [MODULE] zephyr.security.access_control.detectors.cross_session_detector
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] tests/agent_rbac/test_redteam_adversarial.py; tests/test_cross_session_detector.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] sign_token returns SignedToken with non-None signature; verify_token returns {"valid": bool, "reason"/"agent_id": ...}; agent_id mismatch on known session -> valid=False reason="cross_session_forgery"
# [MODIFY-GUARD] blueprint.md §3
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] sign_token/verify_token never raise; verify_token returns {"valid": False, "reason": ...} on invalid input
# [TESTS] tests/agent_rbac/test_redteam_adversarial.py; tests/test_cross_session_detector.py
# [A_module] module_id=MOD-SEC_cross_session_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""CrossSessionDetector — 跨 Session 检测器.

依据蓝图 MOD-INF-018 §3:
- 对 agent session token 进行 HMAC-SHA256 签名
- 检测跨 session 身份盗用（agent_id 与签名时不一致）
- 记录违规事件以供审计
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone

_DEFAULT_SECRET = "zephyr-cross-session-default-secret"


@dataclass
class SessionToken:
    """Session token（legacy，字符串时间戳）."""

    agent_id: str
    session_id: str
    nonce: str = field(default_factory=lambda: secrets.token_hex(8))
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    signature: str = ""


@dataclass
class SignedToken:
    """签名 token（float 时间戳）."""

    agent_id: str
    session_id: str
    nonce: str
    timestamp: float
    signature: str


class CrossSessionDetector:
    """跨 session 检测器."""

    def __init__(self, secret_key: str | None = None) -> None:
        self._secret: str = secret_key or _DEFAULT_SECRET
        self._active_sessions: dict[str, SignedToken] = {}
        self._violations: list[dict] = []

    def _compute_signature(
        self,
        agent_id: str,
        session_id: str,
        nonce: str,
        timestamp,
    ) -> str:
        payload = f"{agent_id}:{session_id}:{nonce}:{timestamp}".encode("utf-8")
        return hmac.new(
            self._secret.encode("utf-8"),
            payload,
            hashlib.sha256,
        ).hexdigest()[:32]

    def sign_token(self, agent_id: str, session_id: str) -> SignedToken:
        """签名 token，返回 SignedToken 并登记到 active_sessions."""
        nonce = secrets.token_hex(8)
        timestamp = time.time()
        signature = self._compute_signature(
            agent_id, session_id, nonce, timestamp
        )
        token = SignedToken(
            agent_id=agent_id,
            session_id=session_id,
            nonce=nonce,
            timestamp=timestamp,
            signature=signature,
        )
        self._active_sessions[session_id] = token
        return token

    def verify_token(
        self,
        agent_id: str,
        session_id: str,
        nonce: str,
        timestamp,
        signature: str,
    ) -> dict:
        """验证 token.

        返回 {"valid": bool, "reason"/"agent_id": ...}。
        - agent_id 与签名时不一致 -> valid=False, reason="cross_session_forgery"
        - 签名不匹配 -> valid=False, reason="signature_mismatch"
        - 通过 -> valid=True, agent_id=...
        """
        if session_id in self._active_sessions:
            stored = self._active_sessions[session_id]
            if stored.agent_id != agent_id:
                self._violations.append(
                    {
                        "type": "CROSS_SESSION_FORGERY",
                        "agent_id": agent_id,
                        "session_id": session_id,
                        "expected_agent_id": stored.agent_id,
                    }
                )
                return {"valid": False, "reason": "cross_session_forgery"}
        expected = self._compute_signature(
            agent_id, session_id, nonce, timestamp
        )
        if not hmac.compare_digest(expected, signature):
            return {"valid": False, "reason": "signature_mismatch"}
        return {"valid": True, "agent_id": agent_id}


__all__ = [
    "CrossSessionDetector",
    "SessionToken",
    "SignedToken",
]
