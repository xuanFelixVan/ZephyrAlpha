# [BLUEPRINT] MOD-L10-001 | 03_modules/l10_compliance/compliance-core/blueprint.md | §
"""L10 Compliance
=====================================

14 层量化架构 · L10 合规层

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
  - CTR-P1-006  StrategyLifecycleEvent ← L05
  - CTR-P1-009  PerformanceAttributionReport ← L07
  - CTR-P1-012  ComplianceRule         ← L10（规则由本层定义，反馈闭环）

作为生产者（Producer）：
  - CTR-P1-012  ComplianceRule         → L04, L06, L10

作为全局配置消费者（Consumer）：
  - CTR-P1-010  SystemConfiguration    ← L01
  - CTR-P1-013  TelemetryEmitter       ← L12

SSoT: cross-layer-contracts.yaml v3.0

架构归属
--------
LPC 双轨架构 C 轨（业务脊柱 · 带 l<NN>_ 前缀）
架构决策：ADR-0022 目录双轨治理
"""

from __future__ import annotations

from zephyr.l10_compliance.aisg_sandbox import AISGSandbox
from zephyr.l10_compliance.artifact_scanner import (
    ArtifactFinding,
    ArtifactScanner,
    ScanReport,
)
from zephyr.l10_compliance.compliance_manager import ComplianceManagerBase, ComplianceRule
from zephyr.l10_compliance.default_security_gateway import (
    DefaultSecurityGateway,
    ScanFinding,
    SecurityContext,
)
from zephyr.l10_compliance.security_gateway_base import (
    AuditAction,
    AuditDecision,
    ComplianceEngine,
    SecurityGateway,
)

__all__ = ['AISGSandbox', 'ArtifactFinding', 'ArtifactScanner', 'AuditAction', 'AuditDecision', 'ComplianceEngine', 'ComplianceManagerBase', 'ComplianceRule', 'DefaultSecurityGateway', 'ScanFinding', 'ScanReport', 'SecurityContext', 'SecurityGateway', 'aisg_sandbox', 'artifact_scanner', 'compliance_manager', 'default_security_gateway', 'security_gateway_base']
