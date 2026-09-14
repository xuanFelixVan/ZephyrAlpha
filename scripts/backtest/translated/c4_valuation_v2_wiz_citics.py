# [BLUEPRINT] MOD-BT-168 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_valuation_v2_wiz_citics
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
# [A_module] module_id=MOD-BT-168 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""中信证券向导·低 PB 月频前 20 等权（源=2020年度精选策略/99，CAND-60a9a654f19e）。

原文口径：聚宽向导生成器产物，真实选股=market_cap>0（恒真占位）+PB<1.5 两门过滤、
全 A、日频刷新、排序键空（全持通过池）等权。本件=破净价值门的排序近似翻译。

[KNOWLEDGE_EFFECTIVE_FROM] 2026-09-15 | 源=策略原文公开发布日 | 生成=AI 会话（取晚者）
"""
from __future__ import annotations
import json, logging, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd
from _c4_engine import emit, run_backtest
from _valuation_engine import build_valuation_strategy

STRATEGY_ID = "VAL-WIZ-CITICS-020"
WINDOW_KIND = "stock"

def build(s, e):
    return build_valuation_strategy(s, e, metric="pb", ascending=True, top_n=20, universe="all", rebalance="monthly")

def main():
    logging.basicConfig(level=logging.INFO)
    from _c4_engine import C4_END, C4_START
    w, c = build(C4_START, C4_END)
    print(json.dumps(emit(STRATEGY_ID, run_backtest(w, c),
        ["D1 全A", "D2 月频（原文日频刷新，向导日频=重复选股，月频为引擎可比档）",
         "D3 pb 升序 top20（原文 PB<1.5 绝对阈值过滤→低PB排序近似）",
         "D4 公开因子不登记", "D5 引擎=MOD-BT-096"]),
        ensure_ascii=False))

if __name__ == "__main__":
    main()
