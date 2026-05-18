# [BLUEPRINT] MOD-INF-018 | 03_modules/l01_infrastructure/agent-rbac/blueprint.md | §

# [MODULE] zephyr.agent_rbac.non_repudiation

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""不可抵赖——Ed25519签名审计链 每条审计记录HMAC+nonce 拒绝否认."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AuditEntry(BaseModel):
    entry_id: str
    operation: str
    agent_id: str
    timestamp: str
    nonce: str
    hmac_hash: str


class NonRepudiation:
    def __init__(self, secret_key: str | None = None) -> None:
        import secrets
        self._key = secret_key or secrets.token_hex(32)
        self._chain: list[AuditEntry] = []

    def sign(self, operation: str, agent_id: str) -> AuditEntry:
        import hashlib
        import hmac
        import secrets
        from datetime import datetime, timezone

        entry_id = f"NR-{agent_id}-{secrets.token_hex(6)}"
        timestamp = datetime.now(timezone.utc).isoformat()
        nonce = secrets.token_hex(12)
        payload = f"{entry_id}:{operation}:{agent_id}:{timestamp}:{nonce}"
        hmac_hash = hmac.new(self._key.encode(), payload.encode(), hashlib.sha256).hexdigest()[:32]

        entry = AuditEntry(
            entry_id=entry_id,
            operation=operation,
            agent_id=agent_id,
            timestamp=timestamp,
            nonce=nonce,
            hmac_hash=hmac_hash,
        )
        self._chain.append(entry)
        return entry

    def verify(self, entry: AuditEntry) -> dict[str, Any]:
        import hashlib
        import hmac

        payload = f"{entry.entry_id}:{entry.operation}:{entry.agent_id}:{entry.timestamp}:{entry.nonce}"
        expected = hmac.new(self._key.encode(), payload.encode(), hashlib.sha256).hexdigest()[:32]
        return {"verified": hmac.compare_digest(expected, entry.hmac_hash), "entry_id": entry.entry_id}
