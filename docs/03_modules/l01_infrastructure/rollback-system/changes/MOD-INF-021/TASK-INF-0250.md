---
task_id: "TASK-INF-0250"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 6.19 + §6.12 B74"
title: "外部可验证 Merkle Proof——回滚完整性证明可交付第三方验证"
description: |
  实现外部可验证 Merkle Proof 机制：
  回滚完成后 Merklize 回滚前后的 file tree → 生成 Merkle root hash。
  提供给外部（审计者/第三方）无需访问完整仓库即可验证回滚完整性。
  对标区块链式可验证状态 + Git LFS verifiable-pointer 机制。
  Merkle root 写入回滚审计日志 → 不可伪造。
priority: "P1"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\external_merkle_proof.py"
    description: "外部可验证 Merkle Proof——回滚 file tree Merkle root + 第三方验证"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\external_merkle_proof.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
    reason: "本蓝图——§6.12 B74 Merkle Proof"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 8000
timeout_minutes: 30
acceptance_criteria:
  - "回滚 file tree → Merkle root hash 计算"
  - "外部无需完整仓库即可验证 Merkle root"
  - "Merkle root 写入回滚审计日志——不可伪造"
rollback_instructions: |
  1. 删除 D:\\ZephyrAlpha\\src\\zephyr\\rollback\\external_merkle_proof.py
depends_on:
  - "TASK-INF-0207"
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
