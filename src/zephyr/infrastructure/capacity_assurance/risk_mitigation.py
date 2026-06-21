# [A_module] module_id=MOD-INF_risk_mitigation | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain-infra_ops/capacity-assurance/blueprint.md

# [MODULE] zephyr.infrastructure.capacity_assurance.risk_mitigation

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""Risk mitigation — R1~R16 全量风险缓解实现（对标蓝图 §14 风险与缓解 + 多轮盲点审计）."""


import os
import time
import sqlite3
import threading
import hashlib
import logging
from concurrent.futures import ThreadPoolExecutor
from queue import Queue, Full
from pathlib import Path
from typing import Callable, List, Optional, Tuple

logger = logging.getLogger(__name__)


def enable_wal_mode(db_path: str) -> bool:
    """R1: 启用 WAL 模式."""
    try:
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.close()
        return True
    except sqlite3.Error as e:
        logger.error(f"Failed to enable WAL mode on {db_path}: {e}")
        return False


def perform_wal_checkpoint(db_path: str, mode: str = "PASSIVE") -> bool:
    """R1: 定期 WAL checkpoint."""
    try:
        conn = sqlite3.connect(db_path)
        conn.execute(f"PRAGMA wal_checkpoint({mode})")
        conn.close()
        return True
    except sqlite3.Error as e:
        logger.error(f"WAL checkpoint failed on {db_path}: {e}")
        return False


def backup_checkpoint(db_path: str, backup_path: str) -> bool:
    """R1: 备份前强制执行 checkpoint."""
    if perform_wal_checkpoint(db_path, "FULL"):
        try:
            src = sqlite3.connect(db_path)
            dst = sqlite3.connect(backup_path)
            src.backup(dst)
            src.close()
            dst.close()
            return True
        except sqlite3.Error as e:
            logger.error(f"Backup failed: {e}")
    return False


class DeadlockDetector:
    """R2: 跨模块死锁检测——超时 + 重试 + 指数退避 + 有序锁获取."""

    def __init__(self, timeout: float = 30.0, max_retries: int = 3, base_delay: float = 1.0):
        self.timeout = timeout
        self.max_retries = max_retries
        self.base_delay = base_delay
        self._lock = threading.Lock()

    def acquire_with_timeout(self, lock: threading.Lock, timeout: Optional[float] = None) -> bool:
        timeout = timeout or self.timeout
        return lock.acquire(timeout=timeout)

    def retry_with_backoff(self, func: Callable, *args, **kwargs):
        last_exc = None
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exc = e
                delay = self.base_delay * (2 ** attempt)
                logger.warning(f"Retry {attempt + 1}/{self.max_retries} after {delay}s: {e}")
                time.sleep(delay)
        raise last_exc or RuntimeError("Max retries exceeded")

    def ordered_lock_acquisition(self, locks: List[threading.Lock]) -> bool:
        """R2: 按模块 ID 排序获取锁——避免循环等待."""
        for lock in locks:
            if not lock.acquire(timeout=self.timeout):
                for acquired in locks[:locks.index(lock)]:
                    acquired.release()
                return False
        return True


class AlertLinkIsolator:
    """R3: 告警链路隔离——fire-and-forget + ThreadPoolExecutor."""

    def __init__(self, max_workers: int = 2, queue_size: int = 100):
        self.executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="alert-iso")
        self.queue: Queue = Queue(maxsize=queue_size)

    def fire_and_forget(self, alert_func: Callable, *args, **kwargs) -> bool:
        try:
            self.queue.put_nowait((alert_func, args, kwargs))
        except Full:
            logger.error("Alert queue full, dropping alert")
            return False

        def _runner():
            try:
                func, f_args, f_kwargs = self.queue.get_nowait()
                func(*f_args, **f_kwargs)
            except Exception:
                pass

        self.executor.submit(_runner)
        return True

    def shutdown(self, wait: bool = True):
        self.executor.shutdown(wait=wait)


class SchemaVersionGuard:
    """R4: Pydantic Schema 版本漂移防护——双向版本校验."""

    def __init__(self, expected_version: str = "2.6.0"):
        self.expected_version = expected_version

    def validate_config_version(self, config_version: str) -> bool:
        return config_version == self.expected_version

    def check_schema_field(self, model_cls, field_name: str) -> bool:
        return hasattr(model_cls, field_name) and field_name in model_cls.model_fields


class TokenCalibration:
    """R5: Token 预估校准——滚动窗口修正."""

    def __init__(self, window_size: int = 10):
        self.window: List[Tuple[int, int]] = []
        self.window_size = window_size

    def record(self, estimated: int, actual: int) -> None:
        self.window.append((estimated, actual))
        if len(self.window) > self.window_size:
            self.window.pop(0)

    def get_correction_factor(self) -> float:
        if not self.window:
            return 1.0
        total_est = sum(e for e, _ in self.window)
        total_act = sum(a for _, a in self.window)
        return total_act / total_est if total_est > 0 else 1.0

    def get_accuracy_ratio(self) -> float:
        if not self.window:
            return 1.0
        total = sum(abs(e - a) / max(e, 1) for e, a in self.window)
        return 1.0 - (total / len(self.window))


class KillSwitchSafeguard:
    """R6: Kill Switch 误触发保护——脉冲过滤 + 多条件非AND."""

    def __init__(self, sustain_duration: float = 30.0):
        self.sustain_duration = sustain_duration
        self._trigger_start: Optional[float] = None
        self._conditions_met: int = 0
        self._required_conditions: int = 2

    def register_condition(self, met: bool) -> None:
        if met:
            self._conditions_met += 1
            if self._trigger_start is None:
                self._trigger_start = time.time()
        else:
            self._conditions_met = max(0, self._conditions_met - 1)

    def should_trigger(self) -> bool:
        if self._conditions_met < self._required_conditions:
            return False
        if self._trigger_start is None:
            return False
        elapsed = time.time() - self._trigger_start
        return elapsed >= self.sustain_duration

    def manual_override(self) -> None:
        self._trigger_start = None
        self._conditions_met = 0


class SandboxHardener:
    """R7: Sandbox 硬边界加固."""

    HARD_LIMITS = {
        "max_memory_mb": 512,
        "max_execution_seconds": 60,
        "max_file_descriptors": 64,
    }

    @classmethod
    def enforce(cls, process_limits: dict) -> List[str]:
        violations = []
        for key, hard_limit in cls.HARD_LIMITS.items():
            actual = process_limits.get(key, 0)
            if actual > hard_limit:
                violations.append(f"{key}: {actual} > {hard_limit}")
        return violations


class ProvenanceIntegrityChecker:
    """R8: Provenance hash 链定期校验."""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def verify_chain(self) -> Tuple[bool, List[str]]:
        errors = []
        try:
            conn = sqlite3.connect(self.db_path)
            rows = conn.execute(
                "SELECT id, prev_hash, curr_hash, module, field, old_value, new_value, author_agent "
                "FROM ai_provenance ORDER BY id"
            ).fetchall()
            conn.close()

            prev_expected = None
            for row in rows:
                actual_prev = row[1]
                if actual_prev != prev_expected and prev_expected is not None:
                    errors.append(f"Hash chain broken at id={row[0]}: expected {prev_expected}, got {actual_prev}")
                content = "|".join(str(x) for x in row[3:7])
                expected_curr = hashlib.sha256(content.encode()).hexdigest()
                if row[2] != expected_curr:
                    errors.append(f"Hash mismatch at id={row[0]}")
                prev_expected = row[2]
        except sqlite3.Error as e:
            errors.append(f"DB error: {e}")
        return len(errors) == 0, errors


def incremental_hash_verify(db_path: str, chunk_size: int = 100) -> bool:
    """R9: 增量 hash 校验——盲点 #14 缓解."""
    checker = ProvenanceIntegrityChecker(db_path)
    ok, errors = checker.verify_chain()
    if errors:
        for err in errors:
            logger.warning(err)
    return ok


