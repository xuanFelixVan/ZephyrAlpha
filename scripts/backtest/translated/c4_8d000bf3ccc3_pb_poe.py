# [BLUEPRINT] MOD-BT-091 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_8d000bf3ccc3_pb_poe
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.data.ch_config; numpy; pandas
# [CONSUMERS] C4 快筛批测（scripts/backtest/c4_batch_screen.py）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] PIT（财务公告门+估值 ≤T-1）；成本=冻结土规
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(数据缺失)
# [TESTS] tests/backtest/test_c4_batch_smoke.py
# [A_module] module_id=MOD-BT-091 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 翻译 092: PB-POE+双均线（原文: 2024年度精选策略1/65.PB-POE+双均线）。

原文逻辑: 每 30 交易日调仓：market_cap>800(亿) + pb_ratio<20 + roe>7(%)，
  按 (roe-pb) 降序前 100；MA10>MA60 且 close>MA60 双均线确认 → 前 5 等权。
译文实现: roe=np_q/equity×100（DS-230 公告门）；市值=total_mv/10000 亿（daily_basic 万元→亿）；
  双均线 HFQ 收盘；等权 5 只。
因子拆解: PB/ROE/均线——公开因子组不登记 factor_registry。
翻译差异声明:
  D1 股票池: 全 A（HFQ 表）剔 ST
  D2 执行时点: 原文开盘 → T 日收盘
  D3 roe 口径: 聚宽 indicator.roe（季报）→ DS-230 单季 np_q/equity×100 近似
  D4 因子登记: 公开因子组不登记
  D5 框架样板: 壳不翻译

[KNOWLEDGE_EFFECTIVE_FROM] 2026-09-14 | 源=策略原文公开发布日 | 生成=AI 会话（取晚者）
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import numpy as np
import pandas as pd

from _c4_engine import (emit, filter_st, fin_snapshot, load_px, load_st_flags, load_valuation,
                        run_backtest, wide)

logger = logging.getLogger(__name__)

STRATEGY_ID = "CAND-8d000bf3ccc3"
WINDOW_KIND = "stock"
_TOP_N, _REBAL = 5, 30


def build(start: str, end: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    load_start = str(pd.Timestamp(start) - pd.Timedelta(days=420))[:10]
    px = load_px(load_start, end, fields=("close",))
    closes = filter_st(wide(px).ffill(), load_st_flags(load_start, end))
    val = load_valuation(load_start, end, fields=("pb", "total_mv"))
    pb = val["pb"].reindex(closes.index).reindex(columns=closes.columns)
    mv_yi = (val["total_mv"] / 10000.0).reindex(closes.index).reindex(columns=closes.columns)  # 万元→亿
    ma10, ma60 = closes.rolling(10).mean(), closes.rolling(60).mean()

    dates = closes.index[(closes.index >= pd.Timestamp(start)) & (closes.index <= pd.Timestamp(end))]
    weights = pd.DataFrame(0.0, index=dates, columns=closes.columns)
    last_rebal = -999
    holdings: dict[str, float] = {}
    for k, dt in enumerate(dates):
        px_row = closes.iloc[k]
        for s in list(holdings):
            v = px_row.get(s)
            if pd.isna(v):  # 停牌/缺失持仓保留
                continue
        if k - last_rebal >= _REBAL:
            last_rebal = k
            asof = str((pd.Timestamp(dt) - pd.Timedelta(days=1)).date())
            fin = fin_snapshot(asof, metrics=("np_q", "equity_incl_minority"))
            if not fin.empty:
                roe = (fin["np_q"] / fin["equity_incl_minority"].replace(0.0, np.nan)) * 100.0
                fdf = pd.DataFrame({"roe": roe})
                prow_mv = mv_yi.shift(1).reindex([dt]).iloc[0]
                prow_pb = pb.shift(1).reindex([dt]).iloc[0]
                cand = []
                for sym in closes.columns:
                    if sym not in fdf.index:
                        continue
                    mvv, pbv, rv = prow_mv.get(sym), prow_pb.get(sym), fdf.loc[sym, "roe"]
                    if any(pd.isna(x) for x in (mvv, pbv, rv)):
                        continue
                    if mvv > 800 and pbv < 20 and rv > 7:
                        cand.append((sym, rv - pbv))
                cand.sort(key=lambda x: -x[1])
                pool = [s for s, _ in cand[:100]]
                picks = []
                for s in pool:
                    m10 = ma10.shift(1).loc[dt].get(s)
                    m60 = ma60.shift(1).loc[dt].get(s)
                    px1 = closes.shift(1).loc[dt].get(s)
                    if all(pd.notna(x) for x in (m10, m60, px1)) and px1 > m60 and m10 > m60:
                        picks.append(s)
                    if len(picks) >= _TOP_N:
                        break
                holdings = {s: 1.0 / len(picks) for s in picks} if picks else {}
        if holdings:
            for s, w in holdings.items():
                weights.loc[dt, s] = w
    return weights, closes


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    from _c4_engine import C4_END, C4_START

    weights, closes = build(C4_START, C4_END)
    stats = run_backtest(weights, closes)
    print(json.dumps(emit(STRATEGY_ID, stats, ["D1 全A剔ST", "D2 T+1收盘", "D3 roe口径近似",
                                               "D4 公开因子不登记", "D5 壳不译"]), ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
