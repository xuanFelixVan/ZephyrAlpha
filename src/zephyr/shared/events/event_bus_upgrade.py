# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.events.event_bus_upgrade
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] tests/utils/test_orphan_integration.py; zephyr.integration.shared.events.event_bus_upgrade(re-export shim); zephyr.shared.events.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
EventBus Upgrade — 事件总线升级 (M-16)
支持事件版本化 + 增量升级机制。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: event_bus_upgrade.py
# 层: 算法
# - id: A1
#   name_zh: ① EventBusUpgrader
#   name_en: EventBusUpgrader
#   intro: 事件总线升级器 (M-16)
#   desc: 事件总线升级器 (M-16) 支持事件版本化迁移： - register_event(): 注册事件 Schema（含 version） - check_compatibilit…；公共方法（定义序）: registe…
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: EventBusUpgrader
#   downstream: tests/utils/test_orphan_integration.py; zephyr.integration.shared.events.event_…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from collections.abc import Callable
from dataclasses import dataclass, field


class EventVersionError(Exception):
    """事件版本错误。"""

    error_code = "ZA-SH-0033"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


@dataclass
class EventSchema:
    event_type: str
    version: int
    fields: list[str]
    deprecated_fields: list[str] = field(default_factory=list)
    migration_fn: Callable[[dict], dict] | None = None


class EventBusUpgrader:
    """
    事件总线升级器 (M-16)
    支持事件版本化迁移：
      - register_event(): 注册事件 Schema（含 version）
      - check_compatibility(): 校验 vN->vN+1 兼容性
      - upgrade(): 执行迁移函数
    """

    def __init__(self):
        self._schemas: dict[str, dict[int, EventSchema]] = {}

    def register(self, schema: EventSchema):
        if schema.event_type not in self._schemas:
            self._schemas[schema.event_type] = {}
        self._schemas[schema.event_type][schema.version] = schema

    def get_latest_version(self, event_type: str) -> int:
        versions = self._schemas.get(event_type, {})
        return max(versions.keys()) if versions else 0

    def check_compatibility(self, event_type: str, current_version: int) -> bool:
        latest = self.get_latest_version(event_type)
        return current_version == latest

    def upgrade(self, event_type: str, event_data: dict, from_version: int, to_version: int) -> dict:
        schemas = self._schemas.get(event_type, {})
        if not schemas:
            raise EventVersionError(f"Unknown event type: {event_type}")

        data = dict(event_data)
        for v in range(from_version, to_version):
            next_schema = schemas.get(v + 1)
            if next_schema is None:
                raise EventVersionError(f"No schema for {event_type} v{v + 1}")
            for deprecated_field in next_schema.deprecated_fields:
                data.pop(deprecated_field, None)

            if next_schema.migration_fn:
                data = next_schema.migration_fn(data)

        return data

    def upgrade_to_latest(self, event_type: str, event_data: dict, from_version: int) -> dict:
        latest = self.get_latest_version(event_type)
        if from_version == latest:
            return event_data
        return self.upgrade(event_type, event_data, from_version, latest)

    def all_event_types(self) -> list[str]:
        return list(self._schemas.keys())
