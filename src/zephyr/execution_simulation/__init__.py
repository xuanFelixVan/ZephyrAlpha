# [BLUEPRINT] MOD-EXEC_SIM | docs/03_modules/_domain_execution_sim/almgren_chriss_impact_model/blueprint.md
# [MODULE] zephyr.execution_simulation
# [DOMAIN] D_EXEC_SIM
# [DEPENDENCIES] 无（守卫式 import 聚合子模块；子模块全注入）
# [CONSUMERS] 运行时装配批（执行仿真/回测冲击成本真源装配）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 子模块导入失败守卫降级为 None 不炸包; __all__ 词表闭合
# [MODIFY-GUARD] docs/03_modules/_domain_execution_sim/almgren_chriss_impact_model/blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 子模块错误契约见各自文件（AlmgrenChrissError 占位 ZA-EXSIM-UNREGISTERED-ALMGREN-CHRISS）
# [TESTS] tests/execution_simulation/
# [A_module] module_id=MOD-EXEC_SIM | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""zephyr.execution_simulation — 执行仿真域包门面（D_EXEC_SIM）。

P2-W08 首件施工：MOD-EXSIM-001 almgren_chriss_impact_model（Almgren-Chriss
冲击成本模型）。守卫式 import：子模块导入失败降级为 None 而不炸包，
运行时装配批按 None 检测决定接线。
"""

from __future__ import annotations

try:  # 守卫式 import：子模块缺失/导入异常不阻断包加载
    from zephyr.execution_simulation.almgren_chriss_impact_model import (
        AlmgrenChrissError,
        AlmgrenChrissImpactModel,
        ImpactParams,
        ImpactQuote,
        ImpactTrajectory,
        MinuteBar,
        ScheduleType,
        TrajectoryPoint,
    )
except ImportError:  # pragma: no cover — 守卫降级路径
    AlmgrenChrissError = None  # type: ignore[assignment]
    AlmgrenChrissImpactModel = None  # type: ignore[assignment]
    ImpactParams = None  # type: ignore[assignment]
    ImpactQuote = None  # type: ignore[assignment]
    ImpactTrajectory = None  # type: ignore[assignment]
    MinuteBar = None  # type: ignore[assignment]
    ScheduleType = None  # type: ignore[assignment]
    TrajectoryPoint = None  # type: ignore[assignment]

__all__ = [
    "AlmgrenChrissError",
    "AlmgrenChrissImpactModel",
    "ImpactParams",
    "ImpactQuote",
    "ImpactTrajectory",
    "MinuteBar",
    "ScheduleType",
    "TrajectoryPoint",
]
