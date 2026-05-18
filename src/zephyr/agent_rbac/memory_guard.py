# [BLUEPRINT] MOD-INF-018 | 03_modules/l01_infrastructure/agent-rbac/blueprint.md | §

# [MODULE] zephyr.agent_rbac.memory_guard

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""内存守卫——防止Agent通过内存操纵(RCE/buffer overflow/use-after-free)清理/篡改权限状态."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class MemoryAccessLog(BaseModel):
    access_id: str
    agent_id: str
    operation: str
    address_range: str = ""
    size_bytes: int = 0
    timestamp: str = Field(default_factory=lambda: __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat())


class MemoryGuard:
    _MAX_ACCESS_SIZE: int = 1048576

    def __init__(self) -> None:
        self._access_log: list[MemoryAccessLog] = []
        self._blocked: int = 0

    def check_access(self, agent_id: str, operation: str, size_bytes: int, address_range: str = "") -> dict[str, Any]:
        import secrets
        from datetime import datetime, timezone

        if size_bytes > self._MAX_ACCESS_SIZE:
            self._blocked += 1
            return {"allowed": False, "reason": "access_size_exceeded", "size_bytes": size_bytes, "limit": self._MAX_ACCESS_SIZE}

        if operation in ("munmap", "mprotect", "mremap", "brk", "sbrk"):
            self._blocked += 1
            return {"allowed": False, "reason": "privileged_memory_operation", "operation": operation}

        log = MemoryAccessLog(
            access_id=f"MEM-{agent_id}-{secrets.token_hex(4)}",
            agent_id=agent_id,
            operation=operation,
            address_range=address_range,
            size_bytes=size_bytes,
        )
        self._access_log.append(log)
        return {"allowed": True, "access_id": log.access_id}

    def stats(self) -> dict[str, Any]:
        return {"total_accesses": len(self._access_log), "blocked": self._blocked}
