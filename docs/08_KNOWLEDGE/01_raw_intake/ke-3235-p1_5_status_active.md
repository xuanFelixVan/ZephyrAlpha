---
module_id: KE-3129------active-001
status: active
title: P1-5：status 字段值 `active` 不在有效状态集合中
category: test_coverage
---

# P1-5：status 字段值 `active` 不在有效状态集合中

P1-5：status 字段值 `active` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/02_enterprise_architecture/ssot-authority-map.md`
- **矛盾值**：`active`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired
