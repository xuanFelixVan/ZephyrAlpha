# [BLUEPRINT] MOD-BT-162 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_valuation_div_high
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
# [A_module] module_id=MOD-BT-162 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""高股息率月频前 20 等权（估值因子族·高股息代表）。

[KNOWLEDGE_EFFECTIVE_FROM] 2026-09-14 | 源=策略原文公开发布日 | 生成=AI 会话（取晚者）
"""
from __future__ import annotations
import json, logging, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd
from _c4_engine import emit, run_backtest
from _valuation_engine import build_valuation_strategy

STRATEGY_ID = "VAL-DIV-HIGH-020"
WINDOW_KIND = "stock"

def build(s, e):
    return build_valuation_strategy(s, e, metric="dividend_yield", ascending=False, top_n=20, universe="hs300", rebalance="monthly")

def main():
    logging.basicConfig(level=logging.INFO)
    from _c4_engine import C4_END, C4_START
    w, c = build(C4_START, C4_END)
    print(json.dumps(emit(STRATEGY_ID, run_backtest(w, c),
        ["D1 HS300", "D2 T+1收盘", "D3 dv_ttm 降序", "D4 公开因子", "D5 引擎=MOD-BT-096"]),
        ensure_ascii=False))

if __name__ == "__main__":
    main()
