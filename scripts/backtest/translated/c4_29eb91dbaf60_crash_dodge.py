# [BLUEPRINT] MOD-BT-067 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_29eb91dbaf60_crash_dodge
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
# [A_module] module_id=MOD-BT-067 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 翻译 067: 躲大跌股债切换（原文: 2023年度精选策略/17 20行代码8年胜率100%躲过了牛年第一场大跌）。

原文逻辑: 信号源=上证指数收盘；买股信号（32 日窗，不含当日）: c[2]==max(c[2:])（30 日前
  为窗内最高）且 MA20>MA30 且 MA10>MA20；卖股信号: 32 日最高点出现在最近 9 日内
  （argmax>22）且最低点在最旧一根（argmin==0）且昨收<MA30 且前收<前 31 日均值；
  买股→全仓 510300，卖股→全仓 511010 国债 ETF。
译文实现: 上证指数 000001 kline_index；持股资产=沪深300 指数收益（510300 无窗口数据，D1）；
  国债 ETF 无数据 → 空仓（D3）；信号 T-1，T 收盘执行。
因子拆解: 均线比较+高低点位置——价格衍生，不入 factor_registry。
翻译差异声明:
  D1 标的: 510300 → 000300 指数收益替代（ETF 窗口无数据）
  D2 执行时点: 原文开盘 → T+1 收盘成交
  D3 防御腿: 511010 国债 ETF 无窗口数据 → 空仓替代（防御收益缺失已声明）
  D4 因子登记: 均线/位置量不入 factor_registry
  D5 框架样板: —
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

STRATEGY_ID = "CAND-29eb91dbaf60"
WINDOW_KIND = "index"
_WIN = 32


def build(start: str, end: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    load_start = str(pd.Timestamp(start) - pd.Timedelta(days=90))[:10]
    sh = load_index("000001", load_start, end, fields=("close",))
    c = sh["close"]

    buy_sig = pd.Series(False, index=c.index)
    sell_sig = pd.Series(False, index=c.index)
    vals = c.values
    for i in range(_WIN, len(c)):
        win = vals[i - _WIN: i]  # 32 日窗，不含当日（与原文 c 一致）
        ma10, ma20, ma30 = win[-10:].mean(), win[-20:].mean(), win[-30:].mean()
        if win[2] == win[2:].max() and ma20 > ma30 and ma10 > ma20:
            buy_sig.iloc[i] = True
        if win.argmax() > 22 and win.argmin() == 0 \
                and win[-1] < win[-30:].mean() and win[-2] < win[:-1].mean():
            sell_sig.iloc[i] = True

    dates = c.index[(c.index >= pd.Timestamp(start)) & (c.index <= pd.Timestamp(end))]
    weights = pd.DataFrame(0.0, index=dates, columns=["000300"])
    pos = 0.0
    for dt in dates:
        if bool(buy_sig.shift(1).loc[dt]):
            pos = 1.0
        elif bool(sell_sig.shift(1).loc[dt]):
            pos = 0.0
        weights.loc[dt, "000300"] = pos
    idx300 = load_index("000300", start, end, fields=("close",))[["close"]].rename(columns={"close": "000300"})
    return weights, idx300


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    from _c4_engine import C4_END, C4_START

    weights, closes = build(C4_START, C4_END)
    stats = run_backtest(weights, closes)
    print(json.dumps(emit(STRATEGY_ID, stats, ["D1 510300→000300", "D2 T+1收盘", "D3 债腿→空仓",
                                               "D4 不入库", "D5 —"]), ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
