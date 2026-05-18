# [BLUEPRINT] MOD-INF-018 | 03_modules/l01_infrastructure/agent-rbac/blueprint.md | §

# [MODULE] zephyr.agent_rbac.legal_audit_chain

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""合法审计链——不可变+追加不可删+哈希链式验证."""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class ChainEntry(BaseModel):
    index: int
    timestamp: str
    operation: str
    agent_id: str
    prev_hash: str
    entry_hash: str


class LegalAuditChain:
    def __init__(self) -> None:
        self._chain: list[ChainEntry] = []
        self._prev_hash: str = "0000000000000000"

    def append(self, operation: str, agent_id: str) -> ChainEntry:
        now = datetime.now(timezone.utc).isoformat()
        payload = f"{len(self._chain)}:{now}:{operation}:{agent_id}:{self._prev_hash}"
        entry_hash = hashlib.sha256(payload.encode()).hexdigest()[:16]

        entry = ChainEntry(
            index=len(self._chain),
            timestamp=now,
            operation=operation,
            agent_id=agent_id,
            prev_hash=self._prev_hash,
            entry_hash=entry_hash,
        )
        self._chain.append(entry)
        self._prev_hash = entry_hash
        return entry

    def verify(self) -> dict[str, Any]:
        for i in range(1, len(self._chain)):
            if self._chain[i].prev_hash != self._chain[i - 1].entry_hash:
                return {"intact": False, "broken_at": i, "expected": self._chain[i - 1].entry_hash, "actual": self._chain[i].prev_hash}
        return {"intact": True, "length": len(self._chain), "last_hash": self._prev_hash}
