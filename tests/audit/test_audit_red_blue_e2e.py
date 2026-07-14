# [A_test] module_id: SRC-TST-0363 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-030 | docs/03_modules/_cross_layer/red_blue_validator/blueprint.md | §test-e2e
# [MODULE] tests.test_audit_red_blue_e2e
# [INVARIANTS] e2e tests MUST use real GateEngine/ConstitutionGuard/SteadyState; no mocking core logic; MUST NOT raise on defense failure
# [MODIFY-GUARD] Adding e2e scenarios MUST update this file; do not modify source modules
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;GateEngineError->graceful_fallback
# [TESTS] test_audit_red_blue_e2e.py
# [TTL] task_bound

from __future__ import annotations

import time
from pathlib import Path

import pytest
from zephyr.shared.io.paths import REPO_ROOT

models_mod = pytest.importorskip("zephyr.security.adversarial_validation.models")
dr_mod = pytest.importorskip("zephyr.security.adversarial_validation.defense_runner")
cg_mod = pytest.importorskip("zephyr.security.adversarial_validation.constitution_guard")
ss_mod = pytest.importorskip("zephyr.security.adversarial_validation.steady_state")

AttackScenario = models_mod.AttackScenario
DefenseResult = models_mod.DefenseResult
DefenseSpec = models_mod.DefenseSpec
InjectionSpec = models_mod.InjectionSpec
AttackTier = models_mod.AttackTier
Severity = models_mod.Severity
BlastRadiusLevel = models_mod.BlastRadiusLevel
SteadyStateSummary = models_mod.SteadyStateSummary

DefenseRunner = dr_mod.DefenseRunner
GATE_MAP = dr_mod.GATE_MAP

ConstitutionGuard = cg_mod.ConstitutionGuard
ConstitutionArticle = cg_mod.ConstitutionArticle

SteadyState = ss_mod.SteadyState
DOMAIN_METRICS = ss_mod.DOMAIN_METRICS

try:
    from zephyr.gov_enforcement.rule_enforcement.gate_engine.gate_engine import GateEngine
except ImportError:
    GateEngine = None


def _make_scenario(
    scenario_id: str = "E2E-001",
    tier: AttackTier = AttackTier.TIER_1,
    severity: Severity = Severity.HIGH,
    gate_id: str = "prompt_injection_filter",
    vector: str = "src/zephyr/llm-security/gateway.py",
    constitution_ref: str | None = None,
) -> AttackScenario:
    return AttackScenario(
        scenario_id=scenario_id,
        name=f"E2E scenario {scenario_id}",
        description="End-to-end red-blue validation test scenario",
        tier=tier,
        severity=severity,
        injection=InjectionSpec(
            vector=vector,
            target_module="zephyr.security.llm_defense.llm_security",
            payload="malicious_prompt_injection",
        ),
        expected_defense=DefenseSpec(
            gate_id=gate_id,
            expected="BLOCKED",
            check_runner="defense_runner",
        ),
        blast_radius=BlastRadiusLevel.MODULE,
        constitution_ref=constitution_ref,
    )


