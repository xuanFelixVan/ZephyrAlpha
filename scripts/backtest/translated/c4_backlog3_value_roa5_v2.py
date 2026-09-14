# [BLUEPRINT] MOD-BT-182 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_backlog3_value_roa5_v2
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
# [A_module] module_id=MOD-BT-182 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""大市值价值投资优化·破净高 ROA 前 5（源=聚宽2026年精选/75，CAND-a016c519e8bd）。

原文=2024/16 同族优化克隆（同五门+ROA 降序前 5），科创板/北交过滤声明剔除。
[KNOWLEDGE_EFFECTIVE_FROM] 2026-09-15 | 源=策略原文公开发布日 | 生成=AI 会话（取晚者）
"""
from __future__ import annotations
import json, logging, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd
from _c4_engine import emit, run_backtest
from _valuation_engine import build_valuation_strategy

STRATEGY_ID = "CAND-a016c519e8bd"
WINDOW_KIND = "stock"

def build(s, e):
    return build_valuation_strategy(s, e, metric="roa", ascending=False, top_n=5,
        universe="all", rebalance="monthly", sort_source="fundamental",
        gates=[("valuation","pb","<",1),("fundamental","roa",">",15),("fundamental","net_profit_yoy",">",0),("fundamental","ocfps",">",0)])

def main():
    logging.basicConfig(level=logging.INFO)
    from _c4_engine import C4_END, C4_START
    w, c = build(C4_START, C4_END)
    print(json.dumps(emit(STRATEGY_ID, run_backtest(w, c), ["D1 全A（原文剔科创/北交，板块过滤无轴声明）", "D2 T+1收盘", "D3 roa 降序 top5", "D4 公开因子不登记", "D5 引擎基本面门扩展版；与 MOD-BT-181 同族孪生件，簇内取舍归 C5"], ensure_ascii=False)))

if __name__ == "__main__":
    main()
