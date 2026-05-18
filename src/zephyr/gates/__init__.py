# [BLUEPRINT] MOD-INF-007 | 03_modules/_cross_layer/gate-engine/blueprint.md | §
"""
ZephyrAlpha 门禁子包
====================

职责：提供 AI Agent 决策门禁——Agent 执行关键操作前进行合规检查与风险评估。

子模块：
  - circuit_breaker.py           断路器门禁（熔断/恢复状态机）
  - contract_template_manager.py  合约模板管理器
  - gate_engine.py                门禁引擎（通用门禁流程编排）
  - task_completion_gate.py       任务完成门禁（提交前合规检查）
  - g1_ingest.yaml                G1 摄入门禁策略配置
  - g2_triage.yaml                G2 分诊门禁策略配置
  - g3_evaluate.yaml              G3 评估门禁策略配置
  - g4_activate.yaml              G4 激活门禁策略配置
  - g5_extract.yaml               G5 提取门禁策略配置

架构归属：B-track 独立能力，bounded_context: true——所有 Layer 中
的 Gate 操作均通过本子包接口调用，禁止跨层直接操作门禁逻辑。
统一决策入口：任何涉及风险控制的 AI 决策在此汇总评估。
"""
from __future__ import annotations

from . import adaptive_threshold
from . import ai_capability_guard
from . import breaking_change_detector
from . import end_to_end_walkthrough
from . import gate_health
from . import gate_integrity_guard
from . import gate_override
from . import gate_simulator
from . import integration_test_runner
from . import kiss_enforcer
from . import secrets_guard

import importlib
import logging
from typing import Any

logger = logging.getLogger(__name__)

_LAZY_IMPORTS: dict[str, dict[str, str]] = {
    "GateContext": {"module": "zephyr.gates.gate_context", "attr": "GateContext"},
    "GatePipeline": {"module": "zephyr.gates.gate_pipeline", "attr": "GatePipeline"},
    "GateSimulator": {"module": "zephyr.gates.gate_simulator", "attr": "GateSimulator"},
    "GateIntegrityGuard": {"module": "zephyr.gates.gate_integrity_guard", "attr": "GateIntegrityGuard"},
    "AdaptiveThreshold": {"module": "zephyr.gates.adaptive_threshold", "attr": "AdaptiveThreshold"},
    "AuditChainVerifier": {"module": "zephyr.gates.audit_chain_verifier", "attr": "AuditChainVerifier"},
    "GateHealth": {"module": "zephyr.gates.gate_health", "attr": "GateHealth"},
    "GateOverride": {"module": "zephyr.gates.gate_override", "attr": "GateOverride"},
    "SysMasterCompliance": {"module": "zephyr.gates.sys_master_compliance", "attr": "SysMasterCompliance"},
    "trigger_recovery": {"module": "zephyr.gates.drift_detector", "attr": "trigger_recovery"},
    "GateViolation": {"module": "zephyr.gates.gate_types", "attr": "GateViolation"},
    "GateResult": {"module": "zephyr.gates.gate_types", "attr": "GateResult"},
    "GateEngineError": {"module": "zephyr.gates.gate_types", "attr": "GateEngineError"},
    "GateViolationError": {"module": "zephyr.gates.gate_types", "attr": "GateViolationError"},
}

__all__ = [
    'AdaptiveThreshold',
    'AuditChainVerifier',
    'GateContext',
    'GateHealth',
    'GateIntegrityGuard',
    'GateOverride',
    'GatePipeline',
    'GateSimulator',
    'SysMasterCompliance',
    'adaptive_threshold',
    'ai_capability_guard',
    'anti_pattern_guard',
    'audit_chain_verifier',
    'breaking_change_detector',
    'can_i_deploy',
    'capability_checker',
    'cbac_matrix',
    'cdc_broker',
    'circuit_breaker',
    'contract_template_manager',
    'drift_detector',
    'end_to_end_walkthrough',
    'gate_context',
    'gate_engine',
    'gate_types',
    'gate_health',
    'gate_integrity_guard',
    'gate_override',
    'gate_pipeline',
    'gate_simulator',
    'integration_test_runner',
    'kiss_enforcer',
    'risk_ssot',
    'secrets_guard',
    'sys_master_compliance',
    'task_completion_gate',
    'task_types',
    "trigger_recovery",
    "triple_alignment",
    "TripleAlignmentResult",
    "truth_source_validator",
]

_LAZY_IMPORTS["TripleAlignmentResult"] = {"module": "zephyr.gates.triple_alignment", "attr": "TripleAlignmentResult"}
_LAZY_IMPORTS["AlignmentViolation"] = {"module": "zephyr.gates.triple_alignment", "attr": "AlignmentViolation"}


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