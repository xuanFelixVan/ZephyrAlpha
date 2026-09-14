# [BLUEPRINT] MOD-BT-180 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_backlog3_growth_peg4
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
# [A_module] module_id=MOD-BT-180 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""业绩增长+PEG·前 4（源=2024年度精选策略1/44，CAND-751983843b3f）。

原文=归母净利增速前 50%+PEG(PE/增速)>0.08 最小前 10%→等权前 4。本件=增速门+PE 升序近似。
[KNOWLEDGE_EFFECTIVE_FROM] 2026-09-15 | 源=策略原文公开发布日 | 生成=AI 会话（取晚者）
"""
from __future__ import annotations
import json, logging, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd
from _c4_engine import emit, run_backtest
from _valuation_engine import build_valuation_strategy

STRATEGY_ID = "CAND-751983843b3f"
WINDOW_KIND = "stock"

def build(s, e):
    return build_valuation_strategy(s, e, metric="pe", ascending=True, top_n=4,
        universe="all", rebalance="monthly", sort_source="valuation",
        gates=[("fundamental","net_profit_yoy",">",0)])

def main():
    logging.basicConfig(level=logging.INFO)
    from _c4_engine import C4_END, C4_START
    w, c = build(C4_START, C4_END)
    print(json.dumps(emit(STRATEGY_ID, run_backtest(w, c), ["D1 全A", "D2 T+1收盘", "D3 pe 升序 top4（PEG=PE/增速 复合因子→增速门+PE 排序近似）", "D4 公开因子不登记", "D5 引擎基本面门扩展版"], ensure_ascii=False)))

if __name__ == "__main__":
    main()
