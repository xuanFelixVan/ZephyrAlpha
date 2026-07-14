# [BLUEPRINT] MOD-INF-015 | docs/03_modules/_domain_infrastructure_operations/system_telemetry/blueprint.md | §3
# [MODULE] zephyr.infrastructure.system_telemetry.facade
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__
# [CONSUMERS] auto_bootstrap.py; zephyr.security.access_control; zephyr.infrastructure.budget_enforcement
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] fail-closed on write; test_mode=True silences all outbound; shutdown() reverses init order; background scheduler daemon thread
# [MODIFY-GUARD] __init__.py; health/; alerts/; profiles/; schema/; auto_bootstrap.py
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError; OSError; RuntimeError
# [TESTS] tests/system-telemetry/test_facade.py
# [A_module] module_id=MOD-INF_facade | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Telemetry — 系统遥测门面类（MOD-INF-015 v2.1.0）

一行接入，9 子系统，完全自动化:
    telemetry = Telemetry("my_module")
    telemetry.metrics.gauge("latency_ms", 42.0)
    telemetry.logs.info("step_start", step=1)
    span = telemetry.traces.span("pipeline:run")
    telemetry.ai_behavior.record(decision="task_assign", model="gpt-4.1")
    telemetry.health.register()
    telemetry.shutdown()

自动化后台线程（test_mode=False 时自动启动）:
    - flush: 每60s 将 ring buffer 刷盘到 JSONL
    - alert: 每30s 评估告警规则
    - health: 每10s 发送心跳
    - archive: 每300s 检查归档

设计约束:
    - test_mode=True 时静默所有出站操作，不启动后台线程
    - fail-closed: 任何子系统写入失败不阻塞主流程
    - shutdown() 按逆序关闭 9 子系统 + 停止后台线程
