# [BLUEPRINT] MOD-RESOURCE_OPTIMIZATION_ENGINE | docs/03_modules/_cross_layer/resource_optimization_engine/blueprint.md | §new-IDE
# [MODULE] zephyr.trading.zombie_scanner
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.trading.__init__
# [CONSUMERS] scripts/ide_health_service.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 扫描只读无副作用；kill 操作必须日志记录；模式计数器原子读写；分类判定仅基于进程指标；SUSPICIOUS 只上报不 kill；进程归属判定 = cmdline 或 cwd 任一包含项目根路径
# [MODIFY-GUARD] MOD-RESOURCE_OPTIMIZATION_ENGINE §new-IDE
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] psutil 不可用时返回空结果；kill 对已退出 PID 不报错；模式文件损坏时重置为空 dict
# [TESTS]
# [A_module] module_id=MOD-ORC_zombie_scanner | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
zombie_scanner.py — 僵尸 Python 进程检测与自动处置
====================================================
四级分类处置：
  SUSPICIOUS（>30min · CPU≈0） → 写入 status 上报，不 kill
  ABNORMAL（>1hr · 从项目目录启动） → kill + 日志 + 模式计数
  DANGEROUS（>10GB 或 >50子进程 或 >6hr） → kill + 日志 + 模式计数
