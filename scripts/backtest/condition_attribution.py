# [BLUEPRINT] MOD-BT-COND-ATTR | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.condition_attribution
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] numpy; pandas; zephyr.backtest.regime_validation.condition_package
# [CONSUMERS] GPU T1/T2 结果判读（分层键归因）；总指挥晨报（胞级主效应表）
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 只读归因零重跑：输入=grid run 的 net_returns 产物+离线条件包（load_pack 禁 CH 依赖）；只统计达标胞（cell_eligible=True），未达标日期进 residual 行单独披露（禁当独立样本计 n）；多重检验口径=每胞 sharpe 仅作分层观察非独立判据（判据仍=全窗成本门，禁胞级挑优）；fail-closed：net_returns 文件缺失/日期列缺失/包目录缺失即抛
# [MODIFY-GUARD] tests/backtest/test_condition_attribution.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] FileNotFoundError(产物/包缺失)；KeyError(日期列)；ValueError(零重叠日)
# [TESTS] tests/backtest/test_condition_attribution.py
# [TTL] permanent
# [A_module] module_id=MOD-BT-COND-ATTR | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
"""条件胞归因（T1/T2 判读端）：把 grid run 的逐日净收益按条件胞分层出主效应表。

设计口径（Owner 裁决①分层 + precheck §2.5）：全窗跑批（1,570 可条件化日）→ 逐日净收益
join 条件包（MOD-BT-COND-PACKAGE）→ 达标胞（9 胞）分层 sharpe/年化/占比；胞级数字仅作
分层观察（禁挑优入判据），判据仍=全窗五档成本门。
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from zephyr.backtest.regime_validation.condition_package import load_pack


def attribute_run(run_dir: str | Path, pack_dir: str | Path) -> pd.DataFrame:
    """读 grid run 产物（summary.json + net_returns.*）× 条件包 → 胞级主效应表。

    net_returns 产物=逐日净收益宽表（index=trade_date）；多列=多格点时按列逐格点归因，
    输出长表 [recipe, cell_id, days, sharpe_cell, ann_ret_cell, weight_pct]。
    """
    run = Path(run_dir)
    summary = json.loads((run / "summary.json").read_text(encoding="utf-8"))
    nr_path = Path(summary["net_returns_file"])
    if not nr_path.exists():
        nr_path = run / "net_returns.parquet"
    if not nr_path.exists():
        raise FileNotFoundError(f"net_returns 产物缺失: {run}")
    nr = pd.read_parquet(nr_path) if nr_path.suffix == ".parquet" else pd.read_csv(nr_path, index_col=0)
    nr.index = pd.to_datetime(nr.index)
    nr.index.name = "date"

    pack = load_pack(pack_dir)
    joined = nr.join(pack.frame.set_index("date")[["cell_id", "cell_eligible"]], how="inner")
    if joined.empty:
        raise ValueError("净收益与条件包零重叠日——窗口口径不一致")

    rows: list[dict] = []
    total_days = int(len(joined))
    for recipe in nr.columns:
        for cell_id, grp in joined.groupby("cell_id", dropna=True):
            if not bool(grp["cell_eligible"].iloc[0]):
                continue
            r = grp[recipe].astype(float)
            days = int(len(r))
            sharpe = float(r.mean() / r.std(ddof=1) * np.sqrt(252)) if r.std(ddof=1) > 0 else 0.0
            rows.append(
                {
                    "recipe": str(recipe),
                    "cell_id": str(cell_id),
                    "days": days,
                    "sharpe_cell": round(sharpe, 4),
                    "ann_ret_cell": round(float(r.mean() * 252), 6),
                    "weight_pct": round(100.0 * days / total_days, 2),
                }
            )
    # 未达标日残差披露行（不进判据，只报覆盖率）
    residual = joined[~joined["cell_eligible"]]
    out = pd.DataFrame(rows).sort_values(["recipe", "sharpe_cell"], ascending=[True, False])
    if not out.empty:
        out.attrs["residual_days"] = int(len(residual))
        out.attrs["total_days"] = total_days
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="条件胞归因（T1/T2 判读端，只读零重跑）")
    ap.add_argument("--run-dir", required=True, help="grid run 目录（含 summary.json）")
    ap.add_argument("--pack-dir", required=True, help="条件包目录（condition_pack_daily.csv.gz）")
    ap.add_argument("--out", default="", help="输出 CSV 路径（默认 run_dir/condition_attribution.csv）")
    args = ap.parse_args()
    table = attribute_run(args.run_dir, args.pack_dir)
    out = Path(args.out) if args.out else Path(args.run_dir) / "condition_attribution.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(out, index=False)
    print(f"OK rows={len(table)} residual_days={table.attrs.get('residual_days')} -> {out}")
    return 0


# noqa: m11-perm-manual-legitimate  T1/T2 判读端跑批件: CLI 手动触发与 c4_batch_screen 同类，非常驻永久系统（无常驻状态/无自动循环），每次调用为一次有界归因作业
if __name__ == "__main__":
    raise SystemExit(main())
