# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §3
# [MODULE] zephyr.infrastructure.auto_fix_engine.fix_reliability
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__
# [CONSUMERS] engine.py;batch_fixer.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] IdempotencyGuard 24h TTL;DeadLetterQueue max 3 retries;ConflictResolver串行化同文件修复
# [MODIFY-GUARD] blueprint.md §3;auto_fix_config.yaml reliability段
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ConflictResolutionError;IdempotencyViolationError
# [TESTS] tests/auto-fix-engine/test_fix_reliability.py
# [A_module] module_id=MOD-INF_fix_reliability | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import logging
import os
import sqlite3
from zephyr.shared.io.sqlite_factory import get_db_connection
import threading
import time
from collections import defaultdict
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from zephyr.infrastructure.auto_fix_engine.models import (
    FixAction,
    FixDeadLetter,
    FixLevel,
)
from zephyr.shared.io.paths import DB_PATH

logger = logging.getLogger(__name__)

_DB_PATH = DB_PATH


class IdempotencyGuard:
    def __init__(self, db_path: str | None = None, ttl_hours: int = 24) -> None:
        self._db_path = db_path or str(_DB_PATH)
        self._ttl = timedelta(hours=ttl_hours)
        self._lock = threading.Lock()
        self._cache: dict[str, tuple[str, float]] = {}
        self._ensure_db()

    def _ensure_db(self) -> None:
        os.makedirs(os.path.dirname(self._db_path), exist_ok=True)
        conn = get_db_connection(self._db_path)
        try:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS fix_idempotency "
                "(fingerprint TEXT PRIMARY KEY, action_type TEXT, target TEXT, "
                "result_status TEXT, created_at TEXT, expires_at TEXT)"
            )
            conn.commit()
        # 5.49.2 修复：异常路径确保连接归还
        finally:
            conn.close()

    def check(self, action: FixAction) -> tuple[bool, str]:
        fp = action.fingerprint
        now = time.time()
        if fp in self._cache:
            status, ts = self._cache[fp]
            if now - ts < self._ttl.total_seconds():
                return False, f"Duplicate fix: {fp} already processed as {status}"
        conn = None
        try:
            conn = get_db_connection(self._db_path)
            row = conn.execute(
                "SELECT result_status, expires_at FROM fix_idempotency WHERE fingerprint=?",
                (fp,),
            ).fetchone()
            if row:
                expires = datetime.fromisoformat(row[1])
                if datetime.now(UTC) < expires:
                    return False, f"Duplicate fix: {fp} already processed as {row[0]}"
        except Exception as e:
            logger.warning("suppressed error in fix_reliability", exc_info=True)
        # 5.49.2 修复：异常路径确保连接归还
        finally:
            if conn is not None:
                conn.close()
        return True, ""

    def record(self, action: FixAction, status: str) -> None:
        fp = action.fingerprint
        now = time.time()
        self._cache[fp] = (status, now)
        conn = None
        try:
            expires = (datetime.now(UTC) + self._ttl).isoformat()
            conn = get_db_connection(self._db_path)
            conn.execute(
                "INSERT OR REPLACE INTO fix_idempotency (fingerprint, action_type, target, result_status, created_at, expires_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (fp, action.action_type, action.target, status, datetime.now(UTC).isoformat(), expires),
            )
            conn.commit()
        except Exception as exc:
            logger.warning("Failed to record idempotency: %s", exc, exc_info=True)
        # 5.49.2 修复：异常路径确保连接归还
        finally:
            if conn is not None:
                conn.close()


class ConflictResolver:
    def __init__(self) -> None:
        self._locks: dict[str, threading.Lock] = {}
        self._global_lock = threading.Lock()
        self._queue: dict[str, list[FixAction]] = defaultdict(list)

    def acquire(self, target: str) -> threading.Lock:
        with self._global_lock:
            if target not in self._locks:
                self._locks[target] = threading.Lock()
            return self._locks[target]

    def resolve(self, actions: list[FixAction]) -> list[FixAction]:
        by_target: dict[str, list[FixAction]] = defaultdict(list)
        for a in actions:
            by_target[a.target].append(a)
        result: list[FixAction] = []
        _CONFIDENCE_ORDER = {"high": 0, "medium": 1, "low": 2}
        for target, target_actions in by_target.items():
            sorted_actions = sorted(
                target_actions,
                key=lambda a: (
                    a.level.value,
                    _CONFIDENCE_ORDER.get(a.confidence.value, 1),
                    a.timestamp.isoformat() if isinstance(a.timestamp, datetime) else str(a.timestamp),
                ),
            )
            result.extend(sorted_actions)
        return result

    def is_conflict(self, action: FixAction) -> bool:
        return action.target in self._queue and len(self._queue[action.target]) > 0


class FixOrderResolver:
    def __init__(self) -> None:
        self._dependency_map: dict[str, set[str]] = {}

    def add_dependency(self, fixer_type: str, depends_on: str) -> None:
        self._dependency_map.setdefault(fixer_type, set()).add(depends_on)

    def resolve(self, actions: list[FixAction]) -> list[FixAction]:
        if not actions:
            return []
        visited: set[str] = set()
        order: list[FixAction] = []
        action_map = {a.action_type: a for a in actions}

        def visit(action_type: str) -> None:
            if action_type in visited:
                return
            visited.add(action_type)
            for dep in self._dependency_map.get(action_type, set()):
                if dep in action_map:
                    visit(dep)
            if action_type in action_map:
                order.append(action_map[action_type])

        for a in actions:
            visit(a.action_type)
        return order


