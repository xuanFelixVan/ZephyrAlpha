# [A_module] module_id=MOD-GOV_rule_enforcement | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.gov_enforcement.rule_enforcement
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""
ZephyrAlpha 门禁子包
====================

职责：提供 AI Agent 决策门禁——Agent 执行关键操作前进行合规检查与风险评估。

子模块：
  - circuit_breaker.py           断路器门禁（熔断/恢复状态机）
  - contract_template_manager.py  合约模板管理器
  - gate_engine.py                门禁引擎（通用门禁流程编排）
  - task_completion_gate.py       任务完成门禁（提交前合规检查）
  - g1-ingest.yaml                G1 摄入门禁策略配置
  - g2-triage.yaml                G2 分诊门禁策略配置
  - g3-evaluate.yaml              G3 评估门禁策略配置
  - g4-activate.yaml              G4 激活门禁策略配置
  - g5-extract.yaml               G5 提取门禁策略配置

架构归属：B-track 独立能力，bounded_context: true——所有 Layer 中
的 Gate 操作均通过本子包接口调用，禁止跨层直接操作门禁逻辑。
统一决策入口：任何涉及风险控制的 AI 决策在此汇总评估。
"""

from __future__ import annotations

import importlib
import logging
from typing import Any

from . import (
    adaptive_threshold,
    ai_capability_guard,
    breaking_change_detector,
    end_to_end_walkthrough,
    integration_test_runner,
    kiss_enforcer,
    secrets_guard,
)
from .gate_engine import (
    gate_health,
    gate_integrity_guard,
    gate_override,
    gate_simulator,
)

logger = logging.getLogger(__name__)

_LAZY_IMPORTS: dict[str, dict[str, str]] = {
    "GateContext": {"module": "zephyr.governance.rule_enforcement.gate_engine.gate_context", "attr": "GateContext"},
    "GatePipeline": {"module": "zephyr.governance.rule_enforcement.gate_engine.gate_pipeline", "attr": "GatePipeline"},
    "GateSimulator": {"module": "zephyr.governance.rule_enforcement.gate_engine.gate_simulator", "attr": "GateSimulator"},
    "GateIntegrityGuard": {
        "module": "zephyr.governance.rule_enforcement.gate_engine.gate_integrity_guard",
        "attr": "GateIntegrityGuard",
    },
    "AdaptiveThreshold": {
        "module": "zephyr.governance.rule_enforcement.adaptive_threshold",
        "attr": "AdaptiveThreshold",
    },
    "AuditChainVerifier": {
        "module": "zephyr.governance.rule_enforcement.audit_chain_verifier",
        "attr": "AuditChainVerifier",
    },
    "GateHealth": {"module": "zephyr.governance.rule_enforcement.gate_engine.gate_health", "attr": "GateHealth"},
    "GateOverride": {"module": "zephyr.governance.rule_enforcement.gate_engine.gate_override", "attr": "GateOverride"},
    "SysMasterCompliance": {
        "module": "zephyr.shared.contracts.sys_master_compliance",
        "attr": "SysMasterCompliance",
    },
    "trigger_recovery": {"module": "zephyr.governance.rule_enforcement.drift_detector", "attr": "trigger_recovery"},
    "GateViolation": {"module": "zephyr.governance.rule_enforcement.gate_types", "attr": "GateViolation"},
    "GateResult": {"module": "zephyr.governance.rule_enforcement.gate_types", "attr": "GateResult"},
    "GateEngineError": {"module": "zephyr.governance.rule_enforcement.gate_types", "attr": "GateEngineError"},
    "GateViolationError": {"module": "zephyr.governance.rule_enforcement.gate_types", "attr": "GateViolationError"},
}

__all__ = [
    "AdaptiveThreshold",
    "AuditChainVerifier",
    "GateContext",
    "GateHealth",
    "GateIntegrityGuard",
    "GateOverride",
    "GatePipeline",
    "GateSimulator",
    "SysMasterCompliance",
    "TripleAlignmentResult",
    "adaptive_threshold",
    "adversarial_strategies",
    "adversarial_validation",
    "ai_capability_guard",
    "anti_pattern_guard",
    "audit_chain_verifier",
    "breaking_change_detector",
    "can_i_deploy",
    "capability_checker",
    "cbac_matrix",
    "cdc_broker",
    "circuit_breaker",
    "contract_template_manager",
    "drift_detector",
    "end_to_end_walkthrough",
    "gate_context",
    "gate_engine",
    "gate_health",
    "gate_integrity_guard",
    "gate_override",
    "gate_pipeline",
    "gate_simulator",
    "gate_types",
    "integration_test_runner",
    "kiss_enforcer",
    "risk_ssot",
    "secrets_guard",
    "sys_master_compliance",
    "task_completion_gate",
    "task_types",
    "trigger_recovery",
    "triple_alignment",
    "truth_source_validator",
'approval', 'default_quality_gate', 'dlq_retry_policy', 'output_quality_gate', 'pre_flight_gate', 'quality_gate', 'rule_canary_manager', 'rule_debt_auditor', 'rule_engine', 'rule_shadow_runner', 'rule_watcher', 'slo_contract']

_LAZY_IMPORTS["TripleAlignmentResult"] = {
    "module": "zephyr.governance.rule_enforcement.triple_alignment",
    "attr": "TripleAlignmentResult",
}
_LAZY_IMPORTS["AlignmentViolation"] = {
    "module": "zephyr.governance.rule_enforcement.triple_alignment",
    "attr": "AlignmentViolation",
}


def __getattr__(name: str) -> Any:
    if name in _LAZY_IMPORTS:
        info = _LAZY_IMPORTS[name]
        try:
            mod = importlib.import_module(info["module"])
            attr = getattr(mod, info["attr"])
            return attr
        except (ImportError, AttributeError) as e:
            logger.debug("Lazy import failed for %s: %s", name, e)
            raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from None
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
