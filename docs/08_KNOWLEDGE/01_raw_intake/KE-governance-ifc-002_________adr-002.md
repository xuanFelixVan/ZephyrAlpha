---
module_id: KE-governance-ifc-002_________adr-002
title: IFC-002：接口变更必须走 ADR
category: governance
---

# IFC-002：接口变更必须走 ADR

IFC-002：接口变更必须走 ADR

任何已 `frozen` 的接口契约发生变更，必须创建 KB 决策记录 记录变更决策。

- 非破坏性变更（新增可选字段）：ADR 简要记录即可
- 破坏性变更（删除字段、修改类型）：ADR 必须包含迁移方案和影响分析
