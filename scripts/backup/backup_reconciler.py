# [BLUEPRINT] MOD-INF-043 | docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/blueprint.md | §3.1
# [MODULE] scripts.backup.backup_reconciler
# [DOMAIN] D_INFRASTRUCTURE
# [DEPENDENCIES] zephyr.governance.audit.reconciliation_registry (ReconcilerSpec, ReconcileResult)
# [CONSUMERS] GitCommitGateway._reconciliation_registry.register
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] INV-08:post-commit reconciler触发非时间触发 | INV-09:双条件触发(重要文件+8h间隔) | INV-10:状态持久化backup_state.json
# [MODIFY-GUARD] gate_id="BACKUP-RECONCILER"
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] reconcile异常降级为warn ReconcileResult，不阻断其他reconciler
# [TESTS] tests/scripts/backup/test_backup_reconciler.py
# [A_module] module_id=MOD-INF-043 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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

公共 API（无下划线前缀）为真源实现；带下划线前缀的私有名（_load_config /
_get_state_file / _load_state / _update_state / _trigger / _reconcile 等）保留为
向后兼容的薄包装，委托给同名公共函数，便于历史调用方平滑过渡。

Usage::

    from zephyr.governance.audit.reconciliation_registry import ReconciliationRegistry
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
# 公共名为真源；PROJECT_ROOT 与 CONFIG_FILE / STATE_FILE 同为模块级路径常量。
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent  # D:\ZephyrAlpha
CONFIG_FILE = PROJECT_ROOT / "scripts" / "backup" / "backup_config.yaml"
STATE_FILE = PROJECT_ROOT / "data" / "databases" / "backup_state.json"

# 重要文件路径前缀（触发条件1）
IMPORTANT_PREFIXES: tuple[str, ...] = (
    "src/",
    "config/",
    "docs/",
    "scripts/",
    "tests/",
    "architecture_model/",
    "data/databases/",
    "data/raw/bdpan/",
    "data/vector_db/",
)

# 重要根文件（触发条件1）
IMPORTANT_FILES: frozenset[str] = frozenset(
    {
        "AGENTS.md",
        "pyproject.toml",
        "docker-compose.yml",
    }
)

# 最小间隔秒数（触发条件2，默认8小时）
MIN_INTERVAL_SECONDS = 8 * 3600

# ── 向后兼容别名（公共名为真源；私有名为静态快照/薄包装，仅供历史调用方过渡）──
# 注意：PROJECT_ROOT / CONFIG_FILE / STATE_FILE 可被 make_backup_reconciler 重新赋值，
# 这些私有别名仅反映导入时的快照，不应在新代码中依赖。
_project_root = PROJECT_ROOT
_CONFIG_FILE = CONFIG_FILE
_STATE_FILE = STATE_FILE
_IMPORTANT_PREFIXES = IMPORTANT_PREFIXES
_IMPORTANT_FILES = IMPORTANT_FILES
_MIN_INTERVAL_SECONDS = MIN_INTERVAL_SECONDS


def load_config() -> dict[str, Any]:
    """加载backup_config.yaml配置"""
    try:
        with open(CONFIG_FILE, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        logger.warning("backup_config.yaml not found, using defaults")
        return {}


def _load_config() -> dict[str, Any]:
    """向后兼容包装：委托给 load_config()。"""
    return load_config()


def rel_path(file_path: str | Path) -> str:
    """将绝对路径转为相对项目根的相对路径（正斜杠）"""
    try:
        rel = os.path.relpath(str(file_path), str(PROJECT_ROOT)).replace("\\", "/")
        return rel
    except ValueError:
        return str(file_path)


def _rel_path(file_path: str | Path) -> str:
    """向后兼容包装：委托给 rel_path()。"""
    return rel_path(file_path)


def get_state_file() -> Path:
    """获取状态文件路径（从 backup_config.yaml §trigger.state_file 读取，fallback 到 STATE_FILE）。

    F-06 Track A 治本：state_file 真源从硬编码 STATE_FILE 迁移到 YAML trigger.state_file，
    硬编码常量仅作 YAML 缺失时的 fallback。
    """
    config = load_config()
    trigger_cfg = config.get("trigger", {}) if config else {}
    state_file_rel = trigger_cfg.get("state_file")
    if state_file_rel:
        return PROJECT_ROOT / state_file_rel
    return STATE_FILE


def _get_state_file() -> Path:
    """向后兼容包装：委托给 get_state_file()。"""
    return get_state_file()


def load_state() -> dict[str, Any]:
    """加载备份状态文件（INV-10）"""
    state_file = get_state_file()
    try:
        with open(state_file, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _load_state() -> dict[str, Any]:
    """向后兼容包装：委托给 load_state()。"""
    return load_state()


def update_state(**kwargs: Any) -> None:
    """更新备份状态文件（INV-10）"""
    state_file = get_state_file()
    state = load_state()
    state.update(kwargs)
    state_file.parent.mkdir(parents=True, exist_ok=True)
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def _update_state(**kwargs: Any) -> None:
    """向后兼容包装：委托给 update_state()。"""
    return update_state(**kwargs)


def trigger(committed_files: list[str]) -> bool:
    """触发条件判断（INV-09：双条件触发）

    条件1：committed_files 中存在重要文件
    条件2：距上次成功备份 ≥ 8小时（首次备份无状态时视为满足）

    F-06 Track A 治本（2026-07-17）：触发参数（prefixes/files/min_interval）真源
    从硬编码常量迁移到 backup_config.yaml §trigger（load_config 加载），硬编码
    常量仅作 YAML 缺失时的 fallback（消除 load_config 定义但未调用的死代码）。
    """
    # 加载配置（YAML 真源 + 硬编码 fallback）
    config = load_config()
    trigger_cfg = config.get("trigger", {}) if config else {}

    # 条件1：检测重要文件变更（prefixes/files 从 YAML 读取，fallback 到硬编码）
    prefixes = tuple(trigger_cfg.get("important_prefixes", IMPORTANT_PREFIXES))
    important_files = frozenset(trigger_cfg.get("important_files", IMPORTANT_FILES))
    has_important = False
    for f in committed_files:
        rel = rel_path(f)
        if rel.startswith(prefixes) or rel in important_files:
            has_important = True
            break
    if not has_important:
        return False

    # 条件2：检查最小间隔（min_interval_seconds 从 YAML 读取，fallback 到硬编码）
    min_interval = trigger_cfg.get("min_interval_seconds", MIN_INTERVAL_SECONDS)
    state = load_state()
    last_backup_str = state.get("last_backup_time")
    if last_backup_str:
        try:
            last_backup = datetime.fromisoformat(last_backup_str)
            if last_backup.tzinfo is None:
                last_backup = last_backup.replace(tzinfo=timezone.utc)
            elapsed = (datetime.now(timezone.utc) - last_backup).total_seconds()
            if elapsed < min_interval:
                logger.debug(
                    "backup_reconciler: skip (elapsed=%.0fs < %ds)",
                    elapsed,
                    min_interval,
                )
                return False
        except (ValueError, TypeError):
            # 状态文件损坏，视为无状态，允许触发
            logger.warning("backup_state.json has invalid last_backup_time, allowing trigger")

    return True


def _trigger(committed_files: list[str]) -> bool:
    """向后兼容包装：委托给 trigger()。"""
    return trigger(committed_files)


def reconcile(committed_files: list[str], session_id: str) -> Any:
    """执行备份——调用PowerShell backup.ps1

    返回 ReconcileResult（auto_committed 或 warn）。
    """
    try:
        from zephyr.governance.audit.reconciliation_registry import ReconcileResult
    except ImportError:
        # 测试环境无zephyr模块时，返回简单dict
        ReconcileResult = dict  # type: ignore

    backup_script = PROJECT_ROOT / "scripts" / "backup" / "backup.ps1"
    if not backup_script.exists():
        return ReconcileResult(
            action="warn",
            detail=f"backup.ps1 not found at {backup_script}",
        )

    try:
        result = subprocess.run(
            [
                "powershell",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(backup_script),
            ],
            capture_output=True,
            text=True,
            timeout=14400,  # 4h超时（CH ~200GiB VHDX Disk备份，见blueprint §4.3）
            cwd=str(PROJECT_ROOT),
        )
    except subprocess.TimeoutExpired:
        update_state(last_backup_status="timeout")
        return ReconcileResult(
            action="warn",
            detail="backup timed out after 14400s",
        )

    if result.returncode == 0:
        now_iso = datetime.now(timezone.utc).isoformat()
        update_state(
            last_backup_time=now_iso,
            last_backup_status="ok",
            last_session_id=session_id,
        )
        # 取最后200字符作为摘要；附带CH阶段状态（ok/skipped及原因）保持可见性
        summary = result.stdout[-200:] if result.stdout else ""
        ch_status = load_state().get("last_ch_backup_status", "unknown")
        return ReconcileResult(
            action="auto_committed",
            detail=f"backup ok (clickhouse={ch_status}): {summary}",
        )
    if result.returncode == 2:
        # CH阶段失败但代码/PG/SQLite/CH配置同步成功（backup.ps1已持久化last_ch_backup_*
        # 到backup_state.json）。8h代码备份计时照常推进；CH 24h计时仅在成功时推进
        # （失败在下一个调度窗口重试）。返回warn使失败在commit/merge时可见——
        # CH失败禁止静默跳过（2026-07-19事件：两次自动备份记录ok但CH未备份）。
        now_iso = datetime.now(timezone.utc).isoformat()
        update_state(
            last_backup_time=now_iso,
            last_backup_status="ch_failed",
            last_session_id=session_id,
        )
        ch_err = load_state().get("last_ch_backup_error", "unknown")
        return ReconcileResult(
            action="warn",
            detail=f"backup ok but ClickHouse stage failed: {ch_err}",
        )
    update_state(last_backup_status="failed")
    err_summary = result.stderr[-200:] if result.stderr else result.stdout[-200:]
    return ReconcileResult(
        action="warn",
        detail=f"backup failed (exit={result.returncode}): {err_summary}",
    )


def _reconcile(committed_files: list[str], session_id: str) -> Any:
    """向后兼容包装：委托给 reconcile()。"""
    return reconcile(committed_files, session_id)


def make_backup_reconciler(project_root: Path | None = None):
    """工厂函数：创建backup reconciler spec。

    Args:
        project_root: 项目根路径（默认自动检测）

    Returns:
        ReconcilerSpec（含 gate_id/trigger/reconcile/priority）
    """
    global PROJECT_ROOT, STATE_FILE, CONFIG_FILE
    if project_root is not None:
        PROJECT_ROOT = Path(project_root)
        CONFIG_FILE = PROJECT_ROOT / "scripts" / "backup" / "backup_config.yaml"
        STATE_FILE = PROJECT_ROOT / "data" / "databases" / "backup_state.json"

    try:
        from zephyr.governance.audit.reconciliation_registry import ReconcilerSpec
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
        trigger=trigger,
        reconcile=reconcile,
        priority=200,  # 低优先级（晚于其他reconciler执行）
        file_ops=frozenset({"read", "write"}),
    )


if __name__ == "__main__":
    # 手动测试入口
    spec = make_backup_reconciler()
    print(f"gate_id={spec.gate_id}, priority={spec.priority}")
    print(f"trigger(['{PROJECT_ROOT / 'src' / 'test.py'}']) = {spec.trigger([str(PROJECT_ROOT / 'src' / 'test.py')])}")