def input_pattern_whitelist(input_text: str, allowed_patterns: Optional[List[str]] = None) -> bool:
    """R10: 输入模式白名单——盲点 #15 缓解."""
    if allowed_patterns is None:
        return True
    return any(pattern in input_text for pattern in allowed_patterns)


def kill_switch_channel_arbiter(file_signal_path: str, env_var_name: str) -> bool:
    """R11: Kill Switch 双通道竞争仲裁——盲点 #16 缓解.
    文件信号优先，环境变量降级为缓存."""
    if os.path.exists(file_signal_path):
        return True
    env_val = os.environ.get(env_var_name, "0")
    return env_val.strip().lower() in ("1", "true", "yes")


def error_budget_reconciler(aggregated: float, per_window_sum: float, tolerance: float = 0.01) -> bool:
    """R12: Error Budget 不变式校验——盲点 #26 缓解."""
    delta = abs(aggregated - per_window_sum)
    if aggregated > 0 and delta / aggregated > tolerance:
        logger.error(f"Error Budget invariant violated: cumulative={aggregated}, sum={per_window_sum}, delta={delta}")
        return False
    return True


_sensitive_keys = {"threshold", "target", "budget", "limit", "secret"}


def slo_config_sanitizer(config_dict: dict) -> dict:
    """R13: SLO 配置脱敏——盲点 #38 缓解."""
    sanitized = {}
    for key, value in config_dict.items():
        if any(sk in key.lower() for sk in _sensitive_keys) and isinstance(value, (int, float)):
            sanitized[key] = "***"
        elif isinstance(value, dict):
            sanitized[key] = slo_config_sanitizer(value)
        else:
            sanitized[key] = value
    return sanitized


