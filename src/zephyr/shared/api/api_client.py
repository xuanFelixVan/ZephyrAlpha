# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.api.api_client
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.foundation.errors; zephyr.shared.resilience.circuit_breaker; zephyr.shared.resilience.retry; zephyr.shared.io.serialization
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
# [A_module] module_id=MOD-SHR_api_client | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
api_client.py —— 统一 API Client 基类（Phase 7 新增 | 盲点 B11 修复）

痛点修复：AI agent 调用 LLM API / 外部服务时需要手动处理 timeout、retry、circuit-breaker——
  1. 每个 consumer 手写裸 aiohttp -> 超时不统一、熔断不统一、重试不统一
  2. LLM API 调用是项目核心路径——没有统一 client = 不可预测的行为
  3. 没有内置 metrics hook——无法追踪 API 调用的成功率/延迟

设计对标：
  - Stripe Python SDK（统一的 APIResource 基类 + 自动重试 + 速率限制）
  - Spring RestTemplate / WebClient（统一超时配置 + 拦截器链）
  - Google API Client Libraries（指数退避 + 幂等重试）

设计原则：
  - async-first——项目主体是异步架构
  - 可组合——timeout / retry / circuit-breaker 都是可选注入
  - 内置 metrics hook——每次调用自动 emit 事件到 Observer（如果有）
  - 零侵入——不强制依赖 aiohttp，接口协议可替换

AI 施工约定：
  - 所有 HTTP API 调用 MUST 使用 ApiClient 或子类——禁止裸 aiohttp
  - 新增 API target 时 SHOULD 创建 ApiClient 子类并配置专用超时

