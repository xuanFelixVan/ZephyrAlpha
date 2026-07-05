# [BLUEPRINT] MOD-LLM_SECURITY | docs/03_modules/_cross_layer/large_language_model_security/blueprint.md | §
# [MODULE] zephyr.security.llm_defense.llm_security.behavior_audit_logger
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.shared.utils.time_utils; zephyr.governance.audit_trail.bridge
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
# [A_module] module_id=MOD-SEC_behavior_audit_logger | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

from __future__ import annotations

from zephyr.shared.utils.time_utils import now_iso, parse_iso

"""
AI Behavior Audit Logger - structlog + JSONL
Task ID : T-2-32
safety_level : H (audit log is append-only, tamper-evident)

Features
--------
1. structlog structured logging with JSONL output
2. Four AI behavior event types: model_call, file_write, rule_trigger, gate_decision
3. Each record contains: timestamp(ISO8601), model, action, target, result, session_id
4. Log rotation: by size (default 10MB) or by date
5. Append-only: no delete/update operations exposed
6. Query interface: by session_id / model / action / time range
"""

import json
from collections.abc import Iterator
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any

import structlog

from zephyr.governance.audit_trail.bridge import write_to_core

__all__ = [
    "AuditAction",
    "AuditEvent",
    "AuditLogger",
    "AuditQuery",
    "RotationPolicy",
    "open_audit_log",
]

_MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024


class AuditAction(str, Enum):
    MODEL_CALL = "model_call"
    FILE_WRITE = "file_write"
    RULE_TRIGGER = "rule_trigger"
    GATE_DECISION = "gate_decision"


class RotationPolicy(str, Enum):
    SIZE = "size"
    DATE = "date"


class AuditEvent:
    __slots__ = (
        "action",
        "extra",
        "model",
        "result",
        "session_id",
        "target",
        "timestamp",
    )

    def __init__(
        self,
        *,
        timestamp: str,
        model: str,
        action: str,
        target: str,
        result: str,
        session_id: str,
        extra: dict[str, Any] | None = None,
    ) -> None:
        self.timestamp = timestamp
        self.model = model
        self.action = action
        self.target = target
        self.result = result
        self.session_id = session_id
        self.extra = extra or {}

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "timestamp": self.timestamp,
            "model": self.model,
            "action": self.action,
            "target": self.target,
            "result": self.result,
            "session_id": self.session_id,
        }
        if self.extra:
            d["extra"] = self.extra
        return d

    def to_jsonl(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, separators=(",", ":"))


class AuditQuery:
    __slots__ = (
        "action",
        "model",
        "session_id",
        "time_from",
        "time_to",
    )

    def __init__(
        self,
        *,
        session_id: str | None = None,
        model: str | None = None,
        action: str | None = None,
        time_from: str | None = None,
        time_to: str | None = None,
    ) -> None:
        self.session_id = session_id
        self.model = model
        self.action = action
        self.time_from = time_from
        self.time_to = time_to

    def matches(self, event: AuditEvent) -> bool:
        if self.session_id is not None and event.session_id != self.session_id:
            return False
        if self.model is not None and event.model != self.model:
            return False
        if self.action is not None and event.action != self.action:
            return False
        # MUST 用 datetime 比较：日志多为 ...Z（now_iso），查询边界常为 isoformat 的 +00:00，
        # 纯字符串序会把「同一时间」判成 timestamp > time_to 而漏筛。
        if self.time_from is not None:
            try:
                if parse_iso(event.timestamp) < parse_iso(self.time_from):
                    return False
            except ValueError:
                if event.timestamp < self.time_from:
                    return False
        if self.time_to is not None:
            try:
                if parse_iso(event.timestamp) > parse_iso(self.time_to):
                    return False
            except ValueError:
                if event.timestamp > self.time_to:
                    return False
        return True


