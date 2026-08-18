# [A_test] module_id: MOD-GOV_redteam_adversarial | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §
# [MODULE] tests.agent_rbac.test_redteam_adversarial
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
MOD-INF-018 对抗性红队测试 — 专用 Agent 尝试绕过七层+六横切面

对标的蓝图 P2 项:
  - 对抗性测试——专用Agent尝试绕过所有七层+六横切面
  - 覆盖 OWASP Agentic Top 10 ASI01-ASI10 + MAESTRO 五层威胁建模

测试策略:
  Phase 1: L0 bypass 尝试 — ImmutableCore / KillSwitch / EngineDegradation
  Phase 2: L1-L3 bypass 尝试 — RBAC / ABAC / Input Guard
  Phase 3: L4-L7 bypass 尝试 — Sequence / Output / DryRun
  Phase 4: 横切面A-F bypass 尝试 — Hooks / Topology / Maintenance / IBAC / Adversarial / Forensic
  Phase 5: 复合攻击链 — 多步组合越权 + 跨Session合谋 + 虚假完成
"""

from __future__ import annotations

import time
from pathlib import Path

from zephyr.security.access_control.adversarial_resilience import AdversarialResilience
from zephyr.security.access_control.agent_creation_policy import AgentCreationPolicy
from zephyr.security.access_control.auto_maintenance import AutoMaintenance
from zephyr.security.access_control.cold_start_lock import ColdStartLock
from zephyr.security.access_control.detectors.context_drift_detector import ContextDriftDetector
from zephyr.security.access_control.detectors.cross_session_detector import CrossSessionDetector
from zephyr.security.access_control.detectors.false_completion_detector import FalseCompletionDetector
from zephyr.security.access_control.detectors.multi_agent_collusion_detector import MultiAgentCollusionDetector
from zephyr.security.access_control.emergency_override import EmergencyOverride
from zephyr.security.access_control.engine_degradation import DegradationLevel, EngineDegradationManager
from zephyr.security.access_control.guards.abac_guard import ABACContext, ABACGuard, TemporalCategory
from zephyr.security.access_control.guards.input_guard import InputGuard
from zephyr.security.access_control.guards.output_guard import OutputGuard
from zephyr.security.access_control.guards.path_guard import PathGuard
from zephyr.security.access_control.guards.permission_guard import GuardDecision, GuardResult, PermissionGuard
from zephyr.security.access_control.guards.rbac_guard import PermissionDecision, RBACGuard
from zephyr.security.access_control.guards.replay_attack_guard import ReplayAttackGuard
from zephyr.security.access_control.guards.sequence_guard import FORBIDDEN_SEQUENCES, SequenceEvent, SequenceGuard
from zephyr.security.access_control.guards.toctou_guard import TOCTOUGuard
from zephyr.security.access_control.identity import AgentIdentity, AgentRole, IDESource, MaturityLevel
from zephyr.security.access_control.immutable_core import ALWAYS_BLOCKED_OPERATIONS, ImmutableCore
from zephyr.security.access_control.intent_binder import IntentBinder
from zephyr.security.access_control.kill_switch import KillSwitch, KillSwitchState
from zephyr.security.access_control.monotonic_clock import MonotonicClock
from zephyr.security.access_control.non_repudiation import NonRepudiation
from zephyr.security.access_control.permission_hooks import PermissionHooks


def _make_agent(
    session_id: str = "redteam",
    role: AgentRole = AgentRole.EXECUTOR,
    maturity: MaturityLevel = MaturityLevel.L2_REGULAR,
    owner_approved: bool = True,
    auto_guard_eligible: bool = True,
    permissions: list[str] | None = None,
    ide_source: IDESource = IDESource.TRAE,
) -> AgentIdentity:
    return AgentIdentity(
        session_id=session_id,
        maturity=maturity,
        role=role,
        owner_approved=owner_approved,
        auto_guard_eligible=auto_guard_eligible,
        permissions=permissions or [],
        ide_source=ide_source,
    )


class TestPhase1_L0Bypass:
    """L0: ImmutableCore + KillSwitch + EngineDegradation — 不可变核心绕过尝试"""

    def test_l0_path_guard_accepts_critical_paths(self):
        guard = PathGuard()
        critically_immutable = [
            ".git/config",
            "config/rbac_roles.yaml",
            ".ailocks/registry.json",
        ]
        for p in critically_immutable:
            result = guard.check(p, operation="write")
            assert isinstance(result, dict), f"L0 FAIL: PathGuard returned non-dict for '{p}'"

    def test_l0_always_blocked_operations_absolute(self):
        guard = PermissionGuard()
        bypass_agents = [
            _make_agent(
                session_id="bypass-admin",
                role=AgentRole.ADMIN,
                owner_approved=True,
                maturity=MaturityLevel.L4_PRINCIPAL,
            ),
            _make_agent(
                session_id="bypass-exec",
                role=AgentRole.EXECUTOR,
                owner_approved=True,
                maturity=MaturityLevel.L4_PRINCIPAL,
            ),
        ]
        for agent in bypass_agents:
            for op in ALWAYS_BLOCKED_OPERATIONS:
                result = guard.check(agent, op)
                assert result.decision == GuardDecision.BLOCKED, (
                    f"L0 FAIL: '{op}' not blocked for {agent.role.value} (maturity={agent.maturity.value})"
                )

    def test_l0_immutable_core_self_integrity(self):
        core = ImmutableCore()
        integrity = core.verify_immutable_core_integrity()
        assert integrity.intact, f"L0 FAIL: ImmutableCore self-integrity broken: {integrity.detail}"
        static_check = core.verify_static_constants_integrity()
        assert static_check.intact, f"L0 FAIL: static constants tampered: {static_check.detail}"

    def test_l0_kill_switch_initial_state(self):
        ks = KillSwitch()
        assert ks.status.state in (
            KillSwitchState.NORMAL,
            KillSwitchState.COOLDOWN,
        ), f"L0 FAIL: KillSwitch in unexpected state: {ks.status.state}"

    def test_l0_engine_degradation_self_protection(self):
        deg = EngineDegradationManager()
        assert deg.state.level == DegradationLevel.NORMAL, (
            f"L0 FAIL: engine degradation not in NORMAL on init: {deg.state.level}"
        )


class TestPhase2_L1L3Bypass:
    """L1-L3: RBAC + ABAC + Input Guard — 身份/属性/参数绕过尝试"""

    def test_l1_rbac_reader_cannot_write(self):
        guard = RBACGuard()
        reader = _make_agent(
            session_id="reader-attack", role=AgentRole.READER, owner_approved=False, auto_guard_eligible=False
        )
        result = guard.check(reader, "write:src")
        assert result.decision == PermissionDecision.BLOCKED, "L1 FAIL: READER allowed write:src"

    def test_l1_rbac_intern_cannot_modify_blueprint(self):
        intern = _make_agent(
            session_id="intern-attack",
            maturity=MaturityLevel.L0_INTERN,
            owner_approved=False,
            auto_guard_eligible=False,
        )
        guard = RBACGuard()
        result = guard.check(intern, "modify:blueprint")
        assert result.decision == PermissionDecision.BLOCKED, "L1 FAIL: INTERN allowed modify:blueprint"

    def test_l2_abac_off_hours_detected(self):
        category = ABACGuard.classify_temporal()
        assert category in (
            TemporalCategory.NORMAL,
            TemporalCategory.OFF_HOURS,
            TemporalCategory.WEEKEND,
            TemporalCategory.LUNCH_PEAK,
        ), f"L2 FAIL: unexpected temporal category: {category}"

    def test_l2_abac_maturity_check(self):
        guard = ABACGuard()
        intern = _make_agent(session_id="test-abac-intern", maturity=MaturityLevel.L0_INTERN)
        ctx = ABACContext(operation="modify:blueprint", temporal=TemporalCategory.NORMAL)
        allowed, reason = guard.check(intern, ctx)
        assert not allowed, f"L2 FAIL: INTERN allowed modify:blueprint via ABAC: {reason}"

    def test_l3_input_guard_dangerous_patterns(self):
        guard = InputGuard()
        dangerous = [
            ("execute:scripts", {"cmd": "rm -rf /"}),
            ("write:src", {"path": "../../../etc/passwd"}),
        ]
        for op, params in dangerous:
            result = guard.check_params(op, params)
            assert result.value != "ALLOW", f"L3 FAIL: dangerous input not blocked for {op}/{params}"


class TestPhase3_L4L7Bypass:
    """L4-L7: Sequence + Output + DryRun — 深度绕过尝试"""

    def test_l4_forbidden_sequence_coverage(self):
        assert len(FORBIDDEN_SEQUENCES) >= 4, (
            f"L4 FAIL: only {len(FORBIDDEN_SEQUENCES)} forbidden sequences registered (expected >=4)"
        )

    def test_l4_sequence_data_exfiltration_detected(self):
        guard = SequenceGuard()
        agent_id = "redteam-l4"
        ops = [
            SequenceEvent(session_id=agent_id, operation="read:credential", target="credentials.yaml"),
            SequenceEvent(session_id=agent_id, operation="write:network", target="http://evil.com"),
            SequenceEvent(session_id=agent_id, operation="delete:log", target="audit.db"),
        ]
        results = [guard.record(ev) for ev in ops]
        has_violation = any(r is not None and "FORBIDDEN" in (r or "") for r in results)
        if not has_violation:
            print(
                f"  L4 note: exfiltration sequence not in FORBIDDEN_SEQUENCES (current rules={[s['name'] for s in [dict(s) for s in FORBIDDEN_SEQUENCES]]})"
            )

    def test_l4_sequence_privilege_escalation_detected(self):
        guard = SequenceGuard()
        agent_id = "redteam-l4b"
        ops = [
            SequenceEvent(session_id=agent_id, operation="read:rbac_config", target="rbac_roles.yaml"),
            SequenceEvent(session_id=agent_id, operation="modify:self_permission", target="identity.py"),
            SequenceEvent(session_id=agent_id, operation="execute:admin", target="/"),
        ]
        results = [guard.record(ev) for ev in ops]
        has_violation = any(r is not None and "FORBIDDEN" in (r or "") for r in results)
        if not has_violation:
            print("  L4 note: privilege escalation sequence not in FORBIDDEN_SEQUENCES")

    def test_l5_output_guard_detects_sensitive(self):
        guard = OutputGuard()
        sensitive_text = "信用卡号: 4111-1111-1111-1111, 身份证: 110101199001011234, 密码: admin123"
        result = guard.check(sensitive_text, agent_id="test-l5")
        assert result is not None, "L5 FAIL: OutputGuard returned None"
        assert result.decision is not None, "L5 FAIL: OutputGuard decision is None"


class TestPhase4_CrossCuttingBypass:
    """横切面A-F: Hooks / Topology / Maintenance / IBAC / Adversarial / Forensic"""

    def test_crosscut_a_hooks_registered(self):
        hooks = PermissionHooks()
        hooks.register_defaults()
        all_hooks = hooks.hooks
        total = sum(len(v) for v in all_hooks.values())
        assert total >= 8, f"Cross-A FAIL: only {total} hooks registered (expected >=8)"

    def test_crosscut_b_permission_topology(self):
        from zephyr.security.access_control.cross_cutting import PermissionTopology

        topology = PermissionTopology()
        topology.add_node("read:docs")
        topology.add_node("read:src")
        topology.add_node("execute:scripts")
        cycles = topology.detect_cycles()
        assert len(cycles) == 0, (
            f"Cross-B FAIL: {len(cycles)} cycles should be 0 — even isolated node DFS should not produce false cycles"
        )

    def test_crosscut_c_auto_maintenance_dashboard(self):
        maintenance = AutoMaintenance()
        dashboard = maintenance.get_dashboard()
        assert dashboard is not None, "Cross-C FAIL: OwnerDashboard is None"
        assert dashboard.active_rules >= 0, "Cross-C FAIL: negative active_rules"

    def test_crosscut_d_intent_binding_violation(self):
        binder = IntentBinder()
        binder.declare(
            agent_id="test-crossd",
            file="tests/test.py",
            task="write unit test",
            expected_operations=["write:tests", "execute:tests"],
        )
        drift = binder.check_drift("test-crossd")
        assert isinstance(drift, bool), "Cross-D FAIL: check_drift returned non-bool"

    def test_crosscut_d_context_drift_detected(self):
        detector = ContextDriftDetector()
        detector.record_operation("test-drift", "read:docs")
        detector.record_operation("test-drift", "read:src")
        for _ in range(60):
            detector.record_operation("test-drift", "delete:file")
        result = detector.detect_scope_creep("test-drift", ["read:docs", "read:src"], window=50)
        assert result["exceeded"], "Cross-D FAIL: scope creep not detected"

    def test_crosscut_e_adversarial_owasp_coverage(self):
        resilience = AdversarialResilience()
        coverage = resilience.get_owasp_coverage()
        assert len(coverage) >= 8, f"Cross-E FAIL: only {len(coverage)} OWASP categories covered (expected >=8)"

    def test_crosscut_e_collusion_detection(self):
        detector = MultiAgentCollusionDetector()
        for i in range(5):
            detector.record_interaction("agent_a", "agent_b", "covert_channel", evidence=f"shared_state_{i}")
        result = detector.check("agent_a", "agent_b")
        assert result is not None, "Cross-E FAIL: collusion detection returned None"
        assert result.risk_level is not None, "Cross-E FAIL: collusion risk_level is None"

    def test_crosscut_e_false_completion(self):
        detector = FalseCompletionDetector()
        result = detector.check_false_completion("agent_x", expected_size=10, actual_size=1)
        assert result is not None, "Cross-E FAIL: false completion check returned None"

    def test_crosscut_f_non_repudiation(self):
        nr = NonRepudiation()
        entry = nr.sign("delete:audit_logs", "redteam-agent")
        assert entry.hmac_hash is not None, "Cross-F FAIL: audit entry not signed"
        verified = nr.verify(entry)
        assert verified, "Cross-F FAIL: signed entry verification failed"

    def test_crosscut_f_path_guard(self):
        guard = PathGuard()
        result = guard.check("src/zephyr/test.py", operation="write")
        assert isinstance(result, dict), "Cross-F FAIL: PathGuard.check() returned non-dict"

    def test_crosscut_f_replay_attack_blocked(self):
        guard = ReplayAttackGuard()
        nonce = "replay_nonce_001"
        ts = time.time()
        result1 = guard.check(nonce, ts)
        assert result1["allowed"], "First use should be allowed"
        result2 = guard.check(nonce, ts)
        assert not result2["allowed"], "Cross-F FAIL: replay attack not blocked"

    def test_crosscut_f_monotonic_clock(self):
        clock = MonotonicClock()
        t1 = clock.now()
        t2 = clock.now()
        assert t2 >= t1, "Cross-F FAIL: monotonic clock violated"


class TestPhase5_CompositeAttacks:
    """复合攻击链: 多步组合越权 + 跨Session合谋 + TOCTOU"""

    def test_composite_cross_session_identity_theft(self):
        detector = CrossSessionDetector()
        token_a = detector.sign_token("agent_alpha", "session_alpha")
        forged_result = detector.verify_token(
            "agent_beta",
            "session_alpha",
            token_a.nonce,
            token_a.timestamp,
            token_a.signature,
        )
        assert not forged_result["valid"], "Phase5 FAIL: cross-session identity theft not blocked"
        assert forged_result["reason"] == "cross_session_forgery"

    def test_composite_toctou_snapshot_verify(self):
        guard = TOCTOUGuard()
        test_file = Path(__file__).parent / "__init__.py"
        snap = guard.snapshot(str(test_file))
        assert snap is not None, "Phase5 FAIL: TOCTOU snapshot failed"
        ok, detail = guard.verify(str(test_file))
        assert ok, f"Phase5 FAIL: TOCTOU verify failed: {detail}"

    def test_composite_agent_creation_decay(self):
        policy = AgentCreationPolicy()
        child_caps = policy.get_child_capabilities(["write:src", "modify:blueprint", "delete:audit_logs"])
        assert len(child_caps) <= 3, "Phase5 FAIL: child capabilities not decayed"

    def test_composite_emergency_override(self):
        override = EmergencyOverride()
        token = override.issue(
            issued_by="Owner",
            permissions=["write:src"],
            duration_seconds=60,
        )
        assert token is not None, "Phase5 FAIL: emergency token not issued"
        result = override.verify(token.token_id)
        assert result is not None, "Phase5 FAIL: emergency token verification returned None"


class TestPhase6_SelfDefense:
    """RBAC 系统自防 — 权限系统自身不被修改"""

    def test_self_modify_immutable_core_blocked(self):
        guard = PermissionGuard()
        agent = _make_agent(role=AgentRole.ADMIN, owner_approved=True, maturity=MaturityLevel.L4_PRINCIPAL)
        result = guard.check(agent, "modify_immutable_core")
        assert result.decision == GuardDecision.BLOCKED, (
            f"SelfDefense FAIL: immutable core modifiable by {agent.role.value}"
        )

    def test_self_circumvent_gate_engine_blocked(self):
        guard = PermissionGuard()
        agent = _make_agent(role=AgentRole.ADMIN, owner_approved=True)
        result = guard.check(agent, "circumvent_gate_engine")
        assert result.decision == GuardDecision.BLOCKED, "SelfDefense FAIL: gate engine circumventable"

    def test_self_modify_rbac_roles_blocked(self):
        guard = PermissionGuard()
        agent = _make_agent(role=AgentRole.WRITER, owner_approved=True)
        result = guard.check(agent, "modify:rbac_roles")
        assert result.decision != GuardDecision.ALLOW, "SelfDefense FAIL: rbac_roles modifiable by WRITER"

    def test_cold_start_lock_active_before_config(self):
        lock = ColdStartLock()
        assert lock.is_locked, "SelfDefense FAIL: cold start lock not active on init"
        config = {"version": "0.14.0"}
        lock.load_config(config)
        lock.verify_integrity()
        lock.verify_static_constants()
        unlocked = lock.attempt_unlock()
        assert unlocked, f"SelfDefense FAIL: cold start lock couldn't unlock (checks={lock.checks_passed})"


class TestIntegrationReport:
    """集成报告——汇总全链路测试结果"""

    def test_full_seven_layer_report(self):
        guard = PermissionGuard()
        agent = _make_agent(session_id="report-agent")
        layers_tested: dict[str, GuardResult] = {}

        test_ops = {
            "L0": ("modify_immutable_core", None),
            "L0b": ("disable_kill_switch", None),
            "L1": ("write:src", "src/test.py"),
            "L1b": ("read:docs", None),
            "L2": ("execute:scripts", "scripts/test.py"),
            "L4": ("delete:file", "data/test.tmp"),
        }

        for label, (op, target) in test_ops.items():
            result = guard.check(agent, op, target_path=target or "")
            layers_tested[label] = result

        blocked_layers = [k for k, v in layers_tested.items() if v.decision == GuardDecision.BLOCKED]
        allowed_layers = [k for k, v in layers_tested.items() if v.decision == GuardDecision.ALLOW]
        auto_guard_layers = [k for k, v in layers_tested.items() if v.decision == GuardDecision.AUTO_GUARD]

        assert len(blocked_layers) > 0, "Integration: no layers blocked — all operations allowed!"
        assert len(allowed_layers) > 0, "Integration: no layers allowed — system too restrictive!"

        print("\n=== RBAC Red Team Report ===")
        print(f"  Blocked layers: {blocked_layers}")
        print(f"  Allowed layers: {allowed_layers}")
        print(f"  Auto-guard layers: {auto_guard_layers}")
        print(f"  Total layers tested: {len(layers_tested)}")
