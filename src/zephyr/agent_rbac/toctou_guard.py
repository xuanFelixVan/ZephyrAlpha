# [BLUEPRINT] MOD-INF-018 | 03_modules/l01_infrastructure/agent-rbac/blueprint.md | §

# [MODULE] zephyr.agent_rbac.toctou_guard

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
TOCTOU Guard — 检查时/使用时竞态防护

MOD-INF-018 §2.18  D-018-34

权限检查通过后操作执行前的窗口防护。
"""

import os
import time
import hashlib
from dataclasses import dataclass, field


@dataclass
class FileIntegrityCheck:
    path: str
    checksum: str
    size: int
    mtime: float
    checked_at: float = field(default_factory=time.time)


class TOCTOUGuard:
    def __init__(self, max_window_seconds: float = 5.0) -> None:
        self._pre_state: dict[str, FileIntegrityCheck] = {}
        self._max_window = max_window_seconds

    def snapshot(self, path: str) -> FileIntegrityCheck:
        try:
            st = os.stat(path)
            with open(path, "rb") as f:
                checksum = hashlib.sha256(f.read()).hexdigest()
        except (OSError, FileNotFoundError):
            checksum = "GONE"
            st = type("FakeStat", (), {"st_size": 0, "st_mtime": 0})()

        check = FileIntegrityCheck(
            path=path,
            checksum=checksum,
            size=st.st_size,
            mtime=st.st_mtime,
        )
        self._pre_state[path] = check
        return check

    def verify(self, path: str) -> tuple[bool, str]:
        pre = self._pre_state.get(path)
        if pre is None:
            return False, "No pre-state snapshot"

        if time.time() - pre.checked_at > self._max_window:
            return False, f"TOCTOU window expired ({self._max_window}s)"

        try:
            st = os.stat(path)
            with open(path, "rb") as f:
                post_checksum = hashlib.sha256(f.read()).hexdigest()
        except (OSError, FileNotFoundError):
            return False, "File disappeared between check and use"

        if post_checksum != pre.checksum:
            return False, f"File content changed (TOCTOU detected)"
        return True, "OK"

    def clear(self) -> None:
        self._pre_state.clear()