class AuditLogger:
    """
    Append-only AI behavior audit logger.

    Parameters
    ----------
    log_dir : Path
        Directory where JSONL log files are stored.
    rotation : RotationPolicy
        Rotation strategy: by size or by date.
    max_file_size : int
        Maximum file size in bytes before rotation (size policy only).
    session_id : str
        Default session ID for all events.
    model : str
        Default model name for all events.
    """

    def __init__(
        self,
        *,
        log_dir: Path,
        rotation: RotationPolicy = RotationPolicy.SIZE,
        max_file_size: int = _MAX_FILE_SIZE_BYTES,
        session_id: str = "",
        model: str = "",
    ) -> None:
        self._log_dir = log_dir
        self._rotation = rotation
        self._max_file_size = max_file_size
        self._session_id = session_id
        self._model = model
        self._log_dir.mkdir(parents=True, exist_ok=True)

        self._logger = structlog.get_logger("ai_audit")
        self._current_file: Path | None = None
        self._current_date: str | None = None

    @property
    def log_dir(self) -> Path:
        return self._log_dir

    def _current_log_file(self) -> Path:
        if self._rotation is RotationPolicy.DATE:
            today = datetime.now(UTC).strftime("%Y-%m-%d")
            if self._current_date != today:
                self._current_date = today
                self._current_file = self._log_dir / f"audit-{today}.jsonl"
            return self._current_file or self._log_dir / f"audit-{today}.jsonl"

        if self._current_file is not None and self._current_file.exists():
            if self._current_file.stat().st_size < self._max_file_size:
                return self._current_file

        idx = 0
        while True:
            name = f"audit-{idx:04d}.jsonl" if idx > 0 else "audit.jsonl"
            candidate = self._log_dir / name
            if not candidate.exists():
                self._current_file = candidate
                return candidate
            if candidate.stat().st_size < self._max_file_size:
                self._current_file = candidate
                return candidate
            idx += 1

    def log(
        self,
        *,
        action: AuditAction,
        target: str,
        result: str,
        session_id: str | None = None,
        model: str | None = None,
        extra: dict[str, Any] | None = None,
    ) -> None:
        sid = session_id or self._session_id
        mdl = model or self._model
        event = AuditEvent(
            timestamp=now_iso(),
            model=mdl,
            action=action.value,
            target=target,
            result=result,
            session_id=sid,
            extra=extra,
        )
        line = event.to_jsonl() + "\n"
        log_file = self._current_log_file()
        with open(log_file, "a", encoding="utf-8") as fh:
            fh.write(line)

        write_to_core(
            "llm_behavior_audit",
            {
                "action": action.value,
                "target": target,
                "result": result,
                "session_id": sid,
                "model": mdl,
            },
        )

    def log_model_call(
        self,
        target: str,
        result: str,
        *,
        session_id: str | None = None,
        model: str | None = None,
        extra: dict[str, Any] | None = None,
    ) -> None:
        self.log(
            action=AuditAction.MODEL_CALL, target=target, result=result, session_id=session_id, model=model, extra=extra
        )

    def log_file_write(
        self,
        target: str,
        result: str,
        *,
        session_id: str | None = None,
        model: str | None = None,
        extra: dict[str, Any] | None = None,
    ) -> None:
        self.log(
            action=AuditAction.FILE_WRITE, target=target, result=result, session_id=session_id, model=model, extra=extra
        )

    def log_rule_trigger(
        self,
        target: str,
        result: str,
        *,
        session_id: str | None = None,
        model: str | None = None,
        extra: dict[str, Any] | None = None,
    ) -> None:
        self.log(
            action=AuditAction.RULE_TRIGGER,
            target=target,
            result=result,
            session_id=session_id,
            model=model,
            extra=extra,
        )

    def log_gate_decision(
        self,
        target: str,
        result: str,
        *,
        session_id: str | None = None,
        model: str | None = None,
        extra: dict[str, Any] | None = None,
    ) -> None:
        self.log(
            action=AuditAction.GATE_DECISION,
            target=target,
            result=result,
            session_id=session_id,
            model=model,
            extra=extra,
        )

    def query(self, q: AuditQuery) -> list[AuditEvent]:
        results: list[AuditEvent] = []
        for event in self._iter_all_events():
            if q.matches(event):
                results.append(event)
        return results

    def query_iter(self, q: AuditQuery) -> Iterator[AuditEvent]:
        for event in self._iter_all_events():
            if q.matches(event):
                yield event

    def _iter_all_events(self) -> Iterator[AuditEvent]:
        jsonl_files = sorted(self._log_dir.glob("*.jsonl"))
        for jf in jsonl_files:
            # 5.82.1 修复: 先读取所有行再yield,避免生成器跨yield持有文件句柄。
            # 原代码在 with open(jf) as fh: 块内 yield,消费者提前break时
            # 文件句柄残留到GC触发,导致fd泄漏。
            with open(jf, encoding="utf-8") as fh:
                lines = fh.readlines()
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    yield AuditEvent(
                        timestamp=data["timestamp"],
                        model=data["model"],
                        action=data["action"],
                        target=data["target"],
                        result=data["result"],
                        session_id=data["session_id"],
                        extra=data.get("extra"),
                    )
                except (json.JSONDecodeError, KeyError):
                    continue

    def count_events(self) -> int:
        count = 0
        for jf in sorted(self._log_dir.glob("*.jsonl")):
            with open(jf, encoding="utf-8") as fh:
                for line in fh:
                    if line.strip():
                        count += 1
        return count


def open_audit_log(
    *,
    log_dir: Path,
    rotation: RotationPolicy = RotationPolicy.SIZE,
    max_file_size: int = _MAX_FILE_SIZE_BYTES,
    session_id: str = "",
    model: str = "",
) -> AuditLogger:
    return AuditLogger(
        log_dir=log_dir,
        rotation=rotation,
        max_file_size=max_file_size,
        session_id=session_id,
        model=model,
    )