@pytest.mark.e2e
class TestDefenseRunnerE2E:
    def test_run_defense_with_gate_engine(self):
        if GateEngine is None:
            pytest.skip("GateEngine not available")
        with GateEngine() as ge:
            runner = DefenseRunner(gate_engine=ge)
            scenario = _make_scenario(
                scenario_id="E2E-DR-001",
                tier=AttackTier.TIER_1,
                gate_id="prompt_injection_filter",
            )
            result = runner.run_defense(scenario)
            assert isinstance(result, DefenseResult)
            assert result.gate_id == GATE_MAP.get("prompt_injection_filter", "prompt_injection_filter")
            assert isinstance(result.passed, bool)
            assert isinstance(result.detail, str)
            assert len(result.detail) > 0
            runner.close()

    def test_run_defense_without_gate_engine_fallback(self):
        runner = DefenseRunner(gate_engine=None)
        runner._gate_engine = None
        scenario = _make_scenario(
            scenario_id="E2E-DR-002",
            tier=AttackTier.TIER_1,
            gate_id="prompt_injection_filter",
        )
        result = runner.run_defense(scenario)
        assert isinstance(result, DefenseResult)
        assert result.passed is True
        assert "fail_closed" in result.detail

    def test_tier1_always_blocked(self):
        runner = DefenseRunner(gate_engine=None)
        runner._gate_engine = None
        for i in range(5):
            scenario = _make_scenario(
                scenario_id=f"E2E-DR-T1-{i:03d}",
                tier=AttackTier.TIER_1,
                gate_id="prompt_injection_filter",
            )
            result = runner.run_defense(scenario)
            assert result.passed is True, f"TIER_1 scenario {scenario.scenario_id} should always be blocked"
        runner.close()

    def test_results_accumulated(self):
        runner = DefenseRunner(gate_engine=None)
        runner._gate_engine = None
        assert runner.results() == []
        scenario_a = _make_scenario(
            scenario_id="E2E-DR-ACC-001",
            tier=AttackTier.TIER_1,
            gate_id="prompt_injection_filter",
        )
        scenario_b = _make_scenario(
            scenario_id="E2E-DR-ACC-002",
            tier=AttackTier.TIER_2,
            gate_id="immutable_core.verify",
        )
        runner.run_defense(scenario_a)
        assert len(runner.results()) == 1
        runner.run_defense(scenario_b)
        assert len(runner.results()) == 2
        ids = [r.gate_id for r in runner.results()]
        assert GATE_MAP.get("prompt_injection_filter", "prompt_injection_filter") in ids
        assert GATE_MAP.get("immutable_core.verify", "immutable_core.verify") in ids
        runner.close()


@pytest.mark.e2e
class TestConstitutionGuardE2E:
    def test_load_constitution(self):
        registry_path = (
            REPO_ROOT
            / "src"
            / "zephyr"
            / "red-blue-validator"
            / "_constitution-registry.yaml"
        )
        guard = ConstitutionGuard(registry_path=registry_path)
        articles = guard.load()
        assert len(articles) > 0
        for article in articles:
            assert isinstance(article, ConstitutionArticle)
            assert article.article_id.startswith("CONST-")
            assert isinstance(article.name, str)
            assert len(article.name) > 0
            assert article.status in ("active", "draft")

    def test_validate_constitution_with_gate_engine(self):
        if GateEngine is None:
            pytest.skip("GateEngine not available")
        registry_path = (
            REPO_ROOT
            / "src"
            / "zephyr"
            / "red-blue-validator"
            / "_constitution-registry.yaml"
        )
        with GateEngine() as ge:
            guard = ConstitutionGuard(registry_path=registry_path, gate_engine=ge)
            guard.load()
            active = guard.get_active()
            assert len(active) > 0
            first_article = active[0]
            result = guard.validate_constitution(first_article.article_id)
            assert isinstance(result, bool)

    def test_validate_constitution_fallback(self):
        registry_path = (
            REPO_ROOT
            / "src"
            / "zephyr"
            / "red-blue-validator"
            / "_constitution-registry.yaml"
        )
        guard = ConstitutionGuard(registry_path=registry_path, gate_engine=None)
        guard.load()
        active = guard.get_active()
        assert len(active) > 0
        first_article = active[0]
        result = guard.validate_constitution(first_article.article_id)
        assert isinstance(result, bool)
        if first_article.defense_action:
            known_actions = {
                "prompt_injection_filter.scan",
                "immutable_core.verify_roles",
                "drift_engine.scan_all",
                "audit-trail.verify_chain",
                "circuit_breaker.hard_check",
                "budget_engine.pre_flight",
                "freeze_manifest.validate",
                "mcp_auth.verify_tool_access",
                "session_audit.verify",
                "kb.verify_provenance",
                "gates_registry.verify_all",
                "route_manifest.validate",
                "event_schemas.validate",
                "migration.verify_checksum",
                "context_budget.enforce",
                "lock_registry.verify_atomicity",
                "secrets.scan_all",
                "error_budget_tracker.report",
                "dependency_registry.detect_cycles",
                "blueprint_registry.audit_status",
                "audit_registration.scan",
                "vector-memory.verify_embeddings",
                "task_repo.verify_schema",
            }
            if first_article.defense_action in known_actions:
                target_map = {
                    "prompt_injection_filter.scan": "src/zephyr/llm-security",
                    "immutable_core.verify_roles": "src/zephyr/agent-rbac",
                    "circuit_breaker.hard_check": "src/zephyr/escalation-engine/circuit_breaker.py",
                    "budget_engine.pre_flight": "src/zephyr/budget-enforcer",
                    "gates_registry.verify_all": "src/zephyr/gov_enforcement/rule_enforcement",
                }
                target = target_map.get(first_article.defense_action)
                if target and Path(target).exists():
                    assert result is True, (
                        f"Article {first_article.article_id} with known existing path should pass fallback check"
                    )

    def test_guard_attack(self):
        registry_path = (
            REPO_ROOT
            / "src"
            / "zephyr"
            / "red-blue-validator"
            / "_constitution-registry.yaml"
        )
        guard = ConstitutionGuard(registry_path=registry_path, gate_engine=None)
        guard.load()
        scenario_with_ref = _make_scenario(
            scenario_id="E2E-CG-001",
            constitution_ref="CONST-001",
        )
        result_with = guard.guard_attack(scenario_with_ref)
        assert isinstance(result_with, bool)
        scenario_without_ref = _make_scenario(
            scenario_id="E2E-CG-002",
            constitution_ref=None,
        )
        result_without = guard.guard_attack(scenario_without_ref)
        assert result_without is True
        scenario_invalid_ref = _make_scenario(
            scenario_id="E2E-CG-003",
            constitution_ref="CONST-NONEXISTENT",
        )
        result_invalid = guard.guard_attack(scenario_invalid_ref)
        assert result_invalid is False


