# [BLUEPRINT] MOD-INF-005 | docs/03_modules/_domain_governance/governance_automation/blueprint.md | §
# [MODULE] scripts.construction.local_layer_daemon
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__; zephyr.infrastructure.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
"""
local_layer_daemon.py — L2 本地模型层守护进程（薄包装）
========================================================
已迁移到 AutoRuntime Core。本文件保留向后兼容。

用法（不变）:
    python local_layer_daemon.py              # 前台运行
    python local_layer_daemon.py --once       # 只跑一遍
    python local_layer_daemon.py --no-demo    # 跳过演示
    python local_layer_daemon.py --interval 30

新方式（推荐）:
    python -m zephyr.autonomy_core.runtime                  # 完整 AutoRuntime Core
    python -m zephyr.autonomy_core.runtime --once           # 单次调和
"""

from __future__ import annotations

import sys


def main() -> None:
    try:
        from zephyr.infrastructure.config.runtime_config import RuntimeConfig
        from zephyr.infrastructure.runtime.auto_runtime_core import AutoRuntimeCore
    except ImportError:
        _fallback()
        return

    import argparse

    parser = argparse.ArgumentParser(description="L2 本地模型层守护进程 (AutoRuntime Core)")
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--interval", type=float, default=10.0)
    parser.add_argument("--no-demo", action="store_true")
    args = parser.parse_args()

    config = RuntimeConfig(poll_interval=args.interval)
    core = AutoRuntimeCore(config)
    boot_report = core.boot()

    if not boot_report.success:
        print(f"Boot failed: {boot_report.errors}")
        sys.exit(1)

    print(f"AutoRuntime Core booted: {boot_report.steps_completed} steps")
    print(core.status_panel())

    if not args.no_demo:
        try:
            from zephyr.governance.knowledge_management.vector_memory.local_model_scheduler import LocalModelScheduler

            scheduler = LocalModelScheduler()
            scheduler.ensure_models()
            scheduler.start()
            print("L2 demo: LocalModelScheduler started")
        except Exception as e:
            print(f"L2 demo skipped: {e}")

    import signal

    shutdown = False

    def _sig(sig: int, frame: object) -> None:
        nonlocal shutdown
        shutdown = True

    signal.signal(signal.SIGINT, _sig)

    if args.once:
        report = core.reconcile()
        print(f"Reconcile: active={report.active} degraded={report.degraded}")
    else:
        while not shutdown:
            import time

            time.sleep(config.poll_interval)
            report = core.reconcile()
            print(f"[{time.strftime('%H:%M:%S')}] active={report.active} orphan_rate={report.orphan_rate:.1%}")

    shutdown_report = core.shutdown()
    print(f"Shutdown: {shutdown_report.steps_completed} steps")


def _fallback() -> None:
    import signal
    import time

    from zephyr.governance.knowledge_management.vector_memory.local_model_scheduler import LocalModelScheduler

    print("Fallback: running LocalModelScheduler directly (AutoRuntime Core not available)")
    scheduler = LocalModelScheduler()
    scheduler.ensure_models()
    scheduler.start()

    running = True

    def _sig(sig: int, frame: object) -> None:
        nonlocal running
        running = False

    signal.signal(signal.SIGINT, _sig)

    while running:
        time.sleep(10)

    scheduler.stop()
    print("Stopped.")


if __name__ == "__main__":
    main()
