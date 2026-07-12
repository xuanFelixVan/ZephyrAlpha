# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §17
# [MODULE] zephyr.gov_enforcement.behavioral_admission.gpu_consensus_scheduler
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.gov_enforcement.behavioral_admission.verdict_engine
# [CONSUMERS] zephyr.gov_enforcement.behavioral_admission.verdict_engine;MOD-INF-027(audit-orchestrator)
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 2/2共识必须两个模型都返回一致verdict才PASS；P0_ANCHOR优先级最高不可被抢占
# [MODIFY-GUARD] docs/docs/03_modules/_cross_layer/behavioral-auditor/blueprint.md;src/zephyr/behavioral-admission/__init__.py
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] submit: GPUTimeout->LOCAL_GPU降级; submit: APIUnavailable->SINGLE_API降级; submit: AllFailed->ConsensusResult(failed)
# [TESTS] tests/test_behavioral_audit/test_gpu_consensus_scheduler.py
# [A_module] module_id=MOD-GOV_gpu_consensus_scheduler | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from http import HTTPStatus

import asyncio
import logging
import os
import threading
import time
import uuid
from enum import Enum, IntEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from zephyr.gov_enforcement.behavioral_admission.verdict_engine import ProtectionLevel, VerdictLevel
from zephyr.shared.foundation.constants import DEFAULT_OLLAMA_URL

logger = logging.getLogger(__name__)

_HAS_REQUESTS = True
try:
    import requests as _requests
except ImportError:
    _HAS_REQUESTS = False


# class-name-alias: migrated from governance/behavioral_admission; pre-existing same-name class in trading/integration (ARCH-034 debt, to be resolved in dedicated cleanup)
class ConsensusPriority(IntEnum):
    P0_ANCHOR = 0
    P1_PROTECTED = 1
    P2_NORMAL = 2
    P3_BASELINE = 3


# class-name-alias: migrated from governance/behavioral_admission; pre-existing same-name class in trading/integration (ARCH-034 debt, to be resolved in dedicated cleanup)
class ConsensusRoute(str, Enum):
    DUAL_API = "DUAL_API"
    SINGLE_API = "SINGLE_API"
    LOCAL_GPU = "LOCAL_GPU"


# class-name-alias: migrated from governance/behavioral_admission; pre-existing same-name class in trading/integration (ARCH-034 debt, to be resolved in dedicated cleanup)
class ConsensusStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    CONSENSUS_REACHED = "CONSENSUS_REACHED"
    PARTIAL_CONSENSUS = "PARTIAL_CONSENSUS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    DEGRADED = "DEGRADED"


# class-name-alias: migrated from governance/behavioral_admission; pre-existing same-name class in trading/integration (ARCH-034 debt, to be resolved in dedicated cleanup)
class ConsensusRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: str = Field(default_factory=lambda: uuid.uuid4().hex[:16])
    content: str = ""
    context: dict[str, Any] = Field(default_factory=dict)
    priority: ConsensusPriority = ConsensusPriority.P3_BASELINE
    protection_level: ProtectionLevel = ProtectionLevel.normal
    expected_verdict: VerdictLevel | None = None
    timeout_s: float = 30.0


# class-name-alias: migrated from governance/behavioral_admission; pre-existing same-name class in trading/integration (ARCH-034 debt, to be resolved in dedicated cleanup)
class ConsensusResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: str = ""
    status: ConsensusStatus = ConsensusStatus.PENDING
    route: ConsensusRoute = ConsensusRoute.LOCAL_GPU
    verdict: VerdictLevel | None = None
    confidence: float = 0.0
    model_responses: list[dict[str, Any]] = Field(default_factory=list)
    latency_ms: float = 0.0
    reason: str = ""


# class-name-alias: migrated from governance/behavioral_admission; pre-existing same-name class in trading/integration (ARCH-034 debt, to be resolved in dedicated cleanup)
class GPUStatus(BaseModel):
    model_config = ConfigDict(extra="forbid")

    available: bool = False
    model_name: str = ""
    vram_used_mb: float = 0.0
    vram_total_mb: float = 0.0
    last_check_time: float = 0.0
    ollama_responding: bool = False


