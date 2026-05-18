# [BLUEPRINT] MOD-INF-018 | 03_modules/l01_infrastructure/agent-rbac/blueprint.md | §

# [MODULE] zephyr.agent_rbac.emergency_override

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""紧急覆盖令牌——Owner JIT临时越权(<5分钟/一次性/可吊销/CLI)."""
from __future__ import annotations

import hashlib
import secrets
import time
from typing import Any

from pydantic import BaseModel, Field


class EmergencyToken(BaseModel):
    token_id: str = Field(default_factory=lambda: f"EMG-{secrets.token_hex(8)}")
    issued_by: str
    issued_at: float = Field(default_factory=time.time)
    expires_at: float = 0.0
    permissions: list[str] = Field(default_factory=list)
    max_duration_seconds: int = 300
    used: bool = False
    revoked: bool = False
    token_hash: str = ""


class EmergencyOverride:
    def __init__(self) -> None:
        self._active_tokens: dict[str, EmergencyToken] = {}

    def issue(self, issued_by: str, permissions: list[str], duration_seconds: int = 300) -> EmergencyToken:
        token = EmergencyToken(
            issued_by=issued_by,
            permissions=permissions,
            max_duration_seconds=min(duration_seconds, 300),
        )
        token.expires_at = token.issued_at + token.max_duration_seconds
        token.token_hash = hashlib.sha256(f"{token.token_id}:{token.issued_by}:{token.issued_at}".encode()).hexdigest()[:16]
        self._active_tokens[token.token_id] = token
        return token

    def verify(self, token_id: str) -> dict[str, Any]:
        token = self._active_tokens.get(token_id)
        if not token:
            return {"valid": False, "reason": "token_not_found"}
        if token.revoked:
            return {"valid": False, "reason": "token_revoked"}
        if token.used:
            return {"valid": False, "reason": "token_already_used"}
        if time.time() > token.expires_at:
            return {"valid": False, "reason": "token_expired", "expired_at": token.expires_at}

        token.used = True
        return {"valid": True, "token_id": token_id, "permissions": token.permissions, "issued_by": token.issued_by}

    def revoke(self, token_id: str) -> dict[str, Any]:
        token = self._active_tokens.get(token_id)
        if not token:
            return {"revoked": False, "reason": "token_not_found"}
        token.revoked = True
        return {"revoked": True, "token_id": token_id}
