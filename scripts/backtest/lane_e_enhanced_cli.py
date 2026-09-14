# [BLUEPRINT] MOD-BT-090 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.lane_e_enhanced_cli
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] lane_e_enhanced（同目录）；zephyr.backtest.run_archive
# [CONSUMERS] 车道 E 分布预测完整化 CLI 入口
# [STARTUP] manual
# [INVARIANTS] 只读校验；三模型对比矩阵报告
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SystemExit
# [TESTS] tests/backtest/test_lane_e_enhanced.py
# [A_module] module_id=MOD-BT-090 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""车道 E 分布预测增强 CLI——三模型 IS+OOS 对比实验入口。"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backtest" / "translated"))

from lane_e_enhanced import run_experiment  # noqa: E402

from zephyr.data.ch_config import ensure_ch_env_loaded  # noqa: E402


class _Engine:
    @staticmethod
    def load_index(symbol, start, end, fields):
        from zephyr.data.ch_writer import get_client_strict

        cli = get_client_strict()
        cols = ", ".join(fields)
        rows = cli.execute(
            f"SELECT trade_date, {cols} FROM c1_market.kline_index "
            f"WHERE symbol='{symbol}' AND trade_date >= '{start}' AND trade_date <= '{end}' "
            f"ORDER BY trade_date"
        )
        import pandas as pd
        df = pd.DataFrame(rows, columns=["trade_date"] + list(fields))
        df["trade_date"] = pd.to_datetime(df["trade_date"])
        for c in fields:
            df[c] = df[c].astype(float)
        return df.set_index("trade_date")


def main() -> int:
    ap = argparse.ArgumentParser(description="车道 E 分布预测增强——三模型对比实验")
    ap.add_argument("--is-start", default="2020-01-01")
    ap.add_argument("--is-end", default="2023-12-31")
    ap.add_argument("--oos-start", default="2024-01-01")
    ap.add_argument("--oos-end", default="2026-06-30")
    args = ap.parse_args()

    ensure_ch_env_loaded()

    print("=== 车道 E 分布预测增强实验 ===")
    print(f"IS: {args.is_start}..{args.is_end} | OOS: {args.oos_start}..{args.oos_end}")

    all_results = {}
    for label, lo, hi in [
        ("IS_2020_2023", args.is_start, args.is_end),
        ("OOS_2024_2026", args.oos_start, args.oos_end),
    ]:
        print(f"\n--- {label} ({lo}..{hi}) ---")
        r = run_experiment(_Engine, lo, hi, models=["linear_qr", "gbr_quantile", "lgbm_quantile"])
        all_results[label] = r
        for mtype, mres in r["models"].items():
            print(f"  {mtype}: inside={mres['coverage_inside']:.4f} width={mres['interval_mean_width']:.5f} pin50={mres['pinball_median']:.6f}")

    print(json.dumps(all_results, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
