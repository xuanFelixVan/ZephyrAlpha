---
task_id: "TASK-INF-0227"
source_blueprint: "MOD-INF-020"
source_section: "蓝图 §6.3 Cold Start（D-020-13）+ §4.3 证据包导出（D-020-24）+ §4.4 合规映射（D-020-25）+ §6.5 KB投毒防护（D-020-28）+ §2.14 确定性重放（D-020-34）"

title: "实现 Phase beta 综合组件——Cold Start 基线/监管证据包/合规映射/KB 投毒防护/确定性重放/供应链审计"
description: |
  批量实现 Phase beta 阶段的六大组件：
  1. ColdStartBootstrapper(§6.3/D-020-13): scan_git_log() + scan_session_logs() + merge_to_baseline()
     → bootstrap_audit_baseline.jsonl, confidence=low
  2. EvidencePackExporter(§4.3/D-020-24): export_json/pdf/for_regulator(task_id)
     → EvidencePack(FCA五维格式)
  3. ComplianceMap(§4.4/D-020-25): GDPR/HIPAA/EU-AI-Act/NIST-AI-RMF → CI 自动校验覆盖度
  4. KBAuditGate(§6.5/D-020-28): filter_before_kb_ingest() + score_for_kb_trust()
     + detect_constructed_pattern()
  5. DeterministicReplayEngine(§2.14/D-020-34): replay_to() + verify_replay()
     → L1_file_state/L2_git_state/L3_system_config
  6. SupplyChainAudit(§5未独立/D-020-23): 每次 pip/npm install → SHA-256+来源验证事件
  落地 D-020-13/23/24/25/28/34。覆盖 R9/R22/R26/R11/R16。
  覆盖盲点 B19/B21/B35/B37/B54/B58。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\evidence_pack.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\supply_chain.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\models.py"

downstream_outputs:
  - path: "D:\ZephyrAlpha\src\zephyr\drift_detector\cold_start.py"
    description: "ColdStartBootstrapper——git log + session-logs → 历史基线"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\evidence_pack.py"
    description: "EvidencePackExporter——JSON/PDF/FCA证据包导出"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\compliance_map.py"
    description: "ComplianceMap——GDPR/HIPAA/EU-AI-Act/NIST 条款映射"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\kb_audit_gate.py"
    description: "KBAuditGate——审计数据→KB 投毒防护"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\replay.py"
    description: "DeterministicReplayEngine——审计→系统状态重建"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\supply_chain.py"
    description: "SupplyChainAudit——包安装 SHA-256+来源验证"
  - path: "D:\\ZephyrAlpha\\tests\\audit_trail\\test_beta_components.py"
    description: "Phase beta 6组件综合集成测试"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\cold_start.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\evidence_pack.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\compliance_map.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\kb_audit_gate.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\replay.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\supply_chain.py"
  - "D:\\ZephyrAlpha\\tests\\audit_trail\\test_beta_components.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"

applicable_rules:
  - module_id: "GOV-CMP-002"
    section: "AUD-001~004"
    reason: "完整审计追踪规则"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
    reason: "§6.3/§4.3/§4.4/§6.5/§2.14——6组件定义 + D-020-13/23/24/25/28/34"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 16000
timeout_minutes: 100

acceptance_criteria:
  - "ColdStart: git log → ≥100 条 historical entries, confidence=low"
  - "EvidencePack: export_json(task_id) → 含 timeline+decision_dossier+crypto_proofs"
  - "ComplianceMap: CI 自动校验 4 框架覆盖度 → 输出 gap report"
  - "KBAuditGate: trust_score < 0.5 → filtered; anomaly_score > 0.7 → blocked"
  - "Replay: weekly_random 3 time_point replay → SHA-256 一致性 ≥ 80%"
  - "SupplyChain: pip install requests → AUDIT SUPPLY_CHAIN_INSTALL event"
  - "6/6 组件测试通过"

rollback_instructions: |
  1. 删除 6 个组件 .py 文件
  2. 删除 test_beta_components.py

depends_on:
  - "TASK-INF-0224"
  - "TASK-INF-0225"
blocked_by: []

status: "done"

tags_fn:
  - "infra"
  - "compliance"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "beta"
tags_mo:
  - "MOD-INF-020"

completed_gates: []
blocked_gates: {}

artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "semi_autonomous"
autonomy_checklist: []
---
