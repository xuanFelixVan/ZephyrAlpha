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
]
