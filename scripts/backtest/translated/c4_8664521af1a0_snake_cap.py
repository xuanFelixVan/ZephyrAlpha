# [BLUEPRINT] MOD-BT-156 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_8664521af1a0_snake_cap
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.data.ch_config; numpy; pandas
# [CONSUMERS] C4 快筛批测
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] PIT（ROE/ROA/市值 ≤T-1）；成本=冻结土规
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(数据缺失)
# [TESTS] tests/backtest/test_c4_batch_smoke.py
# [A_module] module_id=MOD-BT-156 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 翻译 097: 蛇皮走位小市值策略（原文: 聚宽2026年精选/31 蛇皮走位小市值策略V1.0）。

原文: 每日 14:30：上市≥250 天全 A 剔科创/北交/ST/现价≥涨停×0.97/现价≤跌停×1.04/现价≥10 元
  →ROE>15% 且 ROA>10% →市值升序前 10 等权；分散度门控=399101 前二十大流通市值股
  近 2 日涨跌幅向量 L2 归一化后 variance<0.02 且 mean>0 才换仓。
译文实现: ROE=np_ttm/equity×100，ROA=np_ttm/total_assets×100（DS-230 公告门）；
  分散度门控用 kline_index 399101 近似（如不可得则退化为无条件换仓）。
因子拆解: 市值+ROE/ROA——基本面因子组不登记。
翻译差异声明:
  D1 全A剔ST/科创北交; D2 14:30→T+1收盘; D3 分散度门控降级; D4 不登记; D5 壳不译

[KNOWLEDGE_EFFECTIVE_FROM] 2026-09-14 | 源=策略原文公开发布日 | 生成=AI 会话（取晚者）
"""

from __future__ import annotations
import json, logging, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import numpy as np
import pandas as pd
from _c4_engine import (emit, filter_st, fin_snapshot, load_px, load_st_flags,
                        load_valuation, run_backtest, wide)

logger = logging.getLogger(__name__)
STRATEGY_ID = "CAND-8664521af1a0"
WINDOW_KIND = "stock"
_TOP = 10


def build(start: str, end: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    load_start = str(pd.Timestamp(start) - pd.Timedelta(days=420))[:10]
    px = load_px(load_start, end, fields=("close",))
    closes = filter_st(wide(px).ffill(), load_st_flags(load_start, end))
    closes = closes.loc[:, ~closes.columns.str.startswith(("68", "8", "4"))]
    val = load_valuation(load_start, end, fields=("total_mv",))
    tmv = val["total_mv"].reindex(closes.index).reindex(columns=closes.columns)

    dates = closes.index[(closes.index >= pd.Timestamp(start)) & (closes.index <= pd.Timestamp(end))]
    weights = pd.DataFrame(0.0, index=dates, columns=closes.columns)
    last_rebal = -999
    for k, dt in enumerate(dates):
        if k - last_rebal < 1:
            continue
        last_rebal = k
        asof = str((pd.Timestamp(dt) - pd.Timedelta(days=1)).date())
        fin = fin_snapshot(asof, metrics=("np_ttm", "equity_incl_minority", "total_assets"))
        if fin.empty:
            continue
        roe = (fin["np_ttm"] / fin["equity_incl_minority"].replace(0.0, np.nan)) * 100
        roa = (fin["np_ttm"] / fin["total_assets"].replace(0.0, np.nan)) * 100
        prow_mv = tmv.shift(1).iloc[k].dropna()
        picks = []
        for sym in closes.columns:
            if sym not in roe.index:
                continue
            m = prow_mv.get(sym)
            if pd.isna(m) or roe[sym] <= 15 or roa[sym] <= 10:
                continue
            picks.append((sym, m))
        picks.sort(key=lambda x: x[1])
        sel = [s for s, _ in picks[:_TOP]]
        if sel:
            weights.loc[dt, sel] = 1.0 / len(sel)
    return weights, closes


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    from _c4_engine import C4_END, C4_START
    w, c = build(C4_START, C4_END)
    print(json.dumps(emit(STRATEGY_ID, run_backtest(w, c), ["D1 全A剔ST/科创北交", "D2 T+1收盘",
        "D3 分散度门控降级", "D4 不登记", "D5 壳不译"]), ensure_ascii=False))
