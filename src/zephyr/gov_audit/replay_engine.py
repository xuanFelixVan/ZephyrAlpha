# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §9
# [MODULE] zephyr.gov_audit.replay_engine
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.shared.io.streaming_reader
# [CONSUMERS] audit-orchestrator.pipeline_runner; integrity
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 重放不修改任何审计数据; 只读+比对
# [MODIFY-GUARD] 重放格式变更必须同步 evidence_pack.py
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 重放失败返回mismatch
# [TESTS] tests/audit-orchestrator/test_replay_engine.py
# [A_module] module_id=MOD-INF-020 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: event_log_path 参数
#   fields: 参数 event_log_path（无注解）
#   code: replay_engine.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: snapshot_interval 参数
#   fields: 参数 snapshot_interval（无注解）
#   code: replay_engine.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① ReplayEngine
#   name_en: ReplayEngine
#   intro: 重放引擎（补全测试期望接口）。
#   desc: 重放引擎（补全测试期望接口）。 支持基于 Lamport clock 排序的事件重放，构建最终状态和快照。；公共方法（定义序）: snapshot_interval, replay, replay_range, ver…
#   inputs: event_log_path snapshot_interval
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: ReplayEngine
#   downstream: audit-orchestrator.pipeline_runner; integrity
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

__all__ = ["ReplayEngine", "ReplayResult", "ReplaySnapshot"]


class ReplaySnapshot:
    """重放快照（补全测试期望接口）。"""

    def __init__(
        self,
        lamport_counter: int = 0,
        entry_count: int = 0,
        last_entry_id: str = "",
        last_agent_id: str = "",
        state: dict[str, Any] | None = None,
    ) -> None:
        self.lamport_counter = lamport_counter
        self.entry_count = entry_count
        self.last_entry_id = last_entry_id
        self.last_agent_id = last_agent_id
        self.state = state if state is not None else {}


class ReplayResult:
    """重放结果（补全测试期望接口）。"""

    def __init__(
        self,
        events_replayed: int = 0,
        is_deterministic: bool = True,
        divergence_points: list[str] | None = None,
        final_state: dict[str, Any] | None = None,
        snapshots: list[ReplaySnapshot] | None = None,
    ) -> None:
        self.events_replayed = events_replayed
        self.is_deterministic = is_deterministic
        self.divergence_points = divergence_points if divergence_points is not None else []
        self.final_state = final_state if final_state is not None else {}
        self.snapshots = snapshots if snapshots is not None else []


class ReplayEngine:
    """重放引擎（补全测试期望接口）。

    支持基于 Lamport clock 排序的事件重放，构建最终状态和快照。
    """

    def __init__(
        self,
        event_log_path: Path | None = None,
        snapshot_interval: int = 100,
    ) -> None:
        self._event_log_path = Path(event_log_path) if event_log_path is not None else None
        self._snapshot_interval = snapshot_interval

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def snapshot_interval(self):
        """只读：snapshot_interval（Stage 4 公共化）。"""
        return self._snapshot_interval

    @snapshot_interval.setter
    def snapshot_interval(self, value):
        """写入：snapshot_interval（Stage 4 公共化）。"""
        self._snapshot_interval = value

    def _load_events(self) -> list[dict[str, Any]]:
        if self._event_log_path is None or not self._event_log_path.exists():
            return []
        events: list[dict[str, Any]] = []
        try:
            with open(self._event_log_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        events.append(json.loads(line))
        except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.error("Failed to load events from %s: %s", self._event_log_path, exc, exc_info=True)
        return events

    def _sort_events(self, events: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """按 (lamport_clock_counter, lamport_clock_ide) 排序。"""
        return sorted(
            events,
            key=lambda e: (
                e.get("lamport_clock_counter", 0),
                e.get("lamport_clock_ide", ""),
            ),
        )

    def replay(self, events: list[dict[str, Any]] | None = None) -> ReplayResult:
        if events is None:
            events = self._load_events()
        if not events:
            return ReplayResult(events_replayed=0, final_state={})

        sorted_events = self._sort_events(events)
        final_state: dict[str, Any] = {}
        snapshots: list[ReplaySnapshot] = []
        count = 0
        last_entry_id = ""
        last_agent_id = ""
        last_lamport = 0

        for event in sorted_events:
            count += 1
            agent_id = event.get("agent_id", "")
            entry_id = event.get("entry_id", "")
            lamport = event.get("lamport_clock_counter", 0)
            target = event.get("target_path") or event.get("file_path", "")

            if agent_id:
                if agent_id not in final_state:
                    final_state[agent_id] = {"entry_count": 0}
                final_state[agent_id]["entry_count"] += 1

            if target:
                final_state[target] = {"last_modified_by": agent_id}

            last_entry_id = entry_id
            last_agent_id = agent_id
            last_lamport = lamport

            if count % self._snapshot_interval == 0:
                snapshots.append(
                    ReplaySnapshot(
                        lamport_counter=last_lamport,
                        entry_count=count,
                        last_entry_id=last_entry_id,
                        last_agent_id=last_agent_id,
                        state=dict(final_state),
                    )
                )

        return ReplayResult(
            events_replayed=count,
            is_deterministic=True,
            final_state=final_state,
            snapshots=snapshots,
        )

    def replay_range(
        self,
        start_timestamp: str | None = None,
        end_timestamp: str | None = None,
        events: list[dict[str, Any]] | None = None,
    ) -> ReplayResult:
        if events is None:
            events = self._load_events()
        if not events:
            return ReplayResult(events_replayed=0, final_state={})

        start_dt = self._parse_timestamp(start_timestamp)
        end_dt = self._parse_timestamp(end_timestamp)

        filtered: list[dict[str, Any]] = []
        for event in events:
            ts = event.get("timestamp")
            if not ts:
                continue
            event_dt = self._parse_timestamp(ts)
            if event_dt is None:
                continue
            if start_dt and event_dt < start_dt:
                continue
            if end_dt and event_dt > end_dt:
                continue
            filtered.append(event)

        return self.replay(filtered)

    def verify_determinism(
        self,
        events: list[dict[str, Any]] | None = None,
        runs: int = 3,
    ) -> bool:
        if events is None:
            events = self._load_events()
        if not events:
            return True

        baseline = self.replay(events)
        for _ in range(runs - 1):
            result = self.replay(events)
            if result.events_replayed != baseline.events_replayed:
                return False
            if result.final_state != baseline.final_state:
                return False
        return True

    def _parse_timestamp(self, ts: str | None) -> datetime | None:
        if not ts:
            return None
        try:
            if ts.endswith("Z"):
                ts = ts[:-1] + "+00:00"
            return datetime.fromisoformat(ts)
        except (TypeError, ValueError):
            return None
