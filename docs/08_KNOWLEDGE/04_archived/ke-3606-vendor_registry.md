---
module_id: KE-3461
title: Vendor Registry / 厂商注册表设计原则
category: documentation
ttl: permanent
---

# Vendor Registry / 厂商注册表设计原则

Vendor Registry / 厂商注册表设计原则

| 原则 | 说明 |
|:---|:---|
| **Namespace 隔离** | 按 asset_class/jurisdiction 分区，避免同一 namespace 内歧义 |
| **多 Vendor 故障转移** | 主厂商异常 → 自动 Fallback 到备用厂商（保持相同 jurisdiction 范围内）|
| **Vendor → Mapper 强制映射** | 所有 Vendor 数据路径必须经过 mapper 归一化后再消费 |
| **交易所退市处理** | 写入 `data_source_quality=degraded` + 记录 audit event |

```yaml
