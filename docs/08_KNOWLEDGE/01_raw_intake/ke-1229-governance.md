---
module_id: KE-1142
status: active
title: IFC-005：契约状态转换条件
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# IFC-005：契约状态转换条件

IFC-005：契约状态转换条件

| 转换 | 前置条件 |
|------|---------|
| draft → frozen | provider 模块通过 GOV-MOD-ALPHA_SIGNAL_DOMAIN 准入门禁 + 契约 schema 经 owner 审批 |
| frozen → deprecated | 替代契约已 frozen + 所有 consumers 已迁移 + 至少 30 天通知期 |
| deprecated → archived | 契约从注册表物理删除（保留 audit log） |

- `draft` 阶段契约仅供设计讨论，不受 IFC-003 版本兼容规则约束
- `frozen` 阶段契约受完整版本兼容规则约束（§7）
- `deprecated` 阶段契约禁止新增 consumer 引用