SSoT: MOD-INF-016 §2.10 shared-api-client
Version: 0.1.0
"""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum, unique
from typing import TYPE_CHECKING, Any, Protocol, Self

from zephyr.shared.foundation.errors import ZephyrBaseError
from zephyr.shared.io.serialization import to_dict
from zephyr.shared.resilience.circuit_breaker import CircuitBreaker
from zephyr.shared.resilience.retry import RetryConfig, async_retry

if TYPE_CHECKING:
    from zephyr.shared.infra.observer import Observer

__all__ = [
    "AioHttpProvider",
    "ApiCallError",
    "ApiCallMetrics",
    "ApiClient",
    "ApiClientConfig",
    "ApiResponse",
    "HttpMethod",
    "HttpProvider",
]

logger = logging.getLogger(__name__)


class ApiCallError(ZephyrBaseError):
    """API 调用失败——HTTP 错误、超时、协议不匹配。"""
    error_code = "ZA-SH-0021"


@unique
class HttpMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


@dataclass(frozen=True)
class ApiCallMetrics:
    url: str
    method: HttpMethod
    status_code: int
    duration_ms: float
    attempt: int
    success: bool
    error_message: str = ""
    correlation_id: str = ""


@dataclass(frozen=True)
class ApiResponse:
    status_code: int
    headers: dict[str, str]
    body: dict[str, Any] | list[Any] | str
    metrics: ApiCallMetrics

    @property
    def is_success(self) -> bool:
        return 200 <= self.status_code < 300

    def json(self) -> dict[str, Any]:
        if isinstance(self.body, dict):
            return self.body
        raise ApiCallError(
            "response body is not a JSON object",
            details={"status_code": self.status_code, "body_type": type(self.body).__name__},
        )


class HttpProvider(Protocol):
    """HTTP 传输层抽象——可替换为 aiohttp / httpx / mock。"""

    async def request(
        self,
        method: HttpMethod,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        body: dict[str, Any] | None = None,
        timeout_seconds: float = 30.0,
    ) -> ApiResponse: ...


@dataclass
class ApiClientConfig:
    base_url: str = ""
    default_headers: dict[str, str] = field(default_factory=dict)
    timeout_seconds: float = 30.0
    retry: RetryConfig | None = None
    circuit_breaker_name: str | None = None
    trace_id_header: str = "X-Trace-Id"


class ApiClient:
    """统一 API Client——可组合超时/重试/熔断/metrics。

    Usage::

        client = ApiClient(
            provider=AioHttpProvider(),
            config=ApiClientConfig(base_url="https://api.llm.example.com/v1"),
        )
        async with client:
            resp = await client.post("/chat/completions", body={"model":"deepseek","messages":[...]})
            data = resp.json()
    """

    def __init__(
        self,
        provider: HttpProvider,
        config: ApiClientConfig | None = None,
        *,
        circuit_breaker: CircuitBreaker | None = None,
        observer: Observer | None = None,
    ) -> None:
        self._provider = provider
        self._config = config or ApiClientConfig()
        self._circuit_breaker = circuit_breaker
        self._observer = observer
        self._active = False

    async def __aenter__(self) -> Self:
        self._active = True
        return self

    async def __aexit__(self, *args: Any) -> None:
        self._active = False

    @property
    def base_url(self) -> str:
        return self._config.base_url.rstrip("/")

    def _build_url(self, path: str) -> str:
        if path.startswith("https://") or path.startswith("http://"):
            return path
        return f"{self.base_url}/{path.lstrip('/')}"

    def _build_headers(self, extra: dict[str, str] | None = None) -> dict[str, str]:
        headers = dict(self._config.default_headers)
        headers[self._config.trace_id_header] = str(uuid.uuid4())
        headers["Content-Type"] = headers.get("Content-Type", "application/json")
        if extra:
            headers.update(extra)
        return headers

    async def _emit_call_metrics(self, metrics: ApiCallMetrics) -> None:
        if self._observer is None:
            return
        try:
            self._observer.emit("api_call_completed", metrics=to_dict(metrics))
        except Exception as e:
            logger.warning("suppressed error in api_client", exc_info=True)

    def _build_retry(self) -> RetryConfig:
        if self._config.retry:
            return self._config.retry
        return RetryConfig(
            max_attempts=3,
            base_delay_seconds=0.5,
            max_delay_seconds=30.0,
            jitter=True,
            retryable_exceptions=(ApiCallError,),
        )

    async def request(
        self,
        method: HttpMethod,
        path: str,
        *,
        headers: dict[str, str] | None = None,
        body: dict[str, Any] | None = None,
        timeout_seconds: float | None = None,
    ) -> ApiResponse:
        if not self._active:
            raise ApiCallError(
                "ApiClient not active—use 'async with client:' context manager",
                details={"method": method.value, "path": path},
            )

        url = self._build_url(path)
        final_headers = self._build_headers(headers)
        effective_timeout = timeout_seconds or self._config.timeout_seconds

        if self._circuit_breaker is not None and self._circuit_breaker.is_open:
            raise ApiCallError(
                f"circuit breaker '{self._circuit_breaker.name}' is OPEN—request blocked",
                details={"url": url, "method": method.value, "breaker_state": self._circuit_breaker.state.value},
            )

        retry_cfg = self._build_retry()

        @async_retry(config=retry_cfg)
        async def _execute(_attempt: int = 1) -> ApiResponse:
            t0 = time.monotonic()
            try:
                resp = await self._provider.request(
                    method=method,
                    url=url,
                    headers=final_headers,
                    body=body,
                    timeout_seconds=effective_timeout,
                )
            except TimeoutError:
                duration_ms = (time.monotonic() - t0) * 1000
                metrics = ApiCallMetrics(
                    url=url,
                    method=method,
                    status_code=0,
                    duration_ms=duration_ms,
                    attempt=_attempt,
                    success=False,
                    error_message="timeout",
                    correlation_id=final_headers.get(self._config.trace_id_header, ""),
                )
                await self._emit_call_metrics(metrics)
                raise ApiCallError(
                    f"request timed out after {effective_timeout}s: {method.value}",
                    details={"url": url, "method": method.value, "timeout_seconds": effective_timeout},
                )

            duration_ms = (time.monotonic() - t0) * 1000
            metrics = ApiCallMetrics(
                url=url,
                method=method,
                status_code=resp.status_code,
                duration_ms=round(duration_ms, 2),
                attempt=_attempt,
                success=resp.is_success,
                correlation_id=final_headers.get(self._config.trace_id_header, ""),
            )

            if self._circuit_breaker is not None:
                if resp.is_success:
                    self._circuit_breaker.record_success()
                else:
                    self._circuit_breaker.record_failure()

            await self._emit_call_metrics(metrics)

            if not resp.is_success:
                raise ApiCallError(
                    f"API returned {resp.status_code}: {method.value}",
                    details={
                        "url": url,
                        "method": method.value,
                        "status_code": resp.status_code,
                        "response_head": str(resp.body)[:500],
                    },
                )

            return resp

        return await _execute()

    async def get(
        self, path: str, *, headers: dict[str, str] | None = None, timeout_seconds: float | None = None
    ) -> ApiResponse:
        return await self.request(HttpMethod.GET, path, headers=headers, timeout_seconds=timeout_seconds)

    async def post(
        self,
        path: str,
        *,
        body: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        timeout_seconds: float | None = None,
    ) -> ApiResponse:
        return await self.request(HttpMethod.POST, path, headers=headers, body=body, timeout_seconds=timeout_seconds)

    async def put(
        self,
        path: str,
        *,
        body: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        timeout_seconds: float | None = None,
    ) -> ApiResponse:
        return await self.request(HttpMethod.PUT, path, headers=headers, body=body, timeout_seconds=timeout_seconds)

    async def patch(
        self,
        path: str,
        *,
        body: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        timeout_seconds: float | None = None,
    ) -> ApiResponse:
        return await self.request(HttpMethod.PATCH, path, headers=headers, body=body, timeout_seconds=timeout_seconds)

    async def delete(
        self, path: str, *, headers: dict[str, str] | None = None, timeout_seconds: float | None = None
    ) -> ApiResponse:
        return await self.request(HttpMethod.DELETE, path, headers=headers, timeout_seconds=timeout_seconds)


class AioHttpProvider:
    """基于 aiohttp 的 HTTP 传输实现。

    Usage::

        provider = AioHttpProvider()
        client = ApiClient(provider=provider, config=ApiClientConfig(base_url="https://api.example.com"))
    """

    async def request(
        self,
        method: HttpMethod,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        body: dict[str, Any] | None = None,
        timeout_seconds: float = 30.0,
    ) -> ApiResponse:
        import aiohttp

        timeout = aiohttp.ClientTimeout(total=timeout_seconds)

        async with (
            aiohttp.ClientSession(timeout=timeout) as session,
            session.request(
                method=method.value,
                url=url,
                headers=headers or {},
                json=body,
            ) as resp,
        ):
            response_headers = dict(resp.headers)
            try:
                response_body: Any = await resp.json()
            except Exception:
                response_body = await resp.text()

            return ApiResponse(
                status_code=resp.status,
                headers=response_headers,
                body=response_body,
                metrics=ApiCallMetrics(
                    url=url,
                    method=method,
                    status_code=resp.status,
                    duration_ms=0,
                    attempt=1,
                    success=200 <= resp.status < 300,
                ),
            )
