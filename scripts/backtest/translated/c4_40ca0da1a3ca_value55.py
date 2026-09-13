# [BLUEPRINT] MOD-BT-105 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_40ca0da1a3ca_value55
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] c3_fundamental.financial_indicator; c3_fundamental.balance_sheet; c3_fundamental.cashflow_statement; zephyr.data.ch_config
# [CONSUMERS] C4 快筛批测（scripts/backtest/c4_batch_screen.py）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] PIT（财报按 announce_date）；成本=冻结土规；复用 096 的 slater_screen
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(数据缺失)
# [TESTS] tests/backtest/test_c4_batch_smoke.py
# [A_module] module_id=MOD-BT-105 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 翻译 099: 价值投资改进版（原文: 2025年度精选策略/55，md5=40ca0da1a3ca）。

原文逻辑: 07 Slater 同族选股（get_stock_list 共用）+ max_hold 4 + 双周调仓（g.num%2）+
  300 指数月线门（judge_More_average: 收盘在月线上方才买）+ 周度止损。
译文实现: 复用 096 slater_screen + 300 收盘月线门；max_hold 4 只按市值降序取前 4 等权，
  双周调仓；周度止损原文截断→省略（D3）。

[KNOWLEDGE_EFFECTIVE_FROM] 2026-09-14 | 源=策略原文公开发布日 | 生成=AI 会话（取晚者）
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd

from _c4_engine import emit, filter_st, load_index, load_px, load_st_flags, run_backtest, wide

logger = logging.getLogger(__name__)

STRATEGY_ID = "CAND-40ca0da1a3ca"
WINDOW_KIND = "stock"
_TOP, _REFRESH = 4, 10  # 双周约 10 交易日


def build(start: str, end: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    from c4_311220235636_slater_value import slater_screen

    load_start = str(pd.Timestamp(start) - pd.Timedelta(days=400))[:10]
    px = load_px(load_start, end, fields=("close",))
    close = filter_st(wide(px, "close").ffill(), load_st_flags(load_start, end))
    idx300 = load_index("000300", load_start, end, fields=("close",))["close"]
    ma_gate = (idx300 > idx300.rolling(20).mean()).shift(1).reindex(close.index).fillna(False)
    cand, mv_d, _pe = slater_screen(close, start, end)
    dates = close.index[(close.index >= pd.Timestamp(start)) & (close.index <= pd.Timestamp(end))]
    weights = pd.DataFrame(0.0, index=dates, columns=close.columns)
    c_idx = cand.shift(1).reindex(dates).fillna(False)
    mv_prev = mv_d.shift(1).reindex(dates)
    gate = ma_gate.shift(1).reindex(dates).fillna(False)
    last_rebal = -1
    for k, dt in enumerate(dates):
        if last_rebal >= 0 and k - last_rebal < _REFRESH:
            continue
        if not bool(gate.loc[dt]):
            continue
        cond = c_idx.iloc[k].values
        if not cond.any():
            continue
        caps = mv_prev.iloc[k][cond].fillna(0)
        caps = caps[caps > 0].sort_values(ascending=False)
        picks = list(caps.index)[:_TOP]
        weights.loc[dt, picks] = 1.0 / len(picks)
        last_rebal = k
    return weights, close


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    from _c4_engine import C4_END, C4_START

    weights, closes = build(C4_START, C4_END)
    stats = run_backtest(weights, closes)
    print(json.dumps(emit(STRATEGY_ID, stats, ["D1 全A剔ST", "D2 双周收盘", "D3 300月线门",
                                               "D4 公开方法论不入库", "D5 等权替 by_cap_mean"]), ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
