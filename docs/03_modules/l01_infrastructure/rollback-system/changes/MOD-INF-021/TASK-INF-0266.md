---
task_id: "TASK-INF-0266"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 8.10-8.15 + §6.14 B108-B110 + §6.16 B111-B112 + 决策 D-021-31/32"
title: "取证扩展——git notes 沙箱 + 持续证明链 + 只读 snapshot + Owner 缺席分级 + Feature Flag 分离"
description: |
  实现 Phase 8 Part 3 取证扩展，覆盖 B108-B112：
  B108 git notes 纯文本沙箱——回滚证据可写入 git notes（不污染 git log）
  B109 持续完整证明链——连续 Merkle chain 不可中断
  B110 取证只读 snapshot——取证数据存储在只读 mount (chmod 444 dir)
  B111 人力缺席分级——L3 L1 多层次 Owner absent 分级处置 (exit 31 OWNER_ABSENT_L3 / 32 OWNER_ABSENT_L1)
  B112 Feature Flag 分离——发布与回滚分离：Feature Flag 撒销 ≠ 代码 git revert
  涵盖 R37-R44 治理与人因风险。
priority: "P1"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\forensic.py"
    description: "扩展取证——git notes/证明链/只读/Owner absent 分级/Feature Flag 分离"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\owner_absent.py"
    description: "Owner 缺席——L3 (30m) → L1 (7d) → 无人接管分级处置"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\forensic.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\owner_absent.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
    reason: "本蓝图——§6.14 B108-B110 + §6.16 B111-B112 + D-021-31/32"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 11000
timeout_minutes: 40
acceptance_criteria:
  - "git notes——回滚证据写入 git notes refs/notes/forensic"
  - "持续证明链——每个新回滚追加到 Merkle chain"
  - "只读 snapshot——chmod 444 取证输出目录"
  - "Owner 缺席 L3 (30min) / L1 (7天) → exit 31/32"
  - "Feature Flag 撤销——不执行 git revert 而是 toggle FF → exit 33"
rollback_instructions: |
  1. git checkout HEAD~1 -- D:\\ZephyrAlpha\\src\\zephyr\\rollback\\forensic.py
  2. 删除 D:\\ZephyrAlpha\\src\\zephyr\\rollback\\owner_absent.py
depends_on:
  - "TASK-INF-0265"
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
