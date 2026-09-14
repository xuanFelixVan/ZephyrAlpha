# [BLUEPRINT] MOD-BT-169 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_valuation_v2_div_steady5
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
# [A_module] module_id=MOD-BT-169 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""超稳股息率+均线·高股息率月频前 5 等权（源=2025年度精选策略/70，CAND-edcd45b9037f）。

原文口径：自分红送配明细自算股息率（gxl/gxl2/gxl3 三个口径），三轮分级排序逐级收窄
（前 16×N→前 8×N→前 4×N→前 2×N）取前 5，月频调仓，均线仅用于仓位控制非选股。
本件=高股息主导门的排序近似翻译。

[KNOWLEDGE_EFFECTIVE_FROM] 2026-09-15 | 源=策略原文公开发布日 | 生成=AI 会话（取晚者）
"""
from __future__ import annotations
import json, logging, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd
from _c4_engine import emit, run_backtest
from _valuation_engine import build_valuation_strategy

STRATEGY_ID = "VAL-DIV-STEADY-005"
WINDOW_KIND = "stock"

def build(s, e):
    return build_valuation_strategy(s, e, metric="dividend_yield", ascending=False, top_n=5, universe="all", rebalance="monthly")

def main():
    logging.basicConfig(level=logging.INFO)
    from _c4_engine import C4_END, C4_START
    w, c = build(C4_START, C4_END)
    print(json.dumps(emit(STRATEGY_ID, run_backtest(w, c),
        ["D1 全A", "D2 T+1收盘", "D3 dv_ttm 降序 top5（原文自算股息率三轮分级排序→单轮 dv_ttm 排序近似）",
         "D4 公开因子不登记", "D5 引擎=MOD-BT-096"]),
        ensure_ascii=False))

if __name__ == "__main__":
    main()
