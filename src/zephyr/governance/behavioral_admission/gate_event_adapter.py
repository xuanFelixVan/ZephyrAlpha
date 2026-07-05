# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §event-sourcing
# [MODULE] zephyr.governance.behavioral_admission.gate_event_adapter
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.audit_trail.event_store; zephyr.governance.persistence.sqlite_schema
# [CONSUMERS] zephyr.governance.rule_enforcement.gate_engine
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] gate events are appended to task_events atomically with gate persistence
# [MODIFY-GUARD] event_type enum changes MUST update _GATE_EVENT_TYPE_MAP
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] GateEventAdapterError on write failure
# [TESTS] tests/test_event_store_stress.py
# [A_module] module_id=MOD-DAT_gate_event_adapter | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
GateEventAdapter — GateRepo 事件适配器（DW-0006）
===================================================
将 gate 运行结果作为事件追加到 task_events 表，
实现 gate 结果的 Event Sourcing 集成。

功能：
- append_gate_event: 将 gate pass/fail 结果作为 GATE_PASSED/GATE_FAILED 事件追加
- query_gate_events: 按 task_id 查询 gate 相关事件
"""

from __future__ import annotations

import logging
from pathlib import Path

from zephyr.governance.audit_trail.event_store import EventStore
from zephyr.shared.io.paths import DB_PATH

logger = logging.getLogger(__name__)

__all__ = [
    "GateEventAdapter",
]

_GATE_EVENT_TYPE_MAP = {
    "passed": "GATE_PASSED",
    "failed": "GATE_FAILED",
}


class GateEventAdapter:
    """GateRepo 事件适配器——将 gate 结果写入 task_events。

    参数
    ----
    db_path
        SQLite 数据库路径；默认 DB_PATH。
    """

    def __init__(self, db_path: Path | str | None = None) -> None:
        self._db_path: Path = Path(db_path) if db_path is not None else DB_PATH
        self._event_store: EventStore = EventStore(self._db_path, auto_init=True)

    def append_gate_event(
        self,
        task_id: str,
        gate_id: str,
        passed: bool,
        *,
        details: dict | None = None,
        session_id: str | None = None,
    ) -> str:
        """将 gate 运行结果作为事件追加到 task_events。

        参数
        ----
        task_id
            关联的任务 ID。
        gate_id
            门禁 ID（如 G1, G7）。
        passed
            门禁是否通过。
        details
            可选的详细信息。
        session_id
            可选的 session 标识。

        返回
        ----
        str
            事件 event_id。
        """
        event_type = _GATE_EVENT_TYPE_MAP["passed" if passed else "failed"]
        payload = {
            "gate_id": gate_id,
            "passed": passed,
        }
        if details:
            payload["details"] = details

        return self._event_store.append_event(
            task_id=task_id,
            event_type=event_type,
            payload=payload,
            session_id=session_id,
        )

    def query_gate_events(self, task_id: str) -> list[dict]:
        """查询指定 task_id 的 gate 相关事件。

        返回
        ----
        list[dict]
            gate 事件列表，按时间正序。
        """
        events = self._event_store.replay_events(task_id)
        return [
            {
                "event_id": ev.event_id,
                "event_type": ev.event_type,
                "payload": ev.payload,
                "timestamp": ev.timestamp,
                "session_id": ev.session_id,
            }
            for ev in events
            if ev.event_type in ("GATE_PASSED", "GATE_FAILED")
        ]

    def close(self) -> None:
        self._event_store.close()
