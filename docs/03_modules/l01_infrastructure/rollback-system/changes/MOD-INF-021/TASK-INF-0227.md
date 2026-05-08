---
task_id: "TASK-INF-0227"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 5.10 + §6.10 B49 + AP13"
title: "JSONL 完整性保护——Merkle 树 + HMAC-SHA256 签名 + 重建前验证"
priority: "P1"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\sqlite_dumper.py"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\sqlite_dumper.py"
    description: "dump 新增行级 SHA-256 hash + Merkle 根 + HMAC-SHA256 签名"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\sqlite_dumper.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
    reason: "本蓝图——B49 完整性保护 + §8 AP13"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 8000
timeout_minutes: 30
acceptance_criteria:
  - "JSONL 每行附带行级 SHA-256 hash（chained hash 链）"
  - "文件末尾 Merkle 根 + HMAC-SHA256 签名"
  - "回滚重建前验证 → 不一致拒绝 → 尝试上一个有效快照"
rollback_instructions: "1. git checkout HEAD~1 -- D:\\ZephyrAlpha\\src\\zephyr\\rollback\\sqlite_dumper.py"
depends_on: ["TASK-INF-0201"]
blocked_by: []
status: "done"
tags_fn: ["infra"]
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo: ["MOD-INF-021"]
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
