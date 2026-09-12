# [BLUEPRINT] MOD-BT-050 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_c7a8ddbab748_ma10_ma5
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
# [A_module] module_id=MOD-BT-050 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 翻译 050: 高于 MA10 买入低于 MA20 卖出（原文: 2020年度精选策略/66，单标的 000333）。

原文逻辑: 单标的 000333（美的集团）；close > 1.01×MA10 全仓买入；close < "MA5"（变量名
  为 MA5，实为 attribute_history(security,20) 的 20 日均值——原文自身笔误）清仓。
译文实现: 按原文实参忠实翻译（卖出用 20 日均值，D3 声明笔误保真）；信号 T-1，T 收盘执行。
因子拆解: MA10/MA20 均线偏离——技术指标，不入 factor_registry。
翻译差异声明:
  D1 标的: 000333 一致
  D2 执行时点: 原文 handle_data 当日收盘 → T 日收盘（引擎 T+1 起算收益）
  D3 原文笔误保真: 卖出线变量名 MA5 但窗口=20，按 20 日均值实现
  D4 因子登记: MA 技术指标不入 factor_registry
  D5 框架样板: record/log 壳不翻译
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd

from _c4_engine import emit, load_px, run_backtest, wide

logger = logging.getLogger(__name__)

STRATEGY_ID = "CAND-c7a8ddbab748"
WINDOW_KIND = "stock"
_SYM = "000333"


def build(start: str, end: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    load_start = str(pd.Timestamp(start) - pd.Timedelta(days=60))[:10]
    px = load_px(load_start, end, fields=("close",))
    closes = wide(px)
    closes = closes[closes.columns.intersection([_SYM])]
    ma10 = closes.rolling(10).mean()
    ma20 = closes.rolling(20).mean()
    buy_sig = closes > 1.01 * ma10
    sell_sig = closes < ma20
    dates = closes.index[(closes.index >= pd.Timestamp(start)) & (closes.index <= pd.Timestamp(end))]
    weights = pd.DataFrame(0.0, index=dates, columns=closes.columns)
    b_idx = buy_sig.shift(1).reindex(dates).fillna(False).iloc[:, 0]
    s_idx = sell_sig.shift(1).reindex(dates).fillna(False).iloc[:, 0]
    pos = 0.0
    for dt in dates:
        if bool(b_idx.loc[dt]):
            pos = 1.0
        elif bool(s_idx.loc[dt]):
            pos = 0.0
        weights.loc[dt, :] = pos
    return weights, closes


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    from _c4_engine import C4_END, C4_START

    weights, closes = build(C4_START, C4_END)
    stats = run_backtest(weights, closes)
    print(json.dumps(emit(STRATEGY_ID, stats, ["D1 标的一致", "D2 收盘口径", "D3 原文笔误保真(MA5名20日窗)",
                                               "D4 技术指标不入库", "D5 壳不译"]), ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
