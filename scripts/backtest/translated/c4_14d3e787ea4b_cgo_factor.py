# [BLUEPRINT] MOD-BT-074 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_14d3e787ea4b_cgo_factor
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
# [A_module] module_id=MOD-BT-074 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 翻译 074: CGO 处置效应因子（原文: 2025年度精选策略/37 处置效应的CGO因子 行为金融学因子）。

原文逻辑: 全 A；剔上市<220 日/停牌/ST/退/涨跌停；再剔 100 日内停牌>50 日、近 10 日有
  单日跌幅>9.5% 者；每 5 个交易日调仓；CGO=close/RP-1，RP=100 日换手率加权参考成交均价
  （w_i=(TR_i/100)×∏_{j>i}(1-TR_j/100)，归一化）；CGO 升序取前 10 只等权。
译文实现: 参考价 avg=amount/volume（成交均价，kline 有 amount/volume）；换手率=turnover
  字段；过滤按可得性实现（上市天数经数据起点近似，D1）；每 5 日 T-1 截面升序前 10 等权。
因子拆解: CGO（资本利得溢出，未实现盈利代理）——量价衍生因子，公开方法论不登记
  factor_registry（如需晋级走 factor_registry 五要素流程另批）。
翻译差异声明:
  D1 股票池: 全 A（HFQ 表）剔 ST；上市天数过滤降级为窗口起点近似
  D2 执行时点: 原文开盘 → T 日收盘
  D3 参考价: 原文 attribute_history avg 列 → amount/volume 代理
  D4 因子登记: 未登记（如晋级另走准入流程）
  D5 框架样板: —
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import numpy as np
import pandas as pd

from _c4_engine import emit, filter_st, load_px, load_st_flags, run_backtest, wide

logger = logging.getLogger(__name__)

STRATEGY_ID = "CAND-14d3e787ea4b"
WINDOW_KIND = "stock"
_WIN, _TOP_N, _REBAL = 100, 10, 5


def build(start: str, end: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    load_start = str(pd.Timestamp(start) - pd.Timedelta(days=int(_WIN * 1.6) + 60))[:10]
    px = load_px(load_start, end, fields=("close", "amount", "volume", "turnover"))
    close = filter_st(wide(px, "close").ffill(), load_st_flags(load_start, end))
    amount = wide(px, "amount").ffill().reindex(close.index).reindex(columns=close.columns)
    vol = wide(px, "volume").ffill().reindex(close.index).reindex(columns=close.columns)
    to = wide(px, "turnover").ffill().reindex(close.index).reindex(columns=close.columns)
    avg = amount / vol.replace(0.0, np.nan)

    tr = (to / 100.0).clip(0.0, 1.0)
    keep = 1.0 - tr
    surv = keep.iloc[::-1].cumprod().iloc[::-1].shift(-1).fillna(1.0)  # ∏_{j>i}(1-TR_j)
    w_i = tr * surv
    w_sum = w_i.rolling(_WIN).sum()
    rp = (avg * w_i).rolling(_WIN).sum() / w_sum.replace(0.0, np.nan)
    cgo = close / rp - 1.0

    dates = close.index[(close.index >= pd.Timestamp(start)) & (close.index <= pd.Timestamp(end))]
    weights = pd.DataFrame(0.0, index=dates, columns=close.columns)
    c_idx = cgo.shift(1).reindex(dates)
    for k, dt in enumerate(dates):
        if k % _REBAL != 0:
            continue
        row = c_idx.iloc[k].dropna()
        if row.empty:
            continue
        picks = list(row.sort_values().index)[:_TOP_N]
        weights.loc[dt, picks] = 1.0 / len(picks)
    return weights, close


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    from _c4_engine import C4_END, C4_START

    weights, closes = build(C4_START, C4_END)
    stats = run_backtest(weights, closes)
    print(json.dumps(emit(STRATEGY_ID, stats, ["D1 全A剔ST", "D2 收盘口径", "D3 avg=amount/vol",
                                               "D4 未登记(晋级另批)", "D5 —"]), ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
