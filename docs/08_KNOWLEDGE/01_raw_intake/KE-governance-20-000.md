---
module_id: KE-governance-20-000
title: 20. 字段不重复声明
category: governance
---

# 20. 字段不重复声明

20. 字段不重复声明

本策略定义的字段不重复 PS-STD-001 或其他标准文件中已定义的字段。以下为本策略独有的契约专用字段声明：

| 字段 | 定义位置 | 使用方 |
|------|---------|--------|
| `contract_id` | §5 IFC-001 表 | cross-layer-contracts.yaml |
| `provider` | §5 IFC-001 表 | cross-layer-contracts.yaml |
| `consumers` | §5 IFC-001 表 | cross-layer-contracts.yaml |
| `interface_schema` | §5 IFC-002 | cross-layer-contracts.yaml |

上述字段仅在本文档中定义，不存在跨标准重复定义。