模式计数 >3次/24h → repeated_offender 标记到 status
"""

from __future__ import annotations

import json
import logging
import os
import signal
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）
from typing import Any

# 5.97.7 修复: psutil 提升至模块级导入，供 _extract_proc_info / scan_zombie_processes 共享
try:
    import psutil as _psutil
except ImportError:
    _psutil = None

logger = logging.getLogger(__name__)

_PATTERNS_FILE = str(REPO_ROOT / "data" / "runtime" / "zombie-patterns.json")
_ZOMBIE_LOG = str(REPO_ROOT / "data" / "runtime" / "zombie_kill.log")

_SAFE_KEYWORDS = (
    "ide_health_service",
    "ide_health_daemon",
    "resource_optimization",
)
_DANGEROUS_MEM_GB = 10.0
_DANGEROUS_CHILDREN = 50
_DANGEROUS_RUNTIME_S = 6 * 3600
_ABNORMAL_RUNTIME_S = 3600
_SUSPICIOUS_RUNTIME_S = 1800
_SUSPICIOUS_CPU_MAX = 0.5
_REPEATED_THRESHOLD = 3
_REPEATED_WINDOW_S = 24 * 3600

__all__ = [
    "ZombieCategory",
    "ZombieEntry",
    "ZombieScanResult",
    "get_repeated_offenders",
    "handle_zombies",
    "scan_zombie_processes",
]


class ZombieCategory(Enum):
    def __str__(self) -> str:
        # 5.92.2 修复：统一日志格式，返回 value 而非 ClassName.MEMBER
        return self.value

    NORMAL = "normal"
    SUSPICIOUS = "suspicious"
    ABNORMAL = "abnormal"
    DANGEROUS = "dangerous"


@dataclass
class ZombieEntry:
    pid: int
    category: ZombieCategory
    reason: str
    cmdline: str
    runtime_s: float
    mem_gb: float
    cpu_percent: float
    children_count: int
    killed: bool = False


@dataclass
class ZombieScanResult:
    scanned: int = 0
    suspicious: list[ZombieEntry] = field(default_factory=list)
    abnormal: list[ZombieEntry] = field(default_factory=list)
    dangerous: list[ZombieEntry] = field(default_factory=list)
    killed: list[dict[str, Any]] = field(default_factory=list)
    repeated_offenders: list[dict[str, Any]] = field(default_factory=list)


def _load_patterns() -> dict[str, list[float]]:
    try:
        os.makedirs(os.path.dirname(_PATTERNS_FILE), exist_ok=True)
        with open(_PATTERNS_FILE, encoding="utf-8") as f:
            patterns = json.load(f)
            if isinstance(patterns, dict):
                return patterns
    except Exception as e:
        logger.warning("_load_patterns: failed to load patterns file (%s: %s)", type(e).__name__, e, exc_info=True)
    return {}


def _save_patterns(patterns: dict[str, list[float]]) -> None:
    try:
        os.makedirs(os.path.dirname(_PATTERNS_FILE), exist_ok=True)
        # 5.74.1 修复：使用 tmp 文件 + os.replace() 原子写入，防止崩溃时文件损坏
        tmp_path = _PATTERNS_FILE + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(patterns, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, _PATTERNS_FILE)
    except Exception:
        logger.warning("zombie_scanner: failed to save patterns file", exc_info=True)


def _log_kill(pid: int, reason: str) -> None:
    try:
        os.makedirs(os.path.dirname(_ZOMBIE_LOG), exist_ok=True)
        with open(_ZOMBIE_LOG, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] KILLED PID={pid} reason={reason}\n")
    except Exception as e:
        logger.warning("suppressed error in zombie_scanner", exc_info=True)


def _make_signature(cmdline: str) -> str:
    parts = cmdline.replace("\\", "/").split()
    sig_parts: list[str] = []
    for p in parts:
        if p.endswith(".py"):
            sig_parts.append(os.path.basename(p))
        elif any(kw in p for kw in _SAFE_KEYWORDS):
            sig_parts.append("[daemon]")
    if not sig_parts and parts:
        sig_parts.append(parts[0].rsplit("/", 1)[-1])
    return " ".join(sig_parts) if sig_parts else cmdline[:80]


def _is_safe(cmdline: str) -> bool:
    return any(kw in cmdline for kw in _SAFE_KEYWORDS)


def _update_pattern(signature: str) -> int:
    now = time.time()
    patterns = _load_patterns()
    timestamps = patterns.get(signature, [])
    timestamps = [t for t in timestamps if now - t < _REPEATED_WINDOW_S]
    timestamps.append(now)
    patterns[signature] = timestamps
    _save_patterns(patterns)
    return len(timestamps)


def get_repeated_offenders() -> list[dict[str, Any]]:
    now = time.time()
    patterns = _load_patterns()
    offenders: list[dict[str, Any]] = []
    for sig, timestamps in patterns.items():
        recent = [t for t in timestamps if now - t < _REPEATED_WINDOW_S]
        if len(recent) >= _REPEATED_THRESHOLD:
            offenders.append(
                {
                    "signature": sig,
                    "count": len(recent),
                    "last_seen": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(max(recent))),
                }
            )
    return sorted(offenders, key=lambda x: x["count"], reverse=True)


def _extract_proc_info(proc, project_root_str: str, current_pid: int) -> dict[str, Any] | None:
    """提取并过滤进程信息。

    返回 None 表示跳过该进程（自身 / 非 Python / 安全关键字 / 非项目进程 / 进程已退出）。
    返回 dict 包含 pid / cmdline / runtime / mem_gb / cpu / children。
    """
    # 5.151.2: 仅捕获进程枚举期间的预期异常，不遮蔽 AttributeError/TypeError 等 Bug
    try:
        pid = proc.info["pid"]
        if pid == current_pid or pid is None:
            return None

        name = (proc.info.get("name") or "").lower()
        if "python" not in name:
            return None

        cmdline_raw = proc.info.get("cmdline")
        if not cmdline_raw:
            return None
        cmdline = " ".join(cmdline_raw) if isinstance(cmdline_raw, list) else str(cmdline_raw)

        if _is_safe(cmdline):
            return None

        cwd = proc.info.get("cwd") or ""
        belongs_to_project = (project_root_str in cmdline) or (project_root_str in cwd)
        if not belongs_to_project:
            return None
    except (_psutil.NoSuchProcess, _psutil.AccessDenied):
        return None

    try:
        runtime = time.time() - proc.create_time()
        mem_gb = proc.memory_info().rss / (1024**3)
        cpu = proc.cpu_percent()
        try:
            children = len(proc.children())
        except Exception:
            children = 0
    except (_psutil.NoSuchProcess, _psutil.AccessDenied):
        return None

    return {
        "pid": pid,
        "cmdline": cmdline,
        "runtime": runtime,
        "mem_gb": mem_gb,
        "cpu": cpu,
        "children": children,
    }


def _classify_zombie(
    runtime: float, mem_gb: float, cpu: float, children: int
) -> tuple[ZombieCategory | None, list[str]]:
    """根据进程指标分类僵尸进程。

    返回 (category, reason)。category=None 表示 NORMAL（正常，调用方跳过）。
    """
    if mem_gb > _DANGEROUS_MEM_GB or children > _DANGEROUS_CHILDREN or runtime > _DANGEROUS_RUNTIME_S:
        reason = []
        if mem_gb > _DANGEROUS_MEM_GB:
            reason.append(f"mem={mem_gb:.1f}GB")
        if children > _DANGEROUS_CHILDREN:
            reason.append(f"children={children}")
        if runtime > _DANGEROUS_RUNTIME_S:
            reason.append(f"runtime={runtime / 3600:.1f}h")
        return ZombieCategory.DANGEROUS, reason
    if runtime > _ABNORMAL_RUNTIME_S:
        return ZombieCategory.ABNORMAL, [f"runtime={runtime / 3600:.1f}h"]
    if runtime > _SUSPICIOUS_RUNTIME_S and cpu < _SUSPICIOUS_CPU_MAX:
        return ZombieCategory.SUSPICIOUS, [f"runtime={runtime / 3600:.1f}h cpu={cpu:.1f}%"]
    return None, []


def scan_zombie_processes() -> ZombieScanResult:
    result = ZombieScanResult()
    if _psutil is None:
        return result

    project_root_str = str(REPO_ROOT)
    current_pid = os.getpid()

    for proc in _psutil.process_iter(["pid", "name", "cmdline", "create_time", "cwd"]):
        info = _extract_proc_info(proc, project_root_str, current_pid)
        if info is None:
            continue

        result.scanned += 1
        cat, reason = _classify_zombie(
            info["runtime"], info["mem_gb"], info["cpu"], info["children"]
        )
        if cat is None:
            continue

        entry = ZombieEntry(
            pid=info["pid"],
            category=cat,
            reason=", ".join(reason),
            cmdline=info["cmdline"][:200],
            runtime_s=info["runtime"],
            mem_gb=round(info["mem_gb"], 2),
            cpu_percent=round(info["cpu"], 2),
            children_count=info["children"],
        )

        if cat is ZombieCategory.DANGEROUS:
            result.dangerous.append(entry)
        elif cat is ZombieCategory.ABNORMAL:
            result.abnormal.append(entry)
        elif cat is ZombieCategory.SUSPICIOUS:
            result.suspicious.append(entry)

    return result


def _kill_process(pid: int) -> bool:
    try:
        os.kill(pid, signal.SIGTERM)
        time.sleep(1.0)
        try:
            import psutil

            if psutil.pid_exists(pid):
                psutil.Process(pid).terminate()
                time.sleep(2.0)
                if psutil.pid_exists(pid):
                    psutil.Process(pid).kill()
        except (ProcessLookupError, PermissionError) as e:
            logger.warning("_kill_process: failed to clean up process %s (%s: %s)", pid, type(e).__name__, e, exc_info=True)
            return False
        return True
    except OSError as e:
        logger.warning("_kill_process: failed to kill process %s (%s: %s)", pid, type(e).__name__, e)
        return False


def handle_zombies(scan_result: ZombieScanResult | None = None) -> ZombieScanResult:
    if scan_result is None:
        scan_result = scan_zombie_processes()

    for entry in scan_result.dangerous + scan_result.abnormal:
        sig = _make_signature(entry.cmdline)
        count = _update_pattern(sig)
        if _kill_process(entry.pid):
            entry.killed = True
            _log_kill(entry.pid, f"{entry.category.value}: {entry.reason}")
            scan_result.killed.append(
                {
                    "pid": entry.pid,
                    "category": entry.category.value,
                    "reason": entry.reason,
                    "signature": sig,
                    "pattern_count": count,
                }
            )

    scan_result.repeated_offenders = get_repeated_offenders()
    return scan_result