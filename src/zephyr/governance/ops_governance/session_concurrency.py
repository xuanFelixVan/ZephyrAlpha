# [A_module] module_id=MOD-GOV_session_concurrency | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-063 | docs/03_modules/_domain-governance/blueprint.md | §

# [MODULE] zephyr.governance.session_concurrency

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


class LockLevel(str, Enum):
    EXCLUSIVE = "EXCLUSIVE"


class ConflictType(str, Enum):
    SAME_FILE = "two_sessions_same_file"
    IMPORT_DEP = "import_dependency_change"
    REFACTOR_SIG = "refactor_signature_mismatch"
    BLUEPRINT_DRIFT = "blueprint_vs_construction"


CONFLICT_SCENARIOS: dict[ConflictType, str] = {
    ConflictType.SAME_FILE: "两session改同一文件→后写入覆盖",
    ConflictType.IMPORT_DEP: "session-A改imports session-B移除依赖",
    ConflictType.REFACTOR_SIG: "重构函数签名vs旧签名调用",
    ConflictType.BLUEPRINT_DRIFT: "改蓝图vs按旧蓝图施工",
}

LOCK_TTL_SECONDS: int = 1800


@dataclass
class ZephyrLock:
    file_path: str
    session_id: str = ""
    acquired: bool = False

    def acquire(self) -> bool:
        self.acquired = True
        return True

    def release(self) -> bool:
        self.acquired = False
        return True

    @property
    def is_active(self) -> bool:
        return self.acquired


@dataclass
class ConcurrencyManager:
    active_locks: dict[str, ZephyrLock] = field(default_factory=dict)

    def check_conflict(self, path: str, session_id: str) -> Optional[ConflictType]:
        lock = self.active_locks.get(path)
        if lock and lock.is_active:
            return ConflictType.SAME_FILE
        return None

    def pre_allocate(self, paths: list[str], session_id: str) -> list[str]:
        allocated: list[str] = []
        for p in paths:
            if p not in self.active_locks or not self.active_locks[p].is_active:
                lock = ZephyrLock(file_path=p, session_id=session_id, acquired=True)
                self.active_locks[p] = lock
                allocated.append(p)
        return allocated

    def resolve_conflict(
        self,
        conflict_type: ConflictType,
        paths: tuple[str, str],
    ) -> str:
        return "auto_merge" if conflict_type == ConflictType.SAME_FILE else "owner_decision"


def detect_mtime_conflict(path: str, last_read_mtime: float) -> bool:
    try:
        current_mtime = os.path.getmtime(path)
        return current_mtime > last_read_mtime
    except OSError:
        return False
