# [BLUEPRINT] MOD-BT-041 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_c72318f2da1c_bias_ql
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.data.ch_config; numpy; pandas
# [CONSUMERS] C4 快筛批测（scripts/backtest/c4_batch_screen.py）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] PIT（T 日执行用 ≤T-1 信号）；成本=冻结土规（引擎常量）；差异声明完整
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(数据缺失)
# [TESTS] tests/backtest/test_c4_batch_smoke.py
# [A_module] module_id=MOD-BT-041 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 翻译 041: BIAS_QL 乖离率金叉死叉（原文: 2020年度精选策略/21 果核量化 BIAS_QL乖离率策略指数择时1.0）。

原文逻辑: 全 A 池，bias=（收盘-MA29)/MA29×100，biasma=MA19(bias)；bias 上穿 biasma 买入
  （逐只全仓），下穿卖出；14:58 盘中执行；holdSize=50。
译文实现: 池=沪深300 成分快照；信号=T-1 收盘金叉/死叉；持仓≤50 等权，死叉次日移出；
  T+1 收盘执行统一口径。
因子拆解: BIAS 乖离率（价格/均线偏离，OHLCV 可算）——技术指标，不入 factor_registry。
翻译差异声明:
  D1 股票池: 原文全 A（allStocksmacdkdj 预筛池不可考）→ 沪深300 成分快照
  D2 执行时点: 原文 14:58 盘中价 → T+1 收盘成交（C4 统一口径）
  D3 仓位: 原文每信号逐只全仓（时序依赖）→ 等权分散（上限 50=holdSize）
  D4 因子登记: BIAS 属技术指标，不登记 factor_registry，无新增因子
  D5 框架样板: 原文止盈止损参数表（stpPftPrice/stpLosRate）未在主路径生效，不翻译
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

STRATEGY_ID = "CAND-c72318f2da1c"
WINDOW_KIND = "stock"
_N, _M, _MAX_HOLD = 29, 19, 50


def build(start: str, end: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    load_start = str(pd.Timestamp(start) - pd.Timedelta(days=60))[:10]
    px = load_px(load_start, end, fields=("close",))
    hs = load_hs300()
    px = px[px["symbol"].isin(hs)]
    closes = wide(px).ffill()
    closes = filter_st(closes, load_st_flags(load_start, end))
    bias = (closes - closes.rolling(_N).mean()) / closes.rolling(_N).mean() * 100.0
    bma = bias.rolling(_M).mean()
    golden = (bias > bma) & (bias.shift(1) <= bma.shift(1))
    death = (bias < bma) & (bias.shift(1) >= bma.shift(1))
    dates = closes.index[(closes.index >= pd.Timestamp(start)) & (closes.index <= pd.Timestamp(end))]
    weights = pd.DataFrame(0.0, index=dates, columns=closes.columns)
    g_idx = golden.shift(1).reindex(dates).fillna(False)
    d_idx = death.shift(1).reindex(dates).fillna(False)
    holdings: list[str] = []
    for dt in dates:
        for s in list(holdings):
            if bool(d_idx.loc[dt, s]):
                holdings.remove(s)
        if len(holdings) < _MAX_HOLD:
            for s in closes.columns:
                if len(holdings) >= _MAX_HOLD:
                    break
                if bool(g_idx.loc[dt, s]) and s not in holdings:
                    holdings.append(s)
        if holdings:
            weights.loc[dt, holdings] = 1.0 / len(holdings)
    return weights, closes


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    from _c4_engine import C4_END, C4_START

    weights, closes = build(C4_START, C4_END)
    stats = run_backtest(weights, closes)
    print(json.dumps(emit(STRATEGY_ID, stats, ["D1 池=成分快照", "D2 T+1收盘", "D3 等权≤50",
                                               "D4 BIAS技术指标不入库", "D5 未生效参数不译"]),
                      ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
