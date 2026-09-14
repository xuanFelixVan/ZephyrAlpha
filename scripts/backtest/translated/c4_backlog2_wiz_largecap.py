# [BLUEPRINT] MOD-BT-171 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_backlog2_wiz_largecap
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
# [A_module] module_id=MOD-BT-171 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""向导式-1·大市值（流通市值降序）周频前 20 等权（源=2020年度精选策略/26，CAND-5e3284032a17）。

原文口径：聚宽向导生成器产物（约 400 行框架空壳），真实逻辑=利润增速>20 门过滤
+流通市值降序排序（权重 1）、每 10 交易日选股、通过池全持等权（by_cap_mean）。
本件=市值排序主导腿的排序近似翻译（增长门需利润表数据，属 B 档能力）。

[KNOWLEDGE_EFFECTIVE_FROM] 2026-09-15 | 源=策略原文公开发布日 | 生成=AI 会话（取晚者）
"""
from __future__ import annotations
import json, logging, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd
from _c4_engine import emit, run_backtest
from _valuation_engine import build_valuation_strategy

STRATEGY_ID = "CAND-5e3284032a17"
WINDOW_KIND = "stock"

def build(s, e):
    return build_valuation_strategy(s, e, metric="circ_mv", ascending=False, top_n=20, universe="all", rebalance="weekly")

def main():
    logging.basicConfig(level=logging.INFO)
    from _c4_engine import C4_END, C4_START
    w, c = build(C4_START, C4_END)
    print(json.dumps(emit(STRATEGY_ID, run_backtest(w, c),
        ["D1 全A", "D2 周频（原文每10交易日选股近似周档）",
         "D3 circ_mv 降序 top20（原文利润增速>20 门全持→市值排序前20 近似，增长门剔除声明=该门需利润表数据）",
         "D4 公开因子不登记", "D5 引擎=MOD-BT-096"]),
        ensure_ascii=False))

if __name__ == "__main__":
    main()
