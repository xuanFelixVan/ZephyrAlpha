# [BLUEPRINT] MOD-INF-021 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [TTL] permanent
# 代理包：将 zephyr.governance.escalation 重定向到实际模块
# 测试文件导入 from zephyr.governance.escalation import EscalationEngine, RuleCategory, ...
# 实际定义在 escalation_engine.py 和 escalation_models.py

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: escalation_engine 子模块符号 1个
#   fields: EscalationEngine
#   code: zephyr.governance.escalation.escalation_engine
# - id: I2
#   name: escalation_models 子模块符号 9个
#   fields: DelegationRecord / DelegationStrategy / EconomicGuard / EscalationEvent / EscalationLevel / EscalationResult 等9个
#   code: zephyr.governance.escalation.escalation_models
# - id: I3
#   name: delegation_engine 子模块符号 1个
#   fields: DelegationEngine
#   code: zephyr.governance.intelligence_governance.delegation_engine
# - id: I4
#   name: circuit_breaker 子模块符号 3个
#   fields: CircuitBreaker / CircuitBreakerConfig / CircuitState
#   code: zephyr.governance.resilience_governance.circuit_breaker
# 层: 算法
# - id: A1
#   name_zh: ① 包级聚合再导出
#   name_en: zephyr.governance.escalation.__init__
#   intro: 代理包：将 zephyr.governance.escalation 重定向到实际模块
#   desc: __unmanaged__src/zephyr/governance/escalation/__init__.py 包入口，包级聚合再导出并声明 __all__（31项）
#   inputs: I1 I2 I3 I4
#   outputs: zephyr.governance.escalation 包级公共命名空间
#   invariant: 包级导出以 __all__ 声明为准（31项）
# 层: 输出
# - id: O1
#   name_zh: zephyr.governance.escalation 包公共 API
#   name_en: __all__ 31项
#   intro: 代理包：将 zephyr.governance.escalation 重定向到实际模块——对外统一出口
#   downstream: 见蓝图头 [CONSUMERS] 声明
# [/ALGO_FLOW]
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> O1
"""

from zephyr.governance.escalation.escalation_engine import (
    EscalationEngine,
)
from zephyr.governance.escalation.escalation_models import (
    DelegationRecord,
    DelegationStrategy,
    EconomicGuard,
    EscalationEvent,
    EscalationLevel,
    EscalationResult,
    EscalationRule,
    EscalationState,
    RuleCategory,
)
from zephyr.governance.intelligence_governance.delegation_engine import (
    DelegationEngine,
)
from zephyr.governance.resilience_governance.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitState,
)

__all__ = [
    "CircuitBreaker",
    "CircuitBreakerConfig",
    "CircuitState",
    "DelegationEngine",
    "DelegationRecord",
    "DelegationStrategy",
    "EconomicGuard",
    "EscalationEngine",
    "EscalationEvent",
    "EscalationLevel",
    "EscalationResult",
    "EscalationRule",
    "EscalationState",
    "RuleCategory",
    "alternative_path_blocker",
    "consequence_manager",
    "contracts",
    "escalation_api",
    "escalation_fatigue_manager",
    "escalation_loop_detector",
    "escalation_metrics",
    "escalation_models",
    "escalation_smoke_tests",
    "git_hook_pre_scanner",
    "human_factors",
    "identity_verifier",
    "incident_response",
    "order_state_escalator",
    "result_types",
    "spof_checker",
    "triage",
]
