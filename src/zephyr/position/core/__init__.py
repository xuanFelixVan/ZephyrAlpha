# [BLUEPRINT] MOD-POS-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# position/core

"""


# [ALGO_FLOW] external: docs/03_modules/_domain_position/algo_flow/core__init__.yaml
"""

from typing import Final

from zephyr.position.core.drawdown_controller import DrawdownController
from zephyr.position.core.position_sizing_engine import PositionSizingEngine

# NOTE(2026-08-25, W-P1-19): scaffold 注册器斜杠非法 import 变种
# (`from zephyr/position/core.position_adjudication_center import ...`，语法错误级)，
# 已归一为点号合法 import（包门面再导出约定不变，#ARCH-242 同型复发）。
from zephyr.position.core.position_adjudication_center import PositionAdjudicationCenter

# NOTE(2026-08-25, W-P1-20): scaffold 注册器斜杠非法 import 变种复发
# (`from zephyr.position/core.core_satellite_allocator import ...`)，已归一。
from zephyr.position.core.core_satellite_allocator import CoreSatelliteAllocator

__all__: Final[list[str]] = [
    "DrawdownController",
    "PositionSizingEngine",
    "PositionAdjudicationCenter",
    "CoreSatelliteAllocator",
]

# MOD-POS-026 Defensive Asset Whitelist（gw-tdm-20260909：C11 护盘白名单接线，包门面再导出）
from zephyr.position.core.defensive_asset_whitelist import (
    CircuitLevel,
    DefensiveAdditionRequest,
    DefensiveVerdict,
    DefensiveWhitelistConfig,
    DefensiveWhitelistError,
    NationalTeamSignal,
    ReasonCode,
    ReversalSignal,
    WhitelistTier,
    evaluate_defensive_addition,
)

__all__: Final[list[str]] = __all__ + [
    "CircuitLevel",
    "DefensiveAdditionRequest",
    "DefensiveVerdict",
    "DefensiveWhitelistConfig",
    "DefensiveWhitelistError",
    "NationalTeamSignal",
    "ReasonCode",
    "ReversalSignal",
    "WhitelistTier",
    "evaluate_defensive_addition",
]

# ORPHAN-MODULE: 引用登记（gw-tdm-20260909：C9/C10 金字塔加仓）
from zephyr.position.core.pyramiding_rules import (  # noqa: F401
    GateCode,
    PyramidPlan,
    PyramidPlanRequest,
    PyramidingConfig,
    PyramidingError,
    PyramidingGateRequest,
    PyramidingPhase,
    check_pyramiding_eligibility,
    get_default_config,
    plan_pyramid_addition,
)

__all__ = __all__ + [
    "GateCode",
    "PyramidPlan",
    "PyramidPlanRequest",
    "PyramidingConfig",
    "PyramidingError",
    "PyramidingGateRequest",
    "PyramidingPhase",
    "check_pyramiding_eligibility",
    "get_default_config",
    "plan_pyramid_addition",
]

# MOD-POS-029 仓位配方编译器（st-f06combo-20260915：F-06 网格工厂雏形，包门面再导出）
from zephyr.position.core.position_recipe_compiler import (  # noqa: F401
    COST_TIERS,
    DimensionSpec,
    GridCompiler,
    GridExpansion,
    InvalidGridSchemaError,
    PositionRecipe,
)

__all__ = __all__ + [
    "COST_TIERS",
    "DimensionSpec",
    "GridCompiler",
    "GridExpansion",
    "InvalidGridSchemaError",
    "PositionRecipe",
]
