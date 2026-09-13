#!/usr/bin/env python
# [BLUEPRINT] MOD-BT-033 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.compare_state_dualrun
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.data.ch_reader
# [CONSUMERS] TDM AGG 消费切换判据（agg-switch-design §3：连续 5 交易日零缺勤+当日更新）
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] 只读对照（旧 HMM dominant vs 新锚定档 vs L1 shrinkage 三分位），零写入零判定——
#              切换裁决权在 agg-switch-design §3 预注册判据+Owner 门位
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 表缺失/空->exit 1
# [TESTS] 手动 CLI（切换判据观察工具）
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: 双轨并行观察 CLI（切换判据观察工具，每日手动或巡检调用）
"""compare_state_dualrun.py — 新旧状态双轨并行对照（TDM AGG 切换判据观察工具）。

每日并排三路：旧 HMM 7 态 dominant（regime_snapshot_history）× 新锚定四档
（regime_state_anchored）× L1 shrinkage 三分位，输出：
    ① 两源数据新鲜度（最新 trade_date，切换判据①：连续 5 交易日当日更新）
    ② 新旧态交叉矩阵（语义对照观察）
    ③ 锚定档 × shrinkage 分位一致率（L1 合流去重的实证观察）

用法::

    python scripts/backtest/compare_state_dualrun.py            # 近 30 交易日对照
    python scripts/backtest/compare_state_dualrun.py --days 5   # 近 5 日
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))

from zephyr.data import ch_reader  # noqa: E402

_SQL_OLD = (
    "SELECT trade_date, dominant, shrinkage FROM c1_backtest.regime_snapshot_history "
    "WHERE trade_date >= {since} ORDER BY trade_date"
)
_SQL_NEW = (
    "SELECT trade_date, dominant FROM c1_backtest.regime_state_anchored "
    "WHERE trade_date >= {since} ORDER BY trade_date"
)


def _q(sql: str, cols: list[str]) -> pd.DataFrame | None:
    tsv = ch_reader.query(sql)
    if not tsv or not tsv.strip():
        return None
    rows = [line.split("\t") for line in tsv.strip().split("\n")]
    return pd.DataFrame(rows, columns=cols)


def main() -> int:
    parser = argparse.ArgumentParser(description="新旧状态双轨对照（切换判据观察）")
    parser.add_argument("--days", type=int, default=30)
    args = parser.parse_args()

    old = _q(_SQL_OLD.format(since="(today() - INTERVAL " + str(args.days) + " DAY)"), ["td", "v1", "v2"])
    new = _q(_SQL_NEW.format(since="(today() - INTERVAL " + str(args.days) + " DAY)"), ["td", "v1"])
    if old is None or new is None:
        print("FAIL: 双轨任一源无数据（old=%s new=%s）", old is not None, new is not None)
        return 1

    print("=== ① 数据新鲜度（切换判据①：连续 5 交易日当日更新）===")
    print(f"旧 HMM 源最新: {old['td'].max()} | 新锚定源最新: {new['td'].max()} | today={pd.Timestamp.today().date()}")

    m = pd.merge(old, new, on="td", suffixes=("_old", "_new"))
    print(f"\n=== ② 新旧态交叉矩阵（{len(m)} 日）===")
    print(pd.crosstab(m["v1_old"], m["v1_new"]))

    m["shrinkage"] = pd.to_numeric(m["v2"], errors="coerce")
    m = m.dropna(subset=["shrinkage"])
    if m["shrinkage"].nunique() >= 3:
        m["sh_q"] = pd.qcut(m["shrinkage"], 3, labels=["Q1谨慎", "Q2中", "Q3宽松"])
        print("\n=== ③ 锚定档 × L1 谨慎度三分位（合流去重观察）===")
        print(pd.crosstab(m["v1_new"], m["sh_q"]))
        hi_vol_states = {"r1", "r4"}
        m["hi"] = m["v1_new"].isin(hi_vol_states)
        agree = (m.loc[m["hi"], "sh_q"] == "Q1谨慎").mean()
        print(f"\n高波动档(r1+r4)日中 L1 同判谨慎(Q1)占比: {agree:.1%}（合流去重一致率观察）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
