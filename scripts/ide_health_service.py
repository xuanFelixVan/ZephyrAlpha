# [A_module] module_id=MOD-SCR_ide_health_service | layer=script | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-032 | docs/03_modules/_cross_layer/resource-optimization-engine/blueprint.md | §new-IDE
# [MODULE] scripts.ide_health_service
# [INVARIANTS] --status不修改任何状态(只读);--start调用register_daemon后阻塞保持运行
# [MODIFY-GUARD] MOD-INF-032 §new-IDE
# [CONSUMERS] .trae/rules/project_rules.md; .trae/rules/onboarding_detail.md; AGENTS.md; docs/01_policies_and_standards/rules/trae_053_automation_dual_track.yaml
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 导入失败时打印明确错误信息并exit 1;--status守护进程未运行时exit 0并打印stopped
# [TESTS]
"""IDE健康守护进程CLI包装器

包装 src/zephyr/trading/ide_health_daemon.py，提供 --status/--start CLI 接口。
守护进程本身在应用运行时通过 register_daemon() 自动注册启动，本脚本提供
命令行查询和手动启动入口（用于 session 冷启动序列 STEP 0）。

用法:
    python scripts/ide_health_service.py --status    # 查询守护进程状态
    python scripts/ide_health_service.py --start     # 注册并启动守护进程（阻塞）
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

# 确保项目根目录在 sys.path 中
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

logger = logging.getLogger(__name__)


def _get_daemon_status() -> dict[str, str]:
    """查询守护进程状态。

    返回 {"running": "true|false", "ghost_count": "N", "detail": "..."}
    """
    try:
        from zephyr.trading.ide_health_daemon import _daemon_instance
    except ImportError as e:
        return {"running": "false", "ghost_count": "0", "detail": f"导入失败: {e}"}

    if _daemon_instance is None:
        return {"running": "false", "ghost_count": "0", "detail": "守护进程未注册"}

    running = _daemon_instance._running
    ghost_count = _daemon_instance.ghost_count
    return {
        "running": "true" if running else "false",
        "ghost_count": str(ghost_count),
        "detail": f"running={running}, ghost_count={ghost_count}",
    }


def _check_registry_status() -> dict[str, str]:
    """通过 daemon_registry 查询状态（如果可用）。"""
    try:
        from zephyr.integration.shared_08.lifecycle.daemon_registry import registry
        is_running = registry.is_running("ide_health_daemon")
        return {
            "running": "true" if is_running else "false",
            "ghost_count": "0",
            "detail": f"registry.is_running={is_running}",
        }
    except Exception:
        # registry 不可用时回退到 _daemon_instance 检查
        return _get_daemon_status()


def cmd_status() -> int:
    """--status: 查询守护进程状态。"""
    status = _check_registry_status()
    running = status["running"]
    print(f"running={running}")
    print(f"ghost_count={status['ghost_count']}")
    print(f"detail={status['detail']}")
    return 0


def cmd_start() -> int:
    """--start: 注册并启动守护进程，然后阻塞保持运行。"""
    try:
        from zephyr.trading.ide_health_daemon import register_daemon
    except ImportError as e:
        print(f"ERROR: 无法导入 ide_health_daemon: {e}", file=sys.stderr)
        return 1

    print("注册并启动 IdeHealthDaemon...")
    try:
        register_daemon()
    except Exception as e:
        print(f"ERROR: 启动失败: {e}", file=sys.stderr)
        return 1

    print("IdeHealthDaemon 已启动（Ctrl+C 退出）")
    print("守护进程每 30s 扫描一次 TRAE 幽灵窗口并自动清理")

    # 阻塞保持守护进程运行
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n收到退出信号，停止守护进程...")
        return 0


def main() -> None:
    """CLI 入口。"""
    parser = argparse.ArgumentParser(
        description="IDE健康守护进程CLI包装器（包装 src/zephyr/trading/ide_health_daemon.py）",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--status", action="store_true", help="查询守护进程状态")
    group.add_argument("--start", action="store_true", help="注册并启动守护进程（阻塞）")

    args = parser.parse_args()

    if args.status:
        sys.exit(cmd_status())
    elif args.start:
        sys.exit(cmd_start())


if __name__ == "__main__":
    main()
