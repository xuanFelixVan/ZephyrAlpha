# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] zephyr.shared.observability.tracing
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.logging
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
tracing.py —— OpenTelemetry 分布式追踪（Phase B 补充 | 盲点 B1 修复）

对齐：existing src/zephyr/shared/logging.py 的 trace_id_var + TraceContext
      此模块在单进程内复用 TraceContext，跨进程走 OTLP gRPC exporter

设计原则：
  - 零依赖 fallback：opentelemetry 未安装时优雅降级为 noop span
  - span_id 从 logging.trace_id_var 自动传播
  - OTLP exporter 默认 localhost:4317（Jaeger / Grafana Tempo 标准端口）
  - Context propagation：TraceContext 进入时自动创建 parent span

AI 施工约定：
  - 任何跨模块调用 MUST wrap 在 start_span() 内
  - 错误 MUST 通过 span.set_status() 标记
  - span 属性仅允许 string/int/bool——禁止 float（OTLP 精度丢失）

SSoT: MOD-INF-016 §2.19 shared-tracing

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: name 参数
#   fields: 参数 name，类型注解 str
#   code: tracing.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: attributes 参数
#   fields: 参数 attributes，类型注解 dict[str, Any] | None
#   code: tracing.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: kind 参数
#   fields: 参数 kind，类型注解 str
#   code: tracing.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① start_span
#   name_en: start_span
#   intro: start_span(name, attributes, kind) 源码 L138-L172
#   desc: 源码 L138-L172
#   inputs: name attributes kind
#   outputs: Generator[Any, None, None]
# - id: A2
#   name_zh: ② traced
#   name_en: traced
#   intro: traced(name, kind) 源码 L175-L186
#   desc: 源码 L175-L186
#   inputs: name kind
#   outputs: Callable[[Callable[..., Any]], Callable…
# 层: 输出
# - id: O1
#   name_zh: Generator[Any, None, None]
#   name_en: Generator[Any, None, None]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# - id: O2
#   name_zh: Callable[[Callable[..., Any]], Callable…
#   name_en: Callable[[Callable[..., Any]], Callable…
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import functools
import os
from collections.abc import Callable, Generator
from contextlib import contextmanager
from typing import Any

from ..utils.logging import trace_id_var

_SHOULD_SKIP = os.environ.get("ZE_SKIP_OTEL")
_OPENTELEMETRY_AVAILABLE: bool | None = None


def _check_otel() -> bool:
    global _OPENTELEMETRY_AVAILABLE
    if _OPENTELEMETRY_AVAILABLE is not None:
        return _OPENTELEMETRY_AVAILABLE
    if _SHOULD_SKIP:
        _OPENTELEMETRY_AVAILABLE = False
        return False
    try:
        from opentelemetry import trace as otel_trace  # noqa: F401
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (  # noqa: F401
            OTLPSpanExporter,
        )
        from opentelemetry.sdk.trace import TracerProvider  # noqa: F401

        _OPENTELEMETRY_AVAILABLE = True
    except ImportError:
        _OPENTELEMETRY_AVAILABLE = False
    return _OPENTELEMETRY_AVAILABLE


def _get_tracer():
    if not _check_otel():
        return None
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    provider = TracerProvider()
    endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
    exporter = OTLPSpanExporter(endpoint=endpoint)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    return trace.get_tracer("zephyr-alpha")


@contextmanager
def start_span(
    name: str,
    attributes: dict[str, Any] | None = None,
    kind: str = "INTERNAL",
) -> Generator[Any, None, None]:
    tracer = _get_tracer()
    trace_id = trace_id_var.get()

    if tracer is None or not trace_id:
        yield _NoopSpan(name, trace_id or "<no-trace>")
        return

    from opentelemetry import trace
    from opentelemetry.trace import SpanKind

    kind_map = {
        "INTERNAL": SpanKind.INTERNAL,
        "SERVER": SpanKind.SERVER,
        "CLIENT": SpanKind.CLIENT,
        "PRODUCER": SpanKind.PRODUCER,
        "CONSUMER": SpanKind.CONSUMER,
    }
    otel_kind = kind_map.get(kind.upper(), SpanKind.INTERNAL)

    with tracer.start_as_current_span(name, kind=otel_kind) as span:
        if attributes:
            for k, v in attributes.items():
                if isinstance(v, (str, int, bool)):
                    span.set_attribute(k, v)
        span.set_attribute("trace_id", trace_id)
        try:
            yield span
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            span.set_status(trace.Status(trace.StatusCode.ERROR))
            raise


def traced(name: str | None = None, kind: str = "INTERNAL") -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def deco(func: Callable[..., Any]) -> Callable[..., Any]:
        span_name = name or func.__qualname__

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> object:
            with start_span(span_name, kind=kind):
                return func(*args, **kwargs)

        return wrapper

    return deco


class _NoopSpan:
    def __init__(self, name: str, trace_id: str):
        self.name = name
        self._trace_id = trace_id

    def set_attribute(self, key: str, value: object) -> None:
        pass

    def set_status(self, status: object) -> None:
        pass

    def end(self) -> None:
        pass
