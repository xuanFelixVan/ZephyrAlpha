#!/usr/bin/env python
# [BLUEPRINT] MOD-BT-033 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.compare_state_dualrun
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.data.ch_reader; zephyr.data.table_registry
# [CONSUMERS] TDM AGG 切换判据（agg-switch-design section3）
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] 只读对照零写入零判定; 切换裁决权在 agg-switch-design 预注册判据+Owner 门位
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 表缺失或空数据 exit 1
# [TESTS] 手动 CLI 观察工具
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: 双轨并行观察 CLI
"""compare_state_dualrun.py 新旧状态双轨并行对照（TDM AGG 切换判据观察工具）。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))

from zephyr.data import ch_reader  # noqa: E402
from zephyr.data.table_registry import get_registry  # noqa: E402

_TBL_SNAP = "c1_backtest.regime_snapshot_history"  # noqa: 旧教枟表未注册 categories，保留硬编码
_TBL_ANCHORED = get_registry().table("backtest_regime_state_anchored")

_SQL_OLD = (
    "SELECT trade_date, dominant, shrinkage FROM " + _TBL_SNAP +
    " WHERE trade_date >= {since} ORDER BY trade_date"
)
_SQL_NEW = (
    "SELECT trade_date, dominant, vol_pct FROM " + _TBL_ANCHORED +
    " WHERE trade_date >= {since} ORDER BY trade_date"
)


def _q(sql, cols):
    tsv = ch_reader.query(sql)
    if not tsv or not tsv.strip():
        return None
    rows = [line.split("\t") for line in tsv.strip().split("\n")]
    return pd.DataFrame(rows, columns=cols)


def main():
    parser = argparse.ArgumentParser(description="新旧状态双轨对照")
    parser.add_argument("--days", type=int, default=30)
    args = parser.parse_args()
    since = "(today() - INTERVAL " + str(args.days) + " DAY)"
    old = _q(_SQL_OLD.format(since=since), ["td", "old_state", "shrinkage"])
    new = _q(_SQL_NEW.format(since=since), ["td", "new_state", "vol_pct"])
    if old is None or new is None:
        print("FAIL: dual source empty")
        return 1
    print("=== 1. freshness ===")
    print("old latest:", old["td"].max(), "| new latest:", new["td"].max())
    m = pd.merge(old, new, on="td")
    print("=== 2. cross matrix", len(m), "days ===")
    print(pd.crosstab(m["old_state"], m["new_state"]))
    m["shrinkage"] = pd.to_numeric(m["shrinkage"], errors="coerce")
    ms = m.dropna(subset=["shrinkage"])
    if ms["shrinkage"].nunique() >= 3:
        ms["sh_q"] = pd.qcut(ms["shrinkage"], 3, labels=["Q1", "Q2", "Q3"])
        print("=== 3. tier x L1 quantile ===")
        print(pd.crosstab(ms["new_state"], ms["sh_q"]))
        hi = ms[ms["new_state"].isin(["r1", "r4"])]
        if len(hi):
            agree = (hi["sh_q"] == "Q1").mean()
            print("high-vol days L1-agree-cautious ratio:", round(float(agree), 3))
    m["vol_pct"] = pd.to_numeric(m["vol_pct"], errors="coerce")
    mv = m.dropna(subset=["vol_pct"])
    if len(mv):
        mv["cap"] = (1 - 0.7 * ((mv["vol_pct"] - 0.30) / 0.70).clip(0, 1)).round(3)
        print("=== 4. gray cap curve last 10 ===")
        print(mv[["td", "new_state", "vol_pct", "cap"]].tail(10).to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
