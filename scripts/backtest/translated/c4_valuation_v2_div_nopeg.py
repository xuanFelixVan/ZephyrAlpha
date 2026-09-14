# [BLUEPRINT] MOD-BT-170 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_valuation_v2_div_nopeg
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
# [A_module] module_id=MOD-BT-170 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""高股息率-低 PEG-低股价·高股息率月频前 20 等权（源=2024年度精选策略1/26，CAND-a7255b272cc9）。

原文口径：高股息率+低 PEG+低股价三门复合排序取前 20（g.stock_num=20），多条件过滤池。
PEG 门需盈利预测数据（本项目窗口内无 PIT 源），低股价门为名义价格锚（无经济含义）。
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

STRATEGY_ID = "VAL-DIV-NOPEG-020"
WINDOW_KIND = "stock"

def build(s, e):
    return build_valuation_strategy(s, e, metric="dividend_yield", ascending=False, top_n=20, universe="all", rebalance="monthly")

def main():
    logging.basicConfig(level=logging.INFO)
    from _c4_engine import C4_END, C4_START
    w, c = build(C4_START, C4_END)
    print(json.dumps(emit(STRATEGY_ID, run_backtest(w, c),
        ["D1 全A", "D2 T+1收盘",
         "D3 dv_ttm 降序 top20（原文高股息/低PEG/低股价三门复合→高股息单门排序近似，PEG 门无 PIT 源+低股价门剔除声明）",
         "D4 公开因子不登记", "D5 引擎=MOD-BT-096"]),
        ensure_ascii=False))

if __name__ == "__main__":
    main()
