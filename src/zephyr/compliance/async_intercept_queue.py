# [BLUEPRINT] MOD-L10-001 | docs/03_modules/_domain_compliance/blueprint.md | §17
# [MODULE] zephyr.compliance.async_intercept_queue
# [DOMAIN] D_COMPLIANCE
# [DEPENDENCIES] zephyr.governance.security_governance.security_gateway_base; zephyr.shared.foundation.errors
# [CONSUMERS] MOD-L10-001(DefaultSecurityGateway 调用方异步化) ; 治理链路 AI 指令拦截
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 队列满→InterceptQueueFullError(Fail-Closed,调用方按拦截处理); 网关异常→BLOCK裁决(Fail-Closed); 缓存键=sha256(content)+source且容量有界(LRU淘汰); run_worker有界循环(max_iterations封顶+stop_event可停,禁while True无界); 判定逻辑全委托SecurityGateway(本队列只做异步化+缓存,不重造扫描)
# [MODIFY-GUARD] docs/03_modules/_domain_compliance/blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InterceptQueueFullError
# [TESTS] tests/compliance/test_async_intercept_queue.py
# [A_module] module_id=MOD-L10-001 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent
"""



Async Intercept Queue — 合规异步拦截队列 (MOD-L10-001, GAP-L10-001)

蓝图 §17 容量升级缺口 GAP-L10-001：SecurityGateway 同步拦截延迟 → 异步拦截队列 + 缓存
（触发阈值 QPS > 100/s）。本模块把"提交拦截请求"与"安全网关判定"解耦：
  - submit()      非阻塞入队，返回 ticket_id（队列满 → InterceptQueueFullError，
                  Fail-Closed：调用方必须按拦截/阻断处理，不得放行）
  - process_next()/drain()/run_worker()  工作侧消费：pre_filter → security_scan →
                  decide 全委托既有 SecurityGateway（OCP 扩展点，不重造扫描逻辑）
  - 内容缓存      sha256(content)+source 键控的有界 LRU，重复内容免重扫
Fail-Closed：网关执行异常 → 生成 BLOCK 裁决并留 error 痕迹（宁可误拦不可漏拦）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: gateway 参数
#   fields: 参数 gateway（无注解）
#   code: async_intercept_queue.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: max_queue_size 参数
#   fields: 参数 max_queue_size（无注解）
#   code: async_intercept_queue.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: cache_size 参数
#   fields: 参数 cache_size（无注解）
#   code: async_intercept_queue.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① AsyncInterceptQueue
#   name_en: AsyncInterceptQueue
#   intro: 合规异步拦截队列（有界 + 缓存 + 线程安全）。
#   desc: 合规异步拦截队列（有界 + 缓存 + 线程安全）。 Args: gateway: 既有安全网关实现（SecurityGateway OCP 扩展点）。 max_queue_siz…；公共方法（定义序）: submit,…
#   inputs: gateway max_queue_size cache_size
#   outputs: 返回值
#   （注：A1 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（4 定义）
#   name_en: public defs
#   intro: AsyncInterceptQueue
#   downstream: MOD-L10-001(DefaultSecurityGateway 调用方异步化) ; 治理链路 AI 指令拦截
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> O1
"""

from __future__ import annotations

import hashlib
import logging
import queue
import threading
import uuid
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Final

from zephyr.governance.security_governance.security_gateway_base import (
    AuditAction,
    AuditDecision,
    SecurityGateway,
)
from zephyr.shared.foundation.errors import ZephyrBaseError

_logger = logging.getLogger(__name__)

__all__: Final = [
    "AsyncInterceptQueue",
    "InterceptRequest",
    "InterceptResult",
    "InterceptQueueFullError",
]


class InterceptQueueFullError(ZephyrBaseError):
    """拦截队列已满（Fail-Closed：调用方必须按拦截处理，禁止放行）。"""

    error_code = "ZA-CMP-0012"


@dataclass(frozen=True)
class InterceptRequest:
    """入队的拦截请求。"""

    ticket_id: str
    content: str
    source: str
    submitted_at: datetime


@dataclass(frozen=True)
class InterceptResult:
    """拦截处理结果（decision 由 SecurityGateway 产出；from_cache 标记缓存命中）。"""

    ticket_id: str
    decision: AuditDecision
    processed_at: datetime
    from_cache: bool = False
    error: str | None = None


