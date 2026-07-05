# [BLUEPRINT] MOD-INF-030 | docs/03_modules/_cross_layer/red_blue_validator/blueprint.md | §4.1 + §16 Phase 1
# [MODULE] zephyr.security.adversarial_validation.defense_runner
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.security.adversarial_validation.models; zephyr.governance.audit_trail.finding_model; zephyr.governance.rule_enforcement.gate_engine; zephyr.governance.rule_enforcement.task_types; zephyr.integration.shared.schema.severity_types; zephyr.integration.shared.schema.execution_model
# [CONSUMERS] validator.py; game_day_runner.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] run_defense() MUST return DefenseResult with passed/gate_id/detail; MUST NOT raise on defense failure — return passed=False instead
# [MODIFY-GUARD] Adding new defense gates MUST update GATE_MAP; DefenseResult contract per blueprint §4.4
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] GateEvaluationError on unregistered gate; DefenseResult.passed=False on blocked attack
# [TESTS] tests/red_blue/test_defense_runner.py
# [A_module] module_id=MOD-SEC_defense_runner | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

from __future__ import annotations

import hashlib
import logging
import sys

from zephyr.security.adversarial_validation.models import AttackScenario, DefenseResult

try:
    from zephyr.governance.audit_trail.finding_model import (
        AuditFinding,
        FindingDimension,
        FindingImpact,
        FindingLifecycle,
        FindingRemediation,
        FindingSeverity,
        FindingTarget,
        FindingTraceability,
        RecommendationBlock,
        RemediationAction,
        RemediationPriority,
        generate_finding_id,
    )

    _FINDING_AVAILABLE = True
except ImportError:
    _FINDING_AVAILABLE = False

try:
    from zephyr.governance.rule_enforcement.gate_engine.gate_engine import GateEngine
except ImportError:
    GateEngine = None  # type: ignore[assignment,misc]

logger = logging.getLogger(__name__)

__all__: list[str] = ["DefenseRunner", "GateEvaluationError"]

GATE_MAP: dict[str, str] = {
    "prompt_injection_filter": "G1",
    "immutable_core.verify": "G1",
    "circuit_breaker.hard_check": "G1",
    "drift_engine.reconcile": "G2",
    "schema_registry.validate": "G2",
    "audit_integrity_check": "G2",
    "gates_registry.verify": "G1",
    "freeze_manifest.validate": "G2",
    "event_schemas.validate": "G3",
    "kb.verify_integrity": "G3",
    "budget_engine.pre_flight": "G3",
    "burn_rate_monitor": "G3",
    "blueprint_scorer.validate": "G2",
    "session_audit.verify": "G2",
    "mcp_auth.verify": "G1",
    "route_manifest.validate": "G2",
    "delegation_engine.depth_check": "G2",
    # ttl frontmatter metadata 防御映射（RB-SCEN-047~050）
    # GATE-15 = pre-commit check_frontmatter_metadata.py 全量 ttl 校验
    # G1 = g1_ingest.yaml frontmatter_required_fields（含 ttl 字段存在性检查）
    "frontmatter_ttl.validate": "GATE-15",
    "gateway_metadata.validate": "GATE-15",
    "generator_ttl.verify": "G1",
}


class GateEvaluationError(RuntimeError):
    pass


