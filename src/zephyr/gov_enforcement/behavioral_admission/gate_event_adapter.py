# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §event-sourcing
# [MODULE] zephyr.gov_enforcement.behavioral_admission.gate_event_adapter
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.gov_audit.event_store; zephyr.governance.persistence.sqlite_schema
# [CONSUMERS] zephyr.gov_enforcement.rule_enforcement.gate_engine
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] gate events are appended to task_events atomically with gate persistence
# [MODIFY-GUARD] event_type enum changes MUST update _GATE_EVENT_TYPE_MAP
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] GateEventAdapterError on write failure
# [TESTS] tests/test_event_store_stress.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


GateEventAdapter — GateRepo 事件适配器（DW-0006）
===================================================
将 gate 运行结果作为事件追加到 task_events 表，
实现 gate 结果的 Event Sourcing 集成。

功能：
- append_gate_event: 将 gate pass/fail 结果作为 GATE_PASSED/GATE_FAILED 事件追加
- query_gate_events: 按 task_id 查询 gate 相关事件

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: gate 运行结果入参
#   fields: task_id + gate_id + passed + 可选 details/session_id
#   code: append_gate_event(task_id, gate_id, passed, ...) L63-71
# - id: I2
#   name: task_events 事件表 SQLite
#   fields: event_id / event_type / payload / timestamp / session_id
#   code: EventStore(DB_PATH, auto_init=True) L60-61
# 层: 算法
# - id: A1
#   name_zh: ① 事件类型映射与 payload 组装
#   name_en: GateEventAdapter.append_gate_event
#   intro: 把 gate 通过/失败翻译成 GATE_PASSED/GATE_FAILED 事件类型并打包 payload
#   desc: _GATE_EVENT_TYPE_MAP L43-46 查表 passed→GATE_PASSED / failed→GATE_FAILED；payload={gate_id, passed[, details]} L92-98
#   inputs: I1
#   outputs: event_type + payload
#   invariant: event_type 枚举变更必须同步更新 _GATE_EVENT_TYPE_MAP
# - id: A2
#   name_zh: ② 事件原子追加写库
#   name_en: EventStore.append_event
#   intro: 把组装好的 gate 事件原子追加进 task_events 表，落地 Event Sourcing
#   desc: 透传 task_id/event_type/payload/session_id L100-105；与 gate 持久化原子（INVARIANTS）
#   inputs: A1 I2
#   outputs: event_id
# - id: A3
#   name_zh: ③ gate 事件查询过滤
#   name_en: GateEventAdapter.query_gate_events
#   intro: 按 task_id 回放全部事件，只挑 GATE_PASSED/GATE_FAILED 两类按时间正序返回
#   desc: replay_events(task_id) 全量回放 → 过滤 event_type ∈ {GATE_PASSED, GATE_FAILED} → 投影为 dict L115-126
#   inputs: I2
#   outputs: gate 事件列表
# 层: 输出
# - id: O1
#   name_zh: 新事件 event_id
#   name_en: str
#   intro: append_gate_event 返回的事件唯一标识，供调用方追溯
#   downstream: gate_engine MOD-GATE_ENGINE（# [CONSUMERS] 头）
# - id: O2
#   name_zh: gate 事件列表
#   name_en: list[dict]
#   intro: 指定 task 的 gate 通过/失败历史（event_id/type/payload/timestamp/session_id）
#   downstream: gate_engine MOD-GATE_ENGINE（# [CONSUMERS] 头）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# I2 --> A2
# A2 --> O1
# I2 --> A3
# A3 --> O2
"""

from __future__ import annotations

import logging
from pathlib import Path

from zephyr.gov_audit.event_store import EventStore
from zephyr.shared.io.paths import DB_PATH

logger = logging.getLogger(__name__)

__all__ = [
    "GateEventAdapter",
]

_GATE_EVENT_TYPE_MAP = {
    "passed": "GATE_PASSED",
    "failed": "GATE_FAILED",
}


# class-name-alias: migrated from governance/behavioral_admission; pre-existing same-name class in trading/integration (ARCH-034 debt, to be resolved in dedicated cleanup)
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
