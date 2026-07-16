# [BLUEPRINT] MOD-INF-027 | docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/blueprint.md | §3.1
# [MODULE] scripts.backup.backup_reconciler
# [DOMAIN] D_INFRASTRUCTURE
# [DEPENDENCIES] zephyr.gov_enforcement.audit.reconciliation_registry (ReconcilerSpec, ReconcileResult)
# [CONSUMERS] GitCommitGateway._reconciliation_registry.register
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] INV-08:post-commit reconciler触发非时间触发 | INV-09:双条件触发(重要文件+8h间隔) | INV-10:状态持久化backup_state.json
# [MODIFY-GUARD] gate_id="BACKUP-RECONCILER"
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] _reconcile异常降级为warn ReconcileResult，不阻断其他reconciler
# [TESTS] tests/scripts/backup/test_backup_reconciler.py
# [A_module] module_id=MOD-INF-027-reconciler | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""backup_reconciler.py — 灾备备份系统事件触发器（post-commit reconciler）

职责：注册为 ReconciliationRegistry 的 reconciler，post-commit 自动触发。
触发条件（双条件，同时满足）：
  1. committed_files 中存在重要文件（src/config/docs/scripts/tests/data/databases等）
  2. 距上次成功备份 ≥ 8小时（状态持久化到 backup_state.json）

满足条件后调用 PowerShell backup.ps1 执行六阶段备份流水线。

设计：
  - 事件驱动：post-commit reconciler（非 time.sleep/while True 轮询，满足PERM-TRIGGER gate）
  - 间隔保护：8小时最小间隔，避免频繁备份
  - 状态持久化：backup_state.json 记录上次备份时间/快照ID/状态
  - 容错：备份失败降级为 warn ReconcileResult，不阻断其他reconciler

Usage::

    from zephyr.gov_enforcement.audit.reconciliation_registry import ReconciliationRegistry
    from backup_reconciler import make_backup_reconciler

    registry = ReconciliationRegistry()
    registry.register(make_backup_reconciler(project_root))
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

__all__ = ["make_backup_reconciler"]

# ── 配置常量（从backup_config.yaml加载，此处为默认值兜底）──
_project_root = Path(__file__).resolve().parent.parent.parent  # D:\ZephyrAlpha
_CONFIG_FILE = _project_root / "scripts" / "backup" / "backup_config.yaml"
_STATE_FILE = _project_root / "data" / "databases" / "backup_state.json"

# 重要文件路径前缀（触发条件1）
_IMPORTANT_PREFIXES: tuple[str, ...] = (
    "src/", "config/", "docs/", "scripts/", "tests/", "architecture_model/",
    "data/databases/", "data/raw/bdpan/", "data/vector_db/",
)

# 重要根文件（触发条件1）
_IMPORTANT_FILES: frozenset[str] = frozenset({
    "AGENTS.md", "pyproject.toml", "docker-compose.yml",
})

# 最小间隔秒数（触发条件2，默认8小时）
_MIN_INTERVAL_SECONDS = 8 * 3600


