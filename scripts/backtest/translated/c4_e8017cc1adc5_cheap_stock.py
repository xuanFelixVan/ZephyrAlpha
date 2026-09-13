# [BLUEPRINT] MOD-BT-157 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_e8017cc1adc5_cheap_stock
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.data.ch_config; numpy; pandas
# [CONSUMERS] C4 快筛批测（scripts/backtest/c4_batch_screen.py）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] PIT（T 日执行用 ≤T-1 信号；估值/股息截面 ≤T-1）；成本=冻结土规
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(数据缺失)
# [TESTS] tests/backtest/test_c4_batch_smoke.py
# [A_module] module_id=MOD-BT-157 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 翻译 085: 便宜股系列——PB 破净+高股息+PE 升序（原文: 2020年度精选策略/85 我就是要买便宜股）。

原文逻辑: 每半年调仓一次：全 A 中选 PB∈(0,1.5) 且（PE 条件段，原文该段不可见）股票，
  剔除股息率<=3% 者，按 PE 升序（同分看 PB 升序、股息率降序）取前 10 只等权持有。
译文实现: 半年频（每 ~126 交易日）按 T-1 截面：PB∈(0,1.5)、股息率>3%（dv_ttm）、
  PE>0 非亏损，PE 升序前 10 等权。
因子拆解: PB/PE/股息率（估值因子组，公开因子不登记 factor_registry）。
翻译差异声明:
  D1 股票池: 全 A（HFQ 表）剔 ST；原文停牌过滤不可得（声明）
  D2 执行时点: 原文开盘 → T 日收盘（引擎 T+1 起算收益）
  D3 UNCERTAIN: 原文 get_stock_list 的 PE 阈值段提取不可见，仅实现 PB(0,1.5)+股息>3%+PE>0
  D4 因子登记: 公开估值因子不登记
  D5 框架样板: 原文 jy 聚源股息率库 → dv_ttm 替代

[KNOWLEDGE_EFFECTIVE_FROM] 2026-09-14 | 源=策略原文公开发布日 | 生成=AI 会话（取晚者）
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd

from _c4_engine import emit, filter_st, load_px, load_st_flags, load_valuation, run_backtest, wide

logger = logging.getLogger(__name__)

STRATEGY_ID = "CAND-e8017cc1adc5"
WINDOW_KIND = "stock"
_TOP_N, _HALF = 10, 126


def build(start: str, end: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    load_start = str(pd.Timestamp(start) - pd.Timedelta(days=60))[:10]
    px = load_px(load_start, end, fields=("close",))
    closes = filter_st(wide(px).ffill(), load_st_flags(load_start, end))
    val = load_valuation(load_start, end, fields=("pe", "pb", "dividend_yield"))
    pe, pb, dv = (val[f].reindex(closes.index).reindex(columns=closes.columns) for f in ("pe", "pb", "dividend_yield"))

    ok = pb.gt(0) & pb.lt(1.5) & pe.gt(0) & dv.gt(3.0)
    dates = closes.index[(closes.index >= pd.Timestamp(start)) & (closes.index <= pd.Timestamp(end))]
    weights = pd.DataFrame(0.0, index=dates, columns=closes.columns)
    ok_idx = ok.shift(1).reindex(dates).fillna(False)
    pe_idx = pe.shift(1).reindex(dates)
    rebal_days = dates[::_HALF]
    for dt in rebal_days:
        k = dates.get_loc(dt)
        row = ok_idx.iloc[k]
        if not bool(row.any()):
            continue
        picks = pe_idx.iloc[k][row].dropna().sort_values().index[:_TOP_N]
        weights.loc[dt, picks] = 1.0 / len(picks)
    return weights, closes


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    from _c4_engine import C4_END, C4_START

    weights, closes = build(C4_START, C4_END)
    stats = run_backtest(weights, closes)
    print(json.dumps(emit(STRATEGY_ID, stats, ["D1 全A剔ST", "D2 T+1收盘", "D3 PE阈值UNCERTAIN",
                                               "D4 公开因子不登记", "D5 dv_ttm替代聚源"]), ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
