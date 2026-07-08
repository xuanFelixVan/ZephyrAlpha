# [A_module] module_id=MOD-GOV_zero_knowledge_audit_stub | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L10-001 | docs/03_modules/_domain_compliance/blueprint.md
# [MODULE] zephyr.governance.zero_knowledge_audit_stub
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""D_COMPLIANCE Compliance
=====================================

域量化架构 · D_COMPLIANCE 合规层

职责
----
合规校验引擎：法规约束检查、持仓合规审计、前置审批门禁、监管报告生成。
Phase F — SecurityGateway 三层防御 + ArtifactScanner 已落地。

OCP-004 实现:
  - DefaultSecurityGateway: L1 Prompt Injection + L2 危险代码 + L3 审计追踪
  - ArtifactScanner: S-01~S-06 多类别 artifact 扫描器
  - AISGSandbox: AI Safety Gateway 沙箱模式匹配

CTR 契约依赖声明（承重墙标记）
------------------------------
本层是以下跨层数据契约的来源或目标——Phase B 实现前 MUST 阅读对应 YAML 定义。
任何修改本层接口的行为 MUST 先通过 ContractImpactAnalyzer 评估影响范围。

作为消费者（Consumer）：
  - CTR-P1-006  StrategyLifecycleEvent ← D_PORTFOLIO_CORE
  - CTR-P1-009  PerformanceAttributionReport ← D_REPORTING
  - CTR-P1-012  ComplianceRule         ← D_COMPLIANCE（规则由本层定义，反馈闭环）

作为生产者（Producer）：
  - CTR-P1-012  ComplianceRule         -> D_RISK, D_EXECUTION_CORE, D_COMPLIANCE

作为全局配置消费者（Consumer）：
  - CTR-P1-010  SystemConfiguration    ← 基础设施
  - CTR-P1-013  TelemetryEmitter       ← 遥测

SSoT: cross_layer_contracts.yaml v3.0

架构归属
--------
LPC 双轨架构 C 轨（业务脊柱 · 带 l<NN>_ 前缀）
架构决策： 目录双轨治理
"""

from __future__ import annotations

__all__ = [
    "AISGSandbox",
    "ArtifactFinding",
    "ArtifactScanner",
    "AuditAction",
    "AuditDecision",
    "ComplianceEngine",
    "ComplianceManagerBase",
    "ComplianceRule",
    "DefaultSecurityGateway",
    "ScanFinding",
    "ScanReport",
    "SecurityContext",
    "SecurityGateway",
    "aisg_sandbox",
    "artifact_scanner",
    "compliance_manager",
    "default_security_gateway",
    "security_gateway_base",
]

_LAZY_IMPORTS = {
    "AISGSandbox": ("zephyr.governance.intelligence_governance.aisg_sandbox", "AISGSandbox"),
    "ArtifactFinding": ("zephyr.governance.drift_detection.artifact_scanner", "ArtifactFinding"),
    "ArtifactScanner": ("zephyr.governance.drift_detection.artifact_scanner", "ArtifactScanner"),
    "ScanReport": ("zephyr.governance.drift_detection.artifact_scanner", "ScanReport"),
    "ComplianceManagerBase": ("zephyr.governance.compliance_gate_a6.compliance_manager", "ComplianceManagerBase"),
    "ComplianceRule": ("zephyr.governance.compliance_gate_a6.compliance_manager", "ComplianceRule"),
    "DefaultSecurityGateway": ("zephyr.governance.security_governance.default_security_gateway", "DefaultSecurityGateway"),
    "ScanFinding": ("zephyr.governance.security_governance.default_security_gateway", "ScanFinding"),
    "SecurityContext": ("zephyr.governance.security_governance.default_security_gateway", "SecurityContext"),
    "AuditAction": ("zephyr.governance.security_governance.security_gateway_base", "AuditAction"),
    "AuditDecision": ("zephyr.governance.security_governance.security_gateway_base", "AuditDecision"),
    "ComplianceEngine": ("zephyr.governance.security_governance.security_gateway_base", "ComplianceEngine"),
    "SecurityGateway": ("zephyr.governance.security_governance.security_gateway_base", "SecurityGateway"),
}

_SUBMODULES = {
    "aisg_sandbox": "zephyr.governance.intelligence_governance.aisg_sandbox",
    "artifact_scanner": "zephyr.compliance.artifact_scanner",
    "compliance_manager": "zephyr.compliance.compliance_manager",
    "default_security_gateway": "zephyr.governance.implementations.default_security_gateway",
    "security_gateway_base": "zephyr.compliance.security_gateway_base",
}


def __getattr__(name):
    if name in _LAZY_IMPORTS:
        import importlib

        mod_path, attr_name = _LAZY_IMPORTS[name]
        mod = importlib.import_module(mod_path)
        value = getattr(mod, attr_name)
        globals()[name] = value
        return value
    if name in _SUBMODULES:
        import importlib

        mod = importlib.import_module(_SUBMODULES[name])
        globals()[name] = mod
        return mod
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
