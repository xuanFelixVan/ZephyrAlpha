# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain-governance/drift-detector/blueprint.md
# [MODULE] zephyr.gov_drift.detector_core.ml_engineering
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES]
# [CONSUMERS] MOD-GATE_ENGINE;MOD-INF-021;MOD-INF-020
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Git-native漂移检测;自动对账;漂移预算
# [MODIFY-GUARD] docs/03_modules/_domain-governance/drift-detector/blueprint.md;src/zephyr/behavioral-auditor/__init__.py
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/test_behavioral_auditor/
# [A_module] module_id=MOD-INF-023 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: ml_engineering.py
# 层: 算法
# - id: A1
#   name_zh: ① 数据契约声明
#   name_en: data class declarations
#   intro: 纯声明类（无公共方法，AST 事实）: DataLeakCheck, MarketRegime
#   desc: 数据契约/异常/枚举声明共 2 类；无算法流程（AST 事实）
#   inputs: I1
#   outputs: 数据契约类集合
# 层: 输出
# - id: O1
#   name_zh: 数据契约声明（2 类）
#   name_en: data classes
#   intro: DataLeakCheck, MarketRegime
#   downstream: MOD-GATE_ENGINE;MOD-INF-021;MOD-INF-020
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from enum import Enum
from typing import Final


class DataLeakCheck(str, Enum):
    C1_FACTOR_DATE_GT_MARKET = "C1_FACTOR_DATE_GT_MARKET"
    C2_TRAIN_TEST_OVERLAP = "C2_TRAIN_TEST_OVERLAP"
    C3_FUTURE_ACCESS_FACTOR_STORE = "C3_FUTURE_ACCESS_FACTOR_STORE"
    C4_FACTOR_ANALYSIS_FUTURE_IC = "C4_FACTOR_ANALYSIS_FUTURE_IC"
    C5_INTRA_GROUP_SIGNAL_EARLY = "C5_INTRA_GROUP_SIGNAL_EARLY"
    C6_EARNINGS_SPLIT_EX_POST = "C6_EARNINGS_SPLIT_EX_POST"


LEAK_CHECKS: Final[dict[DataLeakCheck, str]] = {
    DataLeakCheck.C1_FACTOR_DATE_GT_MARKET: "factor_date > market_date -> NEVER",
    DataLeakCheck.C2_TRAIN_TEST_OVERLAP: "train < test — time ordering",
    DataLeakCheck.C3_FUTURE_ACCESS_FACTOR_STORE: "不可达 — future barrier",
    DataLeakCheck.C4_FACTOR_ANALYSIS_FUTURE_IC: "用历史IC only — look-forward prevention",
    DataLeakCheck.C5_INTRA_GROUP_SIGNAL_EARLY: "延后1日 — signal delay",
    DataLeakCheck.C6_EARNINGS_SPLIT_EX_POST: "ex-ante only —前瞻性保证",
}


class MarketRegime(str, Enum):
    BULL = "BULL"
    RANGE_BOUND = "RANGE_BOUND"
    BEAR = "BEAR"


FEATURE_STORE_SCHEMA: Final[dict[str, str]] = {
    "symbol": "TEXT NOT NULL",
    "date": "DATE NOT NULL",
    "factor_name": "TEXT NOT NULL",
    "value": "REAL",
    "computed_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
    "pk": "PRIMARY KEY (symbol, date, factor_name)",
}
