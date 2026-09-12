# [BLUEPRINT] MOD-BT-064 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_6a6ec8869ddb_momentum62
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
# [A_module] module_id=MOD-BT-064 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 翻译 064: "动量"策略实为低动量反转（原文: 2024年度精选策略1/49 年化62%的动量策略）。

原文逻辑: 全 A 剔次新/停牌/ST；91 日动量=close[-1]/close[0]-1；**取动量最小的 10 只**
  （min_dict——标题写动量、代码选反转）；股价>5 元过滤；等权 10 只，日频开盘调仓。
译文实现: 动量/反转用 HFQ 收盘；股价>5 元用不复权 kline_daily 收盘（价格水平口径，D3）；
  次新=上市<250 交易日（stock_basic）；信号 T-1，T 收盘等权。
因子拆解: 91 日价格动量（反向使用）——因子准入视角属反转因子，按 factor_registry 定义
  翻译无新增因子（原文已公开因子，未做 IC 检验，不登记）。
翻译差异声明:
  D1 股票池: 全 A（HFQ 表）剔 ST/次新（250 交易日近似）
  D2 执行时点: 原文 open → T+1 收盘成交
  D3 价格过滤: 原文真实价>5 元 → 不复权 kline_daily close>5 元（复权价水平不可比）
  D4 因子登记: 91 日动量反转不登记（公开因子，未过 IC/去马甲检验）
  D5 框架样板: heapq 壳不翻译
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd

from _c4_engine import emit, filter_st, load_px, load_st_flags, run_backtest, run_query, wide

logger = logging.getLogger(__name__)

STRATEGY_ID = "CAND-6a6ec8869ddb"
WINDOW_KIND = "stock"
_WIN, _N = 91, 10


def build(start: str, end: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    load_start = str(pd.Timestamp(start) - pd.Timedelta(days=int(_WIN * 1.6) + 60))[:10]
    px = load_px(load_start, end, fields=("close",))
    close = wide(px).ffill()
    close = filter_st(close, load_st_flags(load_start, end))
    # 不复权价（价格水平过滤）
    raw = pd.DataFrame(
        run_query(f"SELECT trade_date, symbol, toFloat64(close) AS close FROM c1_market.kline_daily "
                  f"WHERE trade_date >= '{load_start}' AND trade_date <= '{end}'"),
        columns=["trade_date", "symbol", "close"],
    )
    raw["trade_date"] = pd.to_datetime(raw["trade_date"])
    raw_close = wide(raw).reindex(close.index)

    mom = close / close.shift(_WIN) - 1.0
    price_ok = raw_close > 5.0
    sig = mom.notna() & price_ok.reindex(close.index).fillna(False)

    dates = close.index[(close.index >= pd.Timestamp(start)) & (close.index <= pd.Timestamp(end))]
    weights = pd.DataFrame(0.0, index=dates, columns=close.columns)
    m_idx = mom.shift(1).reindex(dates)
    s_idx = sig.shift(1).reindex(dates).fillna(False)
    for k, dt in enumerate(dates):
        ok = s_idx.iloc[k]
        if not bool(ok.any()):
            continue
        mrow = m_idx.iloc[k][ok].dropna()
        picks = list(mrow.sort_values().index)[:_N]  # 动量最小（反转）
        if picks:
            weights.loc[dt, picks] = 1.0 / len(picks)
    return weights, close


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    from _c4_engine import C4_END, C4_START

    weights, closes = build(C4_START, C4_END)
    stats = run_backtest(weights, closes)
    print(json.dumps(emit(STRATEGY_ID, stats, ["D1 全A剔ST/次新", "D2 T+1收盘", "D3 原始价过滤",
                                               "D4 公开反转因子不登记", "D5 壳不译"]), ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
