# [BLUEPRINT] SRC-095 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.shared.events.event_bus
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.event_bus
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_event_bus | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
此路径已废弃，请直接使用 zephyr.shared.event_bus。
本文件保留为 compat shim，将在 Phase 4 物理删除。

SRC-0036: compat shim — 事件总线统一至 shared/event_bus

SRC-0036: 向后兼容 shim — event_bus 真源在 zephyr.shared.event_bus

v0.6.0 -> v0.3.0: core/events/event_bus.py 的 EventType、DomainEvent、EventBus 已合并到
shared/event_bus.py。本文件仅重新导出以保证向后兼容。

Import 路径映射:
    from zephyr.shared.events.event_bus import EventType    -> zephyr.shared.event_bus
    from zephyr.shared.events.event_bus import DomainEvent  -> zephyr.shared.event_bus
    from zephyr.shared.events.event_bus import EventBus     -> zephyr.shared.event_bus
"""

from zephyr.shared.event_bus import (  # noqa: F401
    DomainEvent,
    Event,
    EventBus,
    EventBusBackpressure,
    EventHandler,
    EventPriority,
    EventType,
    bus,
)
