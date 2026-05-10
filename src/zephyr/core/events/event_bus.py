"""
SRC-0036: 向后兼容 shim — event_bus 真源在 zephyr.shared.event_bus

v0.6.0 → v0.3.0: core/events/event_bus.py 的 EventType、DomainEvent、EventBus 已合并到
shared/event_bus.py。本文件仅重新导出以保证向后兼容。

Import 路径映射：
    from zephyr.core.events.event_bus import EventType    → zephyr.shared.event_bus
    from zephyr.core.events.event_bus import DomainEvent  → zephyr.shared.event_bus
    from zephyr.core.events.event_bus import EventBus     → zephyr.shared.event_bus
"""

from zephyr.shared.event_bus import (  # noqa: F401, E402
    DomainEvent,
    EventBus,
    EventType,
)
