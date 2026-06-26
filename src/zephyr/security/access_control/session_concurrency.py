# [BLUEPRINT] MOD-SECURITY
# [MODULE] zephyr.security.access_control.session_concurrency
# [DOMAIN] D-SECURITY
# [DEPENDENCIES]
# [CONSUMERS] tests.test_session_concurrency
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] SessionRegistry 原子写入（tmp + os.replace）；session TTL=3600s 自动过期；不替代 lock_files.py（文件级锁）
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SessionRegistry 读写失败不抛异常（返回空/False）；detect_mtime_conflict 文件不存在返回 False
# [TESTS] tests/test_session_concurrency.py
"""Session 级并发协调模块（P2-SES 落地）。

从 Stub 落地为真实的 session 级协调：
1. SessionRegistry：注册活跃 session（PID + session_id + start_time + 持有文件锁）
   - 存储在 .runtime/session_registry.json（原子写入，对标 lock_files.py）
   - TTL=3600s（session 超时自动注销）
2. SessionHandoff：session 结束时写 handoff package
   - 对标 drift_detector/blueprint.md §6.14 Cross-Session HandoffPackage
3. SessionConflictDetector：检测多 session 操作同一文件 → 走 lock_files.py 协调

设计约束：
- 不替代 lock_files.py（文件级锁），而是在其上增加 session 级注册
- 不替代 F23 AgentOrchestrator（任务级），而是补齐 session 级空缺
- 存储用 JSON 文件（非 SQLite，避免并发写锁）
"""

from __future__ import annotations

__all__ = [
    "CONFLICT_SCENARIOS",
    "LOCK_TTL_SECONDS",
    "ConcurrencyManager",
    "ConflictType",
    "LockLevel",
    "SessionConflictDetector",
    "SessionHandoff",
    "SessionInfo",
    "SessionRegistry",
    "ZephyrLock",
    "detect_mtime_conflict",
]

import json
import logging
import os
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

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

    def check_conflict(self, path: str, session_id: str) -> ConflictType | None:
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


# ---------------------------------------------------------------------------
# P2-SES: Session 级协调（SessionRegistry + SessionHandoff + ConflictDetector）
# ---------------------------------------------------------------------------

_SESSION_TTL_SECONDS: int = 3600  # session 超时自动注销（1 小时）
_REGISTRY_PATH: str = ".runtime/session_registry.json"
_HANDOFF_DIR: str = ".runtime/handoffs"


@dataclass
class SessionInfo:
    """活跃 session 注册信息。"""

    session_id: str
    pid: int
    start_time: float
    held_files: list[str] = field(default_factory=list)
    last_heartbeat: float = 0.0

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "pid": self.pid,
            "start_time": self.start_time,
            "held_files": self.held_files,
            "last_heartbeat": self.last_heartbeat,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "SessionInfo":
        return cls(
            session_id=d.get("session_id", ""),
            pid=d.get("pid", 0),
            start_time=d.get("start_time", 0.0),
            held_files=d.get("held_files", []),
            last_heartbeat=d.get("last_heartbeat", 0.0),
        )


