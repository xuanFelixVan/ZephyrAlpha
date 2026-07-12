# [A_test] module_id: SRC-TST-2099 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-commit_gate_registry | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §commit-gate-registry
# [MODULE] tests.test_commit_gate_registry
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""test_commit_gate_registry.py — CommitGateRegistry 单测（架构债务 #AD-001 治本）

权威依据：commit_gate_registry.py（CommitGateRegistry / GateSpec / GateResult）

测试组：
- TestRegister: register 幂等（同 gate_id 覆盖旧 spec）
- TestCheckAllOrder: check_all 按 priority 升序执行
- TestCheckAllException: 单个 gate 异常降级为 fail-closed（passed=False），不阻断后续 gate
- TestEmptyRegistry: 空 registry check_all 返回空列表
- TestKwargsPassthrough: kwargs 透传给 gate check 函数
- TestGet: get(gate_id) 按 gate_id 获取已注册 GateSpec（_commit_auto 复用 DCR gate 用，2026-06-30 治本）
"""
from __future__ import annotations

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import (
    CommitGateRegistry,
    GateResult,
    GateSpec,
)


class TestRegister:
    """register 幂等性测试。"""

    def test_register_idempotent_same_gate_id_overrides(self):
        """同 gate_id 注册两次，后者覆盖前者。"""
        registry = CommitGateRegistry()
        registry.register(GateSpec(
            gate_id="G1", check=lambda gw, f, **kw: (True, "old"), priority=100,
        ))
        registry.register(GateSpec(
            gate_id="G1", check=lambda gw, f, **kw: (False, "override"), priority=100,
        ))
        results = registry.check_all(None, [])
        assert len(results) == 1
        assert results[0].gate_id == "G1"
        assert results[0].passed is False
        assert results[0].detail == "override"

    def test_register_multiple_distinct_gate_ids(self):
        """不同 gate_id 各自保留。"""
        registry = CommitGateRegistry()
        registry.register(GateSpec(gate_id="A", check=lambda gw, f, **kw: (True, ""), priority=100))
        registry.register(GateSpec(gate_id="B", check=lambda gw, f, **kw: (True, ""), priority=100))
        results = registry.check_all(None, [])
        assert {r.gate_id for r in results} == {"A", "B"}


class TestCheckAllOrder:
    """check_all 按 priority 升序执行。"""

    def test_priority_ascending(self):
        """priority 数字小先执行。"""
        order: list[str] = []
        registry = CommitGateRegistry()
        registry.register(GateSpec(
            gate_id="late",
            check=lambda gw, f, **kw: (order.append("late"), (True, ""))[1],
            priority=200,
        ))
        registry.register(GateSpec(
            gate_id="early",
            check=lambda gw, f, **kw: (order.append("early"), (True, ""))[1],
            priority=50,
        ))
        registry.check_all(None, [])
        assert order == ["early", "late"]


class TestCheckAllException:
    """单个 gate 异常降级为 fail-closed。"""

    def test_gate_exception_fail_closed_not_blocking_others(self):
        """gate 抛异常时降级为 passed=False，不阻断后续 gate 执行。"""

        def bad_gate(gw, f, **kw):
            raise RuntimeError("boom")

        def good_gate(gw, f, **kw):
            return True, "ok"

        registry = CommitGateRegistry()
        registry.register(GateSpec(gate_id="bad", check=bad_gate, priority=50))
        registry.register(GateSpec(gate_id="good", check=good_gate, priority=100))
        results = registry.check_all(None, [])
        assert len(results) == 2
        # 异常 gate 降级为 fail-closed
        assert results[0].gate_id == "bad"
        assert results[0].passed is False
        assert "boom" in results[0].detail
        # 后续 gate 正常执行
        assert results[1].gate_id == "good"
        assert results[1].passed is True


class TestEmptyRegistry:
    """空 registry。"""

    def test_empty_registry_returns_empty_list(self):
        registry = CommitGateRegistry()
        results = registry.check_all(None, [])
        assert results == []


class TestKwargsPassthrough:
    """kwargs 透传给 gate check 函数。"""

    def test_kwargs_passed_to_check(self):
        """check_all 的 kwargs 透传给 gate check。"""
        received: dict = {}

        def capturing_gate(gw, f, **kw):
            received.update(kw)
            return True, ""

        registry = CommitGateRegistry()
        registry.register(GateSpec(gate_id="cap", check=capturing_gate, priority=100))
        registry.check_all(None, [], session_id="s-1", allow_overlap=True, extra="x")
        assert received == {"session_id": "s-1", "allow_overlap": True, "extra": "x"}


class TestGet:
    """get(gate_id) 按 gate_id 获取已注册的 GateSpec。"""

    def test_get_returns_registered_spec(self):
        """get 返回已注册的 GateSpec 实例。"""
        registry = CommitGateRegistry()
        spec = GateSpec(gate_id="G1", check=lambda gw, f, **kw: (True, ""), priority=100)
        registry.register(spec)
        got = registry.get("G1")
        assert got is spec

    def test_get_returns_none_for_unregistered_gate_id(self):
        """未注册的 gate_id 返回 None（_commit_auto 用此判定 DCR gate 是否注册）。"""
        registry = CommitGateRegistry()
        assert registry.get("NONEXISTENT") is None

    def test_get_returns_overriding_spec_after_reregister(self):
        """同 gate_id 重新 register 后，get 返回新 spec（幂等覆盖语义）。"""
        registry = CommitGateRegistry()
        old = GateSpec(gate_id="G1", check=lambda gw, f, **kw: (True, "old"), priority=100)
        new = GateSpec(gate_id="G1", check=lambda gw, f, **kw: (False, "new"), priority=100)
        registry.register(old)
        registry.register(new)
        got = registry.get("G1")
        assert got is new


class TestGateResultDefaults:
    """GateResult 默认值。"""

    def test_detail_defaults_empty(self):
        r = GateResult(gate_id="G", passed=True)
        assert r.detail == ""
