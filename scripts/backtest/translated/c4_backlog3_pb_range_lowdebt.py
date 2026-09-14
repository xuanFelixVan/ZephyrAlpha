# [BLUEPRINT] MOD-BT-175 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_backlog3_pb_range_lowdebt
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
# [A_module] module_id=MOD-BT-175 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""低估值+低负债·PB 区间门市值前 20（源=2020年度精选策略/42，CAND-b1ab2a40225a）。

原文=PB(0,2)+流动比率>1.2+资产负债率高于中位数过滤+TRIX/RSI 择时。本件=PB 区间+负债率门近似，择时腿剔除。
[KNOWLEDGE_EFFECTIVE_FROM] 2026-09-15 | 源=策略原文公开发布日 | 生成=AI 会话（取晚者）
"""
from __future__ import annotations
import json, logging, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd
from _c4_engine import emit, run_backtest
from _valuation_engine import build_valuation_strategy

STRATEGY_ID = "CAND-b1ab2a40225a"
WINDOW_KIND = "stock"

def build(s, e):
    return build_valuation_strategy(s, e, metric="circ_mv", ascending=False, top_n=20,
        universe="all", rebalance="monthly", sort_source="valuation",
        gates=[("valuation","pb",">",0),("valuation","pb","<",2),("fundamental","debt_ratio",">",50)])

def main():
    logging.basicConfig(level=logging.INFO)
    from _c4_engine import C4_END, C4_START
    w, c = build(C4_START, C4_END)
    print(json.dumps(emit(STRATEGY_ID, run_backtest(w, c), ["D1 全A（原文中证800）", "D2 T+1收盘", "D3 circ_mv 降序 top20（原文债负中位数筛+TRIX/RSI 择时→负债率>50 门近似+择时剔除声明）", "D4 公开因子不登记", "D5 引擎基本面门扩展版"], ensure_ascii=False)))

if __name__ == "__main__":
    main()
