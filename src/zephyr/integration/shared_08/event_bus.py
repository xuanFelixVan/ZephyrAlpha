# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.integration.shared_08.event_bus
# [DOMAIN] D-INTEGRATION
# [DEPENDENCIES] zephyr.integration.shared_08.contract_bus
# [CONSUMERS] zephyr.shared.events.event_bus (shim chain); legacy imports via integration.shared_08
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] re-export shim only; truth source is zephyr.shared.event_bus (trae_046 GOV-ENG-004)
# [MODIFY-GUARD] truth source MUST NOT be modified here; changes go to zephyr.shared.event_bus
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError if shared.event_bus symbols unavailable
# [TESTS] tests/test_event_bus.py
# [A_module] module_id=MOD-INT_event_bus | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
"""
EventBus re-export shim — 真源已合并至 zephyr.shared.event_bus (trae_046 GOV-ENG-004)。

本文件保留为向后兼容 shim，所有符号从 zephyr.shared.event_bus 重新导出。
新代码应直接 import from zephyr.shared.event_bus。
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