# class-name-alias: migrated from governance/behavioral_admission; pre-existing same-name class in trading/integration (ARCH-034 debt, to be resolved in dedicated cleanup)
class SchedulerMetrics(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total_submitted: int = 0
    consensus_reached: int = 0
    partial_consensus: int = 0
    failed: int = 0
    degraded: int = 0
    cancelled: int = 0
    avg_latency_ms: float = 0.0
    queue_depth: int = 0
    gpu_available: bool = False
    dual_api_count: int = 0
    single_api_count: int = 0
    local_gpu_count: int = 0


# class-name-alias: migrated from governance/behavioral_admission; pre-existing same-name class in trading/integration (ARCH-034 debt, to be resolved in dedicated cleanup)
class _PriorityQueue:
    def __init__(self, max_size: int = 50) -> None:
        self._queues: dict[int, list[ConsensusRequest]] = {p: [] for p in range(4)}
        self._lock = threading.Lock()
        self._max_size = max_size
        self._total: int = 0

    def push(self, request: ConsensusRequest) -> bool:
        with self._lock:
            if self._total >= self._max_size:
                return False
            self._queues[request.priority].append(request)
            self._total += 1
            return True

    def pop(self) -> ConsensusRequest | None:
        with self._lock:
            for priority in sorted(self._queues.keys()):
                if self._queues[priority]:
                    self._total -= 1
                    return self._queues[priority].pop(0)
            return None

    def remove(self, request_id: str) -> bool:
        with self._lock:
            for queue in self._queues.values():
                for i, req in enumerate(queue):
                    if req.request_id == request_id:
                        queue.pop(i)
                        self._total -= 1
                        return True
            return False

    @property
    def depth(self) -> int:
        with self._lock:
            return self._total


# class-name-alias: migrated from governance/behavioral_admission; pre-existing same-name class in trading/integration (ARCH-034 debt, to be resolved in dedicated cleanup)
class GPUConsensusScheduler:
    def __init__(
        self,
        ollama_url: str = DEFAULT_OLLAMA_URL,
        local_model: str = "qwen3:8b",
        api_primary: str = "deepseek-v4-pro",
        api_secondary: str = "claude-sonnet-4",
        timeouts: dict[str, float] | None = None,
        max_queue_size: int = 50,
        max_workers: int = 1,
    ) -> None:
        self._ollama_url = ollama_url.rstrip("/")
        self._local_model = local_model
        self._api_primary = api_primary
        self._api_secondary = api_secondary
        _t = timeouts or {}
        self._gpu_timeout_s = _t.get("gpu", 30.0)
        self._api_timeout_s = _t.get("api", 15.0)
        self._queue = _PriorityQueue(max_size=max_queue_size)
        self._max_workers = max_workers
        # 5.67.2 修复: 使用 max_workers 创建 Semaphore 限制批量并发, 替代 submit_batch 中硬编码的 8
        self._semaphore = asyncio.Semaphore(max_workers)
        self._lock = threading.Lock()
        self._gpu_status = GPUStatus(
            available=False,
            model_name=local_model,
            last_check_time=0.0,
        )
        self._total_submitted: int = 0
        self._consensus_reached: int = 0
        self._partial_consensus: int = 0
        self._failed: int = 0
        self._degraded: int = 0
        self._cancelled: int = 0
        self._total_latency_ms: float = 0.0
        self._dual_api_count: int = 0
        self._single_api_count: int = 0
        self._local_gpu_count: int = 0
        self._check_gpu_availability()

    async def submit(self, request: ConsensusRequest) -> ConsensusResult:
        start = time.monotonic()
        with self._lock:
            self._total_submitted += 1

        route = self._determine_route(request)
        result = await self._execute_route(request, route, start)

        with self._lock:
            self._total_latency_ms += result.latency_ms
            if result.status == ConsensusStatus.CONSENSUS_REACHED:
                self._consensus_reached += 1
            elif result.status == ConsensusStatus.PARTIAL_CONSENSUS:
                self._partial_consensus += 1
            elif result.status == ConsensusStatus.FAILED:
                self._failed += 1
            elif result.status == ConsensusStatus.DEGRADED:
                self._degraded += 1
            if route is ConsensusRoute.DUAL_API:
                self._dual_api_count += 1
            elif route is ConsensusRoute.SINGLE_API:
                self._single_api_count += 1
            else:
                self._local_gpu_count += 1

        return result

    async def submit_batch(self, requests: list[ConsensusRequest]) -> list[ConsensusResult]:
        # 5.67.2 修复: 使用 self._semaphore (基于 max_workers) 替代硬编码 asyncio.Semaphore(8)
        sem = self._semaphore

        async def _limited_submit(coro):
            async with sem:
                return await coro

        tasks = [_limited_submit(self.submit(req)) for req in requests]
        return list(await asyncio.gather(*tasks, return_exceptions=False))

    def get_gpu_status(self) -> GPUStatus:
        return self._gpu_status.model_copy()

    def get_queue_depth(self) -> int:
        return self._queue.depth

    def cancel(self, request_id: str) -> bool:
        removed = self._queue.remove(request_id)
        if removed:
            with self._lock:
                self._cancelled += 1
        return removed

    def get_metrics(self) -> SchedulerMetrics:
        with self._lock:
            avg_latency = self._total_latency_ms / max(self._total_submitted, 1)
            return SchedulerMetrics(
                total_submitted=self._total_submitted,
                consensus_reached=self._consensus_reached,
                partial_consensus=self._partial_consensus,
                failed=self._failed,
                degraded=self._degraded,
                cancelled=self._cancelled,
                avg_latency_ms=round(avg_latency, 2),
                queue_depth=self._queue.depth,
                gpu_available=self._gpu_status.available,
                dual_api_count=self._dual_api_count,
                single_api_count=self._single_api_count,
                local_gpu_count=self._local_gpu_count,
            )

    def health_check(self) -> dict[str, Any]:
        metrics = self.get_metrics()
        return {
            "status": "healthy" if metrics.gpu_available else "degraded",
            "gpu_status": self._gpu_status.model_dump(),
            "metrics": metrics.model_dump(),
        }

    def _determine_route(self, request: ConsensusRequest) -> ConsensusRoute:
        if request.protection_level in (ProtectionLevel.anchor, ProtectionLevel.protected):
            if self._gpu_status.available:
                return ConsensusRoute.DUAL_API
            return ConsensusRoute.SINGLE_API
        if self._gpu_status.available:
            return ConsensusRoute.LOCAL_GPU
        return ConsensusRoute.SINGLE_API

    async def _execute_route(
        self,
        request: ConsensusRequest,
        route: ConsensusRoute,
        start: float,
    ) -> ConsensusResult:
        if route is ConsensusRoute.DUAL_API:
            result = await self._route_dual_api(request, start)
        elif route is ConsensusRoute.SINGLE_API:
            result = await self._route_single_api(request, start)
        else:
            result = await self._route_local_gpu(request, start)
        return result

    async def _route_dual_api(self, request: ConsensusRequest, start: float) -> ConsensusResult:
        responses: list[dict[str, Any]] = []
        verdicts: list[VerdictLevel] = []

        tasks = [
            self._call_api(self._api_primary, request),
            self._call_api(self._api_secondary, request),
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for r in results:
            # 5.112.2 修复：CancelledError 继承 BaseException 而非 Exception，
            # isinstance(r, Exception) 对 CancelledError 返回 False，导致取消信号被吞没。
            if isinstance(r, asyncio.CancelledError):
                raise r  # 传播取消信号
            if isinstance(r, BaseException):
                responses.append({"error": str(r), "verdict": None})
            elif r is not None:
                responses.append(r)
                v = r.get("verdict")
                if v is not None:
                    try:
                        verdicts.append(VerdictLevel(v))
                    except ValueError:
                        pass

        latency = (time.monotonic() - start) * 1000.0

        if len(verdicts) >= 2 and verdicts[0] == verdicts[1]:
            return ConsensusResult(
                request_id=request.request_id,
                status=ConsensusStatus.CONSENSUS_REACHED,
                route=ConsensusRoute.DUAL_API,
                verdict=verdicts[0],
                confidence=0.95,
                model_responses=responses,
                latency_ms=round(latency, 2),
                reason="2/2_consensus",
            )

        if len(verdicts) >= 1:
            return ConsensusResult(
                request_id=request.request_id,
                status=ConsensusStatus.PARTIAL_CONSENSUS,
                route=ConsensusRoute.DUAL_API,
                verdict=verdicts[0],
                confidence=0.6,
                model_responses=responses,
                latency_ms=round(latency, 2),
                reason="partial_consensus_1/2",
            )

        return ConsensusResult(
            request_id=request.request_id,
            status=ConsensusStatus.DEGRADED,
            route=ConsensusRoute.DUAL_API,
            confidence=0.0,
            model_responses=responses,
            latency_ms=round(latency, 2),
            reason="dual_api_failed_degraded",
        )

    async def _route_single_api(self, request: ConsensusRequest, start: float) -> ConsensusResult:
        response = await self._call_api(self._api_primary, request)
        latency = (time.monotonic() - start) * 1000.0

        if response is None or isinstance(response, Exception):
            return ConsensusResult(
                request_id=request.request_id,
                status=ConsensusStatus.DEGRADED,
                route=ConsensusRoute.SINGLE_API,
                confidence=0.0,
                latency_ms=round(latency, 2),
                reason="single_api_failed",
            )

        verdict_str = response.get("verdict", "PASS")
        try:
            verdict = VerdictLevel(verdict_str)
        except ValueError:
            verdict = VerdictLevel.PASS

        return ConsensusResult(
            request_id=request.request_id,
            status=ConsensusStatus.CONSENSUS_REACHED,
            route=ConsensusRoute.SINGLE_API,
            verdict=verdict,
            confidence=0.7,
            model_responses=[response],
            latency_ms=round(latency, 2),
            reason="single_api_consensus",
        )

    async def _route_local_gpu(self, request: ConsensusRequest, start: float) -> ConsensusResult:
        response = await self._call_ollama(request)
        latency = (time.monotonic() - start) * 1000.0

        if response is None:
            return ConsensusResult(
                request_id=request.request_id,
                status=ConsensusStatus.DEGRADED,
                route=ConsensusRoute.LOCAL_GPU,
                confidence=0.0,
                latency_ms=round(latency, 2),
                reason="local_gpu_failed",
            )

        verdict_str = response.get("verdict", "PASS")
        try:
            verdict = VerdictLevel(verdict_str)
        except ValueError:
            verdict = VerdictLevel.PASS

        return ConsensusResult(
            request_id=request.request_id,
            status=ConsensusStatus.CONSENSUS_REACHED,
            route=ConsensusRoute.LOCAL_GPU,
            verdict=verdict,
            confidence=0.8,
            model_responses=[response],
            latency_ms=round(latency, 2),
            reason="local_gpu_consensus",
        )

    async def _call_api(self, model_id: str, request: ConsensusRequest) -> dict[str, Any] | None:
        if not _HAS_REQUESTS:
            return None
        loop = asyncio.get_running_loop()
        try:
            result = await loop.run_in_executor(
                None,
                self._call_api_sync,
                model_id,
                request,
            )
            return result
        except Exception as exc:
            logger.debug("API call failed for model %s: %s", model_id, exc, exc_info=True)
            return None

    def _call_api_sync(self, model_id: str, request: ConsensusRequest) -> dict[str, Any] | None:
        if not _HAS_REQUESTS:
            return None
        prompt = (
            f"Evaluate the following operation and return a verdict (PASS/YELLOW/RED).\n"
            f"Content: {request.content}\n"
            f"Context: {request.context}\n"
            f"Protection level: {request.protection_level.value}\n"
            f'Respond with JSON: {{"verdict": "PASS"|"YELLOW"|"RED", "confidence": 0.0-1.0, "reasoning": "..."}}'
        )
        try:
            resp = _requests.post(
                f"{self._ollama_url}/api/generate",
                json={
                    "model": model_id,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"num_predict": 256},
                },
                timeout=self._api_timeout_s,
            )
            # 5.56.1 修复：原仅接受 200，将 201/202/204 等 2xx 成功响应误判为失败。
            # 改为范围判定，与 HTTP 语义一致。
            if 200 <= resp.status_code < 300:
                data = resp.json()
                text = data.get("response", "")
                return self._parse_model_response(text, model_id)
            return None
        except Exception:
            return None

    async def _call_ollama(self, request: ConsensusRequest) -> dict[str, Any] | None:
        if not _HAS_REQUESTS:
            return None
        loop = asyncio.get_running_loop()
        try:
            result = await loop.run_in_executor(
                None,
                self._call_ollama_sync,
                request,
            )
            return result
        except Exception:
            return None

    def _call_ollama_sync(self, request: ConsensusRequest) -> dict[str, Any] | None:
        if not _HAS_REQUESTS:
            return None
        prompt = (
            f"Evaluate: {request.content}\n"
            f"Context: {request.context}\n"
            f"Protection: {request.protection_level.value}\n"
            f'JSON: {{"verdict": "PASS"|"YELLOW"|"RED", "confidence": 0.0-1.0}}'
        )
        try:
            resp = _requests.post(
                f"{self._ollama_url}/api/generate",
                json={
                    "model": self._local_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"num_predict": 128},
                },
                timeout=self._gpu_timeout_s,
            )
            if resp.status_code == HTTPStatus.OK:
                data = resp.json()
                text = data.get("response", "")
                return self._parse_model_response(text, self._local_model)
            return None
        except Exception:
            return None

    def _parse_model_response(self, text: str, model_id: str) -> dict[str, Any]:
        import json as _json

        verdict = VerdictLevel.PASS
        confidence = 0.5
        reasoning = ""

        try:
            # 5.147.10 修复: 原 text.find("{") + text.rfind("}") 启发式提取,
            # 若文本含多段 JSON 或花括号, text[start:end] 可能横跨非 JSON 内容。
            # 改用 json.JSONDecoder().raw_decode 增量解析, 从首个 { 开始尝试解析完整 JSON 对象
            start = text.find("{")
            if start >= 0:
                decoder = _json.JSONDecoder()
                parsed, _ = decoder.raw_decode(text[start:])
                v = parsed.get("verdict", "PASS")
                try:
                    verdict = VerdictLevel(v)
                except ValueError:
                    verdict = VerdictLevel.PASS
                confidence = float(parsed.get("confidence", 0.5))
                reasoning = parsed.get("reasoning", "")
        except (ValueError, _json.JSONDecodeError):
            lower = text.lower()
            if "red" in lower:
                verdict = VerdictLevel.RED
            elif "yellow" in lower:
                verdict = VerdictLevel.YELLOW
            reasoning = text[:200]

        return {
            "model_id": model_id,
            "verdict": verdict.value,
            "confidence": confidence,
            "reasoning": reasoning,
        }

    def _check_gpu_availability(self) -> None:
        if not _HAS_REQUESTS:
            self._gpu_status = GPUStatus(
                available=False,
                model_name=self._local_model,
                last_check_time=time.monotonic(),
                ollama_responding=False,
            )
            return
        try:
            resp = _requests.get(
                f"{self._ollama_url}/api/tags",
                timeout=5.0,
            )
            if resp.status_code == HTTPStatus.OK:
                data = resp.json()
                models = [m.get("name", "") for m in data.get("models", [])]
                has_model = any(self._local_model in m for m in models)
                self._gpu_status = GPUStatus(
                    available=has_model,
                    model_name=self._local_model,
                    last_check_time=time.monotonic(),
                    ollama_responding=True,
                )
            else:
                self._gpu_status = GPUStatus(
                    available=False,
                    model_name=self._local_model,
                    last_check_time=time.monotonic(),
                    ollama_responding=False,
                )
        except Exception:
            self._gpu_status = GPUStatus(
                available=False,
                model_name=self._local_model,
                last_check_time=time.monotonic(),
                ollama_responding=False,
            )