# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §3
# [MODULE] scripts.ops.auto_fix_cron
# [DOMAIN]
# [DEPENDENCIES]
# [CONSUMERS] crontab
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] MUST使用flock单实例锁;MUST支持--dry-run;MUST支持--warn-only
# [MODIFY-GUARD] blueprint.md §3
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] Returns exit code 0 on success, 1 on error
# [TESTS] tests/test_auto_fix_cron.py
# [A_module] module_id=MOD-INF_auto_fix_cron | layer=script | stability=evolving | safety=M | ai_autonomy=ai_modifiable

"""F15 自动修复引擎 cron 定时启动脚本.

用法:
    python scripts/ops/auto_fix_cron.py --dry-run --warn-only
    python scripts/ops/auto_fix_cron.py --action-type drift_fixer
    python scripts/ops/auto_fix_cron.py --config config/auto_fix_cron.yaml

功能:
    1. 使用 flock 单实例锁防止进程堆积
    2. 读取配置文件确定修复器类型和目标
    3. 调用 AutoFixEngine 执行修复
    4. 输出结果到日志目录
"""
from __future__ import annotations

import argparse
import logging
import os
import sys
import tempfile
from pathlib import Path

logger = logging.getLogger("auto_fix_cron")

LOCK_FILE = os.path.join(tempfile.gettempdir(), "zephyr_auto_fix_cron.lock")
DEFAULT_CONFIG_PATH = "config/auto_fix_cron.yaml"
LOG_DIR = "logs/auto_fix"


def _acquire_lock() -> int | None:
    """尝试获取 flock 单实例锁.

    Returns:
        文件描述符(成功)或 None(已有实例运行)
    """
    try:
        import msvcrt

        lock_fd = os.open(LOCK_FILE, os.O_CREAT | os.O_RDWR)
        try:
            msvcrt.locking(lock_fd, msvcrt.LK_NBLCK, 1)
            return lock_fd
        except OSError:
            os.close(lock_fd)
            return None
    except ImportError:
        import fcntl

        lock_fd = os.open(LOCK_FILE, os.O_CREAT | os.O_RDWR)
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return lock_fd
        except OSError:
            os.close(lock_fd)
            return None


def _release_lock(lock_fd: int) -> None:
    """释放 flock 单实例锁."""
    try:
        import msvcrt

        msvcrt.locking(lock_fd, msvcrt.LK_UNLCK, 1)
    except ImportError:
        import fcntl

        fcntl.flock(lock_fd, fcntl.LOCK_UN)
    os.close(lock_fd)


def _load_config(config_path: str) -> dict:
    """加载配置文件."""
    path = Path(config_path)
    if not path.exists():
        return {"action_type": "drift_fixer", "targets": []}
    try:
        import yaml

        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {"action_type": "drift_fixer", "targets": []}


def _ensure_log_dir() -> Path:
    """确保日志目录存在."""
    log_path = Path(LOG_DIR)
    log_path.mkdir(parents=True, exist_ok=True)
    return log_path


def run_cron(
    action_type: str,
    targets: list[str],
    dry_run: bool = False,
    warn_only: bool = False,
) -> int:
    """执行 cron 修复任务.

    Args:
        action_type: 修复器类型
        targets: 修复目标列表
        dry_run: 仅模拟不实际执行
        warn_only: 仅警告不退出

    Returns:
        0=成功, 1=失败
    """
    if not targets:
        logger.info("No targets specified, nothing to do")
        return 0

    sys.path.insert(0, "src")
    try:
        from zephyr.infrastructure.auto_fix_engine.engine import AutoFixEngine
    except ImportError as e:
        logger.error("Cannot import AutoFixEngine: %s", e)
        return 0 if warn_only else 1

    engine = AutoFixEngine()
    exit_code = 0

    for target in targets:
        try:
            action = engine.fix(action_type, target, dry_run=dry_run)
            logger.info(
                "Fix %s -> %s: %s",
                target,
                action.status.value,
                action.action_id,
            )
            if action.status.value.lower() == "failed" and not warn_only:
                exit_code = 1
        except Exception as e:
            logger.error("Fix %s failed: %s", target, e)
            if not warn_only:
                exit_code = 1

    return exit_code


def main() -> int:
    parser = argparse.ArgumentParser(description="F15 Auto Fix Cron")
    parser.add_argument(
        "--action-type",
        default="drift_fixer",
        help="Fixer action type",
    )
    parser.add_argument(
        "--config",
        default=DEFAULT_CONFIG_PATH,
        help="Config file path",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry run mode, no actual fixes",
    )
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="Warn only, do not exit with error",
    )
    parser.add_argument(
        "--target",
        action="append",
        default=[],
        help="Target path (can be repeated)",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    lock_fd = _acquire_lock()
    if lock_fd is None:
        logger.warning("Another instance is running, exiting")
        return 0

    try:
        config = _load_config(args.config)
        action_type = args.action_type or config.get("action_type", "drift_fixer")
        targets = args.target if args.target else config.get("targets", [])

        _ensure_log_dir()
        return run_cron(
            action_type=action_type,
            targets=targets,
            dry_run=args.dry_run,
            warn_only=args.warn_only,
        )
    finally:
        _release_lock(lock_fd)


if __name__ == "__main__":
    sys.exit(main())
