# [BLUEPRINT] MOD-FE-011 | docs/03_modules/_domain_frontend/frontend_api_proxy/blueprint.md
# [MODULE] zephyr.frontend.frontend_api_proxy
# [DOMAIN] D_FRONTEND
# [DEPENDENCIES] 无（协议核心纯内存；token校验/令牌桶时钟/上游client全注入）
# [CONSUMERS] 运行时装配批（前端唯一接触点 / 上游服务适配器装配）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 方法词表闭合(GET|POST); 路由最长前缀匹配(确定性); token校验未注入Fail-Closed; 限流按principal分桶(注入时钟); 上游client注入不真发(异常→502规范化); 响应规范化(JSON可序列化, 不落token); 非法输入Fail-Closed; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_frontend/frontend_api_proxy/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] FrontendProxyError(占位 ZA-FE-UNREGISTERED-FRONTEND-PROXY)——空路由表/非法前缀/上游未注册/校验器未注入/非法方法/非法路径/空token/限流参数非法时抛
# [TESTS] tests/frontend/test_frontend_api_proxy.py
# [A_module] module_id=MOD-FE-011 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""FrontendApiProxy — 前端 API 代理（MOD-FE-011）。

B9-10703（AUD-DRAFT-001-DIGEST P2 波 P2-W11，CAND-FE-012，B9 D-FRONTEND-22）：
BFF 思想——前后端**唯一接触点**代理：**请求路由表**（前缀→上游，最长前缀
匹配）+ **鉴权**（token 校验注入，返回 principal）+ **限流**（令牌桶注入
时钟，按 principal 分桶）+ **转发**（upstream client 注入不真发）+
**响应规范化**（统一 ok/code/data/error 载荷，不落 token）。

查重分工：default_approval_gateway=审批动作载体（本件仅转发不审批）；
dashboard_feeds=站内数据订阅（本件=请求/响应代理，零交集）。
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any, Final

_log = logging.getLogger(__name__)

__all__: Final = [
    "FrontendApiProxy",
    "FrontendProxyError",
    "ProxyRequest",
    "ProxyResponse",
    "TokenBucket",
    "UpstreamResponse",
]

#: 允许方法（词表闭合）
_METHODS: Final[frozenset[str]] = frozenset({"GET", "POST"})


class FrontendProxyError(Exception):
    """代理配置/请求非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-FE-UNREGISTERED-FRONTEND-PROXY。
    """


@dataclass(frozen=True)
class ProxyRequest:
    """入站代理请求（前端唯一接触点载荷，frozen）。"""

    method: str
    path: str
    token: str
    body: Mapping[str, Any] | None = None
    request_id: str = ""


@dataclass(frozen=True)
class UpstreamResponse:
    """上游响应（client 注入返回）。"""

    status_code: int
    payload: Mapping[str, Any]


@dataclass(frozen=True)
class ProxyResponse:
    """规范化代理响应（payload JSON 可序列化，不落 token）。"""

    status_code: int
    ok: bool
    upstream: str
    payload: Mapping[str, Any]


class TokenBucket:
    """令牌桶限流器（注入时钟，按 key 分桶，纯内存确定性）。"""

    def __init__(
        self,
        *,
        capacity: int,
        refill_per_second: float,
        clock: Callable[[], float],
    ) -> None:
        if not isinstance(capacity, int) or isinstance(capacity, bool) or capacity <= 0:
            raise FrontendProxyError(f"令牌桶容量非法: {capacity!r}")
        if not isinstance(refill_per_second, (int, float)) or refill_per_second <= 0:
            raise FrontendProxyError(f"令牌桶速率非法: {refill_per_second!r}")
        if not callable(clock):
            raise FrontendProxyError("令牌桶时钟未注入")
        self._capacity = float(capacity)
        self._rate = float(refill_per_second)
        self._clock = clock
        self._buckets: dict[str, tuple[float, float]] = {}  # key -> (余量, 上次时间戳)

    def allow(self, key: str) -> bool:
        """取一枚令牌：有余量→True 并扣减；不足→False（不扣）。"""
        if not isinstance(key, str) or not key:
            raise FrontendProxyError("限流 key 为空")
        now = float(self._clock())
        tokens, last = self._buckets.get(key, (self._capacity, now))
        tokens = min(self._capacity, tokens + max(0.0, now - last) * self._rate)
        if tokens >= 1.0:
            self._buckets[key] = (tokens - 1.0, now)
            return True
        self._buckets[key] = (tokens, now)
        return False

    def tokens(self, key: str) -> float:
        """当前余量观测（注入时钟结算，不扣减）。"""
        now = float(self._clock())
        tokens, last = self._buckets.get(key, (self._capacity, now))
        return min(self._capacity, tokens + max(0.0, now - last) * self._rate)


