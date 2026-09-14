# [BLUEPRINT] MOD-BT-173 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_backlog3_wiz63_growth_pb2
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
# [A_module] module_id=MOD-BT-173 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""向导式·成长四门+PB>2 月频市值前 20（源=2020年度精选策略/63，CAND-4da841c734ae）。

原文=营收/净利/营业利润率三门>10+PB>2 过滤、空排序全持等权。本件=四门+市值降序近似。
[KNOWLEDGE_EFFECTIVE_FROM] 2026-09-15 | 源=策略原文公开发布日 | 生成=AI 会话（取晚者）
"""
from __future__ import annotations
import json, logging, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd
from _c4_engine import emit, run_backtest
from _valuation_engine import build_valuation_strategy

STRATEGY_ID = "CAND-4da841c734ae"
WINDOW_KIND = "stock"

def build(s, e):
    return build_valuation_strategy(s, e, metric="circ_mv", ascending=False, top_n=20,
        universe="all", rebalance="weekly", sort_source="valuation",
        gates=[("fundamental","net_profit_yoy",">",10),("fundamental","revenue_yoy",">",10),("fundamental","net_margin",">",10),("valuation","pb",">",2)])

def main():
    logging.basicConfig(level=logging.INFO)
    from _c4_engine import C4_END, C4_START
    w, c = build(C4_START, C4_END)
    print(json.dumps(emit(STRATEGY_ID, run_backtest(w, c), ["D1 全A", "D2 周频（wizard refresh 10日近似）", "D3 circ_mv 降序 top20（原文空排序全持→排序近似；营业利润率门→net_margin 门近似）", "D4 公开因子不登记", "D5 引擎=MOD-BT-096 基本面门扩展版"], ensure_ascii=False)))

if __name__ == "__main__":
    main()
