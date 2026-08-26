# [BLUEPRINT] MOD-INT-APIGW | docs/03_modules/_domain_integration/api_gateway/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-INT-APIGW | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.integration.test_api_gateway
# [TESTS] src/zephyr/integration/api_gateway.py
"""MOD-INT-APIGW 单元测试：api_gateway 单进程轻量 API 网关。

蓝图验收（B1-00322/CAND-INTEGRAT-001，C2 D-INT-01）：
请求路由表 + token 认证注入（未注入对受保护路由 Fail-Closed）+ 限流/熔断
注入挂接（429/503 短路）+ 脱敏过滤器（敏感字段递归脱敏）+ 访问审计回调
（每次 handle 必产记录）。认证器/限流器/熔断器/审计全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.integration.api_gateway",
    reason="api_gateway not importable",
)

from zephyr.integration.api_gateway import (  # noqa: E402
    AccessAudit,
    ApiGateway,
    ApiGatewayError,
    GatewayRequest,
)

_T0 = datetime.datetime(2026, 8, 27, 9, 30, 0)


def _gateway(
    audits: list | None = None,
    *,
    authenticator="default",
    limiter=None,
    breaker=None,
) -> ApiGateway:
    return ApiGateway(
        clock=lambda: _T0,
        authenticator=(
            (lambda token, req: token == "valid-token")
            if authenticator == "default"
            else authenticator
        ),
        limiter=limiter,
        breaker=breaker,
        audit_sink=(lambda r: audits.append(r)) if audits is not None else None,
    )


def _request(
    path: str = "/api/v1/position",
    method: str = "GET",
    token: str = "valid-token",
    request_id: str = "req-1",
) -> GatewayRequest:
    return GatewayRequest(
        request_id=request_id,
        method=method,
        path=path,
        token=token,
        client_id="client-a",
        payload={"account": "main"},
        received_at=_T0,
    )


def _seed(gw: ApiGateway, **handler_kwargs) -> None:
    gw.register_route(
        "GET",
        "/api/v1/position",
        lambda payload: {"symbol": "600519", "api_key": "leak-me", "qty": 100},
        **handler_kwargs,
    )


# ──────────────────────────────────────────────────────────────────────────────
# 路由表
# ──────────────────────────────────────────────────────────────────────────────


class TestRouteTable:
    def test_register_and_list_sorted(self) -> None:
        gw = _gateway()
        gw.register_route("POST", "/b", lambda p: {})
        gw.register_route("GET", "/a", lambda p: {})
        assert gw.routes() == (("GET", "/a"), ("POST", "/b"))

    def test_invalid_method_raises(self) -> None:
        gw = _gateway()
        with pytest.raises(ApiGatewayError):
            gw.register_route("get", "/a", lambda p: {})

    def test_invalid_path_raises(self) -> None:
        gw = _gateway()
        with pytest.raises(ApiGatewayError):
            gw.register_route("GET", "", lambda p: {})
        with pytest.raises(ApiGatewayError):
            gw.register_route("GET", "no-slash", lambda p: {})

    def test_non_callable_handler_raises(self) -> None:
        gw = _gateway()
        with pytest.raises(ApiGatewayError):
            gw.register_route("GET", "/a", "not-callable")

    def test_duplicate_route_raises(self) -> None:
        gw = _gateway()
        gw.register_route("GET", "/a", lambda p: {})
        with pytest.raises(ApiGatewayError):
            gw.register_route("GET", "/a", lambda p: {})

    def test_same_path_different_method_ok(self) -> None:
        gw = _gateway()
        gw.register_route("GET", "/a", lambda p: {})
        gw.register_route("POST", "/a", lambda p: {})
        assert len(gw.routes()) == 2


# ──────────────────────────────────────────────────────────────────────────────
# handle 流水线
# ──────────────────────────────────────────────────────────────────────────────


class TestHandle:
    def test_ok_with_mask_and_audit(self) -> None:
        audits: list[AccessAudit] = []
        gw = _gateway(audits)
        _seed(gw)
        resp = gw.handle(_request())
        assert resp.status_code == 200
        assert resp.body["api_key"] == "***"  # 脱敏
        assert resp.body["symbol"] == "600519"
        assert resp.masked_fields == ("api_key",)
        assert len(audits) == 1
        assert audits[0].status_code == 200
        assert audits[0].reason == "ok"
        assert audits[0].audited_at == _T0
        assert audits[0].client_id == "client-a"

    def test_route_not_found_404(self) -> None:
        audits: list[AccessAudit] = []
        gw = _gateway(audits)
        resp = gw.handle(_request(path="/ghost"))
        assert resp.status_code == 404
        assert resp.body == {"error": "route_not_found"}
        assert audits[0].reason == "route_not_found"

    def test_unauthorized_401(self) -> None:
        audits: list[AccessAudit] = []
        gw = _gateway(audits)
        _seed(gw)
        resp = gw.handle(_request(token="bad-token"))
        assert resp.status_code == 401
        assert audits[0].reason == "unauthorized"
        resp2 = gw.handle(_request(token=""))
        assert resp2.status_code == 401

    def test_authenticator_missing_fail_closed(self) -> None:
        gw = _gateway(authenticator=None)
        _seed(gw)
        resp = gw.handle(_request())
        assert resp.status_code == 503
        assert resp.body == {"error": "authenticator_missing"}

    def test_public_route_no_authenticator_ok(self) -> None:
        gw = _gateway(authenticator=None)
        _seed(gw, auth_required=False)
        resp = gw.handle(_request(token=""))
        assert resp.status_code == 200

    def test_rate_limited_429(self) -> None:
        audits: list[AccessAudit] = []
        gw = _gateway(audits, limiter=lambda client, path: False)
        _seed(gw)
        resp = gw.handle(_request())
        assert resp.status_code == 429
        assert audits[0].reason == "rate_limited"

    def test_circuit_open_503(self) -> None:
        audits: list[AccessAudit] = []
        gw = _gateway(audits, breaker=lambda path: False)
        _seed(gw)
        resp = gw.handle(_request())
        assert resp.status_code == 503
        assert audits[0].reason == "circuit_open"

    def test_limiter_before_breaker(self) -> None:
        calls: list[str] = []
        gw = _gateway(
            limiter=lambda c, p: calls.append("limiter") or False,
            breaker=lambda p: calls.append("breaker") or False,
        )
        _seed(gw)
        resp = gw.handle(_request())
        assert resp.status_code == 429
        assert calls == ["limiter"]  # 限流短路，熔断未评估

    def test_handler_exception_500_no_leak(self) -> None:
        audits: list[AccessAudit] = []
        gw = _gateway(audits)
        gw.register_route(
            "GET", "/boom", lambda p: (_ for _ in ()).throw(ValueError("内部细节"))
        )
        resp = gw.handle(_request(path="/boom"))
        assert resp.status_code == 500
        assert resp.body == {"error": "handler_error"}  # 不泄漏内部异常
        assert audits[0].reason == "handler_error"

    def test_handler_non_mapping_raises(self) -> None:
        gw = _gateway()
        gw.register_route("GET", "/bad", lambda p: ["not", "mapping"])
        with pytest.raises(ApiGatewayError):
            gw.handle(_request(path="/bad"))

    def test_injected_callback_exception_fail_closed(self) -> None:
        def _bad_auth(token: str, req: GatewayRequest) -> bool:
            raise RuntimeError("auth boom")

        gw = _gateway(authenticator=_bad_auth)
        _seed(gw)
        assert gw.handle(_request()).status_code == 401  # 认证器异常按拒绝

    def test_invalid_request_raises(self) -> None:
        gw = _gateway()
        _seed(gw)
        with pytest.raises(ApiGatewayError):
            gw.handle(_request(request_id=""))
        with pytest.raises(ApiGatewayError):
            gw.handle(_request(path="no-slash"))
        with pytest.raises(ApiGatewayError):
            gw.handle(_request(method="TRACE"))

    def test_audit_sink_exception_not_blocking(self) -> None:
        def _bad_sink(_: AccessAudit) -> None:
            raise RuntimeError("boom")

        gw = ApiGateway(
            clock=lambda: _T0,
            authenticator=lambda token, req: True,
            audit_sink=_bad_sink,
        )
        _seed(gw)
        assert gw.handle(_request()).status_code == 200  # 审计异常不阻断

    def test_default_audit_memory_record(self) -> None:
        gw = ApiGateway(clock=lambda: _T0, authenticator=lambda t, r: True)
        _seed(gw)
        gw.handle(_request())
        assert len(gw.audits) == 1
        assert gw.audits[0].status_code == 200


# ──────────────────────────────────────────────────────────────────────────────
# 脱敏过滤器
# ──────────────────────────────────────────────────────────────────────────────


class TestMask:
    def test_mask_nested_and_list(self) -> None:
        gw = _gateway()
        body = {
            "user": {"name": "z", "password": "p"},
            "sessions": [{"token": "t1"}, {"token": "t2"}],
            "note": "ok",
        }
        masked, hits = gw.mask(body)
        assert masked["user"]["password"] == "***"
        assert masked["sessions"][0]["token"] == "***"
        assert masked["sessions"][1]["token"] == "***"
        assert masked["note"] == "ok"
        assert "user.password" in hits
        assert len(hits) == 3

    def test_mask_case_insensitive(self) -> None:
        gw = _gateway()
        masked, _ = gw.mask({"Authorization": "Bearer x", "APIKEY": "k"})
        assert masked["Authorization"] == "***"
        assert masked["APIKEY"] == "***"

    def test_mask_custom_sensitive_fields(self) -> None:
        gw = ApiGateway(clock=lambda: _T0, sensitive_fields=("id_card",))
        masked, hits = gw.mask({"id_card": "110", "token": "keep"})
        assert masked["id_card"] == "***"
        assert masked["token"] == "keep"  # 自定义词表替代缺省
        assert hits == ("id_card",)

    def test_mask_does_not_mutate_original(self) -> None:
        gw = _gateway()
        original = {"token": "t", "nested": {"secret": "s"}}
        gw.mask(original)
        assert original["token"] == "t"
        assert original["nested"]["secret"] == "s"
