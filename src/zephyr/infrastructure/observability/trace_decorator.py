# [BLUEPRINT] SRC-126 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.infrastructure.shared_services.observability.trace_decorator
# [DOMAIN] D-INFRA_RUNTIME
# [DEPENDENCIES]
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
# [A_module] module_id=MOD-INF_trace_decorator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

from __future__ import annotations
"""
Trace Decorator — 可观测性追踪 @trace 装饰器。

依据：
    蓝图 MOD-TASK_SYSTEM §6.3.1 + v0.6.0
    任务卡 TASK-INF-0109 (Part 1/5)
"""

import functools
import json
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass
class TraceSpan:
    span_id: str
    operation: str
    start_time: str
    end_time: str
    duration_ms: float
    success: bool
    error: str = ""


class TraceCollector:
    _instance: TraceCollector | None = None

    def __init__(self) -> None:
        self._spans: list[TraceSpan] = []
        self._output_dir = Path("data/traces")

    @classmethod
    def get_instance(cls) -> TraceCollector:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def add_span(self, span: TraceSpan) -> None:
        self._spans.append(span)

    def flush(self) -> list[TraceSpan]:
        spans = list(self._spans)
        self._output_dir.mkdir(parents=True, exist_ok=True)
        output_path = self._output_dir / f"trace-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}.jsonl"
        with open(output_path, "a", encoding="utf-8") as f:
            for span in spans:
                f.write(
                    json.dumps(
                        {
                            "span_id": span.span_id,
                            "operation": span.operation,
                            "start": span.start_time,
                            "end": span.end_time,
                            "duration_ms": span.duration_ms,
                            "success": span.success,
                            "error": span.error,
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
        self._spans.clear()
        return spans


def trace(operation: str = ""):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            collector = TraceCollector.get_instance()
            t0 = time.time()
            start_ts = datetime.now(UTC).isoformat()
            op_name = operation or func.__name__

            try:
                result = func(*args, **kwargs)
                collector.add_span(
                    TraceSpan(
                        span_id=f"{op_name}-{int(t0 * 1000)}",
                        operation=op_name,
                        start_time=start_ts,
                        end_time=datetime.now(UTC).isoformat(),
                        duration_ms=(time.time() - t0) * 1000,
                        success=True,
                    )
                )
                return result
            except Exception as e:
                collector.add_span(
                    TraceSpan(
                        span_id=f"{op_name}-{int(t0 * 1000)}",
                        operation=op_name,
                        start_time=start_ts,
                        end_time=datetime.now(UTC).isoformat(),
                        duration_ms=(time.time() - t0) * 1000,
                        success=False,
                        error=str(e),
                    )
                )
                raise

        return wrapper

    return decorator
