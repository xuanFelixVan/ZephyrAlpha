# [BLUEPRINT] MOD-FE-011 | docs/03_modules/_domain_frontend/frontend_api_proxy/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-FE-011 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.frontend.test_frontend_api_proxy
# [TESTS] src/zephyr/frontend/frontend_api_proxy.py
"""MOD-FE-011 单元测试：frontend_api_proxy 前端 API 代理。

蓝图验收（B9-10703/CAND-FE-012，B9 D-FRONTEND-22）：请求路由表（前缀→
上游，最长前缀匹配）+ token 鉴权注入 + 令牌桶限流（注入时钟，按 principal
分桶）+ upstream client 注入不真发 + 响应规范化（不落 token）。
校验器/上游/时钟全内存替身，不触网。
"""

from __future__ import annotations

import pytest

pytest.importorskip(
    "zephyr.frontend.frontend_api_proxy",
    reason="frontend_api_proxy not importable",
)

from zephyr.frontend.frontend_api_proxy import (  # noqa: E402
    FrontendApiProxy,
    FrontendProxyError,
    ProxyRequest,
    TokenBucket,
    UpstreamResponse,
)


class _Clock:
    """可推进内存时钟（秒）。"""

    def __init__(self, t: float = 0.0) -> None:
        self.t = t

    def __call__(self) -> float:
        return self.t

    def advance(self, seconds: float) -> None:
        self.t += seconds


def _proxy(
    routes: dict | None = None,
    upstreams: dict | None = None,
    validator=None,
    limiter: TokenBucket | None = None,
) -> FrontendApiProxy:
    return FrontendApiProxy(
        route_table=routes or {"/api/risk": "risk", "/api": "core"},
        token_validator=validator or (lambda token: {"tok-ok": "alice"}.get(token)),
        upstreams=upstreams or {
            "risk": lambda req: UpstreamResponse(200, {"domain": "risk"}),
            "core": lambda req: UpstreamResponse(200, {"domain": "core"}),
        },
        rate_limiter=limiter,
    )


def _request(path: str = "/api/risk/limits", token: str = "tok-ok", method: str = "GET") -> ProxyRequest:
    return ProxyRequest(method=method, path=path, token=token, request_id="req-1")


# ──────────────────────────────────────────────────────────────────────────────
# 构造配置（Fail-Closed）
# ──────────────────────────────────────────────────────────────────────────────


class TestConfig:
    def test_empty_route_table_raises(self) -> None:
        with pytest.raises(FrontendProxyError):
            FrontendApiProxy(
                route_table={},
                token_validator=lambda t: "alice",
                upstreams={"core": lambda req: UpstreamResponse(200, {})},
            )

    def test_prefix_without_slash_raises(self) -> None:
        with pytest.raises(FrontendProxyError):
            _proxy(routes={"api": "core"})

    def test_route_target_unregistered_raises(self) -> None:
        with pytest.raises(FrontendProxyError):
            FrontendApiProxy(
                route_table={"/api": "ghost"},
                token_validator=lambda t: "alice",
                upstreams={"core": lambda req: UpstreamResponse(200, {})},
            )

    def test_missing_validator_raises(self) -> None:
        with pytest.raises(FrontendProxyError):
            FrontendApiProxy(
                route_table={"/api": "core"},
                token_validator=None,
                upstreams={"core": lambda req: UpstreamResponse(200, {})},
            )


# ──────────────────────────────────────────────────────────────────────────────
# 令牌桶限流
# ──────────────────────────────────────────────────────────────────────────────


class TestTokenBucket:
    def test_allow_within_capacity(self) -> None:
        bucket = TokenBucket(capacity=2, refill_per_second=1.0, clock=_Clock())
        assert bucket.allow("alice") is True
        assert bucket.allow("alice") is True

    def test_exhaust_denies(self) -> None:
        bucket = TokenBucket(capacity=1, refill_per_second=0.5, clock=_Clock())
        assert bucket.allow("alice") is True
        assert bucket.allow("alice") is False

    def test_refill_over_injected_time(self) -> None:
        clock = _Clock()
        bucket = TokenBucket(capacity=1, refill_per_second=1.0, clock=clock)
        assert bucket.allow("alice") is True
        assert bucket.allow("alice") is False
        clock.advance(1.0)
        assert bucket.allow("alice") is True

    def test_per_key_isolation(self) -> None:
        bucket = TokenBucket(capacity=1, refill_per_second=0.1, clock=_Clock())
        assert bucket.allow("alice") is True
        assert bucket.allow("bob") is True
        assert bucket.allow("alice") is False

    def test_invalid_capacity_raises(self) -> None:
        with pytest.raises(FrontendProxyError):
            TokenBucket(capacity=0, refill_per_second=1.0, clock=_Clock())


