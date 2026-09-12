# [BLUEPRINT] MOD-BT-044 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_99873fd0bc17_macd_single
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
# [A_module] module_id=MOD-BT-044 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 翻译 044: MACD 单因子多头——金叉日轮换（原文: 2020年度精选策略/08 MACD单因子多头策略）。

原文逻辑: kuanke wizard 框架；池=中证500（000905.XSHG）剔 ST/退；技术过滤=MACD_judge_jincha
  (12,26,26) 金叉日入选；排序 input_dict 为空（空壳）→ 入选序即买入序；max_hold=100；
  卖出=持仓不在当日买入列表即卖（金叉日持有 1 日轮换）；by_market_cap_percent 权重。
译文实现: 中证500 成分快照；T-1 日 MACD 金叉（dif 上穿 dea）等权持有（≤100），非金叉日移出。
因子拆解: MACD 金叉（EMA12/EMA26 差值与其信号线上穿）——技术指标，不入 factor_registry。
翻译差异声明:
  D1 股票池: 中证500 最新成分快照（历史成分未回溯）
  D2 执行时点: T+1 收盘成交（原文 open 价）
  D3 仓位: 原文 by_market_cap_percent（市值加权）→ 等权（市值数据缺）
  D4 因子登记: MACD 技术指标不入 factor_registry
  D5 框架样板: wizard 财务/行情/形态空壳过滤（原文件 452 行约 400 行空壳）不翻译
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd

from _c4_engine import emit, filter_st, load_px, load_index_constituents, load_st_flags, run_backtest, wide

logger = logging.getLogger(__name__)

STRATEGY_ID = "CAND-99873fd0bc17"
WINDOW_KIND = "stock"
_MAX_HOLD = 100


def build(start: str, end: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    load_start = str(pd.Timestamp(start) - pd.Timedelta(days=60))[:10]
    px = load_px(load_start, end, fields=("close",))
    uni = load_index_constituents("000905.SH")
    px = px[px["symbol"].isin(uni)]
    closes = filter_st(wide(px).ffill(), load_st_flags(load_start, end))
    dif = closes.ewm(span=12, adjust=False).mean() - closes.ewm(span=26, adjust=False).mean()
    dea = dif.ewm(span=9, adjust=False).mean()
    golden = (dif > dea) & (dif.shift(1) <= dea.shift(1))
    dates = closes.index[(closes.index >= pd.Timestamp(start)) & (closes.index <= pd.Timestamp(end))]
    weights = pd.DataFrame(0.0, index=dates, columns=closes.columns)
    g_idx = golden.shift(1).reindex(dates).fillna(False)
    for k, dt in enumerate(dates):
        row = g_idx.iloc[k]
        picks = [s for s in closes.columns if bool(row[s])][: _MAX_HOLD]
        if picks:
            weights.loc[dt, picks] = 1.0 / len(picks)
    return weights, closes


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    from _c4_engine import C4_END, C4_START

    weights, closes = build(C4_START, C4_END)
    stats = run_backtest(weights, closes)
    print(json.dumps(emit(STRATEGY_ID, stats, ["D1 成分快照", "D2 T+1收盘", "D3 等权",
                                               "D4 技术指标不入库", "D5 空壳不译"]), ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
