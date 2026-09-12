# [BLUEPRINT] MOD-BT-058 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_d06cab686cef_rsrs_opt
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
# [A_module] module_id=MOD-BT-058 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 翻译 058: RSRS 大盘择时优化（原文: 2020年度精选策略/77，标的 160706 基金）。

原文逻辑: 标的 160706.XSHE（嘉实沪深300 联接基金）；RSRS N=18、标准化窗口 M=1100
  （原 volume 加权段被注释，生效代码=普通 z）；z>0.7 全仓，z<-0.7 清仓；开盘执行。
译文实现: kline_etf_daily 无 160706 且窗口无数据 → 以 000300 指数收益替代（D1）；
  其余同 057（无 R² 加权——原文生效路径未乘 R²）。
因子拆解: RSRS——量价衍生，不入 factor_registry。
翻译差异声明:
  D1 标的: 160706 基金净值跟踪沪深300 → 000300 指数收益替代（ETF/LOF 窗口无数据）
  D2 执行时点: 原文 open 价 → T+1 收盘成交
  D3 std 口径: 原文生效路径 np.std → ddof=0
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

STRATEGY_ID = "CAND-d06cab686cef"
WINDOW_KIND = "index"
_N, _M, _BUY, _SELL = 18, 1100, 0.7, -0.7


def build(start: str, end: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    load_start = str(pd.Timestamp(start) - pd.Timedelta(days=int(_M * 1.6) + 120))[:10]
    idx = load_index("000300", load_start, end, fields=("high", "low", "close"))
    h, l = idx["high"], idx["low"]

    def _slope(win: np.ndarray) -> float:
        x, y = win[:, 1], win[:, 0]
        xv = x.var()
        return float("nan") if xv == 0 else float(((x - x.mean()) * (y - y.mean())).sum() / xv)

    pair = np.stack([h.values, l.values], axis=1)
    beta = pd.Series(
        [_slope(pair[i - _N + 1: i + 1]) for i in range(_N - 1, len(pair))],
        index=h.index[_N - 1:],
    )
    z = (beta - beta.rolling(_M).mean()) / beta.rolling(_M).std(ddof=0)
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
    print(json.dumps(emit(STRATEGY_ID, stats, ["D1 160706→000300替代", "D2 T+1收盘", "D3 ddof=0",
                                               "D4 RSRS不入库", "D5 壳不译"]), ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
