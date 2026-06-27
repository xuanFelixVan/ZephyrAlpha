# [BLUEPRINT] MOD-GOVERNANCE
# [MODULE] zephyr.governance.persistence.event_store
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] zephyr.governance.event_store
# [CONSUMERS] zephyr.governance.gate_event_adapter; zephyr.governance.projection_engine; zephyr.governance.snapshot_manager; tests.test_event_store_stress
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
# 代理模块：将 zephyr.governance.persistence.event_store 重定向到 zephyr.governance.event_store
from sqlite3 import IntegrityError

from zephyr.governance.event_store import (
    EventRecord,
    EventStore,
    EventStoreError,
)

__all__ = ["EventRecord", "EventStore", "EventStoreError", "IntegrityError"]
