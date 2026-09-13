# [BLUEPRINT] MOD-BT-088 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_68cc0a6b40ba_value_select
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
# [A_module] module_id=MOD-BT-088 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 翻译 089: 精选价值策略（原文: 2025年度精选策略/35 精选价值策略）。

原文逻辑: 月频。祖鲁六条选股（同 087）+ 周期行业剔除（申万 20 代码），
  流通市值降序取前 10（max_hold_stocknum=10）等权，调出即卖。
译文实现: 同 087 选股器（DS-230 公告门）；行业剔除降级（申万代码→行业映射缺，D3）；
  市值降序前 10 等权。
因子拆解: 同 087——公开基本面因子组不登记 factor_registry。
翻译差异声明:
  D1 股票池: 全 A（HFQ 表）剔 ST
  D2 执行时点: 原文开盘 → T 日收盘
  D3 行业剔除降级未实现（申万代码映射缺，已声明；剩余规则与 087 同源）
  D4 因子登记: 公开因子组不登记
  D5 框架样板: wizard 壳不翻译

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

from _c4_engine import (emit, filter_st, fin_history, load_px, load_st_flags, load_valuation,
                        run_backtest, wide)

logger = logging.getLogger(__name__)

STRATEGY_ID = "CAND-68cc0a6b40ba"
WINDOW_KIND = "stock"
_TOP_N = 10
_METRICS = ("np_q", "equity_incl_minority", "fcff_cum", "rev_q_yoy", "np_q_yoy",
            "total_current_assets", "total_current_liabilities")


def zulu_symbols(as_of: str) -> set[str]:
    h = fin_history(as_of, _METRICS)
    if h.empty:
        return set()
    h = h.assign(
        cr=h.total_current_assets / h.total_current_liabilities.replace(0.0, np.nan),
        roe_q=h.np_q / h.equity_incl_minority.replace(0.0, np.nan),
    )
    latest = h[h.report_period == h.report_period.max()]
    ok = set(latest[latest.cr > latest.cr.mean()].symbol)
    periods = sorted(h.report_period.unique())[-4:]
    for per in periods:
        sub = h[h.report_period == per]
        ok &= set(sub[sub.roe_q > sub.roe_q.mean()].symbol)
        rev = sub.rev_q_yoy * 100.0
        npg = sub.np_q_yoy * 100.0
        ok &= set(sub[(rev >= 6) & (rev <= 30)].symbol)
        ok &= set(sub[(npg >= 8) & (npg <= 50)].symbol)
    annual = h[h.report_period.dt.month == 12]
    for per in sorted(annual.report_period.unique())[-5:]:
        sub = annual[annual.report_period == per]
        ok &= set(sub[sub.fcff_cum > 0].symbol)
    return ok


def build(start: str, end: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    load_start = str(pd.Timestamp(start) - pd.Timedelta(days=60))[:10]
    px = load_px(load_start, end, fields=("close",))
    closes = filter_st(wide(px).ffill(), load_st_flags(load_start, end))
    val = load_valuation(load_start, end, fields=("circ_mv",))
    cmv = val["circ_mv"].reindex(closes.index).reindex(columns=closes.columns)

    dates = closes.index[(closes.index >= pd.Timestamp(start)) & (closes.index <= pd.Timestamp(end))]
    weights = pd.DataFrame(0.0, index=dates, columns=closes.columns)
    month5 = [d for d in dates.to_series().groupby(dates.to_period("M")).nth(4) if d in set(dates)]
    for dt in month5:
        asof = (pd.Timestamp(dt) - pd.Timedelta(days=1)).date()
        syms = zulu_symbols(str(asof))
        prow = cmv.shift(1).reindex([dt]).iloc[0]
        mkt_mean = prow.mean()
        picks = [s for s in sorted(syms & set(closes.columns))
                 if pd.notna(prow.get(s)) and prow.get(s) >= mkt_mean]
        picks.sort(key=lambda s: -(prow.get(s) or 0))                              # 市值降序
        picks = picks[:_TOP_N]
        if picks:
            weights.loc[dt, picks] = 1.0 / len(picks)
    return weights, closes


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    from _c4_engine import C4_END, C4_START

    weights, closes = build(C4_START, C4_END)
    stats = run_backtest(weights, closes)
    print(json.dumps(emit(STRATEGY_ID, stats, ["D1 全A剔ST", "D2 T+1收盘", "D3 行业剔除降级",
                                               "D4 公开因子不登记", "D5 壳不译"]), ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
