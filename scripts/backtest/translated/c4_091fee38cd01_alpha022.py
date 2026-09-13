# [BLUEPRINT] MOD-BT-071 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_091fee38cd01_alpha022
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.data.ch_config; numpy; pandas
# [CONSUMERS] C4 快筛批测（scripts/backtest/c4_batch_screen.py）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] PIT（T 日执行用 ≤T-1 信号）；成本=冻结土规
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(数据缺失)
# [TESTS] tests/backtest/test_c4_batch_smoke.py
# [A_module] module_id=MOD-BT-071 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 翻译 071: WorldQuant Alpha#22 月频前 5（原文: 2023年度精选策略/61 分享一个最近两年非常有效的因子）。

原文逻辑: 池=沪深300；每月首个交易日按 jqlib.alpha101 的 alpha_022 因子降序取前 5；
  新买入等分 available_cash，调出清仓。
译文实现: Alpha#22 = -1×(delta(corr(high,volume,5),5)×rank(stddev(close,20)))（WorldQuant
  101 公开公式，rank=截面分位）；月频首个交易日 T-1 截面降序前 5 等权。
因子拆解: Alpha#22（公开因子库）——不登记 factor_registry（公开因子，未过本项目 IC/去马甲检验）。
翻译差异声明:
  D1 股票池: 沪深300 成分快照
  D2 执行时点: 原文开盘 → T 日收盘
  D3 公式: jqlib.alpha101 → WorldQuant 101 公开公式直接实现（库不可用时口径）
  D4 因子登记: 公开因子不登记
  D5 框架样板: log 壳不翻译

[KNOWLEDGE_EFFECTIVE_FROM] 2026-09-12 | 源=策略原文公开发布日 | 生成=AI 会话（取晚者）
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd

from _c4_engine import emit, filter_st, load_px, load_hs300, load_st_flags, run_backtest, wide

logger = logging.getLogger(__name__)

STRATEGY_ID = "CAND-091fee38cd01"
WINDOW_KIND = "stock"
_TOP_N = 5


def build(start: str, end: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    load_start = str(pd.Timestamp(start) - pd.Timedelta(days=90))[:10]
    px = load_px(load_start, end, fields=("close", "high", "volume"))
    hs = load_hs300()
    px = px[px["symbol"].isin(hs)]
    close = filter_st(wide(px, "close").ffill(), load_st_flags(load_start, end))
    high = wide(px, "high").ffill().reindex(close.index).reindex(columns=close.columns)
    vol = wide(px, "volume").ffill().reindex(close.index).reindex(columns=close.columns)

    corr5 = high.rolling(5).corr(vol)
    delta5 = corr5 - corr5.shift(5)
    std20 = close.rolling(20).std()
    rank20 = std20.rank(axis=1, pct=True)
    alpha = -1.0 * (delta5 * rank20)

    dates = close.index[(close.index >= pd.Timestamp(start)) & (close.index <= pd.Timestamp(end))]
    month_first = dates.to_series().groupby(dates.to_period("M")).min()
    weights = pd.DataFrame(0.0, index=dates, columns=close.columns)
    a_idx = alpha.shift(1).reindex(dates)
    for dt in month_first:
        row = a_idx.loc[dt].dropna()
        if row.empty:
            continue
        picks = list(row.sort_values(ascending=False).index)[:_TOP_N]
        weights.loc[dt, picks] = 1.0 / len(picks)
    return weights, close


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    from _c4_engine import C4_END, C4_START

    weights, closes = build(C4_START, C4_END)
    stats = run_backtest(weights, closes)
    print(json.dumps(emit(STRATEGY_ID, stats, ["D1 成分快照", "D2 收盘口径", "D3 WQ101公式直实现",
                                               "D4 公开因子不登记", "D5 壳不译"]), ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