class FrontendApiProxy:
    """前端 API 代理（路由 + 鉴权 + 限流 + 转发 + 规范化）。

    Args:
        route_table: 路径前缀 → 上游名（最长前缀匹配）。
        token_validator: token 校验注入（token → principal；None/空串=未通过）。
        upstreams: 上游名 → client 注入（ProxyRequest → UpstreamResponse，不真发）。
        rate_limiter: 令牌桶限流器（可空=不限流）。
    """

    def __init__(
        self,
        *,
        route_table: Mapping[str, str],
        token_validator: Callable[[str], str | None],
        upstreams: Mapping[str, Callable[[ProxyRequest], UpstreamResponse]],
        rate_limiter: TokenBucket | None = None,
    ) -> None:
        if not route_table:
            raise FrontendProxyError("route_table 为空（无路由）")
        if not callable(token_validator):
            raise FrontendProxyError("token_validator 未注入（鉴权 Fail-Closed）")
        if not upstreams:
            raise FrontendProxyError("upstreams 为空（无上游 client）")
        for prefix, upstream in route_table.items():
            if not isinstance(prefix, str) or not prefix.startswith("/"):
                raise FrontendProxyError(f"路由前缀非法: {prefix!r}")
            if not isinstance(upstream, str) or not upstream:
                raise FrontendProxyError(f"上游名非法: {upstream!r}")
            if upstream not in upstreams:
                raise FrontendProxyError(f"路由目标上游未注册: {upstream!r}")
        for name, client in upstreams.items():
            if not callable(client):
                raise FrontendProxyError(f"上游 {name!r} client 不可调用")
        if rate_limiter is not None and not isinstance(rate_limiter, TokenBucket):
            raise FrontendProxyError("rate_limiter 类型非法")
        # 最长前缀优先；同长按字典序保证确定性
        self._routes = sorted(
            ((p.rstrip("/") or "/", u) for p, u in route_table.items()),
            key=lambda kv: (-len(kv[0]), kv[0]),
        )
        self._validator = token_validator
        self._upstreams = dict(upstreams)
        self._limiter = rate_limiter

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _match(self, path: str) -> str:
        for prefix, upstream in self._routes:
            if prefix == "/":
                return upstream
            if path == prefix or path.startswith(prefix + "/"):
                return upstream
        return ""

    @staticmethod
    def _error(request: ProxyRequest, status: int, reason: str, upstream: str) -> ProxyResponse:
        payload = {
            "ok": False,
            "code": status,
            "data": None,
            "error": reason,
            "upstream": upstream,
            "request_id": request.request_id,
            "principal": None,
        }
        return ProxyResponse(status_code=status, ok=False, upstream=upstream, payload=payload)

    # ── 代理主流程 ────────────────────────────────────────────────────────

    def handle(self, request: ProxyRequest) -> ProxyResponse:
        """路由 → 鉴权 → 限流 → 转发 → 规范化（非法输入 Fail-Closed）。"""
        if not isinstance(request, ProxyRequest):
            raise FrontendProxyError(f"请求类型非法: {request!r}")
        if request.method not in _METHODS:
            raise FrontendProxyError(f"非法方法: {request.method!r}（词表 GET|POST）")
        if not isinstance(request.path, str) or not request.path.startswith("/"):
            raise FrontendProxyError(f"非法路径: {request.path!r}")
        if not isinstance(request.token, str) or not request.token:
            raise FrontendProxyError("token 为空")
        upstream = self._match(request.path)
        if not upstream:
            return self._error(request, 404, "route_not_found", "")
        try:
            principal = self._validator(request.token)
        except Exception:  # noqa: BLE001 — 校验器异常按未通过处理
            _log.exception("token_validator 异常")
            return self._error(request, 401, "token_invalid", upstream)
        if not isinstance(principal, str) or not principal:
            return self._error(request, 401, "token_invalid", upstream)
        if self._limiter is not None and not self._limiter.allow(principal):
            _log.warning("限流拒绝: %s %s", principal, request.path)
            return self._error(request, 429, "rate_limited", upstream)
        try:
            response = self._upstreams[upstream](request)
        except Exception:  # noqa: BLE001 — 上游异常规范化 502 不抛
            _log.exception("上游转发异常: %s", upstream)
            return self._error(request, 502, "upstream_error", upstream)
        if (
            not isinstance(response, UpstreamResponse)
            or not isinstance(response.status_code, int)
            or isinstance(response.status_code, bool)
            or not 100 <= response.status_code <= 599
            or not isinstance(response.payload, Mapping)
        ):
            _log.warning("上游响应非法: %s -> %r", upstream, response)
            return self._error(request, 502, "upstream_bad_response", upstream)
        ok = 200 <= response.status_code < 300
        payload = {
            "ok": ok,
            "code": response.status_code,
            "data": dict(response.payload),
            "error": None,
            "upstream": upstream,
            "request_id": request.request_id,
            "principal": principal,
        }
        return ProxyResponse(status_code=response.status_code, ok=ok, upstream=upstream, payload=payload)
