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
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Event Store — 事件持久化存储。

依据：
    蓝图 MOD-TASK_SYSTEM §6.13.3 + v0.6.0
    任务卡 TASK-INF-0124

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: data_dir 参数
#   fields: 参数 data_dir（无注解）
#   code: event_store.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① EventStore
#   name_en: EventStore
#   intro: class EventStore 源码 L73-L130
#   desc: 公共方法（定义序）: append, append_batch, query, get_all_for_task, get_event_count；源码 L73-L130
#   inputs: data_dir
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: EventStore
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
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


# class-name-alias: 本模块 EventStore=JSONL DomainEvent 存储（MOD-INF-016，data/events/
# event_store.jsonl），区别于 zephyr.infrastructure.event_store.EventStore（SQLite 审计
# 事件存储，MOD-INF-002，events.db）。语义与存储引擎均不同——非 re-export。
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
