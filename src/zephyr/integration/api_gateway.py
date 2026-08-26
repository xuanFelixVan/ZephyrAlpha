# [BLUEPRINT] MOD-INT-APIGW | docs/03_modules/_domain_integration/api_gateway/blueprint.md
# [MODULE] zephyr.integration.api_gateway
# [DOMAIN] D_INTEGRATION_GATEWAY
# [DEPENDENCIES] 无（协议核心纯内存；authenticator/limiter/breaker/audit_sink/clock 全注入）
# [CONSUMERS] 运行时装配批（请求路由表装配 / token认证注入 / 限流熔断挂接 / 脱敏过滤 / 访问审计回调）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 路由方法词表闭合(GET|POST|PUT|DELETE|PATCH); (方法,路径) 路由唯一; 流水线固定序 路由→限流→熔断→认证→handler→脱敏→审计; 认证器未注入对受保护路由 Fail-Closed(503); handler 异常不泄漏内部细节(500); 敏感字段递归脱敏; 每次 handle 必产审计记录; 同输入必同输出; 严禁 Kong/Envoy 等外部网关依赖
# [MODIFY-GUARD] docs/03_modules/_domain_integration/api_gateway/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ApiGatewayError(占位 ZA-INT-UNREGISTERED-API-GATEWAY)——非法方法/空路径/路由重复/非法handler/空request_id/空路径请求时抛
# [TESTS] tests/integration/test_api_gateway.py
# [A_module] module_id=MOD-INT-APIGW | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""ApiGateway — 单进程轻量 API 网关（MOD-INT-APIGW）。

B1-00322（AUD-DRAFT-001-DIGEST P2 波 P2-W13，CAND-INTEGRAT-001，C2 D-INT-01）：
单进程轻量网关——请求**路由表** + **token 认证**（注入 authenticator）+
**限流/熔断挂接**（注入 limiter/breaker）+ **脱敏过滤器**（敏感字段规则，
递归脱敏）+ **访问审计回调**（每次 handle 必产审计记录）。AI Gateway 面
复用 llm_gateway 语义；严禁 Kong/Envoy 等外部网关依赖（纯内存协议件）。

查重分工：mcp/gateway_server.py=MCP 协议网关（本件=进程内 HTTP 语义网关，
不起服务不监听端口）；llm_runtime_gateway=LLM 调用门禁（本件复用其"注入
式前置检查"语义，面向通用 API 路由，零交集）。
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from typing import Callable, Final, Mapping

_log = logging.getLogger(__name__)

__all__: Final = [
    "AccessAudit",
    "ApiGateway",
    "ApiGatewayError",
    "GatewayRequest",
    "GatewayResponse",
]

#: HTTP 方法词表（闭合）
_HTTP_METHODS: Final[frozenset[str]] = frozenset(
    {"GET", "POST", "PUT", "DELETE", "PATCH"}
)

#: 缺省敏感字段词表（小写匹配，递归脱敏）
_DEFAULT_SENSITIVE_FIELDS: Final[frozenset[str]] = frozenset(
    {"password", "token", "secret", "api_key", "apikey", "authorization"}
)

_MASK: Final = "***"


class ApiGatewayError(Exception):
    """API 网关输入/配置非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-INT-UNREGISTERED-API-GATEWAY。
    """


@dataclass(frozen=True)
class GatewayRequest:
    """入站请求（frozen）。"""

    request_id: str
    method: str
    path: str
    token: str
    client_id: str
    payload: Mapping | None
    received_at: datetime.datetime


@dataclass(frozen=True)
class GatewayResponse:
    """出站响应（脱敏后载体，frozen）。"""

    request_id: str
    status_code: int
    body: Mapping
    masked_fields: tuple[str, ...]


@dataclass(frozen=True)
class AccessAudit:
    """访问审计记录（审计回调载荷，frozen）。"""

    request_id: str
    client_id: str
    method: str
    path: str
    status_code: int
    reason: str
    audited_at: datetime.datetime


