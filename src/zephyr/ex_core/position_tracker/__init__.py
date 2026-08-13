# [BLUEPRINT] MOD-EX-002 | docs/03_modules/_domain_execution_core/position_tracker/blueprint.md
# [MODULE] zephyr.ex_core.position_tracker
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.ex_core.position_tracker.tracker
# [CONSUMERS] zephyr.governance.adapters.simulation_broker
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/ex_core/test_position_tracker.py
# [A_module] module_id=MOD-EX-002 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""


D_EXECUTION_CORE — Position Tracker 包

持仓跟踪器模块入口。从 SimulationBroker 拆出的独立持仓跟踪逻辑。

设计真源: D-EX-CORE-04 Position Tracker
蓝图: docs/03_modules/_domain_execution_core/position_tracker/blueprint.md

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: tracker 子模块符号 1个
#   fields: PositionTracker
#   code: zephyr.ex_core.position_tracker.tracker
# 层: 算法
# - id: A1
#   name_zh: ① 包级聚合再导出
#   name_en: zephyr.ex_core.position_tracker.__init__
#   intro: D_EXECUTION_CORE — Position Tracker 包
#   desc: MOD-EX-002 包入口，包级聚合再导出并声明 __all__（1项）
#   inputs: I1
#   outputs: zephyr.ex_core.position_tracker 包级公共命名空间
#   invariant: 包级导出以 __all__ 声明为准（1项）
# 层: 输出
# - id: O1
#   name_zh: zephyr.ex_core.position_tracker 包公共 API
#   name_en: __all__ 1项
#   intro: D_EXECUTION_CORE — Position Tracker 包——对外统一出口
#   downstream: 见蓝图头 [CONSUMERS] 声明
# [/ALGO_FLOW]
# 边:
# I1 --> A1
# A1 --> O1
"""

from zephyr.ex_core.position_tracker.tracker import PositionTracker

__all__ = ["PositionTracker"]
