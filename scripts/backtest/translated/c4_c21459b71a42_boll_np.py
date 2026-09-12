# [BLUEPRINT] MOD-BT-049 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_c21459b71a42_boll_np
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
# [A_module] module_id=MOD-BT-049 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 翻译 049: 布林带1（手写 numpy 版）（原文: 2020年度精选策略/52 布林带1）。

原文逻辑: 单标的 600519；手写 20 日均线±2×标准差（np.mean/np.std，注意原文对 DataFrame
  整体求均值——按 close 列语义实现）；close>上轨 买入，close<下轨 清仓。
译文实现: 与 048 同构（轨道参数一致，std 口径 ddof=0 原文 numpy 默认→按总体标准差）。
因子拆解: BOLL 布林带——技术指标，不入 factor_registry。
翻译差异声明:
  D1 标的: 600519 一致
  D2 执行时点: 原文 open 价 → T+1 收盘成交
  D3 std 口径: numpy 默认总体标准差（ddof=0）vs 048 的样本标准差（ddof=1），两份原文实现本就不同
  D4 因子登记: BOLL 技术指标不入 factor_registry
  D5 框架样板: log 壳不翻译
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

STRATEGY_ID = "CAND-c21459b71a42"
WINDOW_KIND = "stock"
_SYM = "600519"


def build(start: str, end: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    load_start = str(pd.Timestamp(start) - pd.Timedelta(days=60))[:10]
    px = load_px(load_start, end, fields=("close",))
    closes = wide(px)
    closes = closes[closes.columns.intersection([_SYM])]
    mid = closes.rolling(20).mean()
    std = closes.rolling(20).std(ddof=0)
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
    print(json.dumps(emit(STRATEGY_ID, stats, ["D1 标的一致", "D2 T+1收盘", "D3 ddof=0",
                                               "D4 技术指标不入库", "D5 壳不译"]), ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
