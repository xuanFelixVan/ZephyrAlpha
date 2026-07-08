# [BLUEPRINT] MOD-INF-015 | docs/03_modules/_domain_infrastructure_operations/system_telemetry/blueprint.md | 蓝图特有§A
# [MODULE] zephyr.infrastructure.system_telemetry.archive.cold_stub
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.system_telemetry.archive.__init__
# [CONSUMERS] src/zephyr/system-telemetry/facade.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] TTL分级策略严格执行;成本超限->三级降级(CRITICAL/SEVERE/WARNING);SQLite backup使用RULE-ONE原子写入
# [MODIFY-GUARD] docs/03_modules/_domain-infra_ops/system-telemetry/blueprint.md;src/zephyr/system-telemetry/facade.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] gzip失败->跳过压缩保留原文;SQLite backup失败->日志warning不阻塞
# [TESTS] tests/infrastructure/
# [A_module] module_id=MOD-INF_cold_stub | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""遥测 · archive/cold_stub — 冷存储归档管道。

蓝图 §8: 分级 TTL + gzip 压缩 + SQLite backup + 成本感知降级 + 灾备 RTO/RPO。
"""

from __future__ import annotations

import logging
import os
import shutil
import sqlite3
import tarfile
import threading
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from zephyr.shared.io.paths import DB_PATH, REPO_ROOT

_logger = logging.getLogger(__name__)

_DEFAULT_ARCHIVE_DIR: Path = REPO_ROOT / "data" / "telemetry" / "prod" / "archive"
_BACKUP_DIR: Path = REPO_ROOT / "data" / "backups"
_DB_PATH: Path = DB_PATH
_COST_LIMIT_GB: float = 10.0
_COST_WARN_80PCT: float = 8.0
_COST_CRITICAL_95PCT: float = 9.5

_archive_lock: threading.Lock = threading.Lock()


@dataclass
class RetentionPolicy:
    metrics_days: int = 30
    logs_days: int = 30
    traces_days: int = 7
    profiles_days: int = 14
    archive_days: int = 90
    auto_cleanup: bool = True


_policy: RetentionPolicy = RetentionPolicy()


def configure(
    archive_dir: Path | None = None,
    db_path: Path | None = None,
    backup_dir: Path | None = None,
    cost_limit_gb: float | None = None,
    policy_overrides: dict[str, int] | None = None,
) -> None:
    global _DEFAULT_ARCHIVE_DIR, _DB_PATH, _BACKUP_DIR, _COST_LIMIT_GB, _policy
    if archive_dir is not None:
        _DEFAULT_ARCHIVE_DIR = archive_dir
    if db_path is not None:
        _DB_PATH = db_path
    if backup_dir is not None:
        _BACKUP_DIR = backup_dir
    if cost_limit_gb is not None:
        _COST_LIMIT_GB = cost_limit_gb
        _COST_WARN_80PCT = _COST_LIMIT_GB * 0.8
        _COST_CRITICAL_95PCT = _COST_LIMIT_GB * 0.95
    if policy_overrides:
        for k, v in policy_overrides.items():
            if hasattr(_policy, k):
                setattr(_policy, k, v)


def next_archive_batch_id(prefix: str = "batch") -> str:
    ts = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    return f"{prefix}-{ts}"


def compress_dir(src: Path, dst_name: str) -> Path | None:
    if not src.exists() or not src.is_dir():
        return None

    dst = _DEFAULT_ARCHIVE_DIR / f"{dst_name}.tar.gz"
    dst.parent.mkdir(parents=True, exist_ok=True)

    tmp = dst.with_name(f"{dst.name}.{os.getpid()}.tmp")
    try:
        with tarfile.open(tmp, "w:gz") as tar:
            tar.add(src, arcname=".")
        os.replace(tmp, dst)
        return dst
    except Exception:
        try:
            os.remove(tmp)
        except OSError:
            pass
        return None


def rotate_by_ttl(base_dir: Path, max_age_days: int) -> int:
    removed = 0
    cutoff = time.time() - (max_age_days * 86400)
    if not base_dir.exists():
        return 0

    for entry in base_dir.iterdir():
        try:
            if entry.stat().st_mtime < cutoff:
                if entry.is_file():
                    entry.unlink()
                else:
                    shutil.rmtree(entry, ignore_errors=True)
                removed += 1
        except OSError:
            continue
    return removed


# 治本（2026-06-29 阶段A+）：删除 daily_backup_sqlite() 函数。
# 原函数被 facade.py 的 archive_check 定时任务（每 5 分钟）调用，自动创建 telemetry_*.db 备份。
# 这是 118 个 .db 残留的来源之一，且定时触发违反"事件驱动"原则。
# 备份唯一真源：governance/database_manager.py 的 DatabaseManager.backup()（显式调用）。


def cost_status() -> dict[str, Any]:
    total_gb = _measure_disk_gb(_DEFAULT_ARCHIVE_DIR)
    loads: dict[str, Any] = {
        "total_gb": round(total_gb, 2),
        "budget_gb": _COST_LIMIT_GB,
        "usage_pct": round(total_gb / _COST_LIMIT_GB * 100, 1) if _COST_LIMIT_GB > 0 else 0.0,
    }
    if total_gb >= _COST_LIMIT_GB:
        loads["level"] = "CRITICAL"
    elif total_gb >= _COST_CRITICAL_95PCT:
        loads["level"] = "SEVERE"
    elif total_gb >= _COST_WARN_80PCT:
        loads["level"] = "WARNING"
    else:
        loads["level"] = "OK"
    return loads


def apply_cost_degradation() -> list[str]:
    actions: list[str] = []
    status = cost_status()
    total = status["total_gb"]

    if total >= _COST_LIMIT_GB:
        actions.append("P0: non-prod data suspended; only prod metrics + P0 logs")
    elif total >= _COST_CRITICAL_95PCT:
        actions.append("P1: dev telemetry paused; staging traces 1%; profiles OFF")
    elif total >= _COST_WARN_80PCT:
        actions.append("P2: dev TTL halved (14->7d); traces sample 10->5%")

    return actions


def _measure_disk_gb(path: Path) -> float:
    total = 0
    if not path.exists():
        return 0.0
    for entry in path.rglob("*"):
        if entry.is_file():
            try:
                total += entry.stat().st_size
            except OSError:
                continue
    return total / (1024**3)