class ApiGateway:
    """单进程轻量 API 网关（路由 + 认证/限流/熔断注入 + 脱敏 + 审计）。

    handle 流水线固定序：路由 → 限流 → 熔断 → 认证 → handler → 脱敏 → 审计。
    任一前置拒绝短路返回对应状态码（404/429/503/401/500），handler 异常
    不泄漏内部细节；每次 handle 必产 AccessAudit 经 audit_sink 回调留痕。
    """

    def __init__(
        self,
        *,
        clock: Callable[[], datetime.datetime] | None = None,
        authenticator: Callable[[str, GatewayRequest], bool] | None = None,
        limiter: Callable[[str, str], bool] | None = None,
        breaker: Callable[[str], bool] | None = None,
        audit_sink: Callable[[AccessAudit], None] | None = None,
        sensitive_fields: frozenset[str] | tuple[str, ...] | None = None,
    ) -> None:
        self._clock = clock or datetime.datetime.now
        self._authenticator = authenticator
        self._limiter = limiter
        self._breaker = breaker
        self._audit_sink = audit_sink
        self._sensitive = (
            frozenset(f.lower() for f in sensitive_fields)
            if sensitive_fields is not None
            else _DEFAULT_SENSITIVE_FIELDS
        )
        # (method, path) -> (handler, auth_required)
        self._routes: dict[tuple[str, str], tuple[Callable[[Mapping], Mapping], bool]] = {}
        self._audits: list[AccessAudit] = []  # audit_sink 缺省时内存留痕

    # ── 路由表 ────────────────────────────────────────────────────────────

    def register_route(
        self,
        method: str,
        path: str,
        handler: Callable[[Mapping], Mapping],
        *,
        auth_required: bool = True,
    ) -> None:
        """登记路由：方法/路径/handler 校验，(方法,路径) 唯一（Fail-Closed）。"""
        if method not in _HTTP_METHODS:
            raise ApiGatewayError(f"非法 HTTP 方法: {method!r}")
        if not path or not path.startswith("/"):
            raise ApiGatewayError(f"非法路径: {path!r}（须以 / 开头）")
        if not callable(handler):
            raise ApiGatewayError("handler 不可调用")
        key = (method, path)
        if key in self._routes:
            raise ApiGatewayError(f"路由重复: {method} {path}")
        self._routes[key] = (handler, bool(auth_required))

    def routes(self) -> tuple[tuple[str, str], ...]:
        """路由表视图（按 (path, method) 确定性排序）。"""
        return tuple(sorted(self._routes, key=lambda k: (k[1], k[0])))

    # ── 请求处理 ──────────────────────────────────────────────────────────

    def handle(self, request: GatewayRequest) -> GatewayResponse:
        """处理请求：固定序流水线，每次必产审计记录。"""
        if not request.request_id:
            raise ApiGatewayError("request_id 为空")
        if not request.path or not request.path.startswith("/"):
            raise ApiGatewayError(f"非法请求路径: {request.path!r}")
        if request.method not in _HTTP_METHODS:
            raise ApiGatewayError(f"非法请求方法: {request.method!r}")

        entry = self._routes.get((request.method, request.path))
        if entry is None:
            return self._reject(request, 404, "route_not_found")

        # 限流（注入；未注入不限流）
        if self._limiter is not None and not self._safe_bool(
            self._limiter, request.client_id, request.path
        ):
            return self._reject(request, 429, "rate_limited")

        # 熔断（注入；未注入不熔断）
        if self._breaker is not None and not self._safe_bool(self._breaker, request.path):
            return self._reject(request, 503, "circuit_open")

        handler, auth_required = entry
        if auth_required:
            if self._authenticator is None:
                # token 认证强制注入：受保护路由无认证器 Fail-Closed
                return self._reject(request, 503, "authenticator_missing")
            if not request.token or not self._safe_bool(
                self._authenticator, request.token, request
            ):
                return self._reject(request, 401, "unauthorized")

        try:
            body = handler(request.payload or {})
            if not isinstance(body, Mapping):
                raise ApiGatewayError(
                    f"handler 返回非 Mapping: {type(body).__name__}"
                )
        except ApiGatewayError:
            raise  # 结构性违约向外抛（Fail-Closed）
        except Exception:  # noqa: BLE001 — 内部异常不泄漏细节
            _log.exception("handler 异常: %s %s", request.method, request.path)
            return self._reject(request, 500, "handler_error")

        masked_body, masked_fields = self.mask(body)
        response = GatewayResponse(
            request_id=request.request_id,
            status_code=200,
            body=masked_body,
            masked_fields=masked_fields,
        )
        self._audit(request, 200, "ok")
        return response

    # ── 脱敏过滤器 ────────────────────────────────────────────────────────

    def mask(self, payload: Mapping) -> tuple[dict, tuple[str, ...]]:
        """递归脱敏：命中敏感字段词表的值替换为 ***（不触发原 Mapping）。"""
        masked, hits = self._mask_node(payload, ())
        return masked, tuple(sorted(hits))

    def _mask_node(
        self, node: object, path: tuple[str, ...]
    ) -> tuple[object, set[str]]:
        hits: set[str] = set()
        if isinstance(node, Mapping):
            out: dict = {}
            for key in sorted(node, key=str):
                value = node[key]
                if str(key).lower() in self._sensitive:
                    out[key] = _MASK
                    hits.add(".".join(path + (str(key),)))
                else:
                    out[key], sub = self._mask_node(value, path + (str(key),))
                    hits |= sub
            return out, hits
        if isinstance(node, (list, tuple)):
            items = []
            for idx, item in enumerate(node):
                masked_item, sub = self._mask_node(item, path + (str(idx),))
                items.append(masked_item)
                hits |= sub
            return (items if isinstance(node, list) else tuple(items)), hits
        return node, hits

    # ── 内部 ─────────────────────────────────────────────────────────────

    @staticmethod
    def _safe_bool(fn: Callable, *args: object) -> bool:
        """注入回调异常按拒绝处理不抛（Fail-Closed）。"""
        try:
            return bool(fn(*args))
        except Exception:  # noqa: BLE001
            _log.exception("注入回调异常（按拒绝处理）: %s", getattr(fn, "__name__", fn))
            return False

    def _reject(self, request: GatewayRequest, status: int, reason: str) -> GatewayResponse:
        self._audit(request, status, reason)
        return GatewayResponse(
            request_id=request.request_id,
            status_code=status,
            body={"error": reason},
            masked_fields=(),
        )

    def _audit(self, request: GatewayRequest, status: int, reason: str) -> None:
        record = AccessAudit(
            request_id=request.request_id,
            client_id=request.client_id,
            method=request.method,
            path=request.path,
            status_code=status,
            reason=reason,
            audited_at=self._clock(),
        )
        if self._audit_sink is not None:
            try:
                self._audit_sink(record)
            except Exception:  # noqa: BLE001 — 审计不阻断响应
                _log.exception("audit_sink 审计失败")
        else:
            self._audits.append(record)

    @property
    def audits(self) -> tuple[AccessAudit, ...]:
        """audit_sink 缺省时的内存审计留痕视图。"""
        return tuple(self._audits)