# ──────────────────────────────────────────────────────────────────────────────
# 代理主流程
# ──────────────────────────────────────────────────────────────────────────────


class TestHandle:
    def test_ok_normalized_payload(self) -> None:
        resp = _proxy().handle(_request())
        assert resp.status_code == 200
        assert resp.ok is True
        assert resp.upstream == "risk"
        assert resp.payload == {
            "ok": True,
            "code": 200,
            "data": {"domain": "risk"},
            "error": None,
            "upstream": "risk",
            "request_id": "req-1",
            "principal": "alice",
        }
        assert "tok-ok" not in str(resp.payload)  # 不落 token

    def test_longest_prefix_match(self) -> None:
        assert _proxy().handle(_request("/api/risk/limits")).upstream == "risk"
        assert _proxy().handle(_request("/api/other")).upstream == "core"

    def test_unknown_route_404(self) -> None:
        resp = _proxy().handle(_request("/nope"))
        assert resp.status_code == 404
        assert resp.ok is False
        assert resp.payload["error"] == "route_not_found"

    def test_invalid_method_raises(self) -> None:
        with pytest.raises(FrontendProxyError):
            _proxy().handle(_request(method="DELETE"))

    def test_invalid_path_raises(self) -> None:
        with pytest.raises(FrontendProxyError):
            _proxy().handle(_request(path="api/risk"))

    def test_empty_token_raises(self) -> None:
        with pytest.raises(FrontendProxyError):
            _proxy().handle(_request(token=""))

    def test_invalid_token_401(self) -> None:
        resp = _proxy().handle(_request(token="bad"))
        assert resp.status_code == 401
        assert resp.payload["error"] == "token_invalid"
        assert resp.payload["principal"] is None

    def test_rate_limited_429(self) -> None:
        clock = _Clock()
        limiter = TokenBucket(capacity=1, refill_per_second=0.01, clock=clock)
        proxy = _proxy(limiter=limiter)
        assert proxy.handle(_request()).status_code == 200
        resp = proxy.handle(_request())
        assert resp.status_code == 429
        assert resp.payload["error"] == "rate_limited"

    def test_upstream_exception_502(self) -> None:
        def _boom(req):
            raise RuntimeError("upstream down")

        proxy = _proxy(upstreams={"risk": _boom, "core": lambda req: UpstreamResponse(200, {})})
        resp = proxy.handle(_request())
        assert resp.status_code == 502
        assert resp.payload["error"] == "upstream_error"

    def test_upstream_non_2xx_passthrough(self) -> None:
        proxy = _proxy(upstreams={
            "risk": lambda req: UpstreamResponse(422, {"msg": "参数非法"}),
            "core": lambda req: UpstreamResponse(200, {}),
        })
        resp = proxy.handle(_request())
        assert resp.status_code == 422
        assert resp.ok is False
        assert resp.payload["data"] == {"msg": "参数非法"}

    def test_malformed_upstream_response_502(self) -> None:
        proxy = _proxy(upstreams={"risk": lambda req: {"status": 200}, "core": lambda req: UpstreamResponse(200, {})})
        resp = proxy.handle(_request())
        assert resp.status_code == 502
        assert resp.payload["error"] == "upstream_bad_response"


# ──────────────────────────────────────────────────────────────────────────────
# 确定性
# ──────────────────────────────────────────────────────────────────────────────


class TestDeterminism:
    def test_same_request_same_response(self) -> None:
        proxy = _proxy()
        r1 = proxy.handle(_request())
        r2 = proxy.handle(_request())
        assert r1 == r2
