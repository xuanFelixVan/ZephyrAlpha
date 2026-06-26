---
module_id: KE-783
status: active
title: 2.1 exit_criteria（Stage 退出门）
category: governance
ttl: permanent
---

# 2.1 exit_criteria（Stage 退出门）

2.1 exit_criteria（Stage 退出门）

**定义**：本 stage 结束时必须同时成立的所有条件。

**格式（frontmatter yaml）**：

```yaml
exit_criteria:
  - id: EXIT-N-01
    description: "SSoT Validator (scripts/governance/validate_ssot.py) 对全仓库执行返回 0 (无 P0 违规)"
    validator: "scripts/governance/validate_ssot.py --phase 0 --check exit"
    machine_verifiable: true
    blocking: true

  - id: EXIT-N-02
    description: "所有 stage taskbook 任务卡的 status 字段为 completed"
    validator: "scripts/governance/validate_phase_exit.py --phase 0"
    machine_verifiable: true
    blocking: true

  - id: EXIT-N-03
    description: "用户验收会议纪要已写入 docs/09_audit/phase-N-acceptance.md"
    machine_verifiable: false
    manual: true
    blocking: true
```

**约束**：

| 字段 | 说明 |
|------|------|
| `id` | 格式 `EXIT-<stage>-<seq>`，全仓库唯一 |
| `description` | 中文描述，≤ 200 字 |
| `validator` | 如果 `machine_verifiable: true` 必填，指向可执行脚本 |
| `machine_verifiable` | 布尔值，默认 true |
| `manual` | 如果 `machine_verifiable: false` 必须为 true |
| `blocking` | 布尔值，默认 true；false 表示"警告但不阻塞"（非 P0 项）|
