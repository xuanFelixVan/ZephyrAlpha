# [BLUEPRINT] (migrated from MOD-INF-021 by ARCH-039 P1, target domain=D_INFRA_RUNTIME)
# [MODULE] zephyr.infrastructure.runtime.concurrency_guard
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.runtime.__init__
# [CONSUMERS] RollbackExecutor._execute; RollbackExecutor.discard_changes
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 只读扫描 .ailocks/；不修改锁状态；BLOCKED 时返回冲突不执行回滚
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ConcurrencyConflictError on blocked; ConflictResult/StashPlan on check
# [TESTS] tests/rollback/test_concurrency_guard.py
# [TTL] permanent

"""
concurrency_guard — 回滚操作并发安全守卫。

检测回滚操作是否会破坏其他 AI session 的工作：
1. 扫描 .ailocks/ 活跃文件锁 → 回滚文件与被锁文件有交集 → BLOCKED
2. 未提交文件归属识别 → 通过 .ailocks 锁信息识别 owner → 非 owner 的未提交文件 → BLOCKED
3. git stash 安全化 → 只允许 stash 本 session 的文件，其他 session 文件阻断

根因：回滚系统与文件锁系统(RULE-ZERO .ailocks/)是两套独立机制未联动。
本模块作为桥梁，在回滚执行前检测并发冲突，防止 session B 回滚覆盖 session A 的工作。
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path

__all__ = [
    "ConcurrencyConflictError",
    "ConflictResult",
    "LockInfo",
    "StashPlan",
    "build_stash_plan",
    "check_rollback_conflict",
    "classify_uncommitted_files",
    "scan_active_locks",
]

DEFAULT_LOCK_DIR = ".ailocks"
DEFAULT_TTL_S = 1800.0  # 30 分钟，与 lock_files.py 一致


@dataclass
class LockInfo:
    """单个文件锁信息。"""

    file_path: str
    owner_id: str
    task: str
    timestamp: float
    pid: int


@dataclass
class ConflictResult:
    """回滚并发冲突检测结果。"""

    has_conflict: bool
    blocked_files: list[str] = field(default_factory=list)
    locked_by: dict[str, str] = field(default_factory=dict)
    reason: str = ""


@dataclass
class StashPlan:
    """git stash 安全计划。"""

    should_stash: bool
    own_files: list[str] = field(default_factory=list)
    other_files: list[str] = field(default_factory=list)
    other_owners: dict[str, str] = field(default_factory=dict)


class ConcurrencyConflictError(Exception):
    """回滚操作因并发冲突被阻断。"""

    def __init__(self, blocked_files: list[str], locked_by: dict[str, str], reason: str = ""):
        self.blocked_files = blocked_files
        self.locked_by = locked_by
        details = []
        for f in blocked_files:
            owner = locked_by.get(f, "unknown")
            details.append(f"  {f} (locked by {owner})")
        msg = "回滚被阻断——检测到其他 session 持有文件锁:\n" + "\n".join(details)
        if reason:
            msg += f"\n原因: {reason}"
        super().__init__(msg)


def _lock_root(project_root: Path) -> Path:
    return project_root / DEFAULT_LOCK_DIR


def _is_stale(timestamp: float, ttl: float = DEFAULT_TTL_S) -> bool:
    return (time.time() - timestamp) > ttl


def _normalize(path: str) -> str:
    return str(path).replace("\\", "/")


def scan_active_locks(project_root: Path) -> list[LockInfo]:
    """扫描 .ailocks/registry.json，返回所有活跃（非过期）文件锁。

    只读操作，不修改锁状态。与 lock_files.py 的 _load_registry 对齐。
    """
    lock_root = _lock_root(project_root)
    registry_path = lock_root / "registry.json"
    if not registry_path.is_file():
        return []
    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []

    locks: list[LockInfo] = []
    for file_path, info in registry.get("locks", {}).items():
        ts = info.get("timestamp", 0.0)
        if _is_stale(ts):
            continue
        locks.append(
            LockInfo(
                file_path=file_path,
                owner_id=info.get("owner_id", "unknown"),
                task=info.get("task", ""),
                timestamp=ts,
                pid=info.get("pid", 0),
            )
        )
    return locks


def check_rollback_conflict(
    files_in_scope: list[str],
    current_session_id: str,
    project_root: Path,
) -> ConflictResult:
    """检测回滚文件范围是否与活跃文件锁冲突。

    冲突 = 回滚范围内的文件被其他 session 锁定。
    本 session 自己的锁不算冲突（允许回滚自己锁的文件）。
    """
    active_locks = scan_active_locks(project_root)
    lock_map: dict[str, LockInfo] = {_normalize(l.file_path): l for l in active_locks}

    blocked: list[str] = []
    locked_by: dict[str, str] = {}

    for f in files_in_scope:
        norm_f = _normalize(f)
        lock = lock_map.get(norm_f)
        if lock is None:
            continue
        if lock.owner_id == current_session_id:
            continue
        blocked.append(f)
        locked_by[f] = lock.owner_id

    return ConflictResult(
        has_conflict=bool(blocked),
        blocked_files=blocked,
        locked_by=locked_by,
        reason="文件被其他 session 锁定" if blocked else "",
    )


def classify_uncommitted_files(
    uncommitted_files: list[str],
    current_session_id: str,
    project_root: Path,
) -> StashPlan:
    """将未提交文件按归属分类：本 session 的 vs 其他 session 的。

    归属判定：
    - 文件被 .ailocks 锁定且 owner != current_session_id → other_files（不可 stash）
    - 其余 → own_files（可 stash）

    局限：未被锁定的未提交文件默认归为本 session，因为 .ailocks 只记录"正在写入"的锁，
    不记录"已写入未提交"的状态。这是已知局限——完整解决需要 git log author + 锁联合判定。
    本模块已覆盖最危险场景（正在写入的文件被回滚覆盖）。
    """
    active_locks = scan_active_locks(project_root)
    lock_map: dict[str, LockInfo] = {_normalize(l.file_path): l for l in active_locks}

    own: list[str] = []
    other: list[str] = []
    other_owners: dict[str, str] = {}

    for f in uncommitted_files:
        norm_f = _normalize(f)
        lock = lock_map.get(norm_f)
        if lock is not None and lock.owner_id != current_session_id:
            other.append(f)
            other_owners[f] = lock.owner_id
        else:
            own.append(f)

    return StashPlan(
        should_stash=bool(own),
        own_files=own,
        other_files=other,
        other_owners=other_owners,
    )


def build_stash_plan(
    uncommitted_files: list[str],
    current_session_id: str,
    project_root: Path,
) -> StashPlan:
    """构建 git stash 安全计划（classify_uncommitted_files 的语义别名）。"""
    return classify_uncommitted_files(uncommitted_files, current_session_id, project_root)
