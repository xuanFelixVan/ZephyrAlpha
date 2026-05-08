---
task_id: "TASK-INF-0226"
source_blueprint: "MOD-INF-020"
source_section: "蓝图 §6.1 隐私脱敏（D-020-11）+ §6.2 保留期执行（D-020-12）+ §2.6 三层存储（D-020-10）"

title: "实现数据生命周期管理——三层存储迁移自动化 + 隐私脱敏 + 保留期执行"
description: |
  实现 `src/zephyr/audit_trail/lifecycle.py` 中的 `TierMigrationEngine` + `PrivacyRedactor` + `RetentionEnforcer`：
  - 三层存储 D-020-10：hot(≤7d JSONL, <5ms) → warm(8~90d gzip, <100ms) → cold(>90d Parquet, batch)
  - 隐私脱敏 D-020-11：PII 检测(.env/secrets/credentials/邮箱/手机号) → hash/mask/redaction_policy
  - 保留期执行 D-020-12：dry-run → Owner 审批 → 冷归档检查 → 执行删除 → 元审计记录
  - CoT 文件生命周期：跟随审计分层存储 hot/warm/cold
  
  实现 `scripts/governance/enforce_audit_retention.py` 保留期强制执行脚本。
  落地 D-020-10/11/12。覆盖 R1/R8/R12/R27。覆盖盲点 B12/B13/B11/B63/B64。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\lifecycle.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\lifecycle.py"
    description: "TierMigrationEngine + PrivacyRedactor + RetentionEnforcer"
  - path: "D:\\ZephyrAlpha\\scripts\\governance\\enforce_audit_retention.py"
    description: "保留期强制执行脚本——dry-run+审批+执行+元审计"
  - path: "D:\\ZephyrAlpha\\tests\\audit_trail\\test_lifecycle.py"
    description: "生命周期测试——三层迁移/脱敏/保留期"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\lifecycle.py"
  - "D:\\ZephyrAlpha\\scripts\\governance\\enforce_audit_retention.py"
  - "D:\\ZephyrAlpha\\tests\\audit_trail\\test_lifecycle.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\data\\audit\\**\\*.jsonl"

applicable_rules:
  - module_id: "GOV-CMP-002"
    section: "AUD-004"
    reason: "审计日志存储/保留/脱敏规则"
  - module_id: "GOV-DATA-003"
    section: "全篇"
    reason: "数据保留策略"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
    reason: "§2.6三层存储 + §6.1/§6.2隐私与保留 + D-020-10/11/12"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 10000
timeout_minutes: 60

acceptance_criteria:
  - "hot→warm: >7d JSONL 自动 gzip 压缩迁移——zero data loss"
  - "warm→cold: >90d JSONL 自动转 Parquet——snappy+zstd 压缩"
  - "PII 检测：file_path 含 'secrets' → redaction=hashed"
  - "Retention: dry_run → 生成报告；enforce(token) → 执行删除"
  - "迁移/删除前 SHA-256 验证 + 迁移/删除后元审计事件写入"
  - "AES-256-GCM 透明加密层——写入前加密 + key 派生自 HMAC secret"

rollback_instructions: |
  1. 删除 lifecycle.py + enforce_audit_retention.py
  2. 删除 test_lifecycle.py
  3. 从 warm/cold 目录移除测试迁移数据

depends_on:
  - "TASK-INF-0217"
blocked_by: []

status: "created"

tags_fn:
  - "infra"
  - "data"
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