class SessionRegistry:
    """Session 级注册表（P2-SES）。

    存储在 .runtime/session_registry.json（原子写入：tmp + os.replace）。
    TTL=3600s（session 超时自动注销）。

    不替代 lock_files.py（文件级锁），而是在其上增加 session 级注册。
    不替代 F23 AgentOrchestrator（任务级），补齐 session 级空缺。
    """

    def __init__(self, project_root: str | Path | None = None) -> None:
        self._project_root: Path = Path(project_root) if project_root else Path.cwd()
        self._registry_path: Path = self._project_root / _REGISTRY_PATH
        self._registry_path.parent.mkdir(parents=True, exist_ok=True)

    def register(
        self,
        session_id: str,
        pid: int | None = None,
        held_files: list[str] | None = None,
    ) -> SessionInfo:
        """注册一个活跃 session。"""
        info = SessionInfo(
            session_id=session_id,
            pid=pid if pid is not None else os.getpid(),
            start_time=time.time(),
            held_files=held_files or [],
            last_heartbeat=time.time(),
        )
        data = self._load()
        data[session_id] = info.to_dict()
        self._save(data)
        logger.info("SessionRegistry: registered session=%s pid=%d", session_id, info.pid)
        return info

    def unregister(self, session_id: str) -> bool:
        """注销一个 session。"""
        data = self._load()
        if session_id not in data:
            return False
        del data[session_id]
        self._save(data)
        logger.info("SessionRegistry: unregistered session=%s", session_id)
        return True

    def heartbeat(self, session_id: str) -> bool:
        """更新 session 心跳时间（防 TTL 过期）。"""
        data = self._load()
        if session_id not in data:
            return False
        data[session_id]["last_heartbeat"] = time.time()
        self._save(data)
        return True

    def list_active(self) -> list[SessionInfo]:
        """列出所有活跃 session（自动清理过期）。"""
        data = self._load()
        now = time.time()
        active: list[SessionInfo] = []
        expired: list[str] = []
        for sid, d in data.items():
            info = SessionInfo.from_dict(d)
            if now - info.last_heartbeat > _SESSION_TTL_SECONDS:
                expired.append(sid)
            else:
                active.append(info)
        # 清理过期 session
        if expired:
            for sid in expired:
                del data[sid]
            self._save(data)
            logger.info("SessionRegistry: cleaned %d expired sessions", len(expired))
        return active

    def find_session_by_file(self, file_path: str) -> SessionInfo | None:
        """查找持有某文件的 session（用于冲突检测）。"""
        for info in self.list_active():
            if file_path in info.held_files:
                return info
        return None

    def _load(self) -> dict[str, dict]:
        """原子读取 registry（文件不存在/损坏返回空 dict）。"""
        try:
            if not self._registry_path.exists():
                return {}
            content = self._registry_path.read_text(encoding="utf-8")
            return json.loads(content) if content.strip() else {}
        except (OSError, ValueError) as e:
            logger.warning("SessionRegistry: failed to load registry: %s", e)
            return {}

    def _save(self, data: dict[str, dict]) -> None:
        """原子写入 registry（tmp + os.replace，防并发写损坏）。"""
        tmp_path = self._registry_path.with_suffix(".tmp")
        try:
            tmp_path.write_text(
                json.dumps(data, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            os.replace(str(tmp_path), str(self._registry_path))
        except OSError as e:
            logger.warning("SessionRegistry: failed to save registry: %s", e)


class SessionHandoff:
    """Session 结束时写 handoff package（P2-SES）。

    对标 drift_detector/blueprint.md §6.14 Cross-Session HandoffPackage。
    存储 .runtime/handoffs/handoff_<session_id>.json。
    """

    def __init__(self, project_root: str | Path | None = None) -> None:
        self._project_root: Path = Path(project_root) if project_root else Path.cwd()
        self._handoff_dir: Path = self._project_root / _HANDOFF_DIR
        self._handoff_dir.mkdir(parents=True, exist_ok=True)

    def write_handoff(
        self,
        session_id: str,
        summary: str,
        pending_tasks: list[str] | None = None,
        warnings: list[str] | None = None,
    ) -> Path:
        """写 handoff package，返回文件路径。"""
        package = {
            "session_id": session_id,
            "timestamp": time.time(),
            "summary": summary,
            "pending_tasks": pending_tasks or [],
            "warnings": warnings or [],
        }
        handoff_path = self._handoff_dir / f"handoff_{session_id}.json"
        tmp_path = handoff_path.with_suffix(".tmp")
        try:
            tmp_path.write_text(
                json.dumps(package, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            os.replace(str(tmp_path), str(handoff_path))
            logger.info("SessionHandoff: wrote handoff for session=%s", session_id)
        except OSError as e:
            logger.warning("SessionHandoff: failed to write handoff: %s", e)
        return handoff_path

    def read_handoff(self, session_id: str) -> dict | None:
        """读 handoff package（不存在返回 None）。"""
        handoff_path = self._handoff_dir / f"handoff_{session_id}.json"
        try:
            return json.loads(handoff_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None


class SessionConflictDetector:
    """检测多 session 操作同一文件（P2-SES）。

    基于 SessionRegistry + ConcurrencyManager 检测跨 session 文件冲突。
    检测到冲突 → 返回 ConflictType，由调用方走 lock_files.py 协调。
    """

    def __init__(self, registry: SessionRegistry) -> None:
        self._registry = registry
        self._manager = ConcurrencyManager()

    def check_file_conflict(
        self, file_path: str, session_id: str
    ) -> ConflictType | None:
        """检测文件是否被其他 session 持有。

        Returns:
            ConflictType.SAME_FILE if 另一 session 持有该文件, None if 无冲突。
        """
        holder = self._registry.find_session_by_file(file_path)
        if holder is not None and holder.session_id != session_id:
            logger.warning(
                "SessionConflictDetector: file %s held by session=%s, "
                "requested by session=%s",
                file_path, holder.session_id, session_id,
            )
            return ConflictType.SAME_FILE
        return None

    def acquire_files(
        self, file_paths: list[str], session_id: str
    ) -> list[str]:
        """为 session 预分配文件（冲突文件不会被分配）。

        Returns:
            成功分配的文件列表（冲突文件被跳过）。
        """
        allocated: list[str] = []
        for fp in file_paths:
            conflict = self.check_file_conflict(fp, session_id)
            if conflict is None:
                allocated.append(fp)
        return allocated
