---
module_id: KE-governance-2_2_next_stage_entry_criteria_-003
title: 2.2 next_stage_entry_criteria（Stage 准入门）
category: governance
---

# 2.2 next_stage_entry_criteria（Stage 准入门）

2.2 next_stage_entry_criteria（Stage 准入门）

**定义**：进入下一个 stage 前必须同时成立的所有前置条件。

**格式（frontmatter yaml）**：

```yaml
next_phase_entry_criteria:
  - id: ENTRY-N+1-01
    description: "scaffold 的所有 exit_criteria 已通过"
    validator: "scripts/governance/validate_phase_exit.py --phase 0"
    references_exit: [EXIT-0-01, EXIT-0-02, EXIT-0-03]
    machine_verifiable: true
    blocking: true

  - id: ENTRY-N+1-02
    description: "experimental 任务卡已创建且 status=draft 的任务 ≥ N 张"
    validator: "scripts/governance/validate_phase_entry.py --phase 1"
    machine_verifiable: true
    blocking: true

  - id: ENTRY-N+1-03
    description: "影子快照 _reorg_snapshots/snapshot--post/ 已创建"
    validator: "scripts/governance/validate_snapshot.py --label -post"
    machine_verifiable: true
    blocking: true
```

**约束（最严苛的一条）**：

```
钢结构约束（零暗门原则）：
 next_stage_entry_criteria 中的每一项，要么：
   (a) references_exit 指向 stage N-1 的某个 EXIT 条目；
   (b) type: pre-existing 并且满足"已在当前环境中成立 ≥ 72 小时"。
 不允许在 ENTRY 中出现 stage N-1 的 EXIT 没有覆盖的新依赖。
```

这条由 `validate_phase_transition.py --check zero-backdoor` 自动校验。

---
