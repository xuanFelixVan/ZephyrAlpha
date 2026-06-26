---
module_id: KE-411-----------adapter-faca-000
status: active
title: 5.2 ACL 选型理由（为何不用 Adapter/Facade）
category: documentation
ttl: permanent
---

# 5.2 ACL 选型理由（为何不用 Adapter/Facade）

5.2 ACL 选型理由（为何不用 Adapter/Facade）

- **Adapter Pattern**：仅做接口签名转换，无法阻止内部模块直接引用外部 Vendor 的数据模型（如 tushare 的 DataFrame 字段结构）
- **Facade Pattern**：简化调用复杂度，但不防止外部 Vendor 的领域模型污染内部
- **ACL（Anti-Corruption Layer）**：在边界处将外部语义完整翻译为内部 canonical schema，内部任何层绝对不接触 Vendor 原始格式 → **防止领域污染**
