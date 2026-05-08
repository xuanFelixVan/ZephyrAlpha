---
task_id: "TASK-INF-0215"
source_blueprint: "MOD-INF-020"
source_section: "蓝图 §2.12 外部独立验证端点（决策 D-020-18）"

title: "实现外部独立验证脚本——verify_audit_integrity.py（零依赖 audit_trail/，CI 门禁用）"
description: |
  实现 `scripts/governance/verify_audit_integrity.py` 外部独立验证脚本。
  零依赖 audit_trail/ 模块——仅使用 stdlib hashlib + hmac + json。
  校验项：
  1. 哈希链连续性（从 genesis 遍历到末尾）
  2. HMAC 签名全量验证（使用 ZEPHYR_AUDIT_HMAC_SECRET 环境变量）
  3. Agent Ed25519 签名抽样验证（10% 随机抽样，使用 cryptography 库）
  4. Merkle 根哈希重建对比（读取 .merkle 文件）
  5. JSONL 行数 vs SQLite 索引记录数一致性
  6. 委托链完整性（深度 + 权限缩小）
  CI 集成：pre-commit / CI 门禁触发——失败 → CI ❌ 阻止合并。
  落地决策 D-020-18 + D-020-31。覆盖盲点 B20。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\compliance\\audit-trail-policy.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\scripts\\governance\\verify_audit_integrity.py"
    description: "外部独立验证脚本——零依赖 audit_trail/"
  - path: "D:\\ZephyrAlpha\\tests\\governance\\test_verify_audit_integrity.py"
    description: "验证脚本单元测试——6项检查正确性 + 独立性验证（不 import audit_trail）"

allowed_touch:
  - "D:\\ZephyrAlpha\\scripts\\governance\\verify_audit_integrity.py"
  - "D:\\ZephyrAlpha\\tests\\governance\\test_verify_audit_integrity.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\**\\*.py"
  - "D:\\ZephyrAlpha\\docs\\**\\*.md"

applicable_rules:
  - module_id: "GOV-CMP-002"
    section: "AUD-001"
    reason: "外部验证协议"
  - module_id: "GOV-DOC-002"
    section: "§5.1.2"
    reason: "脚本路径 scripts/governance/ 合规"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
    reason: "§2.12——外部 verifier 设计 + D-020-18 决策"
  - file_path: "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\compliance\\audit-trail-policy.md"
    reason: "GOV-CMP-002——审计操作留痕规则"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 8000
timeout_minutes: 50

acceptance_criteria:
  - "脚本不 import 任何 audit_trail/ 模块（独立性验证通过）"
  - "哈希链断裂 → exit code 1 + 输出断裂行号"
  - "HMAC 伪造 → exit code 1 + 输出失败行号"
  - "Ed25519 签名抽样 10% → 全部通过时 exit 0"
  - "Merkle 根不一致 → exit code 1"
  - "JSONL vs SQLite 行数不一致 → exit code 1"
  - "委托链断裂 → exit code 1 + 输出链断裂位置"
  - "所有检查通过 → exit 0 + stdout 输出 IntegrityReport JSON"

rollback_instructions: |
  1. 删除 verify_audit_integrity.py
  2. 删除 test_verify_audit_integrity.py
  3. 从 .pre-commit-config.yaml 中移除 verify_audit_integrity hook

depends_on:
  - "TASK-INF-0209"
blocked_by: []

status: "created"

tags_fn:
  - "infra"
  - "security"
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
