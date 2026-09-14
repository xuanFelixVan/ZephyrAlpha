# [BLUEPRINT] MOD-BT-184 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_backlog3_mclean_screen
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
# [A_module] module_id=MOD-BT-184 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""穿越牛熊价值精选·麦克连六门近似（源=2025年度精选策略/87，CAND-0319395c57a7）。

原文=市值≥均值+流动比率≥均值+ROE≥均值+五年FCF>0+营收增速(6,30)+盈余增速(8,50) 门→流通市值升序。本件=增速区间+ROE/现金流正门近似。
[KNOWLEDGE_EFFECTIVE_FROM] 2026-09-15 | 源=策略原文公开发布日 | 生成=AI 会话（取晚者）
"""
from __future__ import annotations
import json, logging, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import pandas as pd
from _c4_engine import emit, run_backtest
from _valuation_engine import build_valuation_strategy

STRATEGY_ID = "CAND-0319395c57a7"
WINDOW_KIND = "stock"

def build(s, e):
    return build_valuation_strategy(s, e, metric="circ_mv", ascending=True, top_n=10,
        universe="all", rebalance="monthly", sort_source="valuation",
        gates=[("fundamental","revenue_yoy",">",6),("fundamental","net_profit_yoy",">",8),("fundamental","roe",">",0),("fundamental","ocfps",">",0)])

def main():
    logging.basicConfig(level=logging.INFO)
    from _c4_engine import C4_END, C4_START
    w, c = build(C4_START, C4_END)
    print(json.dumps(emit(STRATEGY_ID, run_backtest(w, c), ["D1 全A", "D2 T+1收盘", "D3 circ_mv 升序 top10（均值对比门→绝对门槛近似；五年 FCF→当季 ocfps>0 近似；区间上限门剔除）", "D4 公开因子不登记", "D5 引擎基本面门扩展版"], ensure_ascii=False)))

if __name__ == "__main__":
    main()
