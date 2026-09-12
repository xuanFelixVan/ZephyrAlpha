# [BLUEPRINT] MOD-BT-055 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_6485e4cd0844_kdj_timing
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
# [A_module] module_id=MOD-BT-055 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 翻译 055: Stoch(KDJ) 大盘择时（原文: 2020年度精选策略/91，标的 399300=沪深300）。

原文逻辑: talib STOCH(fastk=17, slowk=9, slowd=7)：卖出=slowk 从 >80 下穿 80，或
  slowk∈(20,80) 且 slowk<slowd；买入=slowk 从 <20 上穿 20，或 slowk>80 且 slowk>slowd。
译文实现: kline_index 000300 日线；RSV(17) 平滑（slowk=9/slowd=7 递推 SMA）；
  信号 T-1，T 收盘执行。
因子拆解: Stoch 随机指标——技术指标，不入 factor_registry。
翻译差异声明:
  D1 标的: 399300 → 000300 指数收益模拟
  D2 执行时点: 原文当日 → T 日收盘（引擎 T+1 起算收益）
  D3 STOCH 平滑: 递推 SMA 等价实现（matype=0）
  D4 因子登记: KDJ 技术指标不入 factor_registry
  D5 框架样板: import 的 SVR/GridSearchCV 未使用（死 import）不翻译
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd

from _c4_engine import emit, load_index, run_backtest

logger = logging.getLogger(__name__)

STRATEGY_ID = "CAND-6485e4cd0844"
WINDOW_KIND = "index"
_FASTK, _SLOWK, _SLOWD = 17, 9, 7


def _sma_recursion(s: pd.Series, n: int) -> pd.Series:
    return s.ewm(alpha=1.0 / n, adjust=False).mean()


def build(start: str, end: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    load_start = str(pd.Timestamp(start) - pd.Timedelta(days=90))[:10]
    idx = load_index("000300", load_start, end, fields=("high", "low", "close"))
    hh = idx["high"].rolling(_FASTK).max()
    ll = idx["low"].rolling(_FASTK).min()
    fastk = (idx["close"] - ll) / (hh - ll) * 100.0
    slowk = _sma_recursion(fastk, _SLOWK)
    slowd = _sma_recursion(slowk, _SLOWD)
    cross_down_80 = (slowk < 80) & (slowk.shift(1) > 80)
    mid_dead = (slowk > 20) & (slowk < 80) & (slowk < slowd)
    cross_up_20 = (slowk > 20) & (slowk.shift(1) < 20)
    high_gold = (slowk > 80) & (slowk > slowd)
    sell_sig = cross_down_80 | mid_dead
    buy_sig = cross_up_20 | high_gold
    dates = idx.index[(idx.index >= pd.Timestamp(start)) & (idx.index <= pd.Timestamp(end))]
    weights = pd.DataFrame(0.0, index=dates, columns=["000300"])
    pos = 0.0
    for dt in dates:
        if bool(buy_sig.shift(1).loc[dt]):
            pos = 1.0
        elif bool(sell_sig.shift(1).loc[dt]):
            pos = 0.0
        weights.loc[dt, "000300"] = pos
    closes = idx[["close"]].rename(columns={"close": "000300"})
    return weights, closes


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    from _c4_engine import C4_END, C4_START

    weights, closes = build(C4_START, C4_END)
    stats = run_backtest(weights, closes)
    print(json.dumps(emit(STRATEGY_ID, stats, ["D1 指数收益模拟", "D2 收盘口径", "D3 递推SMA",
                                               "D4 技术指标不入库", "D5 死import不译"]), ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
