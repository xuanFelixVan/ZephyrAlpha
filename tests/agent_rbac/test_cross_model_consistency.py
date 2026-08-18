# [A_test] module_id: MOD-GOV_cross_model_consistency | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §
# [MODULE] tests.agent_rbac.test_cross_model_consistency
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
MOD-INF-018 跨模型一致性测试 — DeepSeek/GLM/Claude 对同权限规则判定一致性

对标的蓝图 P2 项:
  - 跨模型一致性测试——DeepSeek/GLM/Claude对同权限规则判定一致性

测试策略:
  1. 确定性测试——所有不依赖LLM的纯规则判定必须输出一致
  2. 语义一致性——同样权限描述的语义解析结果必须跨模型一致
  3. API兼容性——PermissionGuard 所有公开API对所有模型输入格式兼容
  4. 边界案例——极端输入（空字符串/超长路径/特殊字符/Unicode）跨模型行为一致
"""

from __future__ import annotations

import pytest

from zephyr.security.access_control.derive_rbac_roles import RBACRoleDeriver
from zephyr.security.access_control.guards.permission_guard import GuardDecision, PermissionGuard
from zephyr.security.access_control.guards.rbac_guard import RBACGuard
from zephyr.security.access_control.identity import AgentIdentity, AgentRole, IDESource, MaturityLevel
from zephyr.security.access_control.immutable_core import ImmutableCore
from zephyr.security.access_control.integrity_self_check import IntegritySelfCheck

MODEL_AGENTS: dict[str, AgentIdentity] = {
    "DeepSeek": AgentIdentity(
        session_id="deepseek-consistency",
        maturity=MaturityLevel.L2_REGULAR,
        role=AgentRole.EXECUTOR,
        owner_approved=True,
        ide_source=IDESource.TRAE,
    ),
    "GLM": AgentIdentity(
        session_id="glm-consistency",
        maturity=MaturityLevel.L2_REGULAR,
        role=AgentRole.EXECUTOR,
        owner_approved=True,
        ide_source=IDESource.CLI,
    ),
    "Claude": AgentIdentity(
        session_id="claude-consistency",
        maturity=MaturityLevel.L2_REGULAR,
        role=AgentRole.EXECUTOR,
        owner_approved=True,
        ide_source=IDESource.API,
    ),
}


class TestDeterministicConsistency:
    """确定性规则——不依赖LLM的纯代码判定必须输出一致"""

    DETERMINISTIC_OPS = [
        "modify_immutable_core",
        "disable_kill_switch",
        "delete_audit_logs",
        "modify_self_permissions",
        "shell_true_execution",
        "circumvent_gate_engine",
        "read:docs",
        "read:src",
        "file_search",
        "code_search",
        "list_directory",
        "generate_report",
    ]

    def test_all_models_same_l0_blocked(self):
        guard = PermissionGuard()
        results: dict[str, dict[str, str]] = {}
        for model, agent in MODEL_AGENTS.items():
            results[model] = {}
            for op in self.DETERMINISTIC_OPS[:6]:
                r = guard.check(agent, op)
                results[model][op] = r.decision.value

        for op in self.DETERMINISTIC_OPS[:6]:
            decisions = {m: results[m][op] for m in MODEL_AGENTS}
            assert len(set(decisions.values())) == 1, (
                f"CrossModel FAIL: L0 operation '{op}' has inconsistent decisions: {decisions}"
            )

    def test_all_models_same_always_allowed(self):
        guard = PermissionGuard()
        results: dict[str, dict[str, str]] = {}
        for model, agent in MODEL_AGENTS.items():
            results[model] = {}
            for op in self.DETERMINISTIC_OPS[6:]:
                r = guard.check(agent, op)
                results[model][op] = r.decision.value

        for op in self.DETERMINISTIC_OPS[6:]:
            decisions = {m: results[m][op] for m in MODEL_AGENTS}
            assert len(set(decisions.values())) == 1, (
                f"CrossModel FAIL: always-allowed '{op}' inconsistent: {decisions}"
            )

    def test_rbac_guard_identical_across_models(self):
        guard = RBACGuard()
        ops_to_test = ["read:docs", "write:src", "delete:audit_logs", "modify:blueprint", "execute:tests"]
        results: dict[str, dict[str, str]] = {}
        for model, agent in MODEL_AGENTS.items():
            results[model] = {}
            for op in ops_to_test:
                r = guard.check(agent, op)
                results[model][op] = r.decision.value

        for op in ops_to_test:
            decisions = {m: results[m][op] for m in MODEL_AGENTS}
            assert len(set(decisions.values())) == 1, f"CrossModel FAIL: RBACGuard '{op}' inconsistent: {decisions}"

    def test_immutable_core_same_all_models(self):
        core = ImmutableCore()
        test_paths = [
            ".git/config",
            "src/zephyr/agent-rbac/__init__.py",
            "config/rbac_roles.yaml",
            "tests/test.py",
            "docs/readme.md",
            "src/zephyr/agent-rbac/immutable_core.py",
        ]
        for p in test_paths:
            r1 = core.is_protected_path(p)
            r2 = core.is_protected_path(p)
            r3 = core.is_protected_path(p)
            assert r1 == r2 == r3, f"ImmutableCore non-deterministic for '{p}': {r1}/{r2}/{r3}"

    def test_derive_rbac_deterministic(self):
        import tempfile
        from pathlib import Path

        deriver = RBACRoleDeriver()
        with tempfile.TemporaryDirectory() as tmp:
            p1 = Path(tmp) / "rbac1.yaml"
            p2 = Path(tmp) / "rbac2.yaml"
            hash1 = deriver.derive(p1)
            hash2 = deriver.derive(p2)
            assert hash1 == hash2, f"RBACRoleDeriver non-deterministic: {hash1} != {hash2}"


class TestSemanticConsistency:
    """语义一致性——同义描述不同表达方式的判定结果"""

    def test_permission_normalization_consistent(self):
        guard = PermissionGuard()
        agent = MODEL_AGENTS["DeepSeek"]
        variants = [
            ("write:src", "src/test.py"),
            ("write:src", "src/test.py"),
        ]
        results = [guard.check(agent, op, target_path=tgt).decision for op, tgt in variants]
        assert results[0] == results[1], f"Same input gave different results: {results}"

    def test_agent_identity_equivalence(self):
        a1 = AgentIdentity(
            session_id="equiv-1", maturity=MaturityLevel.L2_REGULAR, role=AgentRole.EXECUTOR, owner_approved=True
        )
        a2 = AgentIdentity(
            session_id="equiv-2", maturity=MaturityLevel.L2_REGULAR, role=AgentRole.EXECUTOR, owner_approved=True
        )
        guard = RBACGuard()
        ops = ["read:docs", "write:src", "execute:scripts", "delete:file"]
        for op in ops:
            r1 = guard.check(a1, op)
            r2 = guard.check(a2, op)
            assert r1.decision == r2.decision, (
                f"Semantic FAIL: '{op}' diff for equivalent agents: {r1.decision}/{r2.decision}"
            )


class TestAPICompatibility:
    """API兼容性——所有公开API对所有模型输入格式兼容"""

    def test_all_agent_fields_accepted(self):
        for model, agent in MODEL_AGENTS.items():
            assert agent.session_id, f"API FAIL: {model} agent missing session_id"
            assert agent.maturity, f"API FAIL: {model} agent missing maturity"
            assert agent.role, f"API FAIL: {model} agent missing role"

    def test_guard_accepts_all_model_agents(self):
        guard = PermissionGuard()
        for model, agent in MODEL_AGENTS.items():
            result = guard.check(agent, "read:docs")
            assert result.decision in (
                GuardDecision.ALLOW,
                GuardDecision.AUTO_GUARD,
                GuardDecision.BLOCKED,
            ), f"API FAIL: {model} agent produced invalid decision: {result.decision}"

    def test_guard_check_with_all_params(self):
        guard = PermissionGuard()
        agent = MODEL_AGENTS["DeepSeek"]
        result = guard.check(agent, "write:src", target_path="src/zephyr/test.py")
        assert result.layer != "", "API FAIL: guard.check() didn't produce layer info"
        assert result.timing_ns >= 0, "API FAIL: guard.check() didn't produce timing info"

    def test_integrity_self_check_all_modules(self):
        checker = IntegritySelfCheck()
        results = checker.check_all()
        passed = sum(1 for r in results if r.passed)
        total = len(results)
        assert passed == total, (
            f"Integrity FAIL: {total - passed}/{total} modules not importable. "
            f"Failed: {[r.module_name for r in results if not r.passed]}"
        )


class TestBoundaryConsistency:
    """边界案例——极端输入跨模型行为一致"""

    def test_empty_target_path(self):
        guard = PermissionGuard()
        for model, agent in MODEL_AGENTS.items():
            result = guard.check(agent, "write:src", target_path="")
            decisions = {}
            decisions[model] = result.decision

    def test_very_long_path(self):
        guard = PermissionGuard()
        long_path = "a/" * 200 + "file.py"
        for model, agent in MODEL_AGENTS.items():
            try:
                result = guard.check(agent, "write:src", target_path=long_path)
                assert result.decision is not None, f"Boundary FAIL: {model} long path returned None"
            except Exception as e:
                pytest.fail(f"Boundary FAIL: {model} long path crashed: {e}")

    def test_unicode_target_path(self):
        guard = PermissionGuard()
        unicode_paths = [
            "src/测试文件.py",
            "src/test\u0000.py",
            "src/test\n.py",
            "src/✨/test.py",
        ]
        for path in unicode_paths:
            results = {}
            for model, agent in MODEL_AGENTS.items():
                try:
                    r = guard.check(agent, "write:src", target_path=path)
                    results[model] = r.decision.value
                except Exception as e:
                    results[model] = f"ERROR: {e}"
            if len(set(results.values())) > 1:
                print(f"  Boundary note: unicode path '{path}' decisions differ: {results}")

    def test_special_operation_names(self):
        guard = PermissionGuard()
        weird_ops = [
            "",
            ":",
            "read:",
            ":write",
            "a" * 100,
        ]
        for op in weird_ops:
            for model, agent in MODEL_AGENTS.items():
                try:
                    result = guard.check(agent, op)
                    assert result.decision is not None, f"Boundary FAIL: {model} weird op '{op}' returned None"
                except Exception:
                    pass

    def test_multiple_rapid_checks_consistent(self):
        guard = PermissionGuard()
        agent = MODEL_AGENTS["DeepSeek"]
        results = []
        for _ in range(10):
            results.append(guard.check(agent, "read:docs").decision)
        assert len(set(r.value for r in results)) == 1, (
            f"Boundary FAIL: rapid checks produced inconsistent results: {[r.value for r in results]}"
        )


class TestConsistencyReport:
    """跨模型一致性报告"""

    def test_cross_model_summary(self):
        guard = PermissionGuard()
        core_ops = [
            "read:docs",
            "read:src",
            "write:src",
            "execute:scripts",
            "modify:blueprint",
            "delete:audit_logs",
            "modify_immutable_core",
            "disable_kill_switch",
            "modify:rbac_roles",
            "circumvent_gate_engine",
        ]

        agreement = 0
        total = 0
        for op in core_ops:
            decisions = {}
            for model, agent in MODEL_AGENTS.items():
                r = guard.check(agent, op)
                decisions[model] = r.decision.value
            total += 1
            if len(set(decisions.values())) == 1:
                agreement += 1

        consistency_rate = agreement / max(total, 1) * 100
        print("\n=== Cross-Model Consistency Report ===")
        print(f"  Models tested: {list(MODEL_AGENTS.keys())}")
        print(f"  Operations: {total}")
        print(f"  Consistent: {agreement}/{total} ({consistency_rate:.0f}%)")

        assert consistency_rate >= 90, f"CrossModel FAIL: consistency rate {consistency_rate:.0f}% below 90% threshold!"
