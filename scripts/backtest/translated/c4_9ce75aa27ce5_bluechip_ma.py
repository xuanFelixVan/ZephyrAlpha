# [BLUEPRINT] MOD-BT-045 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_9ce75aa27ce5_bluechip_ma
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
# [A_module] module_id=MOD-BT-045 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 翻译 045: 蓝筹&均线——MA5>MA20 多头持有前 5（原文: 2020年度精选策略/70 蓝筹&均线）。

原文逻辑: kuanke wizard；池=沪深300（000300.XSHG）剔 ST/退；技术过滤=MA_judge_duotou(5,20)
  （MA5>MA20 多头）；排序空壳 → 按入选序；max_hold=5；不在买入列表即卖（日频轮换）。
译文实现: 沪深300 成分快照；T-1 日 MA5>MA20 者按代码序取前 5 等权持有，日频刷新。
因子拆解: MA5/MA20 均线多头——技术指标，不入 factor_registry。
翻译差异声明:
  D1 股票池: 沪深300 最新成分快照
  D2 执行时点: T+1 收盘成交（原文 open 价）
  D3 仓位: 原文 by_cap_mean（流通市值均值加权）→ 等权（市值数据缺）
  D4 因子登记: MA 技术指标不入 factor_registry
  D5 框架样板: wizard 空壳（财务/概念/形态全空）不翻译

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

STRATEGY_ID = "CAND-9ce75aa27ce5"
WINDOW_KIND = "stock"
_MAX_HOLD = 5


def build(start: str, end: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    load_start = str(pd.Timestamp(start) - pd.Timedelta(days=60))[:10]
    px = load_px(load_start, end, fields=("close",))
    hs = load_hs300()
    px = px[px["symbol"].isin(hs)]
    closes = filter_st(wide(px).ffill(), load_st_flags(load_start, end))
    bull = closes.rolling(5).mean() > closes.rolling(20).mean()
    dates = closes.index[(closes.index >= pd.Timestamp(start)) & (closes.index <= pd.Timestamp(end))]
    weights = pd.DataFrame(0.0, index=dates, columns=closes.columns)
    b_idx = bull.shift(1).reindex(dates).fillna(False)
    for k, dt in enumerate(dates):
        row = b_idx.iloc[k]
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
