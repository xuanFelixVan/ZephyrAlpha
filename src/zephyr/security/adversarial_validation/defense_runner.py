# [BLUEPRINT] MOD-INF-030 | docs/03_modules/_cross_layer/red_blue_validator/blueprint.md | §4.1 + §16 Phase 1
# [MODULE] zephyr.security.adversarial_validation.defense_runner
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.security.adversarial_validation.models; zephyr.gov_audit.finding_model; zephyr.gov_enforcement.rule_enforcement.gate_engine; zephyr.gov_enforcement.rule_enforcement.task_types; zephyr.shared.schema.severity_types; zephyr.shared.schema.execution_model
# [CONSUMERS] validator.py; game_day_runner.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] run_defense() MUST return DefenseResult with passed/gate_id/detail; MUST NOT raise on defense failure — return passed=False instead
# [MODIFY-GUARD] Adding new defense gates MUST update GATE_MAP; DefenseResult contract per blueprint §4.4
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] GateEvaluationError on unregistered gate; DefenseResult.passed=False on blocked attack
# [TESTS] none  # 2026-09-05 AI-00：全仓无测试 import 本模块（原声明路径不存在）
# [A_module] module_id=MOD-INF-030 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


# [ALGO_FLOW] external: docs/03_modules/_domain_security/algo_flow/adversarial_validation/defense_runner.yaml
"""

from __future__ import annotations

import hashlib
import logging
import sys
from typing import Final

from zephyr.security.adversarial_validation.models import AttackScenario, DefenseResult

try:
    from zephyr.gov_audit.finding_model import (
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
    from zephyr.gov_enforcement.rule_enforcement.gate_engine.gate_engine import GateEngine
except ImportError:
    GateEngine = None  # type: ignore[assignment,misc]

logger = logging.getLogger(__name__)

__all__: list[str] = ["DefenseRunner", "GateEvaluationError"]

GATE_MAP: Final[dict[str, str]] = {
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
    error_code = "ZA-SC-0007"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


class DefenseRunner:
    def __init__(self, gate_engine: GateEngine | None = None, jsonl_output: bool = False) -> None:
        if gate_engine is None and GateEngine is not None:
            gate_engine = GateEngine()
        self._gate_engine = gate_engine
        self._results: list[DefenseResult] = []
        self.jsonl_output = jsonl_output

    @property
    def gate_engine(self) -> GateEngine | None:
        """Public accessor for the gate engine (R5: reverse hierarchy)."""
        return self._gate_engine

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

        blocked, source, tool_error = self.evaluate_gate(scenario, gate_id)

        if tool_error:
            # 裁定#359 WP17：工具/入参自身异常 → error 桶，绝不计入 BLOCKED。
            # passed=False 仅表示"防御未能证实成立"，error 字段供上层分桶（TEST_ERROR）。
            detail = f"TOOL_ERROR {gate_id} [{source}]: {tool_error}"
            result = DefenseResult(passed=False, gate_id=gate_id, detail=detail, error=tool_error)
            self._results.append(result)
            logger.error(
                "defense_tool_error scenario_id=%s gate_id=%s source=%s error=%s",
                scenario.scenario_id,
                gate_id,
                source,
                tool_error,
            )
            return result

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

    def evaluate_gate(self, scenario: AttackScenario, gate_id: str) -> tuple[bool, str, str]:
        """三态评估（裁定#359 WP17）：返回 (blocked, source, tool_error)。

        - tool_error 非空：防御评估未能真实执行（Gate 引擎缺失/评估抛异常/入参构造失败）
          → 上层必须计入 error 桶，blocked 恒为 False，绝不计入 BLOCKED（恒真假绿根治）。
        - tool_error 为空：评估真实完成，blocked 为真实判定（含 no_vector 确定性放行分支）。
        """
        if not gate_id or not scenario.injection.vector:
            return False, "no_vector", ""

        outcome, err = self.try_real_gate_detailed(scenario, gate_id)
        if err:
            # 引擎缺失与评估异常统一走 tool_error 桶（原 fail_closed→BLOCKED
            # 语义即裁定#359 D-18 恒真假绿根源，废除）。
            return False, "tool_error", err

        return outcome, "gate_engine", ""

    def _evaluate_gate(self, scenario: AttackScenario, gate_id: str) -> tuple[bool, str, str]:
        """Backward-compatible wrapper. Use evaluate_gate instead (R5: reverse hierarchy)."""
        return self.evaluate_gate(scenario, gate_id)

    def try_real_gate(self, scenario: AttackScenario, gate_id: str) -> bool | None:
        """Backward-compatible wrapper: returns detailed outcome only（None=引擎缺失或异常）。"""
        return self.try_real_gate_detailed(scenario, gate_id)[0]

    def try_real_gate_detailed(self, scenario: AttackScenario, gate_id: str) -> tuple[bool | None, str]:
        """返回 (outcome, tool_error)：outcome=None 且 tool_error 非空 = 工具异常（error 桶）。"""
        if self.gate_engine is None:
            return None, "GateEngine not configured"
        try:
            from datetime import UTC, datetime

            from zephyr.gov_enforcement.rule_enforcement.task_types import Task, TaskNamespace, TaskStatus
            from zephyr.shared.schema.execution_model import ExecutionModel
            from zephyr.shared.schema.severity_types import Priority, SafetyLevel

            task = Task(
                task_id=f"OPS-{abs(hash(scenario.scenario_id)) % 100000:05d}",
                namespace=TaskNamespace.OPS,
                seq=1,
                title=scenario.scenario_id,
                # 裁定#359 WP17 探针实证：description 为 Task 必填字段，缺构造必抛
                # ValidationError（原被宽 except 吞后 fail_closed 计入 BLOCKED=恒真根源之一）。
                # 此处补全为短描述（<100 字，规避 GOV-TASK-001 §2 长描述结构词告警）——
                # 非"补参绕过"：分桶+自检仍是治本主体，本修复仅使真实 gate 评估得以发生
                # （否则 52 场景全数 error 桶，工具零可用）。
                description=f"Adversarial probe {scenario.scenario_id}",
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
            result = self.gate_engine.evaluate(task, gate_id)
            logger.debug("real_gate gate_id=%s passed=%s violations=%d", gate_id, result.passed, len(result.violations))
            return result.passed, ""
        except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
            # 裁定#359 WP17：异常必须显式传递进 error 桶，禁止静默变 None 后被
            # fail-closed 计入 BLOCKED（恒真假绿根源）。
            logger.warning(
                "real_gate_failed gate_id=%s error=%s — routed to error bucket (NOT blocked)",
                gate_id,
                exc,
                exc_info=True,
            )
            return None, f"{type(exc).__name__}: {exc}"

    def _try_real_gate(self, scenario: AttackScenario, gate_id: str) -> bool | None:
        """Backward-compatible wrapper. Use try_real_gate instead (R5: reverse hierarchy)."""
        return self.try_real_gate(scenario, gate_id)

    def simulate_gate(self, scenario: AttackScenario, gate_id: str) -> bool:
        """显式模拟器——tier 分层语义模拟（md5 哈希决定 tier3-6 是否阻断）。

        ⛔ 禁止生产路径（``evaluate_gate``）接线为此方法回退（W3-T2 fail-closed
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

    def _simulate_gate(self, scenario: AttackScenario, gate_id: str) -> bool:
        """Backward-compatible wrapper. Use simulate_gate instead (R5: reverse hierarchy)."""
        return self.simulate_gate(scenario, gate_id)

    def results(self) -> list[DefenseResult]:
        return list(self._results)

    def close(self) -> None:
        if self.gate_engine is not None:
            self.gate_engine.close()
            self._gate_engine = None

    def __enter__(self) -> DefenseRunner:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
