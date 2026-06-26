---
module_id: KE-3128------active-004
status: active
title: P1-48：status 字段值 `active` 不在有效状态集合中
category: test_coverage
ttl: permanent
doc_type: knowledge_entry
---

# P1-48：status 字段值 `active` 不在有效状态集合中

P1-48：status 字段值 `active` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/governance/architecture/phase-transition-protocol.md`
- **矛盾值**：`active`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired
