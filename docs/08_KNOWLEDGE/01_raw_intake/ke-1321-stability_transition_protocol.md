---
module_id: KE-1233
status: active
title: === Stability Transition Protocol 扩展字段（强制）===
category: governance
ttl: permanent
---

# === Stability Transition Protocol 扩展字段（强制）===

=== Stability Transition Protocol 扩展字段（强制）===
phase: 0                              # 本 stage 编号（0=scaffold, 1=experimental, 2=beta, 3=beta, 4=stable）
phase_name: "治理地基"                # 人类可读名称

exit_criteria:
  - id: EXIT-0-01
    description: "..."
    validator: "..."
    machine_verifiable: true
    blocking: true
  # ... （见 §3 具体内容）

next_phase_entry_criteria:
  - id: ENTRY-1-01
    description: "..."
    validator: "..."
    references_exit: [EXIT-0-01]   # 零暗门原则的追溯字段
    machine_verifiable: true
    blocking: true
  # ... （见 §3 具体内容）

rollback_snapshot_path: "_reorg_snapshots/snapshot--post/"  # 目录已物理删除，2026-05-06 AUDIT-10 确认
phase_acceptance_doc: "docs/09_audit/-acceptance.md"
---
```