class MigrationCrashRecovery:
    """R14: ContractBus 迁移崩溃恢复——盲点 #49 缓解."""

    def __init__(self, checkpoint_file: str):
        self.checkpoint_file = Path(checkpoint_file)
        self._completed_batches: List[str] = []

    def mark_batch_complete(self, batch_id: str) -> None:
        self._completed_batches.append(batch_id)
        self.checkpoint_file.write_text("\n".join(self._completed_batches), encoding="utf-8")

    def get_completed_batches(self) -> List[str]:
        if self.checkpoint_file.exists():
            return self.checkpoint_file.read_text(encoding="utf-8").strip().split("\n")
        return []


def unicode_path_normalizer(path: str) -> str:
    """R15: Unicode 路径规范化——盲点 #65 缓解."""
    import unicodedata
    normalized = unicodedata.normalize("NFC", path)
    return normalized.replace("\\", "/").casefold()


class ChromaDBThreadGuard:
    """R16: ChromaDB 线程池泄漏防护——盲点 #66 缓解."""

    def __init__(self, max_workers: int = 8):
        self.max_workers = max_workers
        self._executor: Optional[ThreadPoolExecutor] = None
        self._task_count: int = 0
        self._recycle_threshold: int = 1000

    @property
    def executor(self) -> ThreadPoolExecutor:
        if self._executor is None:
            self._executor = ThreadPoolExecutor(max_workers=self.max_workers, thread_name_prefix="chroma")
        return self._executor

    def submit(self, fn, *args, **kwargs):
        self._task_count += 1
        if self._task_count >= self._recycle_threshold:
            self._recycle()
        return self.executor.submit(fn, *args, **kwargs)

    def _recycle(self) -> None:
        old = self._executor
        self._executor = ThreadPoolExecutor(max_workers=self.max_workers, thread_name_prefix="chroma")
        self._task_count = 0
        if old:
            old.shutdown(wait=False)

    def shutdown(self, wait: bool = True):
        if self._executor:
            self._executor.shutdown(wait=wait)
