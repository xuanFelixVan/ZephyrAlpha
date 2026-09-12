# [BLUEPRINT] MOD-BT-048 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_c30a620e114d_boll_break
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
# [A_module] module_id=MOD-BT-048 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 翻译 048: 布林带突破（talib BBANDS）（原文: 2020年度精选策略/45 布林带策略）。

原文逻辑: 单标的 600519（贵州茅台）；BBANDS(20,2)：close>上轨 全仓买入，close<下轨 清仓
  （原文空头分支因 A 股无融券在多头的语义下等价于清仓）。
译文实现: 日线 20 日均线±2 倍标准差轨道；信号 T-1，T 收盘执行。
因子拆解: BOLL 布林带（均线+波动率轨道）——技术指标，不入 factor_registry。
翻译差异声明:
  D1 标的: 600519 与原文一致
  D2 执行时点: 原文 open 价 → T+1 收盘成交
  D3 空头分支: 原文 close<下轨 时若持仓<=0 则下空单——A 股多头约束下译为清仓
  D4 因子登记: BOLL 技术指标不入 factor_registry
  D5 框架样板: record/send_message 壳不翻译
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

STRATEGY_ID = "CAND-c30a620e114d"
WINDOW_KIND = "stock"
_SYM = "600519"


def build(start: str, end: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    load_start = str(pd.Timestamp(start) - pd.Timedelta(days=60))[:10]
    px = load_px(load_start, end, fields=("close",))
    closes = wide(px)
    closes = closes[closes.columns.intersection([_SYM])]
    mid = closes.rolling(20).mean()
    std = closes.rolling(20).std()
    upper, lower = mid + 2 * std, mid - 2 * std
    buy_sig = closes > upper
    sell_sig = closes < lower
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
    print(json.dumps(emit(STRATEGY_ID, stats, ["D1 标的一致", "D2 T+1收盘", "D3 空头分支清仓",
                                               "D4 技术指标不入库", "D5 壳不译"]), ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
