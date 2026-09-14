# [BLUEPRINT] MOD-BT-166 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_valuation_v2_pb_lowturn
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
# [A_module] module_id=MOD-BT-166 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""低 PB（小市值低换手修饰）月频前 35 等权（源=2022年度精选策略/81，CAND-b6bcb28f7620）。

原文口径：月频，双池合并——①PB 升序前 70→换手率升序前 35；②市值升序前 70→换手率升序前 35，
两池并集等权持有。本件=低 PB 主导腿的排序近似翻译。

[KNOWLEDGE_EFFECTIVE_FROM] 2026-09-15 | 源=策略原文公开发布日 | 生成=AI 会话（取晚者）
"""
from __future__ import annotations
import json, logging, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd
from _c4_engine import emit, run_backtest
from _valuation_engine import build_valuation_strategy

STRATEGY_ID = "VAL-PB-LOWTURN-035"
WINDOW_KIND = "stock"

def build(s, e):
    return build_valuation_strategy(s, e, metric="pb", ascending=True, top_n=35, universe="all", rebalance="monthly")

def main():
    logging.basicConfig(level=logging.INFO)
    from _c4_engine import C4_END, C4_START
    w, c = build(C4_START, C4_END)
    print(json.dumps(emit(STRATEGY_ID, run_backtest(w, c),
        ["D1 全A", "D2 T+1收盘", "D3 pb 升序 top35（原文双池漏斗取低PB主导腿末端35，小市值/低换手腿剔除声明）",
         "D4 公开因子不登记", "D5 引擎=MOD-BT-096"]),
        ensure_ascii=False))

if __name__ == "__main__":
    main()
