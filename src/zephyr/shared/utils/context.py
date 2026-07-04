# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.utils.context
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SHR_context | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""
context.py —— 结构化上下文传播（Phase 8 新增 | 盲点 B16 修复）

痛点修复：logging.py 用 contextvars 传播 trace_id，但缺少统一 RequestContext 对象——
  1. 跨模块调用时上下文断裂——tenant_id / session_id / agent_id 需要手动传参
  2. OpenTelemetry SpanContext 的理念被部分实现（trace_id），但不完整
  3. AI agent 需要知道"当前是谁在请求、哪个租户、什么优先级"——否则无法做决策

设计对标：
  - OpenTelemetry SpanContext（trace_id + span_id + trace_flags + trace_state）
  - Spring Cloud Sleuth（TraceContext = traceId + spanId）
  - K8s resource labels（namespace + labels + annotations 的元数据模型）

设计原则：
  - contextvars——Python 标准库，天然支持 async 上下文传播
  - 不可变——RequestContext 创建后不可修改（新 context 用 replace() 派生）
  - 轻量——不应包含大对象，只包含 key metadata

AI 施工约定：
  - 任何跨模块调用 MUST 传递 RequestContext——禁止裸透传 trace_id
  - 新增上下文字段时 MUST 在 RequestContext dataclass 中追加——保持 SSoT

SSoT: MOD-INF-016 §2.15 shared-context
Version: 0.1.0
"""

from __future__ import annotations

import contextvars
import logging
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Self

__all__ = [
    "RequestContext",
    "current_context",
    "get_request_id",
    "set_context",
    "set_request_id",
]

logger = logging.getLogger(__name__)

_current_context: contextvars.ContextVar[RequestContext | None] = contextvars.ContextVar(
    "request_context", default=None
)


@dataclass(frozen=True)
class RequestContext:
    """不可变的请求上下文——跨模块调用时的元数据载体。

    Usage::

        ctx = RequestContext(
            tenant_id="tenant-001",
            session_id="session-abc",
            agent_id="agent-deepseek-1",
        )
        token = set_context(ctx)
        ...
        ctx = current_context()
        print(ctx.trace_id)  # 在当前 async 调用链中自动可用

    """

    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    span_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    tenant_id: str = "default"
    session_id: str = ""
    agent_id: str = ""
    request_id: str = ""
    priority: int = 5
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    extra: dict[str, Any] = field(default_factory=dict)

    def replace(self, **kwargs: Any) -> RequestContext:
        """创建派生上下文——保留原字段，覆盖指定字段。"""
        current = {f.name: getattr(self, f.name) for f in self.__dataclass_fields__.values()}
        current.update(kwargs)
        return RequestContext(**current)

    def new_span(self, span_name: str = "") -> RequestContext:
        """创建新的 span——生成新 span_id，保留 trace_id。"""
        return self.replace(
            span_id=f"{span_name}:{str(uuid.uuid4())[:8]}" if span_name else str(uuid.uuid4())[:8],
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "tenant_id": self.tenant_id,
            "session_id": self.session_id,
            "agent_id": self.agent_id,
            "request_id": self.request_id,
            "priority": self.priority,
            "created_at": self.created_at,
        }


def current_context() -> RequestContext | None:
    """获取当前请求上下文——跨 async 调用链自动传播。

    Returns:
        当前 RequestContext 或 None（如果未设置）。
    """
    return _current_context.get()


def set_context(ctx: RequestContext) -> contextvars.Token:
    """设置当前请求上下文——返回用于恢复的 Token。

    Usage::

        ctx = RequestContext(tenant_id="tenant-001")
        token = set_context(ctx)
        try:
            await do_work()
        finally:
            _current_context.reset(token)

    Args:
        ctx: 要设置的 RequestContext。

    Returns:
        contextvars.Token——用于后续恢复。
    """
    return _current_context.set(ctx)


def get_request_id() -> str:
    """获取当前 request_id——如果未设置则自动生成（用于日志）。"""
    ctx = current_context()
    if ctx is not None and ctx.request_id:
        return ctx.request_id
    return str(uuid.uuid4())[:8]


def set_request_id(request_id: str) -> None:
    """设置当前 request_id——通常由 HTTP middleware 调用。"""
    token = set_context(RequestContext(request_id=request_id))
    # 不在 stack 上保持 token——因为 middleware 生命周期覆盖整个请求
    logger.debug("request_id set: %s", request_id)
