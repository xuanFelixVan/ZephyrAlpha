# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain-governance/drift-detector/blueprint.md
# [MODULE] zephyr.governance.drift_detector_core.ml_engineering
# [DOMAIN] D_BEHAVIORAL_AUDIT
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
# [A_module] module_id=MOD-SEC_ml_engineering | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from typing import Final
from enum import Enum


class DataLeakCheck(str, Enum):
    C1_FACTOR_DATE_GT_MARKET = "C1_FACTOR_DATE_GT_MARKET"
    C2_TRAIN_TEST_OVERLAP = "C2_TRAIN_TEST_OVERLAP"
    C3_FUTURE_ACCESS_FACTOR_STORE = "C3_FUTURE_ACCESS_FACTOR_STORE"
    C4_FACTOR_ANALYSIS_FUTURE_IC = "C4_FACTOR_ANALYSIS_FUTURE_IC"
    C5_INTRA_GROUP_SIGNAL_EARLY = "C5_INTRA_GROUP_SIGNAL_EARLY"
    C6_EARNINGS_SPLIT_EX_POST = "C6_EARNINGS_SPLIT_EX_POST"


LEAK_CHECKS: Final[dict[DataLeakCheck, str]] = {
    DataLeakCheck.C1_FACTOR_DATE_GT_MARKET: "factor_date > market_date → NEVER",
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
