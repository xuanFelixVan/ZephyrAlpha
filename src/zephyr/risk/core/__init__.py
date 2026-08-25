# [BLUEPRINT] MOD-RK-011 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# risk/core

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: daily_auditor 子模块
#   fields: DailyAuditor日终审计器 + AuditRequest审计请求参数对象
#   code: zephyr.risk.core.daily_auditor L7
# - id: I2
#   name: stress_test_engine 子模块
#   fields: StressTestEngine压力测试引擎
#   code: zephyr.risk.core.stress_test_engine L8
# - id: I3
#   name: tail_risk_monitor 子模块
#   fields: TailRiskMonitor尾部风险监控器
#   code: zephyr.risk.core.tail_risk_monitor L9
# - id: I4
#   name: liquidity_crisis_manager 子模块
#   fields: run_intraday_liquidity_check盘中流动性编排 + 快照/状态/结果/配置4契约
#   code: zephyr.risk.core.liquidity_crisis_manager L10
# 层: 算法
# - id: A1
#   name_zh: ① 包入口导出装配
#   name_en: risk.core.__init__
#   intro: 从4个子模块导入9个公开符号并用__all__固定对外API面
#   desc: from导入DailyAuditor/AuditRequest/StressTestEngine/TailRiskMonitor/run_intraday_liquidity_check+4契约; __all__声明导出顺序; 无运行时逻辑
#   inputs: I1 I2 I3 I4
#   outputs: 9个公开导出符号
# 层: 输出
# - id: O1
#   name_zh: risk.core包公开API
#   name_en: __all__
#   intro: 对外暴露StressTestEngine/TailRiskMonitor/DailyAuditor/AuditRequest/run_intraday_liquidity_check+流动性4契约共9个符号
#   downstream: 无下游/内部使用(包入口被上层风控模块按名导入)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> O1
"""

from typing import Final

from zephyr.risk.core.daily_auditor import AuditRequest, DailyAuditor
from zephyr.risk.core.liquidity_crisis_manager import (
    LiquidityCrisisConfig,
    LiquidityLoopResult,
    LiquidityRecoveryState,
    MarketLiquiditySnapshot,
    run_intraday_liquidity_check,
)
from zephyr.risk.core.stress_test_engine import StressTestEngine
from zephyr.risk.core.tail_risk_monitor import TailRiskMonitor
from zephyr.risk.core.adaptive_risk_forecast import (
    ForwardVarForecast,
    forecast_forward_var,
)
from zephyr.risk.core.adaptive_risk_monitor import (
    RiskWatchSnapshot,
    assess_risk_watch,
)
from zephyr.risk.core.adaptive_risk_coordinator import (
    AdaptiveRiskDecision,
    CircuitBreakerLevel,
    decide_intraday,
    plan_premarket,
)
from zephyr.risk.core.black_swan_pattern_library import (
    BlackSwanScreenResult,
    MarketFeatures,
    screen_black_swan,
)
from zephyr.risk.core.crowding_response_engine import (
    CrowdingResponseAction,
    assess_crowding_response,
)

__all__: Final = [
    "StressTestEngine",
    "TailRiskMonitor",
    "DailyAuditor",
    "AuditRequest",
    "run_intraday_liquidity_check",
    "MarketLiquiditySnapshot",
    "LiquidityRecoveryState",
    "LiquidityLoopResult",
    "LiquidityCrisisConfig",
    "ForwardVarForecast",
    "forecast_forward_var",
    "RiskWatchSnapshot",
    "assess_risk_watch",
    "AdaptiveRiskDecision",
    "CircuitBreakerLevel",
    "decide_intraday",
    "plan_premarket",
    "BlackSwanScreenResult",
    "MarketFeatures",
    "screen_black_swan",
    "CrowdingResponseAction",
    "assess_crowding_response",
]

# NOTE(2026-08-25 W1c): 并行会话 scaffold 的 copula_garch_joint(CAND-RSK-036) 导出注册
# 因该模块尚为 stub(无 CopulaGarchJoint 类)且 scaffold 写入的 import 行语法非法,
# 修复包语法时暂未保留; 由 CAND-RSK-036 施工方实现类后自重挂导出(其 depgraph 节点
# 与 creation token 未受影响)。
# W1d(2026-08-25): CopulaGarchJointModel 已落码(MOD-RK-33), 按上方 NOTE 重挂合法导出。
from zephyr.risk.core.copula_garch_joint import (
    CopulaGarchConfig,
    CopulaGarchJointError,
    CopulaGarchJointModel,
    JointRiskReport,
    MarginalForecast,
)
from zephyr.risk.core.systemic_risk_alert_state_machine import (
    InvalidSystemicAlertInputError,
    RiskDirective,
    RiskLevel,
    SystemicRiskAlertConfig,
    SystemicRiskAlertStateMachine,
    SystemicRiskAssessment,
)

__all__ += [
    "CopulaGarchConfig",
    "CopulaGarchJointError",
    "CopulaGarchJointModel",
    "JointRiskReport",
    "MarginalForecast",
    "InvalidSystemicAlertInputError",
    "RiskDirective",
    "RiskLevel",
    "SystemicRiskAlertConfig",
    "SystemicRiskAlertStateMachine",
    "SystemicRiskAssessment",
]

# W1d(2026-08-25): EmergencyStopConfirmation 已落码(MOD-RK-36), 重挂合法导出(同 copula NOTE 路径)。
from zephyr.risk.core.emergency_stop_confirmation import (
    ConfirmationVerdict,
    EmergencyActionRequest,
    EmergencyActionType,
    EmergencyStopConfirmation,
    EmergencyStopConfirmationError,
)

__all__ += [
    "ConfirmationVerdict",
    "EmergencyActionRequest",
    "EmergencyActionType",
    "EmergencyStopConfirmation",
    "EmergencyStopConfirmationError",
]

# W1d(2026-08-25): PerformanceAttributionDegradationGuard 已落码(MOD-RK-37), 重挂合法导出(同 copula NOTE 路径)。
from zephyr.risk.core.performance_attribution_degradation import (
    DegradationAction,
    DegradationGuardConfig,
    InvalidDegradationInputError,
    PerformanceAttributionDegradationGuard,
    StrategyDegradationVerdict,
)

__all__ += [
    "DegradationAction",
    "DegradationGuardConfig",
    "InvalidDegradationInputError",
    "PerformanceAttributionDegradationGuard",
    "StrategyDegradationVerdict",
]

