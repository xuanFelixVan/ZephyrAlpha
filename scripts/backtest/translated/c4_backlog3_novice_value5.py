# [BLUEPRINT] MOD-BT-186 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_backlog3_novice_value5
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
# [A_module] module_id=MOD-BT-186 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""新手价值五门·月频市值前 20（源=2020年度精选策略/44，CAND-3238a5ce80c8）。

原文=营收增速>15+PB(0,2)+PE<40+净利增速>10+ROA>4 五门、市值百分位权重全持+止损线。本件=五门+市值降序近似。
[KNOWLEDGE_EFFECTIVE_FROM] 2026-09-15 | 源=策略原文公开发布日 | 生成=AI 会话（取晚者）
"""
from __future__ import annotations
import json, logging, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd
from _c4_engine import emit, run_backtest
from _valuation_engine import build_valuation_strategy

STRATEGY_ID = "CAND-3238a5ce80c8"
WINDOW_KIND = "stock"

def build(s, e):
    return build_valuation_strategy(s, e, metric="circ_mv", ascending=False, top_n=20,
        universe="all", rebalance="weekly", sort_source="valuation",
        gates=[("fundamental","revenue_yoy",">",15),("valuation","pb",">",0),("valuation","pb","<",2),("valuation","pe","<",40),("fundamental","net_profit_yoy",">",10),("fundamental","roa",">",4)])

def main():
    logging.basicConfig(level=logging.INFO)
    from _c4_engine import C4_END, C4_START
    w, c = build(C4_START, C4_END)
    print(json.dumps(emit(STRATEGY_ID, run_backtest(w, c), ["D1 全A", "D2 周频（wizard refresh 10日近似）", "D3 circ_mv 降序 top20（市值百分位权重→等权；止损线剔除声明）", "D4 公开因子不登记", "D5 引擎基本面门扩展版"], ensure_ascii=False)))

if __name__ == "__main__":
    main()
