# [BLUEPRINT] MOD-BT-165 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_valuation_v2_pretty50_div
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
# [A_module] module_id=MOD-BT-165 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""漂亮 50 复现·高股息率旬频前 10 等权（源=2022年度精选策略/98，CAND-70ca674cdf4c）。

原文口径：全 A → 剔除流通市值最小 25% → 行业内股息率前 2/3 修饰 → 股息率降序取前 10，
每 10 个交易日调仓（g.shiftdays=10）。本件=股息率主导门的排序近似翻译。

[KNOWLEDGE_EFFECTIVE_FROM] 2026-09-15 | 源=策略原文公开发布日 | 生成=AI 会话（取晚者）
"""
from __future__ import annotations
import json, logging, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd
from _c4_engine import emit, run_backtest
from _valuation_engine import build_valuation_strategy

STRATEGY_ID = "VAL-DIV-PRETTY50-010"
WINDOW_KIND = "stock"

def build(s, e):
    return build_valuation_strategy(s, e, metric="dividend_yield", ascending=False, top_n=10, universe="all", rebalance="weekly")

def main():
    logging.basicConfig(level=logging.INFO)
    from _c4_engine import C4_END, C4_START
    w, c = build(C4_START, C4_END)
    print(json.dumps(emit(STRATEGY_ID, run_backtest(w, c),
        ["D1 全A（原文另剔流通市值后25%+行业内前2/3修饰，此处剔除声明）", "D2 周频（原文10日旬调仓近似）",
         "D3 dv_ttm 降序 top10", "D4 公开因子不登记", "D5 引擎=MOD-BT-096"]),
        ensure_ascii=False))

if __name__ == "__main__":
    main()
