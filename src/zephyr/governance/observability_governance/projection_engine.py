# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §event-sourcing
# [MODULE] zephyr.governance.observability_governance.projection_engine
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.audit_trail.event_store; zephyr.governance.persistence.sqlite_schema
# [CONSUMERS] zephyr.governance.persistence.task_repo; zephyr.governance.audit.snapshot_manager
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] fold_to_current_state returns deterministic state for same event sequence; unknown event_types are no-op
# [MODIFY-GUARD] _HANDLERS registry — new event types MUST register a handler
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ProjectionError on handler failure
# [TESTS] tests/test_event_store_stress.py
# [A_module] module_id=MOD-DAT_projection_engine | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
ProjectionEngine — 事件折叠为当前状态（DW-0003）
=================================================
将 task_events 中的事件流折叠（fold）为任务的当前状态 dict。

支持的事件类型：
- CREATED: 初始化任务状态
- STATUS_CHANGED: 更新 status 字段
- PRIORITY_CHANGED: 更新 priority 字段
- FIELD_UPDATED: 更新任意字段（payload 中指定 field + value）

未知事件类型：no-op（不修改状态，不报错）。
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from zephyr.governance.audit_trail.event_store import EventStore
from zephyr.shared.io.paths import DB_PATH

logger = logging.getLogger(__name__)

__all__ = [
    "ProjectionEngine",
    "ProjectionError",
]


class ProjectionError(RuntimeError):
    """投影计算失败。"""
    error_code = "ZA-GV-0030"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


def _handle_created(state: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    for key, value in payload.items():
        if key not in state or key != "task_id":
            state[key] = value
    return state


def _handle_status_changed(state: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    new_status = payload.get("status") or payload.get("to")
    if new_status is not None:
        state["status"] = new_status
    return state


def _handle_priority_changed(state: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    new_priority = payload.get("priority") or payload.get("to")
    if new_priority is not None:
        state["priority"] = new_priority
    return state


def _handle_field_updated(state: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    field = payload.get("field")
    value = payload.get("value")
    if field is not None:
        state[field] = value
    return state


_HANDLERS: dict[str, Any] = {
    "CREATED": _handle_created,
    "STATUS_CHANGED": _handle_status_changed,
    "PRIORITY_CHANGED": _handle_priority_changed,
    "FIELD_UPDATED": _handle_field_updated,
}


class ProjectionEngine:
    """事件折叠引擎——将事件流 fold 为当前状态 dict。

    参数
    ----
    db_path
        SQLite 数据库路径；默认 DB_PATH。
    """

    def __init__(self, db_path: Path | str | None = None) -> None:
        self._db_path: Path = Path(db_path) if db_path is not None else DB_PATH
        self._event_store: EventStore | None = None

    def _get_event_store(self) -> EventStore:
        if self._event_store is None:
            self._event_store = EventStore(self._db_path, auto_init=True)
        return self._event_store

    def fold_to_current_state(self, task_id: str) -> dict[str, Any]:
        """折叠指定 task_id 的全部事件为当前状态 dict。

        参数
        ----
        task_id
            目标任务 ID。

        返回
        ----
        dict
            折叠后的当前状态。空事件流返回空 dict。
        """
        store = self._get_event_store()
        events = store.replay_events(task_id)

        state: dict[str, Any] = {"task_id": task_id}

        for ev in events:
            handler = _HANDLERS.get(ev.event_type)
            if handler is None:
                continue
            try:
                payload = json.loads(ev.payload) if isinstance(ev.payload, str) else ev.payload
            except (json.JSONDecodeError, TypeError):
                payload = {}
            try:
                state = handler(state, payload)
            except Exception as exc:
                raise ProjectionError(f"Handler {ev.event_type} failed: {exc}") from exc

        return state

    def close(self) -> None:
        if self._event_store is not None:
            self._event_store.close()
            self._event_store = None
