"""Telemetry — 系统遥测门面类（MOD-INF-015 v0.9.0）

一行接入，9 子系统:
    telemetry = Telemetry("my_module")
    telemetry.metrics.gauge("latency_ms", 42.0)
    telemetry.logs.info("step_start", step=1)
    span = telemetry.traces.span("pipeline:run")
    telemetry.ai_behavior.record(decision="task_assign", model="gpt-4.1")
    telemetry.health.register()
    telemetry.shutdown()

设计约束:
    - test_mode=True 时静默所有出站操作
    - fail-closed: 任何子系统写入失败不阻塞主流程
    - shutdown() 按逆序关闭 9 子系统
"""

from __future__ import annotations

import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from zephyr.l12_system_telemetry.health import HealthSubsystem
from zephyr.l12_system_telemetry.alerts import AlertSubsystem
from zephyr.l12_system_telemetry.profiles import ProfileSubsystem
from zephyr.l12_system_telemetry.schema import SchemaSubsystem

_logger = logging.getLogger(__name__)

_SHUTDOWN_ORDER = [
    "metrics", "logs", "traces", "ai_behavior",
    "health", "profiles", "alerts", "schema", "archive",
]

_RING_SIZE = 4096
_JSONL_FLUSH_INTERVAL = 16

_REPO_ROOT = Path(__file__).resolve().parents[3]
_DATA_DIR = _REPO_ROOT / "data" / "telemetry"

_in_memory_ring: list[dict] = []
_ring_write_cursor = 0
_jsonl_countdown = _JSONL_FLUSH_INTERVAL


def _telemetry_data_dir() -> Path:
    env_flag = os.environ.get("ZALPHA_ENV", "dev")
    env_dir = _DATA_DIR / env_flag
    env_dir.mkdir(parents=True, exist_ok=True)
    return env_dir


def _ensure_jsonl(fp: Path) -> None:
    fp.parent.mkdir(parents=True, exist_ok=True)


def _write_ring(point: dict) -> None:
    global _ring_write_cursor, _jsonl_countdown
    idx = _ring_write_cursor % _RING_SIZE
    if idx < len(_in_memory_ring):
        _in_memory_ring[idx] = point
    else:
        _in_memory_ring.append(point)
    _ring_write_cursor += 1
    _jsonl_countdown -= 1
    if _jsonl_countdown <= 0:
        _flush_ring_to_jsonl()
        _jsonl_countdown = _JSONL_FLUSH_INTERVAL


def _flush_ring_to_jsonl() -> None:
    if not _in_memory_ring:
        return
    try:
        data_dir = _telemetry_data_dir()
        fp = data_dir / "metrics.jsonl"
        _ensure_jsonl(fp)
        start = max(0, _ring_write_cursor - _JSONL_FLUSH_INTERVAL)
        with open(fp, "a", encoding="utf-8") as f:
            for i in range(start, _ring_write_cursor):
                idx = i % _RING_SIZE
                if idx < len(_in_memory_ring):
                    f.write(json.dumps(_in_memory_ring[idx], default=str) + "\n")
    except Exception:
        _logger.debug("flush_ring_to_jsonl failed", exc_info=True)


def get_recent_metrics(limit: int = 256) -> list[dict]:
    if not _in_memory_ring:
        return []
    end = _ring_write_cursor
    start = max(0, end - limit)
    result: list[dict] = []
    for i in range(start, end):
        idx = i % _RING_SIZE
        if idx < len(_in_memory_ring):
            result.append(_in_memory_ring[idx])
    return result


class MetricsFacade:
    def __init__(self, module_id: str, test_mode: bool = False):
        self._module_id = module_id
        self._test_mode = test_mode

    def gauge(self, name: str, value: float, **tags: Any) -> dict:
        return self._record("gauge", name, value, tags)

    def counter(self, name: str, delta: float = 1.0, **tags: Any) -> dict:
        return self._record("counter", name, delta, tags)

    def histogram(self, name: str, value: float, **tags: Any) -> dict:
        return self._record("histogram", name, value, tags)

    def summary(self, name: str, value: float, **tags: Any) -> dict:
        return self._record("summary", name, value, tags)

    def _record(self, kind: str, name: str, value: float, tags: dict) -> dict:
        point = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "module_id": self._module_id,
            "kind": kind,
            "name": name,
            "value": value,
            "tags": tags,
        }
        if not self._test_mode:
            _logger.info("metrics %s %s=%s tags=%s", kind, name, value, json.dumps(tags, default=str))
            _write_ring(point)
        return point


class LogsFacade:
    def __init__(self, module_id: str, test_mode: bool = False):
        self._module_id = module_id
        self._test_mode = test_mode

    def info(self, message: str, **labels: Any) -> dict:
        return self._log("INFO", message, labels)

    def warning(self, message: str, **labels: Any) -> dict:
        return self._log("WARNING", message, labels)

    def error(self, message: str, **labels: Any) -> dict:
        return self._log("ERROR", message, labels)

    def _log(self, level: str, message: str, labels: dict) -> dict:
        record = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "module_id": self._module_id,
            "message": message,
            "labels": labels,
        }
        if not self._test_mode:
            log_fn = {"INFO": _logger.info, "WARNING": _logger.warning, "ERROR": _logger.error}[level]
            log_fn("%s labels=%s", message, json.dumps(labels, default=str))
        return record


