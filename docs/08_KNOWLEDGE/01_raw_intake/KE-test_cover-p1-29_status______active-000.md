---
module_id: KE-test_cover-p1-29_status______active-000
title: P1-29：status 字段值 `active` 不在有效状态集合中
category: test_coverage
---

# P1-29：status 字段值 `active` 不在有效状态集合中

P1-29：status 字段值 `active` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/domains/L07_post_trade_analytics/index.md`
- **矛盾值**：`active`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired
