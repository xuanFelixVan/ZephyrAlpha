# [BLUEPRINT] MOD-BT-056 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_5efe26d1992e_rsrs_timing
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
# [A_module] module_id=MOD-BT-056 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 翻译 056: RSRS 大盘择时（标准版）（原文: 2020年度精选策略/93 RSRS——大盘择时）。

原文逻辑: 标的 000300；RSRS 斜率=过去 N=18 日 low→high OLS 斜率；标准化
  z=(beta-MA_M(beta))/STD_M(beta)，M=480；z>0.7 全仓，z<-0.7 清仓。
译文实现: kline_index 000300 日线，逐日 rolling OLS 斜率+滚动标准化；信号 T-1，T 收盘执行。
因子拆解: RSRS 阻力支撑相对强度（高低价回归斜率）——量价衍生指标，不入 factor_registry。
翻译差异声明:
  D1 标的: 000300 指数收益模拟（与原文一致）
  D2 执行时点: 原文 open 价 → T+1 收盘成交
  D3 标准差口径: 原文 pd.rolling_std（样本 ddof=1）→ pandas rolling.std 同口径
  D4 因子登记: RSRS 不入 factor_registry（高低价衍生）
  D5 框架样板: 预计算壳/日志不翻译
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

STRATEGY_ID = "CAND-5efe26d1992e"
WINDOW_KIND = "index"
_N, _M, _BUY, _SELL = 18, 480, 0.7, -0.7


def build(start: str, end: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    load_start = str(pd.Timestamp(start) - pd.Timedelta(days=int(_M * 1.6) + 120))[:10]
    idx = load_index("000300", load_start, end, fields=("high", "low", "close"))
    h, l = idx["high"], idx["low"]

    def _slope(win: np.ndarray) -> float:
        x = win[:, 1]
        y = win[:, 0]
        xv = x.var()
        return float("nan") if xv == 0 else float(((x - x.mean()) * (y - y.mean())).sum() / xv)

    pair = np.stack([h.values, l.values], axis=1)
    beta = pd.Series(
        [_slope(pair[i - _N + 1: i + 1]) for i in range(_N - 1, len(pair))],
        index=h.index[_N - 1:],
    )
    z = (beta - beta.rolling(_M).mean()) / beta.rolling(_M).std()
    dates = idx.index[(idx.index >= pd.Timestamp(start)) & (idx.index <= pd.Timestamp(end))]
    weights = pd.DataFrame(0.0, index=dates, columns=["000300"])
    pos = 0.0
    for dt in dates:
        zc = z.shift(1).loc[dt]
        if pd.notna(zc):
            if zc > _BUY:
                pos = 1.0
            elif zc < _SELL:
                pos = 0.0
        weights.loc[dt, "000300"] = pos
    closes = idx[["close"]].rename(columns={"close": "000300"})
    return weights, closes


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    from _c4_engine import C4_END, C4_START

    weights, closes = build(C4_START, C4_END)
    stats = run_backtest(weights, closes)
    print(json.dumps(emit(STRATEGY_ID, stats, ["D1 指数一致", "D2 T+1收盘", "D3 ddof=1",
                                               "D4 RSRS不入库", "D5 壳不译"]), ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
