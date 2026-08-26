# [BLUEPRINT] MOD-INT-OPENAPI | docs/03_modules/_domain_integration/api_documentation_generator/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-INT-OPENAPI | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.integration.test_api_documentation_generator
# [TESTS] src/zephyr/integration/api_documentation_generator.py
"""MOD-INT-OPENAPI 单元测试：api_documentation_generator API 文档生成器。

蓝图验收（B1-00337/CAND-BACL-004，C2 D-INT-05）：
路由注册表 → OpenAPI 3.0 生成（schema 推导，确定性排序）+ 基线 diff 契约
漂移告警（超阈值经注入 alert_sink 留痕）+ docs 输出语义（注入回调/内存留痕）。
writer/告警全注入内存替身，不触盘不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.integration.api_documentation_generator",
    reason="api_documentation_generator not importable",
)

from zephyr.integration.api_documentation_generator import (  # noqa: E402
    ApiDocError,
    ApiDocumentationGenerator,
    DriftReport,
    FieldSpec,
    RouteSpec,
)

_T0 = datetime.datetime(2026, 8, 27, 9, 30, 0)


def _gen(alerts: list | None = None, threshold: float = 0.2) -> ApiDocumentationGenerator:
    return ApiDocumentationGenerator(
        clock=lambda: _T0,
        alert_sink=(lambda r: alerts.append(r)) if alerts is not None else None,
        drift_threshold=threshold,
    )


def _route(
    operation_id: str = "get_position",
    method: str = "GET",
    path: str = "/api/v1/position",
) -> RouteSpec:
    return RouteSpec(
        method=method,
        path=path,
        operation_id=operation_id,
        summary="查询持仓",
        tags=("trading",),
        request_fields=(FieldSpec(name="account", type="string"),),
        response_fields=(
            FieldSpec(name="symbol", type="string"),
            FieldSpec(name="qty", type="integer"),
            FieldSpec(name="note", type="string", required=False),
        ),
    )


# ──────────────────────────────────────────────────────────────────────────────
# 路由注册（Fail-Closed）
# ──────────────────────────────────────────────────────────────────────────────


class TestRegisterRoute:
    def test_register_ok(self) -> None:
        gen = _gen()
        gen.register_route(_route())
        assert [r.operation_id for r in gen.routes()] == ["get_position"]

    def test_invalid_method_raises(self) -> None:
        gen = _gen()
        with pytest.raises(ApiDocError):
            gen.register_route(_route(method="TRACE"))

    def test_lowercase_method_raises(self) -> None:
        gen = _gen()
        with pytest.raises(ApiDocError):
            gen.register_route(_route(method="get"))

    def test_empty_path_raises(self) -> None:
        gen = _gen()
        with pytest.raises(ApiDocError):
            gen.register_route(_route(path=""))

    def test_path_without_slash_raises(self) -> None:
        gen = _gen()
        with pytest.raises(ApiDocError):
            gen.register_route(_route(path="api/v1/position"))

    def test_empty_operation_id_raises(self) -> None:
        gen = _gen()
        with pytest.raises(ApiDocError):
            gen.register_route(_route(operation_id=""))

    def test_duplicate_operation_id_raises(self) -> None:
        gen = _gen()
        gen.register_route(_route())
        with pytest.raises(ApiDocError):
            gen.register_route(_route(path="/api/v1/other"))

    def test_duplicate_method_path_raises(self) -> None:
        gen = _gen()
        gen.register_route(_route())
        with pytest.raises(ApiDocError):
            gen.register_route(_route(operation_id="another_op"))

    def test_invalid_field_type_raises(self) -> None:
        gen = _gen()
        with pytest.raises(ApiDocError):
            gen.register_route(RouteSpec(
                method="GET", path="/x", operation_id="op_x",
                response_fields=(FieldSpec(name="bad", type="tuple"),),
            ))

    def test_duplicate_field_name_raises(self) -> None:
        gen = _gen()
        with pytest.raises(ApiDocError):
            gen.register_route(RouteSpec(
                method="GET", path="/x", operation_id="op_x",
                response_fields=(
                    FieldSpec(name="a", type="string"),
                    FieldSpec(name="a", type="integer"),
                ),
            ))

    def test_empty_field_name_raises(self) -> None:
        gen = _gen()
        with pytest.raises(ApiDocError):
            gen.register_route(RouteSpec(
                method="GET", path="/x", operation_id="op_x",
                response_fields=(FieldSpec(name="", type="string"),),
            ))


# ──────────────────────────────────────────────────────────────────────────────
# 文档生成（schema 推导 + 确定性）
# ──────────────────────────────────────────────────────────────────────────────


class TestGenerate:
    def test_openapi_structure(self) -> None:
        gen = _gen()
        gen.register_route(_route())
        doc = gen.generate_openapi()
        assert doc["openapi"] == "3.0.3"
        op = doc["paths"]["/api/v1/position"]["get"]
        assert op["operationId"] == "get_position"
        assert op["summary"] == "查询持仓"
        assert op["tags"] == ["trading"]

    def test_schema_derivation(self) -> None:
        gen = _gen()
        gen.register_route(_route())
        doc = gen.generate_openapi()
        schema = doc["paths"]["/api/v1/position"]["get"]["responses"]["200"][
            "content"
        ]["application/json"]["schema"]
        assert schema["properties"] == {
            "note": {"type": "string"},
            "qty": {"type": "integer"},
            "symbol": {"type": "string"},
        }
        assert schema["required"] == ["qty", "symbol"]  # note 非必填

    def test_request_body_present_when_fields(self) -> None:
        gen = _gen()
        gen.register_route(_route())
        op = gen.generate_openapi()["paths"]["/api/v1/position"]["get"]
        req = op["requestBody"]["content"]["application/json"]["schema"]
        assert req["required"] == ["account"]

    def test_no_request_body_when_empty(self) -> None:
        gen = _gen()
        gen.register_route(RouteSpec(method="GET", path="/ping", operation_id="ping"))
        op = gen.generate_openapi()["paths"]["/ping"]["get"]
        assert "requestBody" not in op

    def test_deterministic_same_input_same_output(self) -> None:
        gen_a, gen_b = _gen(), _gen()
        gen_a.register_route(_route(path="/b", operation_id="op_b"))
        gen_a.register_route(_route(path="/a", operation_id="op_a"))
        gen_b.register_route(_route(path="/a", operation_id="op_a"))
        gen_b.register_route(_route(path="/b", operation_id="op_b"))
        assert gen_a.generate_yaml() == gen_b.generate_yaml()  # 注册序无关

    def test_yaml_render_sorted_keys(self) -> None:
        gen = _gen()
        gen.register_route(_route())
        text = gen.generate_yaml()
        assert text.startswith("info:\n")
        assert "openapi: 3.0.3\n" in text
        assert text.endswith("\n")

    def test_routes_sorted_by_path_method(self) -> None:
        gen = _gen()
        gen.register_route(_route(path="/z", operation_id="op_z"))
        gen.register_route(_route(path="/a", operation_id="op_a", method="POST"))
        gen.register_route(_route(path="/a", operation_id="op_a2", method="GET"))
        assert [(r.path, r.method) for r in gen.routes()] == [
            ("/a", "GET"), ("/a", "POST"), ("/z", "GET"),
        ]


# ──────────────────────────────────────────────────────────────────────────────
# docs 输出语义
# ──────────────────────────────────────────────────────────────────────────────


class TestPublishDocs:
    def test_publish_via_injected_writer(self) -> None:
        written: list[str] = []
        gen = ApiDocumentationGenerator(clock=lambda: _T0, docs_writer=written.append)
        gen.register_route(_route())
        content = gen.publish_docs()
        assert written == [content]

    def test_publish_default_memory_record(self) -> None:
        gen = _gen()
        gen.register_route(_route())
        content = gen.publish_docs()
        assert gen.published == (content,)


# ──────────────────────────────────────────────────────────────────────────────
# 契约漂移校验
# ──────────────────────────────────────────────────────────────────────────────


class TestDrift:
    def test_no_drift_no_alert(self) -> None:
        alerts: list[DriftReport] = []
        gen = _gen(alerts)
        gen.register_route(_route())
        report = gen.diff_against_baseline(gen.generate_openapi())
        assert report.exceeded is False
        assert report.diff_ratio == 0.0
        assert alerts == []
        assert report.generated_at == _T0

    def test_added_route_drift_alert(self) -> None:
        alerts: list[DriftReport] = []
        gen = _gen(alerts, threshold=0.4)
        gen.register_route(_route())
        baseline = gen.generate_openapi()
        gen.register_route(_route(path="/new", operation_id="op_new"))
        report = gen.diff_against_baseline(baseline)
        assert report.added == ("GET /new",)
        assert report.diff_ratio == pytest.approx(0.5)  # 1 变更 / 2 并集
        assert report.exceeded is True  # 0.5 > 0.4
        assert len(alerts) == 1

    def test_boundary_ratio_not_exceeded(self) -> None:
        alerts: list[DriftReport] = []
        gen = _gen(alerts, threshold=0.5)
        gen.register_route(_route())
        baseline = gen.generate_openapi()
        gen.register_route(_route(path="/new", operation_id="op_new"))
        report = gen.diff_against_baseline(baseline)
        assert report.diff_ratio == pytest.approx(0.5)
        assert report.exceeded is False  # 严格大于才告警
        assert alerts == []

    def test_removed_route_drift_alert(self) -> None:
        alerts: list[DriftReport] = []
        gen = _gen(alerts, threshold=0.2)
        gen.register_route(_route())
        gen.register_route(_route(path="/b", operation_id="op_b"))
        baseline = gen.generate_openapi()
        gen2 = _gen(alerts, threshold=0.2)
        gen2.register_route(_route())
        report = gen2.diff_against_baseline(baseline)
        assert report.removed == ("GET /b",)
        assert report.exceeded is True
        assert len(alerts) == 1
        assert alerts[0] is report

    def test_changed_schema_drift(self) -> None:
        alerts: list[DriftReport] = []
        gen = _gen(alerts, threshold=0.1)
        gen.register_route(_route())
        baseline = gen.generate_openapi()
        gen2 = _gen(alerts, threshold=0.1)
        gen2.register_route(RouteSpec(
            method="GET", path="/api/v1/position", operation_id="get_position",
            response_fields=(FieldSpec(name="symbol", type="string"),),
        ))
        report = gen2.diff_against_baseline(baseline)
        assert report.changed == ("GET /api/v1/position",)
        assert report.exceeded is True
        assert len(alerts) == 1

    def test_invalid_baseline_raises(self) -> None:
        gen = _gen()
        gen.register_route(_route())
        with pytest.raises(ApiDocError):
            gen.diff_against_baseline({})
        with pytest.raises(ApiDocError):
            gen.diff_against_baseline("not-a-mapping")

    def test_alert_sink_exception_not_blocking(self) -> None:
        def _bad_sink(_: DriftReport) -> None:
            raise RuntimeError("boom")

        gen = ApiDocumentationGenerator(
            clock=lambda: _T0, alert_sink=_bad_sink, drift_threshold=0.1,
        )
        gen.register_route(_route())
        report = gen.diff_against_baseline({"paths": {}})
        assert report.exceeded is True  # 告警异常不阻断报告返回

    def test_invalid_threshold_raises(self) -> None:
        with pytest.raises(ApiDocError):
            ApiDocumentationGenerator(drift_threshold=0.0)
        with pytest.raises(ApiDocError):
            ApiDocumentationGenerator(drift_threshold=1.5)
