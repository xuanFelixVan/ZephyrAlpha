# [BLUEPRINT] MOD-BT-093 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_dc5b80aa3614_tsmall100
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.data.ch_config; numpy; pandas
# [CONSUMERS] C4 快筛批测（scripts/backtest/c4_batch_screen.py）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] PIT（市值/PB/ROE ≤T-1）；成本=冻结土规
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(数据缺失)
# [TESTS] tests/backtest/test_c4_batch_smoke.py
# [A_module] module_id=MOD-BT-093 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 翻译 094: TSmall-100 微盘三正（原文: 聚宽2026年精选/53 TSmall-100, 微盘三正）。

原文逻辑: 每日开盘：三正过滤（PB>0 + ROE>0 + OCF/营收>0）按总市值升序取 120 只候选，
  名单内等权持仓 100 只（1/100 总值），不在名单→清仓。
译文实现: 三正=PB>0（stock_indicator）+ ROE>0（DS-230 np_ttm/equity）+ OCF/营收>0（ocf_ttm/rev_ttm）；
  市值=total_mv 升序；T-1 截面取 120→等权 100 只；每日全量重选（高换手）。
因子拆解: 市值排序+PB/ROE/OCF 正值过滤——规模+质量因子，公开方法论不登记 factor_registry。
翻译差异声明:
  D1 股票池: 399317 指数成分→全 A 近似（成分历史缺）
  D2 执行时点: 原文开盘 → T 日收盘
  D3 "三正"口径: 聚宽 indicator.inc_return/ocf_to_revenue → DS-230 np_ttm/equity 与 ocf_ttm/rev_ttm
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

STRATEGY_ID = "CAND-dc5b80aa3614"
WINDOW_KIND = "stock"
_NPOS, _NCHOICE = 100, 120


def build(start: str, end: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    load_start = str(pd.Timestamp(start) - pd.Timedelta(days=60))[:10]
    px = load_px(load_start, end, fields=("close",))
    closes = filter_st(wide(px).ffill(), load_st_flags(load_start, end))
    val = load_valuation(load_start, end, fields=("pb", "total_mv"))
    pb = val["pb"].reindex(closes.index).reindex(columns=closes.columns)
    tmv = val["total_mv"].reindex(closes.index).reindex(columns=closes.columns)

    dates = closes.index[(closes.index >= pd.Timestamp(start)) & (closes.index <= pd.Timestamp(end))]
    weights = pd.DataFrame(0.0, index=dates, columns=closes.columns)
    last_rebal = -999
    holdings: dict[str, float] = {}
    for k, dt in enumerate(dates):
        if k - last_rebal < 1:
            # 每日调仓（原文 daily）
            pass
        last_rebal = k
        asof = str((pd.Timestamp(dt) - pd.Timedelta(days=1)).date())
        fin = fin_snapshot(asof, metrics=("np_ttm", "equity_incl_minority", "ocf_ttm", "rev_ttm"))
        prow_pb = pb.shift(1).iloc[k] if k > 0 else None
        prow_mv = tmv.shift(1).iloc[k] if k > 0 else None
        if prow_pb is None or prow_mv is None:
            continue
        # 三正过滤
        roe_pos = (fin["np_ttm"] / fin["equity_incl_minority"].replace(0.0, np.nan)) > 0
        ocf_pos = (fin["ocf_ttm"] / fin["rev_ttm"].replace(0.0, np.nan)) > 0
        pb_pos = prow_pb > 0
        passing = set()
        for sym in closes.columns:
            if sym in roe_pos.index and roe_pos[sym] and sym in ocf_pos.index and ocf_pos[sym]:
                v = prow_pb.get(sym)
                if pd.notna(v) and v > 0:
                    passing.add(sym)
        # 市值升序取前 120
        mrow = prow_mv.dropna()
        cand = [s for s in mrow.sort_values().index if s in passing][:_NCHOICE]
        # 等权前 100
        picks = cand[:_NPOS]
        holdings = {s: 1.0 / _NPOS for s in picks}
        for s, w in holdings.items():
            weights.loc[dt, s] = w
    return weights, closes


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    from _c4_engine import C4_END, C4_START

    weights, closes = build(C4_START, C4_END)
    stats = run_backtest(weights, closes)
    print(json.dumps(emit(STRATEGY_ID, stats, ["D1 399317→全A近似", "D2 T+1收盘", "D3 三正DS-230口径",
                                               "D4 公开因子不登记", "D5 壳不译"]), ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
