---
module_id: KE-702
status: active
title: 1.3 责任边界（本标准不管什么）
category: governance
---

# 1.3 责任边界（本标准不管什么）

1.3 责任边界（本标准不管什么）

- 各登记表字段的具体定义 → 以各登记表自身的 `_schema` 为准
- 跨表共享字段的 SSoT 归属 → 以 [registry_of_registries.yaml](../../_registry/catalogs/registry_of_registries.yaml) `cross_registry_rules` 为准
- 登记表存量清单 → 以 [registry-master-index.yaml](../../_registry/catalogs/registry-master-index.yaml) 为准
- AI 操作工具的具体调用方式 → 以 AGENTS.md 为准
- 各类工件的准入审批 → 以对应的准入标准为准（模块=GOV-MOD-001，规则=PS-STD-004，ADR=ADR 治理流程）
- 登记表本身的物理迁移（如 module-registry.yaml → _registry/catalogs/）→ 以 registry-master-index.yaml migration_plan 为准
