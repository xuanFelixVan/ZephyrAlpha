# [BLUEPRINT] MOD-BT-181 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_backlog3_value_roa5
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
# [A_module] module_id=MOD-BT-181 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""大市值价值投资·破净高 ROA 前 5（源=2024年度精选策略1/16，CAND-6ba459329476）。

原文=PB<1+经营现金流>1e6+调整利润>1e6+ROA>15%+增速>0 门→ROA 降序前 5 月频。
[KNOWLEDGE_EFFECTIVE_FROM] 2026-09-15 | 源=策略原文公开发布日 | 生成=AI 会话（取晚者）
"""
from __future__ import annotations
import json, logging, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd
from _c4_engine import emit, run_backtest
from _valuation_engine import build_valuation_strategy

STRATEGY_ID = "CAND-6ba459329476"
WINDOW_KIND = "stock"

def build(s, e):
    return build_valuation_strategy(s, e, metric="roa", ascending=False, top_n=5,
        universe="all", rebalance="monthly", sort_source="fundamental",
        gates=[("valuation","pb","<",1),("fundamental","roa",">",15),("fundamental","net_profit_yoy",">",0),("fundamental","ocfps",">",0)])

def main():
    logging.basicConfig(level=logging.INFO)
    from _c4_engine import C4_END, C4_START
    w, c = build(C4_START, C4_END)
    print(json.dumps(emit(STRATEGY_ID, run_backtest(w, c), ["D1 全A（原文剔创业板/科创/北交+上市200日，板块过滤无轴声明）", "D2 T+1收盘", "D3 roa 降序 top5（现金流绝对额门→ocfps>0 近似）", "D4 公开因子不登记", "D5 引擎基本面门扩展版"], ensure_ascii=False)))

if __name__ == "__main__":
    main()
