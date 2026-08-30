# [A_module] module_id=MOD-UNK-implementations_risk_implementations | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_domain_risk/risk-management-core/blueprint.md
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
"""
D_RISK — Risk Management Concrete Implementations

Phase C 具体实现包。包含所有抽象基类的默认生产级实现。

实现清单：
  - DefaultPositionLimitChecker     : PositionLimitCheckerBase 的具体实现
  - DefaultStopLossEngine           : StopLossEngineBase 的具体实现（4 种止损策略）
  - DefaultRiskLimitsCalculator     : RiskLimitsCalculator 的具体实现
  - DefaultRiskValidator            : RiskValidator 的具体实现（Pre-trade + Portfolio）
  - DefaultRiskManagerOrchestrator  : RiskManagerOrchestratorBase 的具体实现（编排器）

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: __init__.py
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 default_position_limit_checker, default_risk_limits_calculator, default_ris…
#   desc: __init__ import L0；__all__ 5 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（5 符号）
#   name_en: __all__
#   intro: default_position_limit_checker, default_risk_limits_calculator, default_risk_ma…
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

__all__ = [
    "default_position_limit_checker",
    "default_risk_limits_calculator",
    "default_risk_manager_orchestrator",
    "default_risk_validator",
    "default_stop_loss_engine",
]
