# [BLUEPRINT] MOD-BT-053 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_f284270f0ef0_macd_timing
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
# [A_module] module_id=MOD-BT-053 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 翻译 053: MACD 大盘择时（原文: 2020年度精选策略/76，标的 399300=沪深300）。

原文逻辑: 标的 399300.XSHE（沪深300 指数）；talib MACD(9,24,9)（非默认 12/26！）：
  macd 柱（macdsignal，即 dea-dif 单倍）<0 清仓，>0 全仓买入（状态切换式持有）。
译文实现: kline_index 000300 日线；EMA9-EMA24 差与信号线 EMA9；
  macd>0（dif>dea）持有，<0 空仓；信号 T-1，T 收盘执行。
因子拆解: MACD(9,24,9) 趋势——技术指标，不入 factor_registry。
翻译差异声明:
  D1 标的: 原文 399300 指数 → 000300 同指数不同源代码（指数收益模拟）
  D2 执行时点: 原文 handle_data 当日 → T 日收盘（引擎 T+1 起算收益）
  D3 macd 口径: talib macd=dea-dif（单倍），符号判定等价于 dif>dea
  D4 因子登记: MACD 技术指标不入 factor_registry
  D5 框架样板: log 壳不翻译
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

STRATEGY_ID = "CAND-f284270f0ef0"
WINDOW_KIND = "index"


def build(start: str, end: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    load_start = str(pd.Timestamp(start) - pd.Timedelta(days=90))[:10]
    idx = load_index("000300", load_start, end, fields=("close",))
    closes = idx[["close"]].rename(columns={"close": "000300"})
    dif = closes["000300"].ewm(span=9, adjust=False).mean() - closes["000300"].ewm(span=24, adjust=False).mean()
    dea = dif.ewm(span=9, adjust=False).mean()
    macd_pos = (dif > dea).astype(float)
    dates = closes.index[(closes.index >= pd.Timestamp(start)) & (closes.index <= pd.Timestamp(end))]
    pos_series = macd_pos.shift(1).reindex(dates).fillna(0.0)
    weights = pd.DataFrame(0.0, index=dates, columns=["000300"])
    weights["000300"] = pos_series.values
    return weights, closes


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    from _c4_engine import C4_END, C4_START

    weights, closes = build(C4_START, C4_END)
    stats = run_backtest(weights, closes)
    print(json.dumps(emit(STRATEGY_ID, stats, ["D1 指数收益模拟", "D2 收盘口径", "D3 talib符号口径",
                                               "D4 技术指标不入库", "D5 壳不译"]), ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