def _load_config() -> dict[str, Any]:
    """加载backup_config.yaml配置"""
    try:
        with open(_CONFIG_FILE, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        logger.warning("backup_config.yaml not found, using defaults")
        return {}


def _rel_path(file_path: str | Path) -> str:
    """将绝对路径转为相对项目根的相对路径（正斜杠）"""
    try:
        rel = os.path.relpath(str(file_path), str(_project_root)).replace("\\", "/")
        return rel
    except ValueError:
        return str(file_path)


def _load_state() -> dict[str, Any]:
    """加载备份状态文件（INV-10）"""
    try:
        with open(_STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _update_state(**kwargs: Any) -> None:
    """更新备份状态文件（INV-10）"""
    state = _load_state()
    state.update(kwargs)
    _STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(_STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def _trigger(committed_files: list[str]) -> bool:
    """触发条件判断（INV-09：双条件触发）

    条件1：committed_files 中存在重要文件
    条件2：距上次成功备份 ≥ 8小时（首次备份无状态时视为满足）
    """
    # 条件1：检测重要文件变更
    has_important = False
    for f in committed_files:
        rel = _rel_path(f)
        if rel.startswith(_IMPORTANT_PREFIXES) or rel in _IMPORTANT_FILES:
            has_important = True
            break
    if not has_important:
        return False

    # 条件2：检查最小间隔
    state = _load_state()
    last_backup_str = state.get("last_backup_time")
    if last_backup_str:
        try:
            last_backup = datetime.fromisoformat(last_backup_str)
            if last_backup.tzinfo is None:
                last_backup = last_backup.replace(tzinfo=timezone.utc)
            elapsed = (datetime.now(timezone.utc) - last_backup).total_seconds()
            if elapsed < _MIN_INTERVAL_SECONDS:
                logger.debug(
                    "backup_reconciler: skip (elapsed=%.0fs < %ds)",
                    elapsed, _MIN_INTERVAL_SECONDS,
                )
                return False
        except (ValueError, TypeError):
            # 状态文件损坏，视为无状态，允许触发
            logger.warning("backup_state.json has invalid last_backup_time, allowing trigger")

    return True


def _reconcile(committed_files: list[str], session_id: str) -> Any:
    """执行备份——调用PowerShell backup.ps1

    返回 ReconcileResult（auto_committed 或 warn）。
    """
    try:
        from zephyr.gov_enforcement.audit.reconciliation_registry import ReconcileResult
    except ImportError:
        # 测试环境无zephyr模块时，返回简单dict
        ReconcileResult = dict  # type: ignore

    backup_script = _project_root / "scripts" / "backup" / "backup.ps1"
    if not backup_script.exists():
        return ReconcileResult(
            action="warn",
            detail=f"backup.ps1 not found at {backup_script}",
        )

    try:
        # 从config/.env.restic读取RESTIC_PASSWORD（自动触发时环境变量不可用）
        restic_env = _project_root / "config" / ".env.restic"
        if restic_env.exists() and not os.environ.get("RESTIC_PASSWORD"):
            try:
                with open(restic_env, encoding="utf-8") as f:
                    for line in f:
                        if line.strip().startswith("RESTIC_PASSWORD="):
                            os.environ["RESTIC_PASSWORD"] = line.strip().split("=", 1)[1]
                            break
            except OSError:
                pass  # 读取失败不阻断，backup.ps1会报错
        result = subprocess.run(
            [
                "powershell", "-ExecutionPolicy", "Bypass",
                "-File", str(backup_script),
            ],
            capture_output=True,
            text=True,
            timeout=1800,  # 30分钟超时
            cwd=str(_project_root),
        )
    except subprocess.TimeoutExpired:
        _update_state(last_backup_status="timeout")
        return ReconcileResult(
            action="warn",
            detail="backup timed out after 1800s",
        )

    if result.returncode == 0:
        now_iso = datetime.now(timezone.utc).isoformat()
        _update_state(
            last_backup_time=now_iso,
            last_backup_status="ok",
            last_session_id=session_id,
        )
        # 取最后200字符作为摘要
        summary = result.stdout[-200:] if result.stdout else ""
        return ReconcileResult(
            action="auto_committed",
            detail=f"backup ok: {summary}",
        )
    else:
        _update_state(last_backup_status="failed")
        err_summary = result.stderr[-200:] if result.stderr else result.stdout[-200:]
        return ReconcileResult(
            action="warn",
            detail=f"backup failed (exit={result.returncode}): {err_summary}",
        )


def make_backup_reconciler(project_root: Path | None = None):
    """工厂函数：创建backup reconciler spec。

    Args:
        project_root: 项目根路径（默认自动检测）

    Returns:
        ReconcilerSpec（含 gate_id/trigger/reconcile/priority）
    """
    global _project_root, _STATE_FILE, _CONFIG_FILE
    if project_root is not None:
        _project_root = Path(project_root)
        _CONFIG_FILE = _project_root / "scripts" / "backup" / "backup_config.yaml"
        _STATE_FILE = _project_root / "data" / "databases" / "backup_state.json"

    try:
        from zephyr.gov_enforcement.audit.reconciliation_registry import ReconcilerSpec
    except ImportError:
        # 测试环境无zephyr模块时，使用fallback类（避开ARCH-034 CLASS-UNIQUENESS冲突）
        class _ReconcilerSpecFallback:  # type: ignore
            def __init__(self, gate_id, trigger, reconcile, priority=100):
                self.gate_id = gate_id
                self.trigger = trigger
                self.reconcile = reconcile
                self.priority = priority
        ReconcilerSpec = _ReconcilerSpecFallback

    return ReconcilerSpec(
        gate_id="BACKUP-RECONCILER",
        trigger=_trigger,
        reconcile=_reconcile,
        priority=200,  # 低优先级（晚于其他reconciler执行）
    )


if __name__ == "__main__":
    # 手动测试入口
    spec = make_backup_reconciler()
    print(f"gate_id={spec.gate_id}, priority={spec.priority}")
    print(f"_trigger(['{_project_root / 'src' / 'test.py'}']) = {spec.trigger([str(_project_root / 'src' / 'test.py')])}")
