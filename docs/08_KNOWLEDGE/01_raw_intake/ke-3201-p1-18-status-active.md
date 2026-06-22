---
module_id: KE-3095------active-003
status: active
title: P1-18：status 字段值 `active` 不在有效状态集合中
category: test_coverage
---

# P1-18：status 字段值 `active` 不在有效状态集合中

P1-18：status 字段值 `active` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/meta/rule_lifecycle_and_change_standard.yaml`
- **矛盾值**：`active`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired
