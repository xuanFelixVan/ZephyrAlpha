---
module_id: KE-3117------deprecated-003
status: active
title: P1-38：status 字段值 `deprecated` 不在有效状态集合中
category: test_coverage
ttl: permanent
---

# P1-38：status 字段值 `deprecated` 不在有效状态集合中

P1-38：status 字段值 `deprecated` 不在有效状态集合中

- **检查 ID**：`P1-1`
- **涉及文件**：
  - `docs/01_policies_and_standards/governance/ai/ai_autonomy_authority_registry.yaml`
- **矛盾值**：`deprecated`
- **建议**：将 status 修改为有效值：Draft/Review/Active/Superseded/Deprecated/Retired
