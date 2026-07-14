# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.infrastructure.events.event_store
# [DOMAIN] D_INFRA_RUNTIME
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
# [A_module] module_id=MOD-INF_event_store | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Event Store — 事件持久化存储。

依据：
    蓝图 MOD-TASK_SYSTEM §6.13.3 + v0.6.0
    任务卡 TASK-INF-0124
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from zephyr.shared.event_bus import DomainEvent
from zephyr.shared.io.paths import REPO_ROOT


@dataclass
class EventStoreQuery:
    task_id: str = ""
    event_type: str = ""
    since: str = ""
    limit: int = 100


class EventStore:
    def __init__(self, data_dir: Path | None = None) -> None:
        self._data_dir = data_dir or (REPO_ROOT / "data" / "events")
        self._store_path = self._data_dir / "event_store.jsonl"

    def append(self, event: DomainEvent) -> None:
        self._data_dir.mkdir(parents=True, exist_ok=True)

        with open(self._store_path, "a", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "event_id": event.event_id,
                        "event_type": event.event_type.value,
                        "task_id": event.task_id,
                        "payload": event.payload,
                        "timestamp_utc": event.timestamp_utc,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )

    def append_batch(self, events: list[DomainEvent]) -> None:
        for event in events:
            self.append(event)

    def query(self, query: EventStoreQuery) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []

        if not self._store_path.exists():
            return results

        for line in self._store_path.read_text(encoding="utf-8").strip().split("\n"):
            if not line:
                continue

            try:
                data = json.loads(line)
                if query.task_id and data.get("task_id") != query.task_id:
                    continue
                if query.event_type and data.get("event_type") != query.event_type:
                    continue
                if query.since and data.get("timestamp_utc", "") < query.since:
                    continue
                results.append(data)
            except (json.JSONDecodeError, KeyError):
                pass

        return results[: query.limit]

    def get_all_for_task(self, task_id: str) -> list[dict[str, Any]]:
        return self.query(EventStoreQuery(task_id=task_id, limit=1000))

    def get_event_count(self) -> int:
        if not self._store_path.exists():
            return 0
        return len(self._store_path.read_text(encoding="utf-8").strip().split("\n"))
