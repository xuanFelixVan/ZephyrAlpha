# [BLUEPRINT] MOD-INF-005 | docs/03_modules/_domain_governance/governance_automation/blueprint.md | §
# [MODULE] scripts.construction.start_brain
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.infrastructure.__init__
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
# [TTL] permanent
"""
start_brain.py — ZephyrAlpha 系统大脑一键启动
===============================================
⚠️ 定时调度已废除（2026-06-26裁定）：CircadianScheduler.start()/register_task()/
stop()/save_state() 已改为 no-op，_loop() 已删除。start_brain.py 现以 --once 单次
执行模式为默认：执行 boot() → reconcile() → shutdown() → 退出，不再常驻循环。

启动 AutoRuntime Core，运行 MAPE-K 调和循环，
AutoTaskGenerator 扫描项目文件 → 生成推理任务 → 送进 GPU。

用法:
    python scripts/construction/start_brain.py                  # 单次 boot 后退出（默认 --once 模式）
    python scripts/construction/start_brain.py --once           # 显式单次调和后退出
    python scripts/construction/start_brain.py --no-generate    # 跳过自动任务生成
"""

from __future__ import annotations

import argparse
import signal
import sys
import time
from pathlib import Path

from zephyr.shared.contracts.runtime_types import RuntimeConfig
from zephyr.trading.auto_runtime_core import AutoRuntimeCore
from zephyr.trading.auto_task_generator import AutoTaskGenerator

# bootstrap: 定位 scripts/governance/ 以 import _shared.constants（REPO_ROOT SSoT 真源）
_GOV_DIR = str(Path(__file__).resolve().parents[1] / "governance")
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import REPO_ROOT  # noqa: E402

PROJECT_ROOT = REPO_ROOT


def main() -> None:
    parser = argparse.ArgumentParser(description="ZephyrAlpha 系统大脑")
    parser.add_argument("--once", action="store_true", help="单次调和后退出（默认行为，保留以兼容旧调用）")
    parser.add_argument("--interval", type=float, default=10.0, help="已废弃，调度机制已废除（保留以兼容旧调用）")
    parser.add_argument("--no-onboard", action="store_true", help="跳过自动接入扫描")
    parser.add_argument("--no-generate", action="store_true", help="跳过自动任务生成")
    parser.add_argument("--batch", type=int, default=12, help="每批推理任务数")
    args = parser.parse_args()

    config = RuntimeConfig(poll_interval=args.interval)
    core = AutoRuntimeCore(config)

    generator: AutoTaskGenerator | None = None
    if not args.no_generate:
        generator = AutoTaskGenerator(PROJECT_ROOT, max_batch=args.batch)

    print("=" * 60)
    print("  ZephyrAlpha AutoRuntime Core — 系统大脑")
    if generator:
        print(f"  AutoTaskGenerator: 活跃 (batch={args.batch})")
    print("=" * 60)

    boot_report = core.boot()

    if not boot_report.success:
        print(f"\n[FAIL] Boot 失败: {boot_report.errors}")
        sys.exit(1)

    print(f"\n[OK] Boot: {boot_report.steps_completed} 步骤")
    if boot_report.components_started:
        print(f"     已启动: {', '.join(boot_report.components_started)}")
    print()

    # 定时调度已废除（2026-06-26裁定）：默认 --once 单次执行模式，不再常驻循环。
    # CircadianScheduler.start()/register_task()/stop()/save_state() 已改为 no-op。
    # 保留 signal 处理（--once 模式也支持 Ctrl+C 中断）
    def _signal_handler(sig: int, frame: object) -> None:
        print("\n正在安全关闭...")
        raise KeyboardInterrupt

    signal.signal(signal.SIGINT, _signal_handler)

    try:
        _run_cycle(core, generator, args, cycle=0)
        report = core.reconcile()
        _print_brief(core, generator, report, cycle=0)
    except KeyboardInterrupt:
        pass

    core.shutdown()
    print("\n[OK] 关闭完成")
    print("Goodbye.")


def _run_cycle(
    core: AutoRuntimeCore, generator: AutoTaskGenerator | None, args: argparse.Namespace, cycle: int
) -> None:
    if not args.no_onboard:
        _auto_onboard(core)
    if generator and not args.no_generate and core._local_scheduler is not None:
        submitted = generator.generate_and_submit(core._local_scheduler, force=True)
        pending = core._local_scheduler.pending_count
        queue = max(0, submitted - pending)
        print(f"[GEN] 提交={submitted} 待处理={pending} 剩余队列≈{queue}")
        print("  (等待任务完成...)", flush=True)
        for _ in range(6):
            time.sleep(5)
            done = len(core._local_scheduler._results)
            remaining = core._local_scheduler.pending_count
            if remaining == 0 and done > 0:
                break
        for tid, t in list(core._local_scheduler._results.items())[:5]:
            status_icon = "OK" if t.status == "completed" else t.status.upper()
            preview = str(t.result)[:80] if t.result else (t.error or "")
            print(f"  {tid}: {status_icon} → {preview}")


def _auto_onboard(core: AutoRuntimeCore) -> None:
    try:
        unregistered = core.onboarding_scanner.diff_registered()
        if unregistered and len(unregistered) < 50:
            print(f"[ONBOARD] {len(unregistered)} 未注册模块")
    except Exception:
        pass


def _print_brief(core: AutoRuntimeCore, generator: AutoTaskGenerator | None, report, cycle: int) -> None:
    gen_stats = generator.stats if generator else {}
    sched_stats = core._local_scheduler.stats if core._local_scheduler else {}
    orphan_pct = report.orphan_rate * 100 if hasattr(report, "orphan_rate") else 0
    print(f"\n调和: active={report.active} orphan={orphan_pct:.0f}%")
    if gen_stats:
        print(f"生成: {gen_stats.get('generated', 0)} 提交: {gen_stats.get('submitted', 0)}")
    if sched_stats:
        print(f"调度: done={sched_stats.get('completed', 0)} fail={sched_stats.get('failed', 0)}")


if __name__ == "__main__":
    main()
