# [BLUEPRINT] MOD-EX-002 | docs/03_modules/_domain_execution_core/position_tracker/blueprint.md
# [MODULE] zephyr.ex_core.position_tracker
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.ex_core.position_tracker.tracker
# [CONSUMERS] zephyr.governance.adapters.simulation_broker
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/ex_core/test_position_tracker.py
# [TTL] permanent
"""D_EXECUTION_CORE — Position Tracker 包

持仓跟踪器模块入口。从 SimulationBroker 拆出的独立持仓跟踪逻辑。

设计真源: D-EX-CORE-04 Position Tracker
蓝图: docs/03_modules/_domain_execution_core/position_tracker/blueprint.md
"""

from zephyr.ex_core.position_tracker.tracker import PositionTracker

__all__ = ["PositionTracker"]
