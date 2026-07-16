# [BLUEPRINT] MOD-INF-005 | docs/03_modules/_domain_governance/governance_automation/blueprint.md | §
# [MODULE] scripts.construction.local_layer_daemon
# [DOMAIN] D_GOVERNANCE
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
# [DEPRECATED] trae_053 v2.0.0: 常驻 while 循环模式已废除。仅保留 --once 单次执行模式。
# [TTL] permanent
# 原声明"已迁移到 zephyr.autonomy_core.runtime"——该目标模块实际不存在，声明作废。
# 如需 AutoRuntime Core，直接使用 src/zephyr/trading/auto_runtime_core.py。
"""
local_layer_daemon.py — L2 本地模型层守护进程（薄包装，DEPRECATED）
================================================================
trae_053 v2.0.0: 常驻 while 循环模式已废除，仅保留 --once 单次执行模式。

用法:
    python local_layer_daemon.py --once       # 单次调和（合规）
    python local_layer_daemon.py --no-demo    # 跳过演示（隐含 --once）
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
            from zephyr.integration.local_model.local_model_scheduler import LocalModelScheduler

            scheduler = LocalModelScheduler()
            scheduler.ensure_models()
            print("L2 demo: LocalModelScheduler models ensured (start() suppressed per trae_053 v2.0.0)")
        except Exception as e:
            print(f"L2 demo skipped: {e}")

    # trae_053 v2.0.0: 常驻 while 循环已废除，仅执行单次 reconcile。
    report = core.reconcile()
    print(f"Reconcile: active={report.active} degraded={report.degraded}")

    shutdown_report = core.shutdown()
    print(f"Shutdown: {shutdown_report.steps_completed} steps")


def _fallback() -> None:
    # trae_053 v2.0.0: 常驻 daemon 模式已废除，fallback 不再启动后台线程。
    print("Fallback: AutoRuntime Core not available; 常驻模式已废除 (trae_053 v2.0.0)，请使用 --once 单次执行。")
    sys.exit(1)


if __name__ == "__main__":
    main()