class _Span:
    def __init__(self, operation_name: str, test_mode: bool = False):
        self.operation_name = operation_name
        self._test_mode = test_mode
        self._attributes: dict[str, Any] = {}
        self._start = datetime.now(timezone.utc)

    def set_attribute(self, key: str, value: Any) -> None:
        self._attributes[key] = value

    def end(self) -> dict:
        elapsed = (datetime.now(timezone.utc) - self._start).total_seconds()
        result = {
            "operation": self.operation_name,
            "elapsed_s": elapsed,
            "attributes": dict(self._attributes),
        }
        if not self._test_mode:
            _logger.info("trace span=%s elapsed=%.3fs attrs=%s", self.operation_name, elapsed, json.dumps(self._attributes, default=str))
        return result


class TracesFacade:
    def __init__(self, module_id: str, test_mode: bool = False):
        self._module_id = module_id
        self._test_mode = test_mode

    def span(self, operation_name: str) -> _Span:
        if self._test_mode:
            return _Span(operation_name, test_mode=True)
        try:
            from zephyr.l12_system_telemetry.traces.span_stub import noop_span
            return _RealSpanBridge(operation_name, noop_span)
        except Exception:
            return _Span(operation_name, test_mode=self._test_mode)


class _RealSpanBridge:
    def __init__(self, operation_name: str, factory: Any):
        self._name = operation_name
        self._factory = factory
        self._ctx: Any = None
        self._span: Any = None
        self._attributes: dict[str, Any] = {}

    def __enter__(self) -> _RealSpanBridge:
        self._ctx = self._factory(self._name)
        self._span = self._ctx.__enter__()
        for k, v in self._attributes.items():
            self._span.set_attribute(k, v)
        return self

    def __exit__(self, *args: Any) -> None:
        if self._ctx is not None:
            self._ctx.__exit__(*args)

    def set_attribute(self, key: str, value: Any) -> None:
        self._attributes[key] = value

    def end(self) -> dict:
        if self._ctx is not None:
            self._ctx.__exit__(None, None, None)
        return {"operation": self._name, "attributes": dict(self._attributes)}


class AIBehaviorFacade:
    def __init__(self, module_id: str, test_mode: bool = False):
        self._module_id = module_id
        self._test_mode = test_mode

    def record(self, decision: str, model: str = "", reason: str = "", **extra: Any) -> dict:
        if self._test_mode:
            return {
                "ts": datetime.now(timezone.utc).isoformat(),
                "module_id": self._module_id,
                "decision": decision,
                "model": model,
                "reason": reason,
                "extra": extra,
            }
        try:
            from zephyr.l12_system_telemetry.ai_behavior.event_sink import (
                emit_ai_behavior_event,
            )
            event = emit_ai_behavior_event(
                model_name=model or "unknown",
                task_type=decision,
                module_id=self._module_id,
                decision_point=decision,
                chosen_option=model,
                rationale=reason,
            )
            return event.snapshot()
        except Exception:
            _logger.info(
                "ai_behavior decision=%s model=%s reason=%s extra=%s",
                decision, model, reason, json.dumps(extra, default=str),
            )
            return {
                "ts": datetime.now(timezone.utc).isoformat(),
                "module_id": self._module_id,
                "decision": decision,
                "model": model,
                "reason": reason,
                "extra": extra,
            }


class ArchiveFacade:
    def __init__(self, module_id: str, test_mode: bool = False):
        self._module_id = module_id
        self._test_mode = test_mode

    def next_batch_id(self, prefix: str = "arc") -> str:
        if self._test_mode:
            import uuid
            return f"{prefix}-{uuid.uuid4().hex[:12]}"
        try:
            from zephyr.l12_system_telemetry.archive.cold_stub import next_archive_batch_id
            return next_archive_batch_id(prefix)
        except Exception:
            import uuid
            batch_id = f"{prefix}-{uuid.uuid4().hex[:12]}"
            _logger.info("archive batch_id=%s module=%s", batch_id, self._module_id)
            return batch_id


class Telemetry:
    def __init__(self, module_id: str, environment: str = "dev", test_mode: bool = False):
        self.module_id = module_id
        self.environment = environment
        self.test_mode = test_mode

        self.metrics = MetricsFacade(module_id, test_mode)
        self.logs = LogsFacade(module_id, test_mode)
        self.traces = TracesFacade(module_id, test_mode)
        self.ai_behavior = AIBehaviorFacade(module_id, test_mode)
        self.health = HealthSubsystem(module_id, test_mode)
        self.profiles = ProfileSubsystem(module_id, test_mode)
        self.alerts = AlertSubsystem(module_id, test_mode)
        self.schema = SchemaSubsystem(module_id, test_mode)
        self.archive = ArchiveFacade(module_id, test_mode)

        self._shutdown_called = False

        if not test_mode:
            _logger.info(
                "Telemetry initialized module=%s env=%s",
                module_id, environment,
            )

    def shutdown(self) -> None:
        if self._shutdown_called:
            return
        self._shutdown_called = True

        for attr_name in reversed(_SHUTDOWN_ORDER):
            sub = getattr(self, attr_name, None)
            if sub is not None and hasattr(sub, "shutdown"):
                try:
                    sub.shutdown()
                except Exception:
                    _logger.debug("shutdown %s failed", attr_name, exc_info=True)

        self.health.set_unhealthy("") if hasattr(self.health, "set_unhealthy") else None
        self.health.shutdown()

        if not self.test_mode:
            _logger.info("Telemetry shutdown complete module=%s", self.module_id)