"""

from __future__ import annotations
from zephyr.shared.io.serialization import dumps

import logging
import os
import threading
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from zephyr.infrastructure.system_telemetry.alerts import AlertSubsystem
from zephyr.infrastructure.system_telemetry.health import HealthSubsystem
from zephyr.infrastructure.system_telemetry.profiles import ProfileSubsystem
from zephyr.infrastructure.system_telemetry.schema import SchemaSubsystem
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

_logger = logging.getLogger(__name__)

_SHUTDOWN_ORDER = [
    "metrics",
    "logs",
    "traces",
    "ai_behavior",
    "health",
    "profiles",
    "alerts",
    "schema",
    "archive",
]

_RING_SIZE = 4096
_JSONL_FLUSH_INTERVAL = 16

_DATA_DIR = REPO_ROOT / "data" / "telemetry"

# 5.81.1 修复：模块级 ring buffer 共享可变状态, 加 threading.Lock 保护并发写入
_ring_lock = threading.Lock()
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
    # 5.81.1 修复：模块级 ring buffer 并发写入需持锁, 防止 cursor/列表交叉修改导致数据错位
    global _ring_write_cursor, _jsonl_countdown
    with _ring_lock:
        idx = _ring_write_cursor % _RING_SIZE
        if idx < len(_in_memory_ring):
            _in_memory_ring[idx] = point
        else:
            _in_memory_ring.append(point)
        _ring_write_cursor += 1
        _jsonl_countdown -= 1
        need_flush = _jsonl_countdown <= 0
        if need_flush:
            _jsonl_countdown = _JSONL_FLUSH_INTERVAL
    if need_flush:
        _flush_ring_to_jsonl()


def _flush_ring_to_jsonl() -> None:
    # 5.81.1 修复：在锁内取出快照, 锁外执行 I/O 避免长持锁
    with _ring_lock:
        if not _in_memory_ring:
            return
        cursor_snapshot = _ring_write_cursor
        start = max(0, cursor_snapshot - _JSONL_FLUSH_INTERVAL)
        lines: list[str] = []
        for i in range(start, cursor_snapshot):
            idx = i % _RING_SIZE
            if idx < len(_in_memory_ring):
                lines.append(dumps(_in_memory_ring[idx]))
    if not lines:
        return
    try:
        data_dir = _telemetry_data_dir()
        fp = data_dir / "metrics.jsonl"
        _ensure_jsonl(fp)
        content = "\n".join(lines) + "\n"
        tmp_path = f"{fp}.{os.getpid()}.tmp"
        try:
            existing = fp.read_text(encoding="utf-8") if fp.exists() else ""
            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(existing)
                f.write(content)
            os.replace(tmp_path, str(fp))
        except PermissionError:
            try:
                os.remove(tmp_path)
            except OSError:
                pass
            with open(fp, "a", encoding="utf-8") as f:
                f.write(content)
    except Exception:
        _logger.debug("flush_ring_to_jsonl failed", exc_info=True)


def get_recent_metrics(limit: int = 256) -> list[dict]:
    # 5.81.1 修复：读取也持锁, 防止读到中间状态
    with _ring_lock:
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
            "ts": datetime.now(UTC).isoformat(),
            "module_id": self._module_id,
            "kind": kind,
            "name": name,
            "value": value,
            "tags": tags,
        }
        if not self._test_mode:
            _logger.info("metrics %s %s=%s tags=%s", kind, name, value, dumps(tags))
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
            "ts": datetime.now(UTC).isoformat(),
            "level": level,
            "module_id": self._module_id,
            "message": message,
            "labels": labels,
        }
        if not self._test_mode:
            log_fn = {"INFO": _logger.info, "WARNING": _logger.warning, "ERROR": _logger.error}[level]
            log_fn("%s labels=%s", message, dumps(labels))
        return record


class _Span:
    def __init__(self, operation_name: str, test_mode: bool = False):
        self.operation_name = operation_name
        self._test_mode = test_mode
        self._attributes: dict[str, Any] = {}
        self._start = datetime.now(UTC)

    def __enter__(self) -> _Span:
        return self

    def __exit__(self, *exc: Any) -> None:
        self.end()

    def set_attribute(self, key: str, value: object) -> None:
        self._attributes[key] = value

    def set_metadata(self, **kwargs: Any) -> None:
        self._attributes.update(kwargs)

    def end(self) -> dict:
        elapsed = (datetime.now(UTC) - self._start).total_seconds()
        result = {
            "operation": self.operation_name,
            "elapsed_s": elapsed,
            "attributes": dict(self._attributes),
        }
        if not self._test_mode:
            _logger.info(
                "trace span=%s elapsed=%.3fs attrs=%s",
                self.operation_name,
                elapsed,
                dumps(self._attributes),
            )
        return result


class TracesFacade:
    def __init__(self, module_id: str, test_mode: bool = False):
        self._module_id = module_id
        self._test_mode = test_mode

    def span(self, operation_name: str) -> _Span:
        if self._test_mode:
            return _Span(operation_name, test_mode=True)
        try:
            from zephyr.infrastructure.system_telemetry.traces.span_stub import noop_span

            return _RealSpanBridge(operation_name, noop_span)
        except Exception:
            return _Span(operation_name, test_mode=self._test_mode)


class _RealSpanBridge:
    def __init__(self, operation_name: str, factory: object):
        self._name = operation_name
        self._factory = factory
        self._ctx: object = None
        self._span: object = None
        self._attributes: dict[str, Any] = {}

    def __enter__(self) -> _RealSpanBridge:
        self._ctx = self._factory(self._name)
        self._span = self._ctx.__enter__()
        for k, v in self._attributes.items():
            self._span.set_attribute(k, v)
        return self

    def __exit__(self, *args: Any) -> bool | None:
        # 5.73.1 修复：原 __exit__ 调用底层 self._ctx.__exit__(*args) 但未 return 其返回值。
        # 若底层上下文管理器返回True以抑制异常，该语义被丢失。
        # 5.163.4 修复: __exit__ 后置 _ctx=None,防止 end() 再次调用 _ctx.__exit__ 重复退出。
        if self._ctx is not None:
            ctx = self._ctx
            self._ctx = None
            return ctx.__exit__(*args)
        return None

    def set_attribute(self, key: str, value: object) -> None:
        self._attributes[key] = value

    def end(self) -> dict:
        # 5.163.4 修复: 检查 _ctx 是否已 None(__exit__ 已调用),避免重复退出。
        if self._ctx is not None:
            ctx = self._ctx
            self._ctx = None
            ctx.__exit__(None, None, None)
        return {"operation": self._name, "attributes": dict(self._attributes)}


class AIBehaviorFacade:
    def __init__(self, module_id: str, test_mode: bool = False):
        self._module_id = module_id
        self._test_mode = test_mode

    def record(self, decision: str, model: str = "", reason: str = "", **extra: Any) -> dict:
        if self._test_mode:
            return {
                "ts": datetime.now(UTC).isoformat(),
                "module_id": self._module_id,
                "decision": decision,
                "model": model,
                "reason": reason,
                "extra": extra,
            }
        try:
            from zephyr.infrastructure.system_telemetry.ai_behavior.event_sink import (
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
                decision,
                model,
                reason,
                dumps(extra), exc_info=True
            )
            return {
                "ts": datetime.now(UTC).isoformat(),
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
            from zephyr.infrastructure.system_telemetry.archive.cold_stub import next_archive_batch_id

            return next_archive_batch_id(prefix)
        except Exception:
            import uuid

            batch_id = f"{prefix}-{uuid.uuid4().hex[:12]}"
            _logger.info("archive batch_id=%s module=%s", batch_id, self._module_id, exc_info=True)
            return batch_id


class Telemetry:
    _SCHEDULE = {
        "flush": 60,
        "alert": 30,
        "health_heartbeat": 10,
        "watchdog_check": 10,
        "archive_check": 300,
        "health_aggregator": 15,
        "profiles_snapshot": 60,
    }

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

        from zephyr.infrastructure.system_telemetry.health_aggregator import HealthAggregator

        self._health_aggregator = HealthAggregator()

        from zephyr.infrastructure.system_telemetry.watchdog import Watchdog

        self._watchdog = Watchdog(watchdog_id=f"wd-{module_id}")

        if not test_mode:
            self.profiles.start("auto")

        self._shutdown_called = False
        self._scheduler_stop = threading.Event()
        self._scheduler_thread: threading.Thread | None = None

        if not test_mode:
            self._start_scheduler()
            _logger.info(
                "Telemetry initialized module=%s env=%s auto=True",
                module_id,
                environment,
            )

    def _start_scheduler(self) -> None:
        self._scheduler_thread = threading.Thread(
            target=self._scheduler_loop,
            name="telemetry-scheduler",
            daemon=True,
        )
        self._scheduler_thread.start()

    def _scheduler_loop(self) -> None:
        last_run: dict[str, float] = {k: 0.0 for k in self._SCHEDULE}
        while not self._scheduler_stop.is_set():
            now = time.monotonic()
            for task, interval in self._SCHEDULE.items():
                if now - last_run[task] >= interval:
                    try:
                        self._run_scheduled_task(task)
                    except Exception:
                        _logger.debug("scheduled %s failed", task, exc_info=True)
                    last_run[task] = time.monotonic()
            self._scheduler_stop.wait(timeout=1.0)

    def _run_scheduled_task(self, task: str) -> None:
        if task == "flush":
            _flush_ring_to_jsonl()
        elif task == "alert":
            self.alerts.evaluate("__scheduled__", 0.0)
        elif task == "health_heartbeat":
            self.health.heartbeat()
        elif task == "watchdog_check":
            self._watchdog_tick()
        elif task == "archive_check":
            # 治本（2026-06-29 阶段A+）：删除 daily_backup_sqlite() 调用（定时备份违反
            # 事件驱动原则，且是 .db 残留来源）。保留 rotate_by_ttl()（TTL 清理，非备份）。
            try:
                from zephyr.infrastructure.system_telemetry.archive import rotate_by_ttl

                rotate_by_ttl()
            except Exception:
                _logger.debug("archive_check failed", exc_info=True)
        elif task == "health_aggregator":
            self._health_aggregator_tick()
        elif task == "profiles_snapshot":
            self._profiles_snapshot_tick()

    def _health_aggregator_tick(self) -> None:
        try:
            self._health_aggregator.poll_all()
        except Exception:
            _logger.debug("health_aggregator_tick failed", exc_info=True)

    def _profiles_snapshot_tick(self) -> None:
        try:
            self.profiles.start("auto_snapshot")
        except Exception:
            _logger.debug("profiles_snapshot_tick failed", exc_info=True)

    def _watchdog_tick(self) -> None:
        try:
            if self._watchdog is not None:
                self._watchdog.write_external_heartbeat()
        except Exception:
            _logger.debug("watchdog_tick failed", exc_info=True)

    def shutdown(self) -> None:
        if self._shutdown_called:
            return
        self._shutdown_called = True

        self._scheduler_stop.set()
        if self._scheduler_thread is not None and self._scheduler_thread.is_alive():
            self._scheduler_thread.join(timeout=5.0)

        _flush_ring_to_jsonl()

        # 5.144.12 修复: health 已在 _SHUTDOWN_ORDER 中, 循环会调用 shutdown()。
        # set_unhealthy 需在 shutdown 前调用, 移除循环后的重复 health.shutdown()
        if hasattr(self.health, "set_unhealthy"):
            self.health.set_unhealthy("shutdown")

        for attr_name in reversed(_SHUTDOWN_ORDER):
            sub = getattr(self, attr_name, None)
            if sub is not None and hasattr(sub, "shutdown"):
                try:
                    sub.shutdown()
                except Exception:
                    _logger.debug("shutdown %s failed", attr_name, exc_info=True)

        if not self.test_mode:
            _logger.info("Telemetry shutdown complete module=%s", self.module_id)