class AsyncInterceptQueue:
    """合规异步拦截队列（有界 + 缓存 + 线程安全）。

    Args:
        gateway: 既有安全网关实现（SecurityGateway OCP 扩展点）。
        max_queue_size: 队列容量上限（背压；满则 submit 抛 InterceptQueueFullError）。
        cache_size: 内容缓存容量（LRU 淘汰；0=禁用缓存）。
    """

    def __init__(
        self,
        gateway: SecurityGateway,
        *,
        max_queue_size: int = 1000,
        cache_size: int = 256,
    ) -> None:
        if max_queue_size <= 0:
            raise ValueError(f"max_queue_size 必须为正: {max_queue_size}")
        if cache_size < 0:
            raise ValueError(f"cache_size 不允许负数: {cache_size}")
        self._gateway = gateway
        self._cache_size = cache_size
        self._queue: queue.Queue[InterceptRequest] = queue.Queue(maxsize=max_queue_size)
        self._lock = threading.Lock()
        self._results: dict[str, InterceptResult] = {}
        self._cache: OrderedDict[str, AuditDecision] = OrderedDict()

    # ── 提交侧 ───────────────────────────────────────────────────────

    def submit(self, content: str, source: str) -> str:
        """非阻塞提交拦截请求，返回 ticket_id。

        Raises:
            InterceptQueueFullError: 队列已满（Fail-Closed，调用方按拦截处理）。
        """
        request = InterceptRequest(
            ticket_id=f"aiq-{uuid.uuid4().hex[:12]}",
            content=content,
            source=source,
            submitted_at=datetime.now(UTC),
        )
        try:
            self._queue.put_nowait(request)
        except queue.Full as exc:
            raise InterceptQueueFullError(
                "拦截队列已满，拒绝入队（Fail-Closed：调用方必须按拦截/阻断处理）",
                details={"max_queue_size": self._queue.maxsize},
            ) from exc
        return request.ticket_id

    @property
    def pending_count(self) -> int:
        return self._queue.qsize()

    # ── 结果侧 ───────────────────────────────────────────────────────

    def get_result(self, ticket_id: str) -> InterceptResult | None:
        with self._lock:
            return self._results.get(ticket_id)

    # ── 工作侧 ───────────────────────────────────────────────────────

    def process_next(self) -> InterceptResult | None:
        """处理一条队首请求；空队列返回 None。"""
        try:
            request = self._queue.get_nowait()
        except queue.Empty:
            return None
        try:
            result = self._execute(request)
        finally:
            self._queue.task_done()
        with self._lock:
            self._results[result.ticket_id] = result
        return result

    def drain(self, max_items: int) -> list[InterceptResult]:
        """批量处理最多 max_items 条（有界）。"""
        results: list[InterceptResult] = []
        for _ in range(max(0, max_items)):
            result = self.process_next()
            if result is None:
                break
            results.append(result)
        return results

    def run_worker(
        self,
        stop_event: threading.Event,
        *,
        poll_interval_s: float = 0.1,
        max_iterations: int = 1000,
    ) -> int:
        """有界工作循环：处理直到 stop_event 置位 / 队列空 / 达 max_iterations。

        返回本轮处理条数。禁 while True 无界循环纪律：迭代上限硬封顶。
        """
        processed = 0
        for _ in range(max(0, max_iterations)):
            if stop_event.is_set():
                break
            result = self.process_next()
            if result is None:
                break
            processed += 1
            if poll_interval_s > 0 and not self._queue.empty():
                stop_event.wait(poll_interval_s)
        return processed

    # ── 内部：判定委托 ───────────────────────────────────────────────

    def _cache_key(self, content: str, source: str) -> str:
        digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
        return f"{source}:{digest}"

    def _cache_get(self, key: str) -> AuditDecision | None:
        with self._lock:
            decision = self._cache.get(key)
            if decision is not None:
                self._cache.move_to_end(key)
            return decision

    def _cache_put(self, key: str, decision: AuditDecision) -> None:
        if self._cache_size == 0:
            return
        with self._lock:
            self._cache[key] = decision
            self._cache.move_to_end(key)
            while len(self._cache) > self._cache_size:
                self._cache.popitem(last=False)

    def _execute(self, request: InterceptRequest) -> InterceptResult:
        cache_key = self._cache_key(request.content, request.source)
        cached = self._cache_get(cache_key)
        if cached is not None:
            return InterceptResult(
                ticket_id=request.ticket_id,
                decision=cached,
                processed_at=datetime.now(UTC),
                from_cache=True,
            )
        try:
            if self._gateway.pre_filter(request.content, request.source):
                risks = self._gateway.security_scan(request.content)
            else:
                risks = []
            decision = self._gateway.decide(risks, {"source": request.source})
            self._cache_put(cache_key, decision)
            return InterceptResult(
                ticket_id=request.ticket_id,
                decision=decision,
                processed_at=datetime.now(UTC),
            )
        except Exception as exc:  # noqa: BLE001 — Fail-Closed 转 BLOCK 裁决
            _logger.error(
                "ASYNC_INTERCEPT_GATEWAY_ERROR fail-closed ticket=%s error=%s",
                request.ticket_id,
                exc,
            )
            return InterceptResult(
                ticket_id=request.ticket_id,
                decision=AuditDecision(
                    decision_id=f"aiq-err-{uuid.uuid4().hex[:8]}",
                    action=AuditAction.BLOCK,
                    rule_id="async_intercept_gateway_error",
                    reason="安全网关执行异常，Fail-Closed 阻断",
                    timestamp=datetime.now(UTC),
                    metadata={},
                ),
                processed_at=datetime.now(UTC),
                error=str(exc),
            )