class FixResultCache:
    def __init__(self, max_size: int = 1000) -> None:
        self._cache: dict[str, Any] = {}
        self._max_size = max_size
        self._lock = threading.Lock()

    def get(self, key: str) -> object | None:
        with self._lock:
            return self._cache.get(key)

    def set(self, key: str, value: object) -> None:
        with self._lock:
            if len(self._cache) >= self._max_size:
                oldest = next(iter(self._cache))
                del self._cache[oldest]
            self._cache[key] = value

    def invalidate(self, key: str) -> None:
        with self._lock:
            self._cache.pop(key, None)


class BlastRadiusEstimator:
    def estimate(self, action: FixAction) -> dict[str, Any]:
        target = Path(action.target)
        files = 1
        modules = 0
        lines_estimate = 10
        risk = "low"
        if target.is_dir():
            py_files = list(target.rglob("*.py"))
            files = len(py_files)
            lines_estimate = files * 50
        elif target.is_file() and target.suffix == ".py":
            try:
                lines_estimate = len(target.read_text(encoding="utf-8").splitlines())
            except Exception as e:
                logger.warning("suppressed error in fix_reliability", exc_info=True)
        if action.level is FixLevel.L2_LLM:
            risk = "medium"
        elif action.level is FixLevel.L3_AGENT:
            risk = "high"
        if files > 5 or lines_estimate > 200:
            risk = "high" if risk != "low" else "medium"
        return {"files": files, "modules": modules, "lines_estimate": lines_estimate, "risk": risk}


class DeadLetterQueue:
    def __init__(self, max_retries: int = 3, db_path: str | None = None) -> None:
        self._max_retries = max_retries
        self._db_path = db_path or str(_DB_PATH)
        self._queue: list[FixDeadLetter] = []
        self._lock = threading.Lock()

    def add(self, action: FixAction, reason: str) -> FixDeadLetter:
        entry = FixDeadLetter(
            original_fix=action,
            failure_reason=reason,
            retry_count=0,
        )
        with self._lock:
            self._queue.append(entry)
        logger.error("Dead letter added: %s for %s - %s", action.action_id, action.target, reason)
        return entry

    def retry(self, dead_letter_id: str) -> FixDeadLetter | None:
        with self._lock:
            for entry in self._queue:
                if entry.dead_letter_id == dead_letter_id:
                    if entry.retry_count >= self._max_retries:
                        entry.escalated = True
                        return entry
                    entry.retry_count += 1
                    entry.last_retry = datetime.now(UTC)
                    return entry
        return None

    def get_pending(self) -> list[FixDeadLetter]:
        with self._lock:
            return [e for e in self._queue if not e.escalated and e.retry_count < self._max_retries]

    def get_escalated(self) -> list[FixDeadLetter]:
        with self._lock:
            return [e for e in self._queue if e.escalated]

    @property
    def size(self) -> int:
        with self._lock:
            return len(self._queue)


class ApprovalQueue:
    def __init__(self) -> None:
        self._queue: list[FixAction] = []
        self._lock = threading.Lock()

    def enqueue(self, action: FixAction) -> None:
        with self._lock:
            action.status = FixStatus.APPROVAL_PENDING
            self._queue.append(action)

    def approve(self, action_id: str) -> FixAction | None:
        with self._lock:
            for i, a in enumerate(self._queue):
                if a.action_id == action_id:
                    a.status = FixStatus.PENDING
                    return self._queue.pop(i)
        return None

    def reject(self, action_id: str) -> FixAction | None:
        with self._lock:
            for i, a in enumerate(self._queue):
                if a.action_id == action_id:
                    a.status = FixStatus.CANCELLED
                    return self._queue.pop(i)
        return None

    def get_pending(self) -> list[FixAction]:
        with self._lock:
            return list(self._queue)

    @property
    def size(self) -> int:
        with self._lock:
            return len(self._queue)


class CanaryFixer:
    def __init__(self, ratios: list[float] | None = None, delay_sec: int = 60) -> None:
        self._ratios = ratios or [0.1, 0.3, 0.5, 1.0]
        self._delay_sec = delay_sec
        self._current_stage: dict[str, int] = {}

    def get_ratio(self, fixer_type: str) -> float:
        stage = self._current_stage.get(fixer_type, 0)
        if stage >= len(self._ratios):
            return 1.0
        return self._ratios[stage]

    def advance(self, fixer_type: str) -> float:
        self._current_stage[fixer_type] = self._current_stage.get(fixer_type, 0) + 1
        return self.get_ratio(fixer_type)

    def should_apply(self, fixer_type: str, sample: int, total: int) -> bool:
        ratio = self.get_ratio(fixer_type)
        if total == 0:
            return True
        return sample / total <= ratio

    def reset(self, fixer_type: str) -> None:
        self._current_stage.pop(fixer_type, None)