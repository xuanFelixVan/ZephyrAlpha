# [BLUEPRINT] MOD-BT-177 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_backlog3_peg_ebit_tiny
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
# [A_module] module_id=MOD-BT-177 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""PEG+EBIT+小市值·前 5（源=2022年度精选策略/56，CAND-9519cb55d6b7）。

原文=净利 TTM 增速>10%+EBIT yield 前 25%+换手波动<0.5 门→流通市值升序前 5。本件=增速+EBIT>0 门+市值升序近似。
[KNOWLEDGE_EFFECTIVE_FROM] 2026-09-15 | 源=策略原文公开发布日 | 生成=AI 会话（取晚者）
"""
from __future__ import annotations
import json, logging, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd
from _c4_engine import emit, run_backtest
from _valuation_engine import build_valuation_strategy

STRATEGY_ID = "CAND-9519cb55d6b7"
WINDOW_KIND = "stock"

def build(s, e):
    return build_valuation_strategy(s, e, metric="circ_mv", ascending=True, top_n=5,
        universe="all", rebalance="monthly", sort_source="valuation",
        gates=[("fundamental","net_profit_yoy",">",10),("fundamental","ebit",">",0)])

def main():
    logging.basicConfig(level=logging.INFO)
    from _c4_engine import C4_END, C4_START
    w, c = build(C4_START, C4_END)
    print(json.dumps(emit(STRATEGY_ID, run_backtest(w, c), ["D1 全A", "D2 T+1收盘", "D3 circ_mv 升序 top5（EBIT yield 分位→ebit>0 门近似；换手波动门无列剔除）", "D4 公开因子不登记", "D5 引擎基本面门扩展版"], ensure_ascii=False)))

if __name__ == "__main__":
    main()
