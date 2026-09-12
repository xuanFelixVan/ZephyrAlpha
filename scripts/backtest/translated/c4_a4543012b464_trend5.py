# [BLUEPRINT] MOD-BT-061 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_a4543012b464_trend5
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
# [A_module] module_id=MOD-BT-061 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 翻译 061: 趋势交易 5.0（原文: 2023年度精选策略/33 趋势交易5.0 无择时）。

原文逻辑: 池=沪深300 剔 688；①多头结构: 最新收盘>MA100 且 MA30>MA60>MA100；
  ②100 日 linregress: R>0.5 且 slope/intercept>0.005；按 slope 降序；
  ③HHV(high,30)/昨收<=1.1（不过度超买）；全列表等权买入，调出即卖，日频。
译文实现: 全规则日线向量化（sliding_window_view 闭式回归）；信号 T-1，T 收盘等权。
因子拆解: 均线结构+线性回归趋势（slope/R）——价格衍生，不入 factor_registry。
翻译差异声明:
  D1 股票池: 沪深300 最新成分快照（原文同池）
  D2 执行时点: 原文 open 价 → T+1 收盘成交
  D3 —（全规则可日频向量化）
  D4 因子登记: 回归趋势量不入 factor_registry
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

from _c4_engine import emit, filter_st, load_px, load_hs300, load_st_flags, run_backtest, wide

logger = logging.getLogger(__name__)

STRATEGY_ID = "CAND-a4543012b464"
WINDOW_KIND = "stock"
_WIN = 100


def build(start: str, end: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    load_start = str(pd.Timestamp(start) - pd.Timedelta(days=200))[:10]
    px = load_px(load_start, end, fields=("close", "high"))
    hs = load_hs300()
    px = px[px["symbol"].isin(hs)]
    px = px[~px["symbol"].str.startswith("68")]
    close = filter_st(wide(px, "close").ffill(), load_st_flags(load_start, end))
    high = wide(px, "high").ffill().reindex(close.index).ffill()

    ma30, ma60, ma100 = close.rolling(30).mean(), close.rolling(60).mean(), close.rolling(100).mean()
    align = (close > ma100) & (ma30 > ma60) & (ma60 > ma100)

    vals = close.values
    t, c = vals.shape
    if t < _WIN:
        raise RuntimeError("样本不足以计算 100 日回归")
    sw = np.lib.stride_tricks.sliding_window_view(vals, _WIN, axis=0)  # (t-_WIN+1, c, _WIN)
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
    idx100 = close.index[_WIN - 1:]
    ks = pd.DataFrame(k, index=idx100, columns=close.columns)
    bs = pd.DataFrame(b, index=idx100, columns=close.columns)
    rs = pd.DataFrame(r, index=idx100, columns=close.columns)
    reg_ok = (rs > 0.5) & ((ks / bs) > 0.005)
    hhv30 = high.rolling(30).max()
    not_over = (hhv30 / close) <= 1.1
    cand = align & reg_ok.reindex(close.index).fillna(False) & not_over

    dates = close.index[(close.index >= pd.Timestamp(start)) & (close.index <= pd.Timestamp(end))]
    weights = pd.DataFrame(0.0, index=dates, columns=close.columns)
    c_idx = cand.shift(1).reindex(dates).fillna(False)
    slope_rank = ks.shift(1).reindex(dates)
    for kk, dt in enumerate(dates):
        row = c_idx.iloc[kk]
        picks = [s for s in close.columns if bool(row[s])]
        if picks:
            ranks = slope_rank.iloc[kk][picks].sort_values(ascending=False)
            picks = list(ranks.index)
            weights.loc[dt, picks] = 1.0 / len(picks)
    return weights, close


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    from _c4_engine import C4_END, C4_START

    weights, closes = build(C4_START, C4_END)
    stats = run_backtest(weights, closes)
    print(json.dumps(emit(STRATEGY_ID, stats, ["D1 成分快照剔688", "D2 T+1收盘", "D3 无",
                                               "D4 回归量不入库", "D5 壳不译"]), ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
