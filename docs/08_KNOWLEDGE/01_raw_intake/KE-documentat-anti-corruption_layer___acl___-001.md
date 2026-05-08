---
module_id: KE-documentat-anti-corruption_layer___acl___-001
title: Anti-Corruption Layer / ACL 三段结构（L00 数据接入）
category: documentation
---

# Anti-Corruption Layer / ACL 三段结构（L00 数据接入）

Anti-Corruption Layer / ACL 三段结构（L00 数据接入）

L00 数据接入采用 ACL 三段架构，解耦外部数据格式与内部 canonical schema：

```
外部券商/数据源 API
    ↓
connectors/（连接器）  ─── 处理网络、认证、原始协议
    ↓
mappers/（映射器）     ─── 数据归一化 → canonical schema
    ↓
adapters/（适配器）     ─── 填充 PIT 三字段，注入 Layer L00 domain context
    ↓
共享契约 (shared/contracts/)
```

**关键约束**：
- mapper 必须输出 `shared/contracts/` canonical schema（含 PIT 三字段：`data_source`、`as_of_date`、`ingestion_ts`）
- 不允许跨 jurisdiction 共享 mapper
- Fallback 激活时必须标记 `data_source_quality_degraded=True`
- `source_quality` 应为 `vetted`（可信）或 `degraded`（降级），前端需据此显示数据新鲜度
