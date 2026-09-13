# [BLUEPRINT] MOD-BT-069 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_6cb29d4d9ba8_mom_rev_300
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
# [A_module] module_id=MOD-BT-069 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 翻译 069: 反转效应月频 25 只（原文: 2023年度精选策略/66 基于动量和反转效应的沪深300成分股策略）。

原文逻辑: 池=沪深300；反转腿（动量腿被注释未启用）：每 30 个"周"（周=5 交易日计数，
  约 150 交易日）触发一次；30 根 5 日线（history 30×5d），ret=周线[-2]/周线[1]-1
  （剔首尾），取 ret 最小 25 只，清仓重建等权。
译文实现: 5 日线=收盘每 5 日取样（周线由日线聚合）；信号=T-1 截面，触发日收盘重建；
  每 150 交易日触发。
因子拆解: 30 周长期动量（反向）——反转因子，公开因子不登记 factor_registry。
翻译差异声明:
  D1 股票池: 沪深300 成分快照
  D2 执行时点: 原文开盘 → 触发日收盘（引擎 T+1 起算）
  D3 周线: 聚宽 5d bar → 日线每 5 日取样对齐
  D4 因子登记: 公开反转因子不登记
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

from _c4_engine import emit, filter_st, load_px, load_hs300, load_st_flags, run_backtest, wide

logger = logging.getLogger(__name__)

STRATEGY_ID = "CAND-6cb29d4d9ba8"
WINDOW_KIND = "stock"
_WEEKS, _TOP_N, _TRIGGER = 30, 25, 150


def build(start: str, end: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    load_start = str(pd.Timestamp(start) - pd.Timedelta(days=260))[:10]
    px = load_px(load_start, end, fields=("close",))
    hs = load_hs300()
    px = px[px["symbol"].isin(hs)]
    close = filter_st(wide(px).ffill(), load_st_flags(load_start, end))

    # 每 5 个交易日取样一根"周线"
    wk = close.iloc[::5]

    dates = close.index[(close.index >= pd.Timestamp(start)) & (close.index <= pd.Timestamp(end))]
    weights = pd.DataFrame(0.0, index=dates, columns=close.columns)
    last_trigger_pos = None
    for k, dt in enumerate(dates):
        if last_trigger_pos is not None and k - last_trigger_pos < _TRIGGER:
            continue
        up_to = wk.loc[wk.index < dt]  # 截至昨日已收盘的周线
        if len(up_to) < _WEEKS:
            continue
        hist = up_to.iloc[-_WEEKS:]
        r = hist.iloc[-2] / hist.iloc[1] - 1.0  # 30 根内 [-2]/[1]
        picks = list(r.dropna().sort_values().index)[:_TOP_N]
        weights.loc[dt, picks] = 1.0 / len(picks)
        last_trigger_pos = k
    return weights, close


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    from _c4_engine import C4_END, C4_START

    weights, closes = build(C4_START, C4_END)
    stats = run_backtest(weights, closes)
    print(json.dumps(emit(STRATEGY_ID, stats, ["D1 成分快照", "D2 触发日收盘", "D3 5日线取样对齐",
                                               "D4 公开反转因子不登记", "D5 —"]), ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
