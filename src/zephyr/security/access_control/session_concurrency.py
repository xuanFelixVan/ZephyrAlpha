# [BLUEPRINT] MOD-SECURITY
# [MODULE] zephyr.security.access_control.session_concurrency
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] tests.test_session_concurrency; zephyr.gov_enforcement.rule_bridge.git_commit_gateway; zephyr.gov_enforcement.rule_bridge.session_worktree (find_breaking_change_session)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] SessionRegistry 原子写入（tmp + os.replace）；session TTL=3600s 自动过期；不替代 lock_files.py（文件级锁）；claim_file 懒注册+不覆盖冲突+幂等；release_file 移除 held_files；get_session 只读无写副作用；is_breaking_change 字段标记治本变更 session（§9.7 治本 2026-07-04）；find_breaking_change_session 查找活跃 breaking_change session（只读，排除自身+忽略过期，供 session_worktree_start 双向阻断调用）
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SessionRegistry 读写失败不抛异常（返回空/False）；detect_mtime_conflict 文件不存在返回 False
# [TESTS] tests/test_session_concurrency.py
# [TTL] permanent
"""Session 级并发协调模块（P2-SES 落地）。

从 Stub 落地为真实的 session 级协调：
1. SessionRegistry：注册活跃 session（PID + session_id + start_time + 持有文件锁）
   - 存储在 .runtime/session_registry.json（原子写入，对标 lock_files.py）
   - TTL=3600s（session 超时自动注销）
2. SessionHandoff：session 结束时写 handoff package
   - 对标 drift_detector/blueprint.md §6.14 Cross-Session HandoffPackage
3. SessionConflictDetector：检测多 session 操作同一文件 -> 走 lock_files.py 协调

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
import threading
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
    ConflictType.SAME_FILE: "两session改同一文件->后写入覆盖",
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
        return "auto_merge" if conflict_type is ConflictType.SAME_FILE else "owner_decision"


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


def _normalize_file_path(file_path: str, project_root: Path | None = None) -> str:
    """归一化为绝对路径字符串（与 gateway 的 str(Path(f).resolve()) 对齐）。

    claim/release/find 内部统一用此 helper，避免相对路径与绝对路径不匹配。
    Path.resolve() 默认 strict=False，对不存在路径也能解析（支持 deletion commit 场景）。
    """
    p = Path(file_path)
    if not p.is_absolute() and project_root is not None:
        p = project_root / p
    return str(p.resolve())


@dataclass
class SessionInfo:
    """活跃 session 注册信息。"""

    session_id: str
    pid: int
    start_time: float
    held_files: list[str] = field(default_factory=list)
    last_heartbeat: float = 0.0
    is_breaking_change: bool = False

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "pid": self.pid,
            "start_time": self.start_time,
            "held_files": self.held_files,
            "last_heartbeat": self.last_heartbeat,
            "is_breaking_change": self.is_breaking_change,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "SessionInfo":
        return cls(
            session_id=d.get("session_id", ""),
            pid=d.get("pid", 0),
            start_time=d.get("start_time", 0.0),
            # 5.147.9 修复: JSON 中 held_files 为 null 时 d.get 返回 None 而非默认 [], 后续 .append() 会 AttributeError
            held_files=d.get("held_files") or [],
            last_heartbeat=d.get("last_heartbeat", 0.0),
            is_breaking_change=d.get("is_breaking_change", False),
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
        # 进程内读写锁：串行化 _load->修改->_save 的 read-modify-write 序列，
        # 消除 claim_file/release_file 等的 TOCTOU 竞态（两线程并发 claim 同一文件
        # 都读到"无人持有"->都写回->双 claim）。跨进程并发由 gateway 全局锁 + 原子
        # os.replace 兜底；此处只解决进程内多线程竞态（红蓝对抗 TestConcurrentClaimRace）。
        self._lock = threading.RLock()

    def register(
        self,
        session_id: str,
        pid: int | None = None,
        held_files: list[str] | None = None,
        is_breaking_change: bool = False,
    ) -> SessionInfo:
        """注册一个活跃 session。"""
        with self._lock:
            info = SessionInfo(
                session_id=session_id,
                pid=pid if pid is not None else os.getpid(),
                start_time=time.time(),
                held_files=held_files or [],
                last_heartbeat=time.time(),
                is_breaking_change=is_breaking_change,
            )
            data = self._load()
            data[session_id] = info.to_dict()
            self._save(data)
            logger.info(
                "SessionRegistry: registered session=%s pid=%d breaking_change=%s",
                session_id, info.pid, is_breaking_change,
            )
            return info

    def find_breaking_change_session(self, exclude_session_id: str = "") -> SessionInfo | None:
        """查找是否有活跃 session 声明了 breaking_change（治本变更并发阻断，§9.7 治本 2026-07-04）。

        - 排除 exclude_session_id 自身
        - 过期 session 忽略（不查不删，只读）
        - 返回第一个匹配的 SessionInfo，无则 None

        供 session_worktree_start 双向阻断逻辑调用：
        - breaking_change=True 的新 session 启动时：检查是否有任何其他活跃 session
        - breaking_change=False 的新 session 启动时：检查是否有其他活跃 session 声明了 breaking_change
        """
        data = self._load()
        now = time.time()
        for sid, d in data.items():
            if sid == exclude_session_id:
                continue
            info = SessionInfo.from_dict(d)
            if now - info.last_heartbeat > _SESSION_TTL_SECONDS:
                continue  # 过期 session，忽略
            if info.is_breaking_change:
                return info
        return None

    def unregister(self, session_id: str) -> bool:
        """注销一个 session。"""
        with self._lock:
            data = self._load()
            if session_id not in data:
                return False
            del data[session_id]
            self._save(data)
            logger.info("SessionRegistry: unregistered session=%s", session_id)
            return True

    def heartbeat(self, session_id: str) -> bool:
        """更新 session 心跳时间（防 TTL 过期）。"""
        with self._lock:
            data = self._load()
            if session_id not in data:
                return False
            data[session_id]["last_heartbeat"] = time.time()
            self._save(data)
            return True

    def list_active(self) -> list[SessionInfo]:
        """列出所有活跃 session（自动清理过期）。"""
        with self._lock:
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
        norm = _normalize_file_path(file_path, self._project_root)
        for info in self.list_active():
            held_norm = [_normalize_file_path(f, self._project_root) for f in info.held_files]
            if norm in held_norm:
                return info
        return None

    def get_session(self, session_id: str) -> SessionInfo | None:
        """只读查询某 session 信息（不做过期清理，不回写文件）。

        过期 session 返回 None（但不删除——删除是 list_active 的职责）。
        供 GitCommitGateway 等只读消费者使用，避免 list_active 的写副作用。
        """
        data = self._load()
        if session_id not in data:
            return None
        info = SessionInfo.from_dict(data[session_id])
        if time.time() - info.last_heartbeat > _SESSION_TTL_SECONDS:
            return None  # 过期，视为不存在（不删除）
        return info

    def other_held_files(self, session_id: str) -> set[str]:
        """返回其他活跃 session 持有的文件（归一化绝对路径集合），只读无写副作用。

        用于 session 隔离 stash 的强不变量：commit 时始终排除其他 session 持有的文件，
        即使本 session 未注册（未 claim）。过期 session 的持有被忽略。
        供 GitCommitGateway._get_session_held_non_target 调用。
        """
        data = self._load()
        now = time.time()
        held: set[str] = set()
        for sid, d in data.items():
            if sid == session_id:
                continue
            info = SessionInfo.from_dict(d)
            if now - info.last_heartbeat > _SESSION_TTL_SECONDS:
                continue  # 过期 session，忽略其持有
            for f in info.held_files:
                held.add(_normalize_file_path(f, self._project_root))
        return held

    def claim_file(self, session_id: str, file_path: str) -> bool:
        """为 session 声明持有某文件（动态 claim）。

        - session 未注册/过期 -> 懒注册（held_files=[]），记 warning
        - 文件被其他活跃 session 持有 -> 返回 False（冲突，调用方走 lock_files.py）
        - 文件已被自己持有 -> 幂等返回 True
        - 文件无人持有 -> 加入 held_files，顺带 heartbeat，原子写回，返回 True

        Returns: True=claim 成功（含幂等），False=被其他 session 持有。
        """
        with self._lock:
            norm = _normalize_file_path(file_path, self._project_root)
            data = self._load()
            now = time.time()

            # 懒注册：session 不存在或过期
            existing = data.get(session_id)
            if existing is None or now - SessionInfo.from_dict(existing).last_heartbeat > _SESSION_TTL_SECONDS:
                logger.warning(
                    "SessionRegistry: claim_file auto-registering session=%s (not registered or expired)",
                    session_id,
                )
                data[session_id] = SessionInfo(
                    session_id=session_id, pid=os.getpid(), start_time=now,
                    held_files=[], last_heartbeat=now,
                ).to_dict()
                self._save(data)  # 立即持久化懒注册（即使后续 claim 冲突，session 仍可查询）

            # 检查是否被其他活跃 session 持有
            for sid, d in data.items():
                if sid == session_id:
                    continue
                other = SessionInfo.from_dict(d)
                if now - other.last_heartbeat > _SESSION_TTL_SECONDS:
                    continue  # 过期 session，忽略其 claim
                other_held_norm = [_normalize_file_path(f, self._project_root) for f in other.held_files]
                if norm in other_held_norm:
                    logger.warning(
                        "SessionRegistry: claim_file conflict — file=%s held by session=%s, requested by=%s",
                        norm, sid, session_id,
                    )
                    return False

            # 幂等 / 新增
            own = SessionInfo.from_dict(data[session_id])
            own.last_heartbeat = now  # claim 顺带心跳
            own_norm = [_normalize_file_path(f, self._project_root) for f in own.held_files]
            if norm not in own_norm:
                own.held_files.append(norm)
            data[session_id] = own.to_dict()
            self._save(data)
            return True

    def release_file(self, session_id: str, file_path: str) -> bool:
        """释放 session 对某文件的持有。

        Returns: True=成功释放，False=session 未注册 或 文件未被持有。
        """
        with self._lock:
            norm = _normalize_file_path(file_path, self._project_root)
            data = self._load()
            if session_id not in data:
                return False
            info = SessionInfo.from_dict(data[session_id])
            held_norm = [_normalize_file_path(f, self._project_root) for f in info.held_files]
            if norm not in held_norm:
                return False
            # 移除归一化匹配到的原始条目
            for orig in list(info.held_files):
                if _normalize_file_path(orig, self._project_root) == norm:
                    info.held_files.remove(orig)
            data[session_id] = info.to_dict()
            self._save(data)
            return True

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

    def read_latest_handoff(self) -> dict | None:
        """读最近的 handoff package（按 mtime，不需 session_id）。

        供 session_startup 读取上一 session 交接——跨 session 上下文恢复。
        无 handoff 文件时返回 None（首次运行）。
        """
        try:
            candidates = sorted(
                self._handoff_dir.glob("handoff_*.json"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
        except OSError:
            return None
        if not candidates:
            return None
        try:
            return json.loads(candidates[0].read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None


class SessionConflictDetector:
    """检测多 session 操作同一文件（P2-SES）。

    基于 SessionRegistry + ConcurrencyManager 检测跨 session 文件冲突。
    检测到冲突 -> 返回 ConflictType，由调用方走 lock_files.py 协调。
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
        """为 session 预分配文件（冲突文件不会被分配，成功分配的写回 registry）。

        Returns:
            成功分配的文件列表（冲突文件被跳过）。
        """
        allocated: list[str] = []
        for fp in file_paths:
            conflict = self.check_file_conflict(fp, session_id)
            if conflict is None:
                # 写回 registry，使 claim 持久化（修复：原版只读不写回）
                if self._registry.claim_file(session_id, fp):
                    allocated.append(fp)
        return allocated
