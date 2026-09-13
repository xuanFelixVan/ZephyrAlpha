# [BLUEPRINT] MOD-BT-052 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_2e4d39a3f50b_multi_ma
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
# [A_module] module_id=MOD-BT-052 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 翻译 052: 多均线择时（原文: 2020年度精选策略/89 test1，单标的 600196）。

原文逻辑: 单标的 600196（复星医药）；MA5/10/20/30 多头排列（5>10>20>30）持有；
  MA5/10/20 空头排列（5<10<20）清仓；均线纠缠（相邻差 <0.3%/0.2%）观望不动作。
译文实现: 日线向量化状态机；信号 T-1，T 收盘执行（纠缠日维持原状）。
因子拆解: 多均线排列——技术指标，不入 factor_registry。
翻译差异声明:
  D1 标的: 600196 一致
  D2 执行时点: 原文 handle_data 当日收盘 → T 日收盘（引擎 T+1 起算收益）
  D3 纠缠判定: 原文按 handle_data 逐日现价语义，译文以收盘均线序列等价实现
  D4 因子登记: MA 技术指标不入 factor_registry
  D5 框架样板: record 壳不翻译

[KNOWLEDGE_EFFECTIVE_FROM] 2026-09-12 | 源=策略原文公开发布日 | 生成=AI 会话（取晚者）
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

STRATEGY_ID = "CAND-2e4d39a3f50b"
WINDOW_KIND = "stock"
_SYM = "600196"


def build(start: str, end: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    load_start = str(pd.Timestamp(start) - pd.Timedelta(days=60))[:10]
    px = load_px(load_start, end, fields=("close",))
    closes = wide(px)
    closes = closes[closes.columns.intersection([_SYM])]
    m5, m10 = closes.rolling(5).mean(), closes.rolling(10).mean()
    m20, m30 = closes.rolling(20).mean(), closes.rolling(30).mean()
    bull = (m5 > m10) & (m10 > m20) & (m20 > m30)
    bear = (m5 < m10) & (m10 < m20)
    entangle = ((m5 - m10).abs() / m10 < 0.003) | ((m10 - m20).abs() / m20 < 0.002)
    dates = closes.index[(closes.index >= pd.Timestamp(start)) & (closes.index <= pd.Timestamp(end))]
    weights = pd.DataFrame(0.0, index=dates, columns=closes.columns)
    b_idx = (bull & ~entangle).shift(1).reindex(dates).fillna(False).iloc[:, 0]
    s_idx = (bear & ~entangle).shift(1).reindex(dates).fillna(False).iloc[:, 0]
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
    print(json.dumps(emit(STRATEGY_ID, stats, ["D1 标的一致", "D2 收盘口径", "D3 纠缠等价实现",
                                               "D4 技术指标不入库", "D5 壳不译"]), ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
