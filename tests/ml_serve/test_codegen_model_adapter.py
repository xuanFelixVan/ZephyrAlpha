# [BLUEPRINT] MOD-MLS-003 | docs/03_modules/_domain_ml_serve/codegen_model_adapter/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-MLS-003 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.ml_serve.test_codegen_model_adapter
# [TESTS] src/zephyr/ml_serve/codegen_model_adapter.py
"""MOD-MLS-003 单元测试：codegen_model_adapter 代码生成模型适配器。

蓝图验收（B10-02296/CAND-MLS-003，A1 D-ML-46）：
DeepSeek-V4-Pro profile 注册（能力/上下文窗/成本单价）+ token 成本计量
（按 token 计费累计 + 预算告警）+ 调用 schema 规范化（client 注入不真发）。
client/registrar/告警全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.ml_serve.codegen_model_adapter",
    reason="codegen_model_adapter not importable",
)

from zephyr.ml_serve.codegen_model_adapter import (  # noqa: E402
    BudgetAlertKind,
    CodegenAdapterError,
    CodegenCapability,
    CodegenModelAdapter,
    CodegenProfile,
    CodegenRequest,
)

_T0 = datetime.datetime(2026, 8, 25, 9, 30, 0)

#: 默认单价下单次调用成本 = 2×0.002 + 0.5×0.008 = 0.008
_RAW_OK = {"text": "def signal(close): ...", "prompt_tokens": 2000, "completion_tokens": 500}


def _custom_profile(**overrides) -> CodegenProfile:
    kwargs = dict(
        model_id="deepseek-v4-pro-mini",
        provider="deepseek",
        capabilities=frozenset({CodegenCapability.CODE_GENERATION}),
        context_window=8192,
        input_price_per_1k=0.001,
        output_price_per_1k=0.002,
    )
    kwargs.update(overrides)
    return CodegenProfile(**kwargs)


def _adapter(
    alerts: list | None = None,
    client=None,
    raw: dict | None = None,
    registrar=None,
    budget_limit: float | None = None,
    warn_ratio: float = 0.8,
) -> CodegenModelAdapter:
    if client is None:
        client = lambda payload: dict(raw) if raw is not None else dict(_RAW_OK)
    return CodegenModelAdapter(
        client=client,
        profile_registrar=registrar,
        budget_alert_sink=(lambda a: alerts.append(a)) if alerts is not None else None,
        budget_limit=budget_limit,
        warn_ratio=warn_ratio,
        clock=lambda: _T0,
    )


def _request(
    model_id: str = "deepseek-v4-pro",
    capability: CodegenCapability = CodegenCapability.CODE_GENERATION,
    request_id: str = "req-1",
    prompt: str = "实现 T+0 均线突破信号函数",
    max_tokens: int = 1024,
) -> CodegenRequest:
    return CodegenRequest(
        request_id=request_id,
        model_id=model_id,
        capability=capability,
        prompt=prompt,
        max_tokens=max_tokens,
        submitted_at=_T0,
    )


# ──────────────────────────────────────────────────────────────────────────────
# profile 注册（model_router 挂钩）
# ──────────────────────────────────────────────────────────────────────────────


class TestProfileRegistration:
    def test_default_profile_registered(self) -> None:
        adapter = _adapter()
        profile = adapter.profile_of("deepseek-v4-pro")
        assert profile.provider == "deepseek"
        assert profile.capabilities == frozenset(CodegenCapability)
        assert profile.context_window == 131072
        assert adapter.registered_models() == ("deepseek-v4-pro",)

    def test_profile_of_unknown_raises(self) -> None:
        with pytest.raises(CodegenAdapterError):
            _adapter().profile_of("ghost")

    def test_register_custom_profile_with_registrar_hook(self) -> None:
        registered: list[CodegenProfile] = []
        adapter = _adapter(registrar=lambda p: registered.append(p))
        adapter.register_profile(_custom_profile())
        assert [p.model_id for p in registered] == ["deepseek-v4-pro", "deepseek-v4-pro-mini"]
        assert adapter.registered_models() == ("deepseek-v4-pro", "deepseek-v4-pro-mini")

    def test_register_duplicate_raises(self) -> None:
        adapter = _adapter()
        with pytest.raises(CodegenAdapterError):
            adapter.register_profile(_custom_profile(model_id="deepseek-v4-pro"))

    def test_invalid_profile_raises(self) -> None:
        with pytest.raises(CodegenAdapterError):
            _custom_profile(output_price_per_1k=-0.1)
        with pytest.raises(CodegenAdapterError):
            _custom_profile(capabilities=frozenset())
        with pytest.raises(CodegenAdapterError):
            _custom_profile(context_window=0)

    def test_registrar_failure_raises(self) -> None:
        with pytest.raises(CodegenAdapterError):
            CodegenModelAdapter(
                client=lambda payload: dict(_RAW_OK),
                profile_registrar=lambda p: 1 / 0,
                clock=lambda: _T0,
            )


# ──────────────────────────────────────────────────────────────────────────────
# 请求 schema 规范化
# ──────────────────────────────────────────────────────────────────────────────


class TestNormalizeRequest:
    def test_normalize_ok(self) -> None:
        adapter = _adapter()
        assert adapter.normalize_request(_request()) == {
            "model": "deepseek-v4-pro",
            "capability": "code_generation",
            "prompt": "实现 T+0 均线突破信号函数",
            "max_tokens": 1024,
            "temperature": 0.0,
            "stream": False,
        }

    def test_empty_request_id_and_prompt_raises(self) -> None:
        adapter = _adapter()
        with pytest.raises(CodegenAdapterError):
            adapter.normalize_request(_request(request_id=""))
        with pytest.raises(CodegenAdapterError):
            adapter.normalize_request(_request(prompt=""))

    def test_unknown_model_raises(self) -> None:
        with pytest.raises(CodegenAdapterError):
            _adapter().normalize_request(_request(model_id="ghost"))

    def test_capability_not_declared_raises(self) -> None:
        adapter = _adapter()
        adapter.register_profile(_custom_profile())  # 仅声明 code_generation
        with pytest.raises(CodegenAdapterError):
            adapter.normalize_request(
                _request(model_id="deepseek-v4-pro-mini", capability=CodegenCapability.REFACTOR)
            )

    def test_max_tokens_over_window_raises(self) -> None:
        with pytest.raises(CodegenAdapterError):
            _adapter().normalize_request(_request(max_tokens=131073))

    def test_max_tokens_non_positive_raises(self) -> None:
        adapter = _adapter()
        with pytest.raises(CodegenAdapterError):
            adapter.normalize_request(_request(max_tokens=0))
        with pytest.raises(CodegenAdapterError):
            adapter.normalize_request(_request(max_tokens=-1))


# ──────────────────────────────────────────────────────────────────────────────
# 调用适配（client 注入不真发）
# ──────────────────────────────────────────────────────────────────────────────


class TestInvoke:
    def test_invoke_ok(self) -> None:
        sent: list[dict] = []
        adapter = _adapter(client=lambda payload: sent.append(payload) or dict(_RAW_OK))
        response = adapter.invoke(_request())
        assert sent == [adapter.normalize_request(_request())]  # client 收到规范化载荷
        assert response.text == _RAW_OK["text"]
        assert response.prompt_tokens == 2000
        assert response.completion_tokens == 500
        assert response.cost == pytest.approx(0.008)
        assert response.finished_at == _T0

    def test_client_not_injected_fail_closed(self) -> None:
        adapter = CodegenModelAdapter(clock=lambda: _T0)
        with pytest.raises(CodegenAdapterError):
            adapter.invoke(_request())

    def test_client_exception_wrapped(self) -> None:
        def _boom(payload: dict) -> dict:
            raise RuntimeError("HTTP 503")

        with pytest.raises(CodegenAdapterError):
            _adapter(client=_boom).invoke(_request())

    def test_response_missing_key_raises(self) -> None:
        adapter = _adapter(raw={"text": "...", "completion_tokens": 1})
        with pytest.raises(CodegenAdapterError):
            adapter.invoke(_request())

    def test_response_negative_tokens_raises(self) -> None:
        adapter = _adapter(raw={"text": "...", "prompt_tokens": -1, "completion_tokens": 1})
        with pytest.raises(CodegenAdapterError):
            adapter.invoke(_request())

    def test_response_tokens_over_window_raises(self) -> None:
        adapter = _adapter(raw={"text": "...", "prompt_tokens": 131072, "completion_tokens": 1})
        with pytest.raises(CodegenAdapterError):
            adapter.invoke(_request())

    def test_cost_accumulates(self) -> None:
        adapter = _adapter()
        adapter.invoke(_request(request_id="r1"))
        adapter.invoke(_request(request_id="r2"))
        usage = adapter.usage_of("deepseek-v4-pro")
        assert usage.calls == 2
        assert usage.prompt_tokens == 4000
        assert usage.completion_tokens == 1000
        assert usage.total_cost == pytest.approx(0.016)


# ──────────────────────────────────────────────────────────────────────────────
# 预算告警（预警/越限留痕，越限后 Fail-Closed）
# ──────────────────────────────────────────────────────────────────────────────


class TestBudget:
    def test_budget_warning_alert_once(self) -> None:
        alerts: list = []
        adapter = _adapter(alerts, budget_limit=0.02)  # 预警线 0.016
        adapter.invoke(_request(request_id="r1"))  # 0.008 未越线
        adapter.invoke(_request(request_id="r2"))  # 0.016 恰越预警线（仅此一次）
        assert [a.kind for a in alerts] == [BudgetAlertKind.WARNING]
        assert alerts[0].total_cost == pytest.approx(0.016)
        assert alerts[0].budget_limit == 0.02

    def test_budget_exceeded_then_fail_closed(self) -> None:
        alerts: list = []
        adapter = _adapter(alerts, budget_limit=0.01)  # 预警线 0.008
        adapter.invoke(_request(request_id="r1"))  # 0.008 → 预警
        adapter.invoke(_request(request_id="r2"))  # 0.016 → 越限
        assert [a.kind for a in alerts] == [BudgetAlertKind.WARNING, BudgetAlertKind.EXCEEDED]
        with pytest.raises(CodegenAdapterError):
            adapter.invoke(_request(request_id="r3"))  # 预算耗尽 Fail-Closed

    def test_warn_and_exceeded_crossed_together(self) -> None:
        alerts: list = []
        adapter = _adapter(alerts, budget_limit=0.005)  # 单次 0.008 一并越两线
        adapter.invoke(_request())
        assert [a.kind for a in alerts] == [BudgetAlertKind.WARNING, BudgetAlertKind.EXCEEDED]

    def test_no_budget_no_alerts(self) -> None:
        alerts: list = []
        adapter = _adapter(alerts)  # 未设预算
        adapter.invoke(_request(request_id="r1"))
        adapter.invoke(_request(request_id="r2"))
        assert alerts == []


# ──────────────────────────────────────────────────────────────────────────────
# 查询 / 确定性
# ──────────────────────────────────────────────────────────────────────────────


class TestUsage:
    def test_usage_of_unknown_raises(self) -> None:
        with pytest.raises(CodegenAdapterError):
            _adapter().usage_of("ghost")

    def test_determinism(self) -> None:
        def _script() -> tuple:
            adapter = _adapter()
            r1 = adapter.invoke(_request(request_id="r1"))
            r2 = adapter.invoke(_request(request_id="r2"))
            return (r1, r2, adapter.usage_of("deepseek-v4-pro"))

        assert _script() == _script()  # 同输入必同输出
