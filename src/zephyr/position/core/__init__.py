# [BLUEPRINT] MOD-POS-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# position/core

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 子模块公共类定义
#   fields: DrawdownController（drawdown_controller）+ PositionSizingEngine（position_sizing_engine）
#   code: position/core/__init__.py L7-8
# 层: 算法
# - id: A1
#   name_zh: ① 包门面再导出
#   name_en: position.core __init__
#   intro: 把核心子模块的两个公共类聚合成 position.core 包级命名空间
#   desc: from 子模块 import 两类 + __all__ 白名单声明（L7-10），无计算逻辑
#   inputs: I1
#   outputs: 包级公共 API
# 层: 输出
# - id: O1
#   name_zh: position.core 公共 API
#   name_en: DrawdownController / PositionSizingEngine
#   intro: 对上游暴露回撤控制器与仓位裁决引擎两个入口类
#   downstream: zephyr.position 内部使用（仓位域各模块 import）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
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
