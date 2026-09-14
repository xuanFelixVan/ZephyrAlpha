# [BLUEPRINT] MOD-BT-183 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_backlog3_div_roe5
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] scripts.backtest.translated._valuation_engine
# [CONSUMERS] C4 快筛批测
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] PIT；成本=冻结土规
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(数据缺失)
# [TESTS] tests/backtest/test_c4_batch_smoke.py
# [A_module] module_id=MOD-BT-183 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""菜场大妈·高股息高 ROE 前 5（源=2024年度精选策略1/36，CAND-bb0b9f37ce93）。

原文=股息率前 25%+PEG<0+PB<3 门+ROE/PB 排序+小市值前 5。本件=股息/PB/ROE 三门+ROE 降序近似。
[KNOWLEDGE_EFFECTIVE_FROM] 2026-09-15 | 源=策略原文公开发布日 | 生成=AI 会话（取晚者）
"""
from __future__ import annotations
import json, logging, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd
from _c4_engine import emit, run_backtest
from _valuation_engine import build_valuation_strategy

STRATEGY_ID = "CAND-bb0b9f37ce93"
WINDOW_KIND = "stock"

def build(s, e):
    return build_valuation_strategy(s, e, metric="roe", ascending=False, top_n=5,
        universe="all", rebalance="monthly", sort_source="fundamental",
        gates=[("valuation","pb","<",3),("valuation","dividend_yield",">",0),("fundamental","roe",">",0)])

def main():
    logging.basicConfig(level=logging.INFO)
    from _c4_engine import C4_END, C4_START
    w, c = build(C4_START, C4_END)
    print(json.dumps(emit(STRATEGY_ID, run_backtest(w, c), ["D1 全A", "D2 T+1收盘", "D3 roe 降序 top5（PEG<0 门无列剔除；ROE/PB 复合比→ROE 排序近似；小市值尾排序剔除；盘中涨停检查剔除）", "D4 公开因子不登记", "D5 引擎基本面门扩展版"], ensure_ascii=False)))

if __name__ == "__main__":
    main()
