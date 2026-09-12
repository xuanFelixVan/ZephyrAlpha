# [BLUEPRINT] MOD-BT-066 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_9c0136ec8f42_kucoffee_trend
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
# [A_module] module_id=MOD-BT-066 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 翻译 066: 苦咖啡——120 日强趋势周频双持（原文: 2023年度精选策略/3 苦咖啡-默默赚钱系列-改）。

原文逻辑: 池=沪深300，剔 688/停牌/涨跌停开盘/昨收>500 元/HHV(high,30)/昨收>1.1/
  量比 MA(VOL,7)/MA(VOL,180)>1.5；120 日 linregress: slope/intercept>0.005 且 r>0.9；
  按 slope 降序取 2 只等权；每周第一个交易日调仓。
译文实现: 全规则向量化（与 061 同款闭式回归）；周频=每周首个交易日按 T-1 信号重设权重。
因子拆解: 120 日趋势回归——价格衍生，不入 factor_registry。
翻译差异声明:
  D1 股票池: 沪深300 成分快照
  D2 执行时点: 原文周首开盘 → 周首 T 日收盘（引擎 T+1 起算）
  D3 价上限: 昨收<=500 元按不复权 kline_daily 收盘（复权价水平不可比）
  D4 因子登记: 趋势回归量不入 factor_registry
  D5 框架样板: log 壳不翻译
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import numpy as np
import pandas as pd

from _c4_engine import emit, filter_st, load_px, load_hs300, load_st_flags, run_backtest, run_query, wide

logger = logging.getLogger(__name__)

STRATEGY_ID = "CAND-9c0136ec8f42"
WINDOW_KIND = "stock"
_WIN, _TOP_N = 120, 2


def build(start: str, end: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    load_start = str(pd.Timestamp(start) - pd.Timedelta(days=260))[:10]
    px = load_px(load_start, end, fields=("close", "high", "volume"))
    hs = load_hs300()
    px = px[px["symbol"].isin(hs)]
    px = px[~px["symbol"].str.startswith("68")]
    close = filter_st(wide(px, "close").ffill(), load_st_flags(load_start, end))
    high = wide(px, "high").ffill().reindex(close.index).ffill().reindex(columns=close.columns)
    vol = wide(px, "volume").ffill().reindex(close.index).ffill().reindex(columns=close.columns)

    raw = pd.DataFrame(
        run_query(f"SELECT trade_date, symbol, toFloat64(close) AS close FROM c1_market.kline_daily "
                  f"WHERE trade_date >= '{load_start}' AND trade_date <= '{end}'"),
        columns=["trade_date", "symbol", "close"],
    )
    raw["trade_date"] = pd.to_datetime(raw["trade_date"])
    raw_close = wide(raw).reindex(close.index).reindex(columns=close.columns)

    hhv30 = high.rolling(30).max()
    volratio = vol.rolling(7).mean() / vol.rolling(180).mean()
    base = (raw_close <= 500) & ((hhv30 / close) <= 1.1) & (volratio <= 1.5)

    vals = close.values
    t, c = vals.shape
    sw = np.lib.stride_tricks.sliding_window_view(vals, _WIN, axis=0)
    x = np.arange(_WIN, dtype=float)
    xbar = x.mean()
    sxx = ((x - xbar) ** 2).sum()
    ybar = sw.mean(axis=2)
    sxy = ((sw - ybar[:, :, None]) * (x - xbar)).sum(axis=2)
    k = sxy / sxx
    b = ybar - k * xbar
    syy = ((sw - ybar[:, :, None]) ** 2).sum(axis=2)
    with np.errstate(invalid="ignore", divide="ignore"):
        r = np.where((sxx > 0) & (syy > 0), sxy / np.sqrt(sxx * syy), 0.0)
    idx_win = close.index[_WIN - 1:]
    ks = pd.DataFrame(k, index=idx_win, columns=close.columns)
    bs = pd.DataFrame(b, index=idx_win, columns=close.columns)
    rs = pd.DataFrame(r, index=idx_win, columns=close.columns)
    sig = base.reindex(idx_win).fillna(False) & (rs > 0.9) & ((ks / bs) > 0.005)

    dates = close.index[(close.index >= pd.Timestamp(start)) & (close.index <= pd.Timestamp(end))]
    week_first = dates.to_series().groupby(dates.to_period("W")).min()
    weights = pd.DataFrame(0.0, index=dates, columns=close.columns)
    for dt in week_first:
        if dt not in dates:
            continue
        srow = sig.shift(1).reindex([dt]).fillna(False).iloc[0]
        if not bool(srow.any()):
            continue
        krow = ks.shift(1).reindex([dt]).iloc[0]
        picks = list(krow[srow].dropna().sort_values(ascending=False).index)[:_TOP_N]
        weights.loc[dt, picks] = 1.0 / len(picks)
    return weights, close


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    from _c4_engine import C4_END, C4_START

    weights, closes = build(C4_START, C4_END)
    stats = run_backtest(weights, closes)
    print(json.dumps(emit(STRATEGY_ID, stats, ["D1 成分快照", "D2 周首收盘", "D3 原始价上限",
                                               "D4 趋势量不入库", "D5 壳不译"]), ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
