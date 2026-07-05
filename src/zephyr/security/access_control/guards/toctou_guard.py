# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §3
# [MODULE] zephyr.security.access_control.guards.toctou_guard
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] tests/agent_rbac/test_redteam_adversarial.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] snapshot returns non-None for valid files; verify never raises; unchanged file returns (True, "ok")
# [MODIFY-GUARD] blueprint.md §3
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] snapshot() returns None on missing file; verify() returns (False, detail) on error, never raises
# [TESTS] tests/agent_rbac/test_redteam_adversarial.py
# [A_module] module_id=MOD-SEC_toctou_guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""TOCTOUGuard — TOCTOU (Time-of-Check to Time-of-Use) 防护.

依据蓝图 MOD-INF-018 §3:
- 对文件做快照（mtime, size, hash）
- 在使用前验证文件是否被修改
- 防止检查与使用之间的时间窗口被利用
"""

from __future__ import annotations

import hashlib
import logging
import os
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class FileSnapshot:
    """文件快照 — 记录文件在某一时刻的状态."""

    file_path: str
    mtime: float = 0.0
    size: int = 0
    file_hash: str = ""
    snapshot_time: float = 0.0


class FileIntegrityCheck:
    """文件完整性检查器 — 底层哈希计算工具."""

    @staticmethod
    def compute_hash(file_path: str) -> str:
        """计算文件 SHA256 哈希."""
        try:
            h = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    h.update(chunk)
            return h.hexdigest()
        except OSError as exc:
            logger.warning("FileIntegrityCheck hash failed for %s: %s", file_path, exc)
            return ""

    @staticmethod
    def get_stat(file_path: str) -> tuple[float, int] | None:
        """获取文件 mtime 和 size."""
        try:
            stat = os.stat(file_path)
            return (stat.st_mtime, stat.st_size)
        except OSError as exc:
            logger.warning("FileIntegrityCheck stat failed for %s: %s", file_path, exc)
            return None


class TOCTOUGuard:
    """TOCTOU 防护器 — 快照与验证.

    在"检查"时刻对文件做快照，在"使用"时刻验证文件是否被修改。
    """

    def __init__(self) -> None:
        self._snapshots: dict[str, FileSnapshot] = {}
        self._pre_state: dict[str, Any] = {}

    def snapshot(self, file_path: str) -> dict[str, Any] | None:
        """对文件做快照.

        Args:
            file_path: 文件路径

        Returns:
            包含 mtime/size/hash 的字典，文件不存在时返回 None
        """
        stat_info = FileIntegrityCheck.get_stat(file_path)
        if stat_info is None:
            return None
        mtime, size = stat_info
        file_hash = FileIntegrityCheck.compute_hash(file_path)
        snap = FileSnapshot(
            file_path=file_path,
            mtime=mtime,
            size=size,
            file_hash=file_hash,
        )
        self._snapshots[file_path] = snap
        logger.debug("TOCTOU snapshot taken: %s (size=%d, hash=%s...)", file_path, size, file_hash[:8])
        return {
            "file_path": file_path,
            "mtime": mtime,
            "size": size,
            "hash": file_hash,
        }

    def verify(self, file_path: str) -> tuple[bool, str]:
        """验证文件是否在快照后被修改.

        Args:
            file_path: 文件路径

        Returns:
            (ok, detail) — 文件未变返回 (True, "ok")，被修改返回 (False, "modified")
        """
        snap = self._snapshots.get(file_path)
        if snap is None:
            return (False, "no_snapshot")

        stat_info = FileIntegrityCheck.get_stat(file_path)
        if stat_info is None:
            return (False, "file_missing")

        mtime, size = stat_info

        if mtime != snap.mtime:
            return (False, "modified")
        if size != snap.size:
            return (False, "modified")

        current_hash = FileIntegrityCheck.compute_hash(file_path)
        if current_hash != snap.file_hash:
            return (False, "modified")

        return (True, "ok")

    def clear(self) -> None:
        """清除所有快照和预状态."""
        self._snapshots.clear()
        self._pre_state.clear()


__all__ = [
    "FileIntegrityCheck",
    "FileSnapshot",
    "TOCTOUGuard",
]
