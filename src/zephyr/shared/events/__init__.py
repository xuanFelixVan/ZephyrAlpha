# [A_module] module_id=MOD-SHR-events | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: EventBusUpgrader, EventSchema, EventVersionError, EVENT_PAYLOAD_MAP,…
#   code: __init__.py import L35
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 EVENT_PAYLOAD_MAP, EventBusUpgrade, EventBusUpgrader, EventSchema, EventVer…
#   desc: __init__ import L35；__all__ 20 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（20 符号）
#   name_en: __all__
#   intro: EVENT_PAYLOAD_MAP, EventBusUpgrade, EventBusUpgrader, EventSchema, EventVersion…
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from . import dlq_bridge, event_schemas
from .event_bus_upgrade import (
    EventBusUpgrader,
    EventSchema,
    EventVersionError,
)
from .event_schemas import (
    EVENT_PAYLOAD_MAP,
    FileEventPayload,
    ManualEventPayload,
    MetricEventPayload,
    TaskEventPayload,
    TimeEventPayload,
)
from .upgrade_strategy import (
    EventBusUpgrade,
    UpgradePlan,
    UpgradeStatus,
    UpgradeStep,
)

__all__ = [
    "EVENT_PAYLOAD_MAP",
    "EventBusUpgrade",
    "EventBusUpgrader",
    "EventSchema",
    "EventVersionError",
    "FileEventPayload",
    "ManualEventPayload",
    "MetricEventPayload",
    "TaskEventPayload",
    "TimeEventPayload",
    "UpgradePlan",
    "UpgradeStatus",
    "UpgradeStep",
    "dlq",
    "dlq_bridge",
    "event_bus_upgrade",
    "event_reactor",
    "event_schemas",
    "hook_dispatcher",
    "upgrade_strategy",
]
