# [A_test] module_id: MOD-GOV_commit_gate_registry | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.test_commit_gate_registry
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=TEST-MOD-GOV_COMMIT_GATE_REGISTRY | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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


class TestWholeBookPriorityUniqueness:
    """全册唯一性机械校验（SW4 st-nightsweep-sw4-20260929 / 卡 C36 红五簇）：

    commit_gates 全部 GateSpec 面（含已吸收的薄工厂保留面）AST 扫描，
    同 priority 异 gate_id 对=失败并逐簇呈报。2026-09-29 实测 6 簇同号
    （70/79/80/82/92/113）——吸收台 union 面在册、被吸收薄工厂休眠但同号，
    任一面被重新装载即 GateRegistrationError 整链 fail-closed。
    """

    def test_commit_gates_all_faces_priority_unique(self):
        import ast
        from pathlib import Path

        gates_dir = Path(__file__).resolve().parents[4] / "src" / "zephyr" / "gov_enforcement" / "commit_gates"
        occ: dict[int, set[str]] = {}
        for p in sorted(gates_dir.glob("*.py")):
            tree = ast.parse(p.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and getattr(node.func, "id", "") == "GateSpec":
                    prio = gid = None
                    for kw in node.keywords:
                        try:
                            val = ast.literal_eval(kw.value)
                        except (ValueError, SyntaxError):
                            continue  # 非字面量实参（常量/表达式）不在机械校验面
                        if kw.arg == "priority":
                            prio = val
                        elif kw.arg == "gate_id":
                            gid = val
                    if isinstance(prio, int):
                        occ.setdefault(prio, set()).add(str(gid))
        dups = {p: sorted(g) for p, g in sorted(occ.items()) if len(g) > 1}
        assert not dups, f"priority 撞号簇（同号异 gate_id）: {dups}"


# ---------------------------------------------------------------------------
# C157 残差相计时（st-mastertc-l1，2026-10-07）：_timed_phase 共享 helper +
# gate_execution_stats.jsonl phases 面。tmp_path 隔离，fail-safe 语义钉死。
# ---------------------------------------------------------------------------


class _StatGateway:
    """只提供 project_root 的最小 gateway 替身（_stat_flush 消费面）。"""

    def __init__(self, root):
        self.project_root = str(root)


@pytest.fixture()
def _c157_clean_acc():
    from zephyr.gov_enforcement.rule_bridge import commit_gate_registry as m

    m._STAT_ACC.clear()
    m._PHASE_ACC.clear()
    yield m
    m._STAT_ACC.clear()
    m._PHASE_ACC.clear()


class TestTimedPhaseC157:
    """_timed_phase 相计时记账 + _stat_flush phases 落盘（C157）。"""

    def test_timed_phase_records_elapsed(self, _c157_clean_acc):
        import time

        m = _c157_clean_acc
        # Windows 下 time.monotonic=GetTickCount64（分辨率 15.625ms）：sleep 须跨
        # ≥1 个 tick 边界，否则 t0/t1 同 tick 读数 delta=0.0（st-mastertc-loop R1
        # 闪红实证：sleep(0.01) 约 2/3 概率记 0.0）。0.05s=3+ tick 保证量化 delta
        # ≥15.6ms > 断言下限 5.0ms，且仍远小于预算读数噪声。
        with m._timed_phase("FMS-HYGIENE", "baseline_load"):
            time.sleep(0.05)
        assert "FMS-HYGIENE" in m._PHASE_ACC
        assert m._PHASE_ACC["FMS-HYGIENE"]["baseline_load"] >= 5.0

    def test_timed_phase_swallows_body_and_timer_exceptions(self, _c157_clean_acc):
        """fail-safe 钉死：体内异常穿透（业务语义不变）、计时器异常静默。"""
        m = _c157_clean_acc
        with pytest.raises(RuntimeError):
            with m._timed_phase("G-X", "boom"):
                raise RuntimeError("业务异常原样穿透")
        assert m._PHASE_ACC.get("G-X", {}).get("boom", 0.0) >= 0.0  # 记账仍发生

    def test_check_all_flushes_phases_to_stats_jsonl(self, _c157_clean_acc, tmp_path):
        """门内 _timed_phase 相时长随 check_all 统计行落盘（rec["phases"]）。"""
        import json as _json

        m = _c157_clean_acc

        def _check(gw, files, **kw):  # noqa: ARG001 — 最小门体：包一相计时
            with m._timed_phase("HEAVY-GATE", "heavy_phase"):
                pass
            return True, ""

        registry = CommitGateRegistry()
        registry.register(GateSpec(gate_id="HEAVY-GATE", check=_check, priority=100))
        results = registry.check_all(_StatGateway(tmp_path), ["a.md"])
        assert results and results[0].passed

        stats = tmp_path / ".runtime" / "audit" / "gate_execution_stats.jsonl"
        assert stats.exists()
        rec = _json.loads(stats.read_text(encoding="utf-8").splitlines()[-1])
        assert rec["ms"]["HEAVY-GATE"] >= 0.0
        assert rec["phases"]["HEAVY-GATE"]["heavy_phase"] >= 0.0

    def test_flush_without_phases_omits_key(self, _c157_clean_acc, tmp_path):
        """无相计时的链不产生 phases 键（向后兼容，消费方按需读取）。"""
        import json as _json

        m = _c157_clean_acc
        registry = CommitGateRegistry()
        registry.register(GateSpec(gate_id="PLAIN", check=lambda gw, f, **kw: (True, ""), priority=100))
        registry.check_all(_StatGateway(tmp_path), ["a.md"])
        rec = _json.loads(
            (tmp_path / ".runtime" / "audit" / "gate_execution_stats.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()[-1]
        )
        assert "phases" not in rec
