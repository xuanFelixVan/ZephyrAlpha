# [BLUEPRINT] MOD-BT-172 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_backlog2_mktcap5
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
# [A_module] module_id=MOD-BT-172 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""价值投资策略-大盘择时·大市值月频前 5 等权（源=2025年度精选策略/54，CAND-ab4dc295d8eb）。

原文口径：全 A → ST/涨停/停牌过滤 → 流通市值降序取前 5（g.buy_stock_count=5）、
月度选股+周度执行、000300 均线择时门（RiskControl，看多才开仓）。
本件=市值排序主导腿的排序近似翻译（择时门属 C 档能力，剔除声明）。

[KNOWLEDGE_EFFECTIVE_FROM] 2026-09-15 | 源=策略原文公开发布日 | 生成=AI 会话（取晚者）
"""
from __future__ import annotations
import json, logging, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd
from _c4_engine import emit, run_backtest
from _valuation_engine import build_valuation_strategy

STRATEGY_ID = "CAND-ab4dc295d8eb"
WINDOW_KIND = "stock"

def build(s, e):
    return build_valuation_strategy(s, e, metric="circ_mv", ascending=False, top_n=5, universe="all", rebalance="monthly")

def main():
    logging.basicConfig(level=logging.INFO)
    from _c4_engine import C4_END, C4_START
    w, c = build(C4_START, C4_END)
    print(json.dumps(emit(STRATEGY_ID, run_backtest(w, c),
        ["D1 全A", "D2 月频（原文月选股+周执行，执行周频仅为择时门节拍，剔门后=月频持有）",
         "D3 circ_mv 降序 top5（择时门剔除声明=000300 均线择时属 C 档能力）",
         "D4 公开因子不登记", "D5 引擎=MOD-BT-096"]),
        ensure_ascii=False))

if __name__ == "__main__":
    main()
