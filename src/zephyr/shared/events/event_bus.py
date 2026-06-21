# [A_module] module_id=MOD-INF_event_bus | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-095 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md

# [MODULE] zephyr.infrastructure.shared_services.events.event_bus

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
此路径已废弃，请直接使用 zephyr.integration.shared_08.event_bus。
本文件保留为 compat shim，将在 Phase 4 物理删除。

SRC-0036: compat shim — 事件总线统一至 shared/event_bus

SRC-0036: 向后兼容 shim — event_bus 真源在 zephyr.integration.shared_08.event_bus

v0.6.0 -> v0.3.0: core/events/event_bus.py 的 EventType、DomainEvent、EventBus 已合并到
shared/event_bus.py。本文件仅重新导出以保证向后兼容。

Import 路径映射:
    from zephyr.shared.shared_services.events.event_bus import EventType    -> zephyr.integration.shared_08.event_bus
    from zephyr.shared.shared_services.events.event_bus import DomainEvent  -> zephyr.integration.shared_08.event_bus
    from zephyr.shared.shared_services.events.event_bus import EventBus     -> zephyr.integration.shared_08.event_bus
"""


from zephyr.integration.shared_08.event_bus import (  # noqa: F401
    DomainEvent,
    EventBus,
    EventType,
)
