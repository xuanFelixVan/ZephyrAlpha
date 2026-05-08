"""横向越权防护——SessionToken HMAC-SHA256签名+跨Session伪造检测."""
from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class SessionToken(BaseModel):
    agent_id: str
    session_id: str
    nonce: str = Field(default_factory=lambda: secrets.token_hex(16))
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    signature: str = ""


class CrossSessionDetector:
    def __init__(self, secret_key: str | None = None) -> None:
        self._secret = secret_key or secrets.token_hex(32)
        self._active_sessions: dict[str, SessionToken] = {}
        self._violations: list[dict[str, Any]] = []

    def sign_token(self, agent_id: str, session_id: str) -> SessionToken:
        token = SessionToken(agent_id=agent_id, session_id=session_id)
        payload = f"{agent_id}:{session_id}:{token.nonce}:{token.timestamp}"
        token.signature = hmac.new(self._secret.encode(), payload.encode(), hashlib.sha256).hexdigest()[:32]
        self._active_sessions[session_id] = token
        return token

    def verify_token(self, agent_id: str, session_id: str, nonce: str, timestamp: str, signature: str) -> dict[str, Any]:
        active = self._active_sessions.get(session_id)
        if active and active.agent_id != agent_id:
            self._violations.append({"type": "CROSS_SESSION_FORGERY", "agent_id": agent_id, "original_agent": active.agent_id, "session_id": session_id})
            return {"valid": False, "reason": "cross_session_forgery"}

        payload = f"{agent_id}:{session_id}:{nonce}:{timestamp}"
        expected = hmac.new(self._secret.encode(), payload.encode(), hashlib.sha256).hexdigest()[:32]
        valid = hmac.compare_digest(expected, signature)
        if not valid:
            return {"valid": False, "reason": "signature_mismatch"}
        return {"valid": True, "agent_id": agent_id, "session_id": session_id}
