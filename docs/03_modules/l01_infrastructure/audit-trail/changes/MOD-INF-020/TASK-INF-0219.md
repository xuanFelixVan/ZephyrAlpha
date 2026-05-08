---
task_id: "TASK-INF-0219"
source_blueprint: "MOD-INF-020"
source_section: "蓝图 §2.2 consistency_check ci_gate + §2.12 ci_integration"

title: "实现 CI 门禁集成——pre-commit hook + G7 任务卡门禁 + JSONL vs SQLite 一致性校验"
description: |
  实现审计系统的 CI/CD 集成：
  1. pre-commit hook: verify_audit_integrity.py（快速模式——仅 Merkle root 检查）
  2. CI 门禁: verify_audit_integrity.py（全量模式——所有 6 项检查）
  3. JSONL vs SQLite 行数一致性校验——每次 CI 启动自动执行
  4. 哈希链连续性 + HMAC 有效性批验
  5. 失败阻断——CI ❌ → 阻止合并 → 通知 Owner
  6. 自愈：索引损坏 → 自动从 JSONL 重建（零人工干预）
  待更新的 .pre-commit-config.yaml hook 条目。
  落地决策 D-020-18 + D-020-02。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
  - "D:\\ZephyrAlpha\\.pre-commit-config.yaml"
  - "D:\\ZephyrAlpha\\scripts\\governance\\verify_audit_integrity.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\.pre-commit-config.yaml"
    description: "追加 audit-integrity-check hook"
  - path: "D:\\ZephyrAlpha\\.github\\workflows\\audit-integrity.yml"
    description: "CI 门禁 workflow——全量 audit integrity check"

allowed_touch:
  - "D:\\ZephyrAlpha\\.pre-commit-config.yaml"
  - "D:\\ZephyrAlpha\\.github\\workflows\\audit-integrity.yml"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\**\\*.py"

applicable_rules:
  - module_id: "GOV-CMP-002"
    section: "AUD-001"
    reason: "CI 门禁审计规则"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
    reason: "§2.2 consistency_check + §2.12 ci_integration"
  - file_path: "D:\\ZephyrAlpha\\.pre-commit-config.yaml"
    reason: "需追加 audit-integrity hook"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 4000
timeout_minutes: 25

acceptance_criteria:
  - "pre-commit run audit-integrity → 快速模式 < 5s"
  - "CI workflow audit-integrity → 全量模式 < 60s（10000条数据）"
  - "完整性失败 → CI ❌ + Owner 通知"
  - "索引损坏 → 自动重建 + CI ✅（自愈后）"
  - "pre-commit 和 CI 使用同一 verify_audit_integrity.py 脚本——只是参数不同"

rollback_instructions: |
  1. 从 .pre-commit-config.yaml 中移除 audit-integrity hook
  2. 删除 .github/workflows/audit-integrity.yml

depends_on:
  - "TASK-INF-0215"
blocked_by: []

status: "done"

tags_fn:
  - "infra"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-020"

completed_gates: []
blocked_gates: {}

artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