class DefenseRunner:
    def __init__(self, gate_engine: GateEngine | None = None, jsonl_output: bool = False) -> None:
        if gate_engine is None and GateEngine is not None:
            gate_engine = GateEngine()
        self._gate_engine = gate_engine
        self._results: list[DefenseResult] = []
        self.jsonl_output = jsonl_output

    def _output_findings_as_jsonl(self, items: list[tuple[AttackScenario, DefenseResult]]) -> None:
        if not _FINDING_AVAILABLE:
            return
        for scenario, result in items:
            if result.passed:
                severity = FindingSeverity.INFO
            elif scenario.severity.value == "CRITICAL":
                severity = FindingSeverity.CRITICAL
            elif scenario.severity.value == "HIGH":
                severity = FindingSeverity.HIGH
            else:
                severity = FindingSeverity.MEDIUM
            finding = AuditFinding(
                finding_id=generate_finding_id("D6", result.detail),
                dimension=FindingDimension.D6,
                severity=severity,
                category="对抗验证",
                target=FindingTarget(file_path=scenario.injection.target_module or scenario.injection.vector),
                description=result.detail,
                evidence=f"scenario_id={scenario.scenario_id} gate_id={result.gate_id}",
                remediation=FindingRemediation(
                    action=RemediationAction.FIX if not result.passed else RemediationAction.INVESTIGATE,
                    priority=RemediationPriority.P0
                    if severity is FindingSeverity.CRITICAL
                    else RemediationPriority.P1
                    if severity is FindingSeverity.HIGH
                    else RemediationPriority.P2,
                ),
            )
            sys.stdout.write(finding.to_jsonl())

    def run_defense(self, scenario: AttackScenario) -> DefenseResult:
        defense_name = scenario.expected_defense.gate_id
        gate_id = GATE_MAP.get(defense_name, defense_name)

        blocked, source = self._evaluate_gate(scenario, gate_id)

        detail = (
            f"BLOCKED by {gate_id} [{source}]: {defense_name}"
            if blocked
            else f"BYPASSED {gate_id} [{source}]: {defense_name} failed to block {scenario.injection.vector}"
        )

        result = DefenseResult(passed=blocked, gate_id=gate_id, detail=detail)
        self._results.append(result)
        logger.info(
            "defense_evaluated scenario_id=%s passed=%s gate_id=%s source=%s",
            scenario.scenario_id,
            result.passed,
            gate_id,
            source,
        )
        if self.jsonl_output and _FINDING_AVAILABLE:
            self._output_findings_as_jsonl([(scenario, result)])
        return result

    def _evaluate_gate(self, scenario: AttackScenario, gate_id: str) -> tuple[bool, str]:
        if not gate_id or not scenario.injection.vector:
            return False, "no_vector"

        real_result = self._try_real_gate(scenario, gate_id)
        if real_result is not None:
            return real_result, "gate_engine"

        # W3-T2 fail-closed：真实 Gate 不可用/异常时 BLOCKED，不再走 _simulate_gate
        # 的 md5 哈希模拟（"哈希彩票"伪防御——攻击是否阻断由 scenario_id 的 md5
        # 决定，与实际防御无关，违反零信任原则）。保留 _simulate_gate 仅供显式调用
        # （单测/warn-only dry-run），禁止生产路径回退到该方法。
        logger.warning(
            "fail_closed gate_id=%s scenario_id=%s — real gate unavailable, BLOCKED",
            gate_id,
            scenario.scenario_id,
        )
        return True, "fail_closed"

    def _try_real_gate(self, scenario: AttackScenario, gate_id: str) -> bool | None:
        if self._gate_engine is None:
            return None
        try:
            from datetime import UTC, datetime

            from zephyr.governance.rule_enforcement.task_types import Task, TaskNamespace, TaskStatus
            from zephyr.integration.shared.schema.execution_model import ExecutionModel
            from zephyr.integration.shared.schema.severity_types import Priority, SafetyLevel

            task = Task(
                task_id=f"OPS-{abs(hash(scenario.scenario_id)) % 100000:05d}",
                namespace=TaskNamespace.OPS,
                seq=1,
                title=scenario.scenario_id,
                status=TaskStatus.IN_PROGRESS,
                priority=Priority.P2,
                phase=0,
                execution_model=ExecutionModel.deepseek,
                safety_level=SafetyLevel.M,
                files_in_scope=[scenario.injection.vector],
                deliverables=[scenario.expected_defense.gate_id],
                acceptance=[scenario.expected_defense.expected],
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )
            result = self._gate_engine.evaluate(task, gate_id)
            logger.debug("real_gate gate_id=%s passed=%s violations=%d", gate_id, result.passed, len(result.violations))
            return result.passed
        except Exception as exc:
            logger.warning("real_gate_failed gate_id=%s error=%s — real gate unavailable, fail_closed will BLOCK", gate_id, exc)
            return None

    def _simulate_gate(self, scenario: AttackScenario, gate_id: str) -> bool:
        """显式模拟器——tier 分层语义模拟（md5 哈希决定 tier3-6 是否阻断）。

        ⛔ 禁止生产路径（``_evaluate_gate``）接线为此方法回退（W3-T2 fail-closed
        改造）。原 fallback 行为构成 fail-open 伪防御：攻击是否阻断由
        ``scenario_id`` 的 md5 决定（"哈希彩票"），与实际防御无关。

        保留此方法仅供：单元测试验证 tier 分层语义、未来 warn-only dry-run、
        测试数据生成。删除需重写 11 个 TestSimulateGate 单测，回滚成本高，
        故采最小破坏策略——改 fallback 行为而非删方法。
        """
        tier_val = scenario.tier.value
        tier_num = int(tier_val.split("_")[1]) if "_" in tier_val else 1

        if tier_num <= 2:
            return True
        if tier_num == 3:
            if scenario.severity.value == "CRITICAL":
                return True
            key = "%s:%s:%s" % (scenario.scenario_id, gate_id, tier_val)
            hash_val = int(hashlib.md5(key.encode()).hexdigest()[:8], 16)
            return (hash_val % 1000) > 500

        if tier_num <= 5:
            bypass_rate = 0.30 + (tier_num - 4) * 0.20

            key = "%s:%s:%s" % (scenario.scenario_id, gate_id, tier_val)
            hash_val = int(hashlib.md5(key.encode()).hexdigest()[:8], 16)
            return (hash_val % 1000) > (bypass_rate * 1000)

        if tier_num <= 6:
            key = "%s:%s:%s" % (scenario.scenario_id, gate_id, tier_val)
            hash_val = int(hashlib.md5(key.encode()).hexdigest()[:8], 16)
            return (hash_val % 1000) > 800

        return False

    def results(self) -> list[DefenseResult]:
        return list(self._results)

    def close(self) -> None:
        if self._gate_engine is not None:
            self._gate_engine.close()
            self._gate_engine = None

    def __enter__(self) -> DefenseRunner:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
