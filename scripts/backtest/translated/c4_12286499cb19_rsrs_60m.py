# [BLUEPRINT] MOD-BT-059 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_12286499cb19_rsrs_60m
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
# [A_module] module_id=MOD-BT-059 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 翻译 059: RSRS 指标择时（60 分钟线版）（原文: 2020年度精选策略/69，标的 510300 ETF）。

原文逻辑: 标的 510300（沪深300ETF）；RSRS 用 400 根 60 分钟线（N=18 根窗口），
  z=beta 标准化×R²，阈值 ±0.7（每 60 根 bar≈日频判定一次）。
译文实现: 60 分钟数据不进 C4 统一口径 → 声明降为日线 RSRS（N=18 日，标准化窗口
  M=100 日≈400 小时/4）；标的 510300 无窗口内 ETF 数据 → 000300 指数收益替代（D1）。
因子拆解: RSRS×R²——量价衍生，不入 factor_registry。
翻译差异声明:
  D1 标的: 510300 ETF → 000300 指数收益替代
  D2 执行时点: 原文 60 分钟 bar 判定 → 日收盘口径（C4 统一）
  D3 频率: 60m 线 RSRS → 日线 RSRS（窗口 N/M 同比折算，形态保真度有限已声明）
  D4 因子登记: RSRS 不入 factor_registry
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

from _c4_engine import emit, load_index, run_backtest

logger = logging.getLogger(__name__)

STRATEGY_ID = "CAND-12286499cb19"
WINDOW_KIND = "index"
_N, _M, _THR = 18, 100, 0.7


def build(start: str, end: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    load_start = str(pd.Timestamp(start) - pd.Timedelta(days=int(_M * 1.6) + 120))[:10]
    idx = load_index("000300", load_start, end, fields=("high", "low", "close"))
    h, l = idx["high"], idx["low"]

    def _stats(win: np.ndarray) -> tuple[float, float]:
        x, y = win[:, 1], win[:, 0]
        xv = x.var()
        if xv == 0:
            return float("nan"), 0.0
        beta = float(((x - x.mean()) * (y - y.mean())).sum() / xv)
        corr = float(np.corrcoef(x, y)[0, 1]) if x.std() > 0 and y.std() > 0 else 0.0
        return beta, corr * corr

    pair = np.stack([h.values, l.values], axis=1)
    res = [_stats(pair[i - _N + 1: i + 1]) for i in range(_N - 1, len(pair))]
    beta = pd.Series([r[0] for r in res], index=h.index[_N - 1:])
    r2 = pd.Series([r[1] for r in res], index=h.index[_N - 1:])
    beat_mean, beat_std = beta.expanding().mean(), beta.expanding().std(ddof=0)
    z = r2 * (beta - beat_mean) / beat_std
    dates = idx.index[(idx.index >= pd.Timestamp(start)) & (idx.index <= pd.Timestamp(end))]
    weights = pd.DataFrame(0.0, index=dates, columns=["000300"])
    pos = 0.0
    prev = None
    for dt in dates:
        zc = z.shift(1).loc[dt]
        if pd.notna(zc) and prev is not None:
            if prev < _THR <= zc:
                pos = 1.0
            elif prev > -_THR >= zc:
                pos = 0.0
        if pd.notna(zc):
            prev = float(zc)
        weights.loc[dt, "000300"] = pos
    closes = idx[["close"]].rename(columns={"close": "000300"})
    return weights, closes


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    from _c4_engine import C4_END, C4_START

    weights, closes = build(C4_START, C4_END)
    stats = run_backtest(weights, closes)
    print(json.dumps(emit(STRATEGY_ID, stats, ["D1 510300→000300", "D2 收盘口径", "D3 60m→日线折算",
                                               "D4 RSRS不入库", "D5 壳不译"]), ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
