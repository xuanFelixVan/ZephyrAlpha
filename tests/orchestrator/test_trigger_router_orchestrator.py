# [A_test] module_id: SRC-TST-1921 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-540 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.orchestrator.test_trigger_router
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
T-V2-007 单元测试 — TriggerRouter (RI-03)
==========================================
覆盖场景（验收标准 #7 ≥ 80%）：
  - load_router_config：YAML 解析正常 / 文件缺失 / 顶层键缺失 / 字段非法
  - TriggerHandlerSpec：必填字段 / extra=forbid / frozen
  - RouterDispatchResult：契约字段
  - dispatch 5 种 trigger_type 全成功（onboarding / drift_detected / compression_needed
    / cleanup_due / blueprint_published）
  - dispatch 未注册 trigger_type → skipped + audit log
  - dispatch disabled trigger → skipped + audit log
  - dispatch handler import 失败 → skipped + audit log（不抛异常）
  - dispatch handler 抛异常 → success=False + 异常被收敛
  - 注入 handlers 优先级覆盖 YAML
  - 单例 get_trigger_router / reset_trigger_router
  - 默认 stub 处理器签名正确 + 返回 dict
  - 审计日志通过 duck-typed audit_logger 注入
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from zephyr.orchestrator.execution.trigger_router import (
    DEFAULT_ROUTER_YAML_PATH,
    PHASE1D_TRIGGER_TYPES,
    RouterDispatchResult,
    TriggerHandlerSpec,
    TriggerRouter,
    TriggerRouterConfigError,
    TriggerSafety,
    get_trigger_router,
    handle_blueprint_stub,
    handle_cleanup_stub,
    handle_drift_detected,
    handle_onboarding_stub,
    load_router_config,
    reset_trigger_router,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def reset_singleton():
    reset_trigger_router()
    yield
    reset_trigger_router()


@pytest.fixture
def good_yaml(tmp_path: Path) -> Path:
    yaml_path = tmp_path / "trigger_router.yaml"
    yaml_path.write_text(
        textwrap.dedent(
            """\
            version: "1.0.0"
            triggers:
              onboarding:
                handler: "zephyr.trading.orchestrator.trigger_router.handle_onboarding_stub"
                description: "test onboarding"
                safety: "M"
                enabled: true
              drift_detected:
                handler: "zephyr.trading.orchestrator.trigger_router.handle_drift_detected"
                description: "test drift"
                safety: "H"
                enabled: true
              cleanup_due:
                handler: "zephyr.trading.orchestrator.trigger_router.handle_cleanup_stub"
                description: "test cleanup"
                safety: "L"
                enabled: true
              blueprint_published:
                handler: "zephyr.trading.orchestrator.trigger_router.handle_blueprint_stub"
                description: "test blueprint"
                safety: "M"
                enabled: true
              disabled_one:
                handler: "zephyr.trading.orchestrator.trigger_router.handle_cleanup_stub"
                description: "disabled trigger"
                safety: "L"
                enabled: false
              broken_handler:
                handler: "zephyr.trading.orchestrator.nonexistent.module.func"
                description: "import will fail"
                safety: "L"
                enabled: true
            """
        ),
        encoding="utf-8",
        newline="\n",
    )
    return yaml_path


# ---------------------------------------------------------------------------
# 1. TriggerHandlerSpec 数据模型
# ---------------------------------------------------------------------------


class TestTriggerHandlerSpec:
    def test_full_construction(self):
        spec = TriggerHandlerSpec(
            handler="pkg.mod.func",
            description="desc",
            safety=TriggerSafety.H,
            enabled=True,
        )
        assert spec.handler == "pkg.mod.func"
        assert spec.safety == TriggerSafety.H

    def test_defaults(self):
        spec = TriggerHandlerSpec(handler="pkg.mod.func")
        assert spec.safety == TriggerSafety.M
        assert spec.enabled is True
        assert spec.description == ""

    def test_handler_required(self):
        with pytest.raises(Exception):
            TriggerHandlerSpec(handler="")

    def test_extra_field_forbidden(self):
        with pytest.raises(Exception):
            TriggerHandlerSpec(
                handler="pkg.mod.func",
                unknown_field="x",  # type: ignore[call-arg]
            )

    def test_frozen(self):
        spec = TriggerHandlerSpec(handler="pkg.mod.func")
        with pytest.raises(Exception):
            spec.handler = "tampered"  # type: ignore[misc]


class TestPhase1DTriggerTypes:
    def test_phase1d_set_size(self):
        assert len(PHASE1D_TRIGGER_TYPES) == 6

    def test_phase1d_contains_required(self):
        required = {
            "onboarding",
            "drift_detected",
            "compression_needed",
            "cleanup_due",
            "blueprint_published",
            "blueprint_lookup",
        }
        assert required <= PHASE1D_TRIGGER_TYPES


# ---------------------------------------------------------------------------
# 2. load_router_config
# ---------------------------------------------------------------------------


class TestLoadRouterConfig:
    def test_loads_good_yaml(self, good_yaml):
        specs = load_router_config(good_yaml)
        assert "onboarding" in specs
        assert specs["onboarding"].safety == TriggerSafety.M
        assert specs["disabled_one"].enabled is False

    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(TriggerRouterConfigError):
            load_router_config(tmp_path / "missing.yaml")

    def test_missing_triggers_key_raises(self, tmp_path):
        bad = tmp_path / "bad.yaml"
        bad.write_text("version: '1.0.0'\n", encoding="utf-8")
        with pytest.raises(TriggerRouterConfigError):
            load_router_config(bad)

    def test_invalid_spec_raises(self, tmp_path):
        bad = tmp_path / "bad.yaml"
        bad.write_text(
            textwrap.dedent(
                """\
                triggers:
                  bad_one:
                    handler: ""
                    safety: "M"
                """
            ),
            encoding="utf-8",
        )
        with pytest.raises(TriggerRouterConfigError):
            load_router_config(bad)

    def test_non_mapping_value_raises(self, tmp_path):
        bad = tmp_path / "bad.yaml"
        bad.write_text(
            textwrap.dedent(
                """\
                triggers:
                  bad_one: "just a string"
                """
            ),
            encoding="utf-8",
        )
        with pytest.raises(TriggerRouterConfigError):
            load_router_config(bad)

    def test_repository_default_yaml_exists(self):
        """`config/trigger_router.yaml` 真实存在且可解析（experimental 起始集 5 种）。"""
        assert DEFAULT_ROUTER_YAML_PATH.exists(), f"trigger_router.yaml 缺失：{DEFAULT_ROUTER_YAML_PATH}"
        specs = load_router_config(DEFAULT_ROUTER_YAML_PATH)
        # 至少包含 experimental 起始集 5 种
        assert set(specs.keys()) >= PHASE1D_TRIGGER_TYPES


# ---------------------------------------------------------------------------
# 3. TriggerRouter 加载
# ---------------------------------------------------------------------------


class TestTriggerRouterLoad:
    def test_constructor_loads_yaml(self, good_yaml):
        router = TriggerRouter(config_path=good_yaml)
        assert router.is_registered("onboarding")
        assert router.is_registered("drift_detected")
        assert "disabled_one" in router.trigger_types

    def test_lazy_load_on_dispatch(self, good_yaml):
        router = TriggerRouter(config_path=good_yaml, auto_load=False)
        # 未加载也应在 dispatch 时自动加载
        result = router.dispatch("onboarding")
        assert result.success is True

    def test_inject_handlers_overrides_yaml(self, good_yaml):
        called = {"flag": False}

        def custom_onboarding(payload, **_):
            called["flag"] = True
            return {"custom": True}

        router = TriggerRouter(config_path=good_yaml, handlers={"onboarding": custom_onboarding})
        result = router.dispatch("onboarding")
        assert called["flag"] is True
        assert result.handler_result == {"custom": True}

    def test_inject_handlers_unknown_to_yaml_still_works(self, good_yaml):
        def my_trigger(payload, **_):
            return "ok"

        router = TriggerRouter(config_path=good_yaml, handlers={"my_custom_trigger": my_trigger})
        result = router.dispatch("my_custom_trigger")
        assert result.success is True
        assert result.handler_result == "ok"

    def test_yaml_missing_with_handlers_falls_back(self, tmp_path):
        """YAML 不存在 + 注入 handlers → 仍可运行（测试/离线场景）。"""

        def fn(payload, **_):
            return 42

        router = TriggerRouter(
            config_path=tmp_path / "missing.yaml",
            handlers={"x": fn},
        )
        assert router.dispatch("x").handler_result == 42

    def test_yaml_missing_no_handlers_raises(self, tmp_path):
        with pytest.raises(TriggerRouterConfigError):
            TriggerRouter(config_path=tmp_path / "missing.yaml")

    def test_reload_picks_up_changes(self, good_yaml):
        router = TriggerRouter(config_path=good_yaml)
        assert "onboarding" in router.trigger_types
        # 重写 YAML 删除 onboarding
        good_yaml.write_text(
            textwrap.dedent(
                """\
                version: "1.0.0"
                triggers:
                  cleanup_due:
                    handler: "zephyr.trading.orchestrator.trigger_router.handle_cleanup_stub"
                    safety: "L"
                    enabled: true
                """
            ),
            encoding="utf-8",
        )
        router.reload()
        assert "onboarding" not in router.trigger_types
        assert "cleanup_due" in router.trigger_types


# ---------------------------------------------------------------------------
# 4. dispatch 路径：5 种 trigger_type 成功路径
# ---------------------------------------------------------------------------


class TestDispatchSuccessPaths:
    def test_onboarding(self, good_yaml):
        router = TriggerRouter(config_path=good_yaml)
        result = router.dispatch("onboarding", payload={"agent_id": "A1"})
        assert isinstance(result, RouterDispatchResult)
        assert result.success is True
        assert result.skipped is False
        assert result.error is None
        assert result.handler_result["handler"] == "onboarding"

    def test_drift_detected(self, good_yaml):
        router = TriggerRouter(config_path=good_yaml)
        result = router.dispatch("drift_detected", payload={"factor": "alpha_001", "z": 3.5})
        assert result.success is True
        assert result.handler_result["handler"] == "drift_detected"

    def test_cleanup_due(self, good_yaml):
        router = TriggerRouter(config_path=good_yaml)
        result = router.dispatch("cleanup_due", payload={"scope": "snapshots"})
        assert result.success is True
        assert result.handler_result["handler"] == "cleanup_due"

    def test_blueprint_published(self, good_yaml):
        router = TriggerRouter(config_path=good_yaml)
        result = router.dispatch("blueprint_published", payload={"blueprint_id": "B-007"})
        assert result.success is True
        assert result.handler_result["handler"] == "blueprint_published"


# ---------------------------------------------------------------------------
# 5. dispatch 路径：失败 / 跳过
# ---------------------------------------------------------------------------


class TestDispatchSkipPaths:
    def test_unknown_trigger_skipped_silently(self, good_yaml):
        router = TriggerRouter(config_path=good_yaml)
        result = router.dispatch("never_registered")
        assert result.success is False
        assert result.skipped is True
        assert result.skip_reason == "unknown_trigger_type"
        assert result.error is None

    def test_disabled_trigger_skipped(self, good_yaml):
        router = TriggerRouter(config_path=good_yaml)
        result = router.dispatch("disabled_one")
        assert result.success is False
        assert result.skipped is True
        assert result.skip_reason == "disabled"

    def test_handler_import_failure_skipped(self, good_yaml):
        router = TriggerRouter(config_path=good_yaml)
        result = router.dispatch("broken_handler")
        assert result.success is False
        assert result.skipped is True
        assert result.skip_reason == "handler_unresolvable"

    def test_handler_exception_caught(self, good_yaml):
        def raises_handler(payload, **_):
            raise RuntimeError("handler boom")

        router = TriggerRouter(config_path=good_yaml, handlers={"onboarding": raises_handler})
        result = router.dispatch("onboarding")
        assert result.success is False
        assert result.skipped is False
        assert "handler boom" in (result.error or "")

    def test_dispatch_never_raises(self, tmp_path):
        """无 YAML 也无 handlers 应该构造失败而不是 dispatch 抛异常。"""

        def fn(payload, **_):
            raise ValueError("downstream")

        router = TriggerRouter(
            config_path=tmp_path / "missing.yaml",
            handlers={"x": fn},
        )
        # 即使 handler 异常，dispatch 也不抛
        result = router.dispatch("x")
        assert result.success is False


# ---------------------------------------------------------------------------
# 6. dispatch 上下文与 payload 透传
# ---------------------------------------------------------------------------


class TestDispatchContextPassing:
    def test_payload_passed_to_handler(self, good_yaml):
        captured = {}

        def my_handler(payload, **ctx):
            captured["payload"] = payload
            captured["ctx"] = ctx
            return "ok"

        router = TriggerRouter(config_path=good_yaml, handlers={"onboarding": my_handler})
        router.dispatch(
            "onboarding",
            payload={"key": "value"},
            session_id="sess-1",
            now="2026-04-27",
        )
        assert captured["payload"] == {"key": "value"}
        # session_id 不会作为 context 传给 handler；其他 kw 会
        assert captured["ctx"]["now"] == "2026-04-27"

    def test_default_payload_empty_dict(self, good_yaml):
        captured = {}

        def my_handler(payload, **_):
            captured["payload"] = payload
            return None

        router = TriggerRouter(config_path=good_yaml, handlers={"onboarding": my_handler})
        router.dispatch("onboarding")
        assert captured["payload"] == {}


# ---------------------------------------------------------------------------
# 7. 审计日志注入
# ---------------------------------------------------------------------------


class FakeAuditLogger:
    """Duck-typed AuditLogger 替身。"""

    def __init__(self):
        self.entries: list[dict] = []

    def log_rule_trigger(self, *, target, result, session_id=None, model=None, extra=None):
        self.entries.append(
            {
                "target": target,
                "result": result,
                "session_id": session_id,
                "model": model,
                "extra": extra or {},
            }
        )


class TestAuditLogIntegration:
    def test_audit_logged_on_success(self, good_yaml):
        audit = FakeAuditLogger()
        router = TriggerRouter(config_path=good_yaml, audit_logger=audit)
        router.dispatch("onboarding", payload={"a": 1})
        assert len(audit.entries) == 1
        assert audit.entries[0]["target"] == "trigger:onboarding"
        assert audit.entries[0]["result"] == "dispatched"
        assert audit.entries[0]["model"] == "M3:trigger_router"
        assert "payload_keys" in audit.entries[0]["extra"]

    def test_audit_logged_on_unknown_trigger(self, good_yaml):
        audit = FakeAuditLogger()
        router = TriggerRouter(config_path=good_yaml, audit_logger=audit)
        router.dispatch("never_registered")
        assert len(audit.entries) == 1
        assert audit.entries[0]["result"] == "skipped:unknown_trigger_type"

    def test_audit_logged_on_disabled(self, good_yaml):
        audit = FakeAuditLogger()
        router = TriggerRouter(config_path=good_yaml, audit_logger=audit)
        router.dispatch("disabled_one")
        assert audit.entries[0]["result"] == "skipped:disabled"

    def test_audit_logged_on_handler_failure(self, good_yaml):
        audit = FakeAuditLogger()

        def fn(payload, **_):
            raise RuntimeError("downstream")

        router = TriggerRouter(
            config_path=good_yaml,
            handlers={"onboarding": fn},
            audit_logger=audit,
        )
        router.dispatch("onboarding")
        assert audit.entries[0]["result"] == "failed"
        assert "downstream" in audit.entries[0]["extra"]["error"]

    def test_audit_failure_does_not_raise(self, good_yaml):
        """审计日志写入失败不应影响 dispatch 主流程。"""

        class BrokenAudit:
            def log_rule_trigger(self, **_):
                raise RuntimeError("disk full")

        router = TriggerRouter(config_path=good_yaml, audit_logger=BrokenAudit())
        # 不抛异常即视为通过
        result = router.dispatch("onboarding")
        assert result.success is True


# ---------------------------------------------------------------------------
# 8. 单例
# ---------------------------------------------------------------------------


class TestSingleton:
    def test_get_returns_same_instance(self, good_yaml):
        a = get_trigger_router(config_path=good_yaml)
        b = get_trigger_router()
        assert a is b

    def test_reset_creates_new(self, good_yaml):
        a = get_trigger_router(config_path=good_yaml)
        b = get_trigger_router(config_path=good_yaml, reset=True)
        assert a is not b


# ---------------------------------------------------------------------------
# 9. 默认 stub 处理器
# ---------------------------------------------------------------------------


class TestDefaultStubHandlers:
    @pytest.mark.parametrize(
        "stub, expected",
        [
            (handle_onboarding_stub, "onboarding"),
            (handle_cleanup_stub, "cleanup_due"),
            (handle_blueprint_stub, "blueprint_published"),
        ],
    )
    def test_stub_returns_dict(self, stub, expected):
        result = stub({"k": "v"})
        assert isinstance(result, dict)
        assert result["handler"] == expected
        assert result["phase"] in ("1d-stub", "operational")

    def test_drift_stub_operational(self):
        """``handle_drift_detected`` 已升级为真实调用 trigger_recovery，返回 operational。"""
        result = handle_drift_detected({"k": "v"})
        assert isinstance(result, dict)
        assert result["handler"] == "drift_detected"
        assert result["phase"] == "operational"
        assert "recovery_result" in result

    def test_stub_handles_kwargs(self):
        result = handle_onboarding_stub({"k": "v"}, session_id="s1", extra="x")
        assert result["handler"] == "onboarding"

    def test_stub_handles_empty_payload(self):
        result = handle_cleanup_stub({})
        assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# 10. RouterDispatchResult 契约
# ---------------------------------------------------------------------------


class TestRouterDispatchResultContract:
    def test_success_result_fields(self, good_yaml):
        router = TriggerRouter(config_path=good_yaml)
        result = router.dispatch("onboarding")
        assert result.trigger_type == "onboarding"
        assert result.handler_path is not None
        assert result.dispatched_at  # ISO 时间字符串
        assert result.latency_ms >= 0

    def test_skipped_result_has_no_handler_result(self, good_yaml):
        router = TriggerRouter(config_path=good_yaml)
        result = router.dispatch("never_registered")
        assert result.handler_result is None
        assert result.handler_path is None
