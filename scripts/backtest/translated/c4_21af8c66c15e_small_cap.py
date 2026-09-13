# [BLUEPRINT] MOD-BT-092 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_21af8c66c15e_small_cap
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.data.ch_config; numpy; pandas
# [CONSUMERS] C4 快筛批测（scripts/backtest/c4_batch_screen.py）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] PIT（市值/估值/均线 ≤T-1）；成本=冻结土规
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(数据缺失)
# [TESTS] tests/backtest/test_c4_batch_smoke.py
# [A_module] module_id=MOD-BT-092 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 翻译 093: 小市值策略之再优化（原文: 2025年度精选策略/15 小市值策略之再优化，年化接近翻倍）。

原文逻辑: 每日 14:30：中小板综(399101) 成分→按流通市值升序取 9 只→过滤 ST/停牌/涨跌停→
  逐只检查现价≥MA5 才买入，补满 3 只即停；持仓不在当日 3 只→清仓。
译文实现: 流通市值=stock_indicator.circ_mv（tushare）；MA5=收盘 5 日均线；信号 T-1，T 收盘执行。
因子拆解: 市值排序——规模因子，公开因子不登记 factor_registry。
翻译差异声明:
  D1 股票池: 全 A（HFQ 表）剔 ST；原文中小板综成分→全 A 近似（指数成分历史缺）
  D2 执行时点: 原文 14:30 盘中 MA5→T-1 收盘 MA5（PIT 近似）
  D3 涨跌停过滤: HFQ 无涨跌停列→不剔除（声明）
  D4 因子登记: 规模因子不登记
  D5 框架样板: 壳不翻译
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd

from _c4_engine import emit, filter_st, load_px, load_st_flags, load_valuation, run_backtest, wide

logger = logging.getLogger(__name__)

STRATEGY_ID = "CAND-21af8c66c15e"
WINDOW_KIND = "stock"
_TOP_N, _CAND, _MA = 3, 9, 5


def build(start: str, end: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    load_start = str(pd.Timestamp(start) - pd.Timedelta(days=60))[:10]
    px = load_px(load_start, end, fields=("close",))
    closes = filter_st(wide(px).ffill(), load_st_flags(load_start, end))
    val = load_valuation(load_start, end, fields=("circ_mv",))
    cmv = val["circ_mv"].reindex(closes.index).reindex(columns=closes.columns)
    ma5 = closes.rolling(_MA).mean()

    dates = closes.index[(closes.index >= pd.Timestamp(start)) & (closes.index <= pd.Timestamp(end))]
    weights = pd.DataFrame(0.0, index=dates, columns=closes.columns)
    for k, dt in enumerate(dates):
        row_mv = cmv.shift(1).iloc[k].dropna()
        if len(row_mv) < _CAND:
            continue
        cand = list(row_mv.sort_values().index[:_CAND])
        ma_row = ma5.shift(1).iloc[k]
        px_row = closes.iloc[k]
        picks = []
        for s in cand:
            if pd.isna(px_row.get(s)) or pd.isna(ma_row.get(s)):
                continue
            if px_row[s] >= ma_row[s]:  # 现价≥MA5
                picks.append(s)
            if len(picks) >= _TOP_N:
                break
        if picks:
            weights.loc[dt, picks] = 1.0 / len(picks)
    return weights, closes


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    from _c4_engine import C4_END, C4_START

    weights, closes = build(C4_START, C4_END)
    stats = run_backtest(weights, closes)
    print(json.dumps(emit(STRATEGY_ID, stats, ["D1 全A剔ST近似中小板", "D2 T+1收盘", "D3 涨跌停不可剔",
                                               "D4 规模因子不登记", "D5 壳不译"]), ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
