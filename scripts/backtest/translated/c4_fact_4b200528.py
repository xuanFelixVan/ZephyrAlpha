# [BLUEPRINT] MOD-BT-159 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.translated.c4_fact_4b200528
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] scripts.backtest.factor_strategy_template
# [CONSUMERS] C4 快筛批测（E4 考卷件·公式轨桥生成）
# [STARTUP] manual
# [MATURITY] experimental
# [MODIFY-GUARD] schema-change
# [INVARIANTS] 模板生成件零逻辑（build 统一由 factor_strategy_template 承载）；
#   表达式=abs(ret_5d)；PIT+冻结土规由引擎保证；出生候选=CAND-32e5c7444cc0
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(数据缺失)
# [TESTS] tests/backtest/test_factor_strategy_template.py
# [A_module] module_id=MOD-BT-159 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""公式轨考卷件：abs(ret_5d)

生成=factor_strategy_template（MOD-BT-159 机械翻译桥）；出生候选=CAND-32e5c7444cc0；
因子方向=多头正向（增量 IC>0 验收锁定）。
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))          # _c4_engine 同目录
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))  # 仓库根（scripts.*）

STRATEGY_ID = "FACT-4b200528"
WINDOW_KIND = "stock"

EXPR = 'abs(ret_5d)'
TOP_N = 20


def build(s, e):
    from scripts.backtest.factor_strategy_template import build_factor_weights

    return build_factor_weights(s, e, EXPR, top_n=TOP_N)


def main():
    import json
    import logging

    logging.basicConfig(level=logging.INFO)
    from _c4_engine import C4_END, C4_START, emit, run_backtest

    w, c = build(C4_START, C4_END)
    print(json.dumps(emit(STRATEGY_ID, run_backtest(w, c),
        ["D1 HS300口径见面板", "D2 T+1收盘", "D3 公式因子多头正向", "D4 生成件=MOD-BT-159",
         "D5 引擎=MOD-BT-039"]),
        ensure_ascii=False))


if __name__ == "__main__":
    main()
