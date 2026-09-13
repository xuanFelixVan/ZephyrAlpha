# [BLUEPRINT] MOD-BT-164 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_valuation_pe_zz500
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
# [A_module] module_id=MOD-BT-164 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""低 PE 月频前 20 等权（中证500 域）（估值因子族·中盘代表）。

[KNOWLEDGE_EFFECTIVE_FROM] 2026-09-14 | 源=策略原文公开发布日 | 生成=AI 会话（取晚者）
"""
from __future__ import annotations
import json, logging, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd
from _c4_engine import emit, run_backtest
from _valuation_engine import build_valuation_strategy

STRATEGY_ID = "VAL-PE-ZZ500-020"
WINDOW_KIND = "stock"

def build(s, e):
    return build_valuation_strategy(s, e, metric="pe", ascending=True, top_n=20, universe="zz500", rebalance="monthly")

def main():
    logging.basicConfig(level=logging.INFO)
    from _c4_engine import C4_END, C4_START
    w, c = build(C4_START, C4_END)
    print(json.dumps(emit(STRATEGY_ID, run_backtest(w, c),
        ["D1 中证500", "D2 T+1收盘", "D3 pe_ttm", "D4 公开因子", "D5 引擎"]),
        ensure_ascii=False))

if __name__ == "__main__":
    main()