@pytest.mark.e2e
@pytest.mark.filterwarnings("ignore::pytest.PytestUnhandledThreadExceptionWarning")
class TestSteadyStateE2E:
    def test_import_time_real_measurement(self):
        ss = SteadyState()
        metric_def = None
        for domain_metrics in DOMAIN_METRICS.values():
            for m in domain_metrics:
                if m["check"].startswith("import_time:"):
                    metric_def = m
                    break
            if metric_def is not None:
                break
        assert metric_def is not None, "import_time metric must exist in DOMAIN_METRICS"
        value = ss._evaluate_metric(metric_def)
        assert value >= 0, f"import_time measurement returned {value}, expected >= 0"
        assert isinstance(value, float)
        t1 = ss._import_time("zephyr.red_blue_validator")
        time.sleep(0.01)
        t2 = ss._import_time("zephyr.red_blue_validator")
        assert isinstance(t1, float)
        assert isinstance(t2, float)
        assert t1 >= 0
        assert t2 >= 0
        assert abs(t1 - t2) < 500, f"Repeated import_time measurements should be close: t1={t1}ms t2={t2}ms"

    def test_verify_before_after_attack(self):
        ss = SteadyState()
        before = ss.verify_before_attack()
        assert isinstance(before, dict)
        assert len(before) > 0
        for domain, metrics in before.items():
            assert isinstance(domain, str)
            assert isinstance(metrics, dict)
            assert len(metrics) > 0
            for metric_name, value in metrics.items():
                assert isinstance(metric_name, str)
                assert isinstance(value, float)
        summary = ss.verify_after_attack()
        assert isinstance(summary, SteadyStateSummary)
        assert summary.total_metrics > 0
        assert summary.within_threshold + summary.drifted == summary.total_metrics
        assert 0.0 <= summary.drift_rate <= 100.0

    def test_drift_detection(self):
        ss = SteadyState()
        ss._snapshot_before = {
            "compliance": {"rule_coverage": 100.0, "registry_completeness": 30.0},
            "security": {"secret_leak_count": 0.0, "rbac_violations": 0.0},
            "performance": {"import_time_ms": 200.0},
        }
        ss._snapshot_after = {
            "compliance": {"rule_coverage": 50.0, "registry_completeness": 30.0},
            "security": {"secret_leak_count": 10.0, "rbac_violations": 0.0},
            "performance": {"import_time_ms": 200.0},
        }
        summary = ss._compute_drift()
        assert isinstance(summary, SteadyStateSummary)
        assert summary.drifted >= 1, f"Artificially drifted metrics should be detected: drifted={summary.drifted}"
        assert summary.drift_rate > 0.0, (
            f"Drift rate should be positive when metrics changed: rate={summary.drift_rate}"
        )
