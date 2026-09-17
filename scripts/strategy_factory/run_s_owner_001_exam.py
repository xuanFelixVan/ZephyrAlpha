# [BLUEPRINT] MOD-SOWNER-001 | docs/03_modules/_domain_ashare_signal/blueprint.md
# [MODULE] scripts.strategy_factory.run_s_owner_001_exam
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.strategy_factory.owner_band_t.exam; zephyr.strategy_factory.owner_band_t.data_loader
# [CONSUMERS] data/backtest_artifacts/runs/S-OWNER-001-e4/（E4 考试档案）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 考试唯一执行入口；OOS 单次（summary.json 已存在时拒绝重跑，防复试图救）；产物落 data/backtest_artifacts/runs/
# [MODIFY-GUARD] 冻结文档 e4_freeze_s_owner_001_300etf_band_t.md
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SystemExit(2)(OOS 已存在拒绝重跑)
# [TESTS] tests/strategy_factory/test_s_owner_001_exam.py
# [A_module] module_id=MOD-SOWNER-001 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""S-OWNER-001 E4 考试执行入口（用法: python scripts/strategy_factory/run_s_owner_001_exam.py）。

防复试图救: 默认 out 目录已含 summary.json 时退出（--force 仅供诊断重算，产物另存时间戳目录）。
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
OUT_DIR = _REPO / "data" / "backtest_artifacts" / "runs" / "S-OWNER-001-e4"


def main() -> int:
    ap = argparse.ArgumentParser(description="S-OWNER-001 E4 exam runner")
    ap.add_argument("--force", action="store_true", help="诊断重算（产物另存时间戳目录，不覆盖首次出证）")
    args = ap.parse_args()

    out = OUT_DIR
    if (out / "summary.json").exists() and not args.force:
        print(f"[EXAM] OOS 出证已存在: {out / 'summary.json'} —— OOS 单次纪律，拒绝重跑")
        return 2
    if args.force:
        out = out.with_name(f"{out.name}-rerun-{time.strftime('%Y%m%d-%H%M%S')}")

    from zephyr.strategy_factory.owner_band_t.data_loader import build_panel
    from zephyr.strategy_factory.owner_band_t.exam import run_full_exam

    t0 = time.time()
    panel = build_panel()
    print(f"[EXAM] panel ready: idx={len(panel['idx'])} etf_days={len(panel['etf'])} hourly={len(panel['hourly'])} ({time.time()-t0:.1f}s)")
    summary = run_full_exam(out, panel)
    print(f"[EXAM] verdict={summary['verdict']} ({time.time()-t0:.1f}s) -> {out / 'summary.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
