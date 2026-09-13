# [BLUEPRINT] MOD-BT-104 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_68cc0a6b40ba_value_select35
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
# [A_module] module_id=MOD-BT-104 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 翻译 098: 精选价值策略（原文: 2025年度精选策略/35，md5=68cc0a6b40ba）。

原文逻辑: 与 07（Slater 四条件）同族+行业过滤（周期行业剔除白名单 801xxx）+
  max_hold_stocknum=10 + by_cap_mean 权重 + 月频第 5 交易日调仓。
译文实现: 复用 096 slater_screen（剔除周期行业条件省略，D3——行业映射不可得）；
  max_hold 10 只按流通市值降序等权持有，月频第 5 交易日调仓。

[KNOWLEDGE_EFFECTIVE_FROM] 2026-09-14 | 源=策略原文公开发布日 | 生成=AI 会话（取晚者）
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd

from _c4_engine import emit, filter_st, load_px, load_st_flags, run_backtest, wide

logger = logging.getLogger(__name__)

STRATEGY_ID = "CAND-68cc0a6b40ba"
WINDOW_KIND = "stock"
_TOP, _REFRESH = 10, 21  # 月频约 21 交易日


def build(start: str, end: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    from c4_311220235636_slater_value import slater_screen

    load_start = str(pd.Timestamp(start) - pd.Timedelta(days=400))[:10]
    px = load_px(load_start, end, fields=("close",))
    close = filter_st(wide(px, "close").ffill(), load_st_flags(load_start, end))
    cand, mv_d, _pe = slater_screen(close, start, end)
    dates = close.index[(close.index >= pd.Timestamp(start)) & (close.index <= pd.Timestamp(end))]
    weights = pd.DataFrame(0.0, index=dates, columns=close.columns)
    c_idx = cand.shift(1).reindex(dates).fillna(False)
    mv_prev = mv_d.shift(1).reindex(dates)
    last_rebal = -1
    for k, dt in enumerate(dates):
        if last_rebal >= 0 and k - last_rebal < _REFRESH:
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
    print(json.dumps(emit(STRATEGY_ID, stats, ["D1 全A剔ST", "D2 月频收盘", "D3 行业剔除省略",
                                               "D4 公开方法论不入库", "D5 等权替 by_cap_mean"]), ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
