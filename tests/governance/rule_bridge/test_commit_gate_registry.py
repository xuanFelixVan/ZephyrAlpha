# [A_test] module_id: MOD-GOV_commit_gate_registry | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_COMMIT_GATE_REGISTRY | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §commit-gate-registry
# [MODULE] tests.test_commit_gate_registry
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GOV_COMMIT_GATE_REGISTRY | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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
- TestPriorityConflictBlock: 同 priority 不同 gate_id 抛 GateRegistrationError 阻断（#ARCH-GATE-PRIORITY-UNIQUENESS-001 Phase 2 fail-closed 治本）
"""

from __future__ import annotations

import pytest

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import (
    CommitGateRegistry,
    GateRegistrationError,
    GateResult,
    GateSpec,
)


class TestRegister:
    """register 幂等性测试。"""

    def test_register_idempotent_same_gate_id_overrides(self):
        """同 gate_id 注册两次，后者覆盖前者。"""
        registry = CommitGateRegistry()
        registry.register(
            GateSpec(
                gate_id="G1",
                check=lambda gw, f, **kw: (True, "old"),
                priority=100,
            )
        )
        registry.register(
            GateSpec(
                gate_id="G1",
                check=lambda gw, f, **kw: (False, "override"),
                priority=100,
            )
        )
        results = registry.check_all(None, [])
        assert len(results) == 1
        assert results[0].gate_id == "G1"
        assert results[0].passed is False
        assert results[0].detail == "override"

    def test_register_multiple_distinct_gate_ids(self):
        """不同 gate_id 各自保留（必须用不同 priority——Phase 2 fail-closed 后同 priority 抛异常）。"""
        registry = CommitGateRegistry()
        registry.register(GateSpec(gate_id="A", check=lambda gw, f, **kw: (True, ""), priority=100))
        registry.register(GateSpec(gate_id="B", check=lambda gw, f, **kw: (True, ""), priority=101))
        results = registry.check_all(None, [])
        assert {r.gate_id for r in results} == {"A", "B"}


class TestCheckAllOrder:
    """check_all 按 priority 升序执行。"""

    def test_priority_ascending(self):
        """priority 数字小先执行。"""
        order: list[str] = []
        registry = CommitGateRegistry()
        registry.register(
            GateSpec(
                gate_id="late",
                check=lambda gw, f, **kw: (order.append("late"), (True, ""))[1],
                priority=200,
            )
        )
        registry.register(
            GateSpec(
                gate_id="early",
                check=lambda gw, f, **kw: (order.append("early"), (True, ""))[1],
                priority=50,
            )
        )
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


class TestSkipGates:
    """skip_gates 跳过执行（tracker #92：worktree 物理隔离 commit 跳过搭便车三 gate）。

    跳过集合单一真源=session_worktree._WORKTREE_SKIP_GATES；注册表层只认 skip_gates
    参数（不关心来源），跳过结果保留 passed=True 记录供审计（禁隐式消失）。
    """

    def test_skip_gates_skips_matching_gate_with_audit_record(self):
        """命中的 gate 不执行，结果保留 skipped 记录（passed=True 不阻断）。"""
        executed: list[str] = []
        registry = CommitGateRegistry()
        registry.register(
            GateSpec(
                gate_id="HELD-OVERLAP",
                priority=100,
                check=lambda gw, f, **kw: (executed.append("HELD-OVERLAP"), (False, "would-block"))[1],
            )
        )
        registry.register(
            GateSpec(
                gate_id="OTHER-GATE",
                priority=101,
                check=lambda gw, f, **kw: (executed.append("OTHER-GATE"), (True, ""))[1],
            )
        )
        results = registry.check_all(None, [], skip_gates=frozenset({"HELD-OVERLAP"}))
        # 被跳过的 gate 未执行（不会误拦），其余 gate 正常执行
        assert executed == ["OTHER-GATE"]
        by_id = {r.gate_id: r for r in results}
        assert by_id["HELD-OVERLAP"].passed is True
        assert "skipped" in by_id["HELD-OVERLAP"].detail
        assert by_id["OTHER-GATE"].passed is True

    def test_skip_gates_default_empty_no_behavior_change(self):
        """默认空集合 → 全量执行（非 worktree 路径向后兼容回归锁）。"""
        executed: list[str] = []
        registry = CommitGateRegistry()
        registry.register(
            GateSpec(
                gate_id="G1",
                priority=100,
                check=lambda gw, f, **kw: (executed.append("G1"), (False, "still-blocks"))[1],
            )
        )
        results = registry.check_all(None, [])
        assert executed == ["G1"]
        assert results[0].passed is False  # 未跳过：阻断语义完整保留


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


class TestPriorityConflictBlock:
    """同 priority 不同 gate_id 抛 GateRegistrationError 阻断（#ARCH-GATE-PRIORITY-UNIQUENESS-001 Phase 2）。

    治本背景（2026-07-21）：100% AI 开发场景下，原 warn-only 不构成闭环
    （AI 把 warn 当"通过"，与 #ARCH-WORKSPACE-DRIFT-SYSTEMIC-001 同一病根）。
    升级为 fail-closed 阻断注册——新 AI 添加 priority 撞号的 gate 时立即抛异常。
    """

    def test_same_priority_different_gate_id_raises(self):
        """同 priority 不同 gate_id 抛 GateRegistrationError。"""
        registry = CommitGateRegistry()
        registry.register(
            GateSpec(
                gate_id="FIRST",
                check=lambda gw, f, **kw: (True, ""),
                priority=77,
            )
        )
        with pytest.raises(GateRegistrationError) as exc_info:
            registry.register(
                GateSpec(
                    gate_id="SECOND",
                    check=lambda gw, f, **kw: (True, ""),
                    priority=77,
                )
            )
        # 错误信息含 priority 值 + 两个 gate_id
        msg = str(exc_info.value)
        assert "77" in msg
        assert "FIRST" in msg
        assert "SECOND" in msg

    def test_same_priority_same_gate_id_no_raise(self):
        """同 priority 同 gate_id（幂等覆盖）不抛异常。"""
        registry = CommitGateRegistry()
        registry.register(
            GateSpec(
                gate_id="G1",
                check=lambda gw, f, **kw: (True, "old"),
                priority=100,
            )
        )
        # 不应抛异常——幂等覆盖语义
        registry.register(
            GateSpec(
                gate_id="G1",
                check=lambda gw, f, **kw: (False, "new"),
                priority=100,
            )
        )
        got = registry.get("G1")
        assert got.check(None, [])[0] is False  # 新 spec 生效

    def test_different_priority_no_raise(self):
        """不同 priority 不抛异常。"""
        registry = CommitGateRegistry()
        registry.register(GateSpec(gate_id="A", check=lambda gw, f, **kw: (True, ""), priority=100))
        registry.register(GateSpec(gate_id="B", check=lambda gw, f, **kw: (True, ""), priority=200))
        results = registry.check_all(None, [])
        assert {r.gate_id for r in results} == {"A", "B"}

    def test_blocked_gate_not_registered(self):
        """抛异常后，撞号 gate 未被注册（_specs 不含 SECOND）。"""
        registry = CommitGateRegistry()
        registry.register(
            GateSpec(
                gate_id="FIRST",
                check=lambda gw, f, **kw: (True, ""),
                priority=77,
            )
        )
        with pytest.raises(GateRegistrationError):
            registry.register(
                GateSpec(
                    gate_id="SECOND",
                    check=lambda gw, f, **kw: (True, ""),
                    priority=77,
                )
            )
        # SECOND 未被注册
        assert registry.get("SECOND") is None
        assert registry.get("FIRST") is not None

    def test_error_message_contains_historical_precedent(self):
        """错误信息含历史先例（后到者让位），引导新 AI 选择空闲 priority。"""
        registry = CommitGateRegistry()
        registry.register(
            GateSpec(
                gate_id="EXISTING",
                check=lambda gw, f, **kw: (True, ""),
                priority=85,
            )
        )
        with pytest.raises(GateRegistrationError) as exc_info:
            registry.register(
                GateSpec(
                    gate_id="NEW",
                    check=lambda gw, f, **kw: (True, ""),
                    priority=85,
                )
            )
        msg = str(exc_info.value)
        # 含至少一个历史先例
        assert "RULING-COMMIT-VERIFIED 77->109" in msg or "DATA-TASK 78->41" in msg

    def test_error_code_attribute(self):
        """GateRegistrationError 含 error_code 属性（对标 GatewayError 模式）。"""
        registry = CommitGateRegistry()
        registry.register(
            GateSpec(
                gate_id="FIRST",
                check=lambda gw, f, **kw: (True, ""),
                priority=50,
            )
        )
        with pytest.raises(GateRegistrationError) as exc_info:
            registry.register(
                GateSpec(
                    gate_id="SECOND",
                    check=lambda gw, f, **kw: (True, ""),
                    priority=50,
                )
            )
        assert exc_info.value.error_code == "ZA-GV-0050"

    def test_first_registration_unaffected(self):
        """第一个 gate 注册成功，不受后续撞号影响。"""
        registry = CommitGateRegistry()
        registry.register(
            GateSpec(
                gate_id="FIRST",
                check=lambda gw, f, **kw: (True, "first"),
                priority=77,
            )
        )
        with pytest.raises(GateRegistrationError):
            registry.register(
                GateSpec(
                    gate_id="SECOND",
                    check=lambda gw, f, **kw: (True, "second"),
                    priority=77,
                )
            )
        # FIRST 仍可正常 check
        results = registry.check_all(None, [])
        assert len(results) == 1
        assert results[0].gate_id == "FIRST"
        assert results[0].passed is True
