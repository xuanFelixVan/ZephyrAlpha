# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] zephyr.trading.__main__
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.trading.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ORC___main__ | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
python -m zephyr.trading — AutoRuntime Core 入口
===================================================
"""

import argparse
import signal
import sys
import time

from zephyr.trading.auto_runtime_core import AutoRuntimeCore
from zephyr.trading.runtime_config import RuntimeConfig


def main() -> None:
    parser = argparse.ArgumentParser(description="ZephyrAlpha AutoRuntime Core")
    parser.add_argument("--once", action="store_true", help="run one reconcile cycle then exit")
    parser.add_argument("--no-demo", action="store_true", help="skip demo tasks")
    parser.add_argument("--no-dream", action="store_true", help="skip dream cycle")
    parser.add_argument("--interval", type=float, default=5.0, help="reconcile interval in seconds")
    args = parser.parse_args()

    config = RuntimeConfig(poll_interval=args.interval)
    if args.no_dream:
        config.enable_dream_cycle = False

    core = AutoRuntimeCore(config)
    boot_report = core.boot()

    if not boot_report.success:
        print(f"Boot failed: {boot_report.errors}")
        sys.exit(1)

    print(f"Boot OK: {boot_report.steps_completed} steps, {len(boot_report.components_started)} components")
    print(core.status_panel())

    shutdown_requested = False

    def _signal_handler(sig: int, frame: object) -> None:
        nonlocal shutdown_requested
        shutdown_requested = True

    signal.signal(signal.SIGINT, _signal_handler)
    # 5.26.5 修复：添加 SIGTERM 处理，与 SIGINT 共用 handler
    # Docker/K8s 发送 SIGTERM 优雅停止，原仅处理 SIGINT 导致容器停止时被 SIGKILL 强制终止
    signal.signal(signal.SIGTERM, _signal_handler)

    if args.once:
        report = core.reconcile()
        print(f"Reconcile: active={report.active} degraded={report.degraded} orphan_rate={report.orphan_rate:.1%}")
    else:
        print("Running... (Ctrl+C to stop)")
        while not shutdown_requested:
            try:
                time.sleep(config.poll_interval)
                report = core.reconcile()
                print(
                    f"[{time.strftime('%H:%M:%S')}] active={report.active} degraded={report.degraded} orphan_rate={report.orphan_rate:.1%}"
                )
            except KeyboardInterrupt:
                shutdown_requested = True

    shutdown_report = core.shutdown()
    print(f"Shutdown: {shutdown_report.steps_completed} steps completed")
    print("Goodbye.")


if __name__ == "__main__":
    main()
