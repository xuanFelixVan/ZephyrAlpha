# [A_module] module_id=MOD-SHR_events | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.integration.shared.events
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
from zephyr.integration.shared.events.dlq import DeadLetter, DeadLetterQueue, attach_dlq_to_observer
from zephyr.integration.shared.events.dlq_bridge import DLQEventBridge, make_dlq_event_handler
from zephyr.integration.shared.events.dlq_bridge import attach_dlq_to_observer as dlq_bridge_attach
from zephyr.integration.shared.events.event_bus_upgrade import EventBusUpgrader, EventSchema, EventVersionError
from zephyr.integration.shared.events.event_schemas import (
    EVENT_PAYLOAD_MAP,
    FileEventPayload,
    ManualEventPayload,
    MetricEventPayload,
    TaskEventPayload,
    TimeEventPayload,
)
from zephyr.integration.shared.events.upgrade_strategy import EventBusUpgrade, UpgradePlan, UpgradeStatus, UpgradeStep

__all__ = [
    "EVENT_PAYLOAD_MAP",
    "DLQEventBridge",
    "DeadLetter",
    "DeadLetterQueue",
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
    "attach_dlq_to_observer",
    "dlq",
    "dlq_bridge",
    "dlq_bridge_attach",
    "event_schemas",
    "make_dlq_event_handler",
    "upgrade_strategy",
]
