# [A_module] module_id=MOD-INF_event_bus | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-095 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md

# [MODULE] zephyr.shared.shared_services.events.event_bus

# [INVARIANTS] re-export shim only; truth source is zephyr.shared.event_bus (trae_046 GOV-ENG-004)
# [MODIFY-GUARD] truth source MUST NOT be modified here; changes go to zephyr.shared.event_bus
# [CONSUMERS] zephyr.infrastructure.events.event_store; zephyr.shared.events.event_reactor; zephyr.shared.events.hook_dispatcher

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] ImportError if shared.event_bus symbols unavailable

# [TESTS]
"""
EventBus re-export shim — 真源已合并至 zephyr.shared.event_bus (trae_046 GOV-ENG-004)。

本文件保留为向后兼容 shim，所有符号从 zephyr.shared.event_bus 重新导出。
新代码应直接 import from zephyr.shared.event_bus。

Import 路径映射:
    from zephyr.shared.shared_services.events.event_bus import EventType    -> zephyr.shared.event_bus
    from zephyr.shared.shared_services.events.event_bus import DomainEvent  -> zephyr.shared.event_bus
    from zephyr.shared.shared_services.events.event_bus import EventBus     -> zephyr.shared.event_bus
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
