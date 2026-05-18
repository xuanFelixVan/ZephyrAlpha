"""[BLUEPRINT] MOD-INF-028 | docs/03_modules/_cross_layer/semantic-auditor/blueprint.md


[MODULE] zephyr.semantic_auditor


[INVARIANTS] 蓝图 §4 文件清单与代码双向对齐


[MODIFY-GUARD] semantic-auditor/blueprint.md; semantic_auditor/__init__.py __all__


[CONSUMERS] 见蓝图 §4 接口契约


[STABILITY] evolving


[SAFETY] M


[AI_AUTONOMY] ai_modifiable


[ERROR_CONTRACT] SemanticAuditError


[TESTS] tests/semantic_auditor/





semantic_auditor — MOD-INF-028 · 语义审计器


============================================


蓝图: docs/03_modules/_cross_layer/semantic-auditor/blueprint.md


actual_disk_path: src/zephyr/semantic_auditor/





职责


----


  规则文档语义审计——9 阶段管道 / 跨文档引用检测 / LLM Bridge 修复


  整合自 audit_trail/ (MOD-INF-020) 的语义审计相关代码


"""



from __future__ import annotations





from zephyr.semantic_auditor.compliance_map import ComplianceMapper


from zephyr.semantic_auditor.feedback_self_audit import FeedbackSelfAuditor


from zephyr.semantic_auditor.kb_gate import KBAuditGate


from zephyr.semantic_auditor.privacy import PrivacyGuard


from zephyr.semantic_auditor.spec_auditor import record_agent_spec


from zephyr.semantic_auditor.supply_chain import SupplyChainAuditor





from zephyr.semantic_auditor.compliance_map import (


    ComplianceFramework,


    ComplianceRequirement,


    ComplianceMapping,


    ComplianceMapper,


)


from zephyr.semantic_auditor.feedback_self_audit import (


    FeedbackNode,


    SelfReinforcementResult,


    CircularDependencyResult,


    FeedbackSelfAuditor,


)


from zephyr.semantic_auditor.kb_gate import KBWriteCheckResult, PoisoningScanResult, KBAuditGate


from zephyr.semantic_auditor.privacy import (


    PIICategory,


    RedactionPolicy,


    PIIDetection,


    PIIScanResult,


    PrivacyGuard,


    hash_path,


)


from zephyr.semantic_auditor.spec_auditor import record_agent_spec


from zephyr.semantic_auditor.supply_chain import (


    PackageRecord,


    AuditPackageResult,


    IntegrityVerifyResult,


    SupplyChainAuditor,


)












__all__ = [


    'compliance_map',


    'feedback_self_audit',


    'hash_path',


    'kb_gate',


    'privacy',


    'record_agent_spec',


    'spec_auditor',


    'supply_chain',


    'AuditPackageResult',


    'CircularDependencyResult',


    'ComplianceFramework',


    'ComplianceMapper',


    'ComplianceMapping',


    'ComplianceRequirement',


    'FeedbackNode',


    'FeedbackSelfAuditor',


    'IntegrityVerifyResult',


    'KBAuditGate',


    'KBWriteCheckResult',


    'PackageRecord',


    'PIICategory',


    'PIIDetection',


    'PIIScanResult',


    'PoisoningScanResult',


    'PrivacyGuard',


    'RedactionPolicy',


    'SelfReinforcementResult',


    'SupplyChainAuditor',


]