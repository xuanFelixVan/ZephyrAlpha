# [BLUEPRINT] MOD-BT-075 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_ea8b60272c03_300etf_1060
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
# [A_module] module_id=MOD-BT-075 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 翻译 075: 沪深300ETF 10/60 双均线（原文: 2020年度精选策略/83 沪深300ETF-1060双均线）。

原文逻辑: 单标的 510310（沪深300ETF）；MA10>MA60 全仓买入，MA10<MA60 清仓，相等不动作。
译文实现: 510310 无窗口内 ETF 数据 → 000300 指数收益替代（D1）；MA10/60 于指数收盘；
  信号 T-1，T 收盘执行。
因子拆解: MA10/MA60 双均线——技术指标，不入 factor_registry。
翻译差异声明:
  D1 标的: 510310 ETF → 000300 指数收益替代（ETF 窗口无数据）
  D2 执行时点: 原文 every_bar → T 日收盘（引擎 T+1 起算收益）
  D3 —（无额外口径差异）
  D4 因子登记: MA 技术指标不入 factor_registry
  D5 框架样板: —

[KNOWLEDGE_EFFECTIVE_FROM] 2026-09-12 | 源=策略原文公开发布日 | 生成=AI 会话（取晚者）
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

STRATEGY_ID = "CAND-ea8b60272c03"
WINDOW_KIND = "index"


def build(start: str, end: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    load_start = str(pd.Timestamp(start) - pd.Timedelta(days=120))[:10]
    idx = load_index("000300", load_start, end, fields=("close",))
    closes = idx[["close"]].rename(columns={"close": "000300"})
    ma10, ma60 = closes["000300"].rolling(10).mean(), closes["000300"].rolling(60).mean()
    dates = closes.index[(closes.index >= pd.Timestamp(start)) & (closes.index <= pd.Timestamp(end))]
    weights = pd.DataFrame(0.0, index=dates, columns=["000300"])
    pos = 0.0
    for dt in dates:
        m10, m60 = ma10.shift(1).loc[dt], ma60.shift(1).loc[dt]
        if pd.notna(m10) and pd.notna(m60):
            if m10 > m60:
                pos = 1.0
            elif m10 < m60:
                pos = 0.0
        weights.loc[dt, "000300"] = pos
    return weights, closes


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    from _c4_engine import C4_END, C4_START

    weights, closes = build(C4_START, C4_END)
    stats = run_backtest(weights, closes)
    print(json.dumps(emit(STRATEGY_ID, stats, ["D1 510310→000300", "D2 收盘口径", "D3 无",
                                               "D4 不入库", "D5 —"]), ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
