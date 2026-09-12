# [BLUEPRINT] MOD-BT-057 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_eaddc3f9db4e_rsrs_r2
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
# [A_module] module_id=MOD-BT-057 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 翻译 057: RSRS 大盘择时（R² 加权 M=1100）（原文: 2020年度精选策略/05 兄台且慢）。

原文逻辑: 标的 000300；RSRS N=18 斜率序列，标准化窗口 M=1100；z 乘以当期 R²
  （fitting quality 加权）；z>0.7 全仓，z<-0.7 清仓；开盘执行。
译文实现: 同 056 引擎口径 + R² 加权；信号 T-1，T 收盘执行。
因子拆解: RSRS×R²（斜率标准化×拟合优度）——量价衍生，不入 factor_registry。
翻译差异声明:
  D1 标的: 000300 一致
  D2 执行时点: 原文 open 价 → T+1 收盘成交
  D3 std 口径: 原文 np.std（总体 ddof=0）→ 同口径 ddof=0
  D4 因子登记: RSRS 不入 factor_registry
  D5 框架样板: send_message 壳不翻译
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

STRATEGY_ID = "CAND-eaddc3f9db4e"
WINDOW_KIND = "index"
_N, _M, _BUY, _SELL = 18, 1100, 0.7, -0.7


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
    z = (beta - beta.rolling(_M).mean()) / beta.rolling(_M).std(ddof=0) * r2
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
    print(json.dumps(emit(STRATEGY_ID, stats, ["D1 指数一致", "D2 T+1收盘", "D3 ddof=0",
                                               "D4 RSRS不入库", "D5 壳不译"]), ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
