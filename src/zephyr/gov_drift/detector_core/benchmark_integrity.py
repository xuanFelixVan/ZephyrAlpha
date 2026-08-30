# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain-governance/drift-detector/blueprint.md
# [MODULE] zephyr.gov_drift.detector_core.benchmark_integrity
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
#   code: benchmark_integrity.py
# 层: 算法
# - id: A1
#   name_zh: ① 数据契约声明
#   name_en: data class declarations
#   intro: 纯声明类（无公共方法，AST 事实）: IntegrityDim
#   desc: 数据契约/异常/枚举声明共 1 类；无算法流程（AST 事实）
#   inputs: I1
#   outputs: 数据契约类集合
# 层: 输出
# - id: O1
#   name_zh: 数据契约声明（1 类）
#   name_en: data classes
#   intro: IntegrityDim
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


class IntegrityDim(str, Enum):
    MARKET_COVERAGE = "MARKET_COVERAGE"
    FACTOR_CONSISTENCY = "FACTOR_CONSISTENCY"
    BACKTEST_STABILITY = "BACKTEST_STABILITY"
    HFT_FIDELITY = "HFT_FIDELITY"


PIT_MAX_DELAY_MINUTES: Final[int] = 15
HEALTH_CHECK_INTERVAL: Final[dict[str, str]] = {
    "monthly": "所有dim+grid自动run",
    "quarterly": "full2016-2024 re-run vs Sept->bias report",
}
