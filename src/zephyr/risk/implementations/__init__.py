# [A_module] module_id=MOD-UNK_implementations | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_domain-risk/risk-management-core/blueprint.md
# [MODULE] zephyr.risk.implementations
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""D_RISK — Risk Management Concrete Implementations

Phase C 具体实现包。包含所有抽象基类的默认生产级实现。

实现清单：
  - DefaultPositionLimitChecker     : PositionLimitCheckerBase 的具体实现
  - DefaultStopLossEngine           : StopLossEngineBase 的具体实现（4 种止损策略）
  - DefaultRiskLimitsCalculator     : RiskLimitsCalculator 的具体实现
  - DefaultRiskValidator            : RiskValidator 的具体实现（Pre-trade + Portfolio）
  - DefaultRiskManagerOrchestrator  : RiskManagerOrchestratorBase 的具体实现（编排器）
"""

# MIGRATED: from zephyr.risk.implementations.default_position_limit_checker import (  # removed by TC-7-2
# DefaultPositionLimitChecker,  # removed by TC-7-2
# )  # removed by TC-7-2
# MIGRATED: from zephyr.risk.implementations.default_stop_loss_engine import (  # removed by TC-7-2
# DefaultStopLossEngine,  # removed by TC-7-2
# StopLossRules,  # removed by TC-7-2
# )  # removed by TC-7-2
# MIGRATED: from zephyr.risk.implementations.default_risk_limits_calculator import (  # removed by TC-7-2
# DefaultRiskLimitsCalculator,  # removed by TC-7-2
# )  # removed by TC-7-2
# MIGRATED: from zephyr.risk.implementations.default_risk_validator import (  # removed by TC-7-2
# DefaultRiskValidator,  # removed by TC-7-2
# )  # removed by TC-7-2
# MIGRATED: from zephyr.risk.implementations.default_risk_manager_orchestrator import (  # removed by TC-7-2
# DefaultRiskManagerOrchestrator,  # removed by TC-7-2
# )  # removed by TC-7-2
#
# __all__ = ['DefaultPositionLimitChecker', 'DefaultRiskLimitsCalculator', 'DefaultRiskManagerOrchestrator', 'DefaultRiskValidator', 'DefaultStopLossEngine', 'StopLossRules', 'default_position_limit_checker', 'default_risk_limits_calculator', 'default_risk_manager_orchestrator', 'default_risk_validator', 'default_stop_loss_engine']
#

__all__ = [
    "default_position_limit_checker",
    "default_risk_limits_calculator",
    "default_risk_manager_orchestrator",
    "default_risk_validator",
    "default_stop_loss_engine",
]
