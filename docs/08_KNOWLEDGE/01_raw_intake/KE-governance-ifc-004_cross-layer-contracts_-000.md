---
module_id: KE-governance-ifc-004_cross-layer-contracts_-000
title: IFC-004：cross-layer-contracts.yaml 为契约注册表
category: governance
---

# IFC-004：cross-layer-contracts.yaml 为契约注册表

IFC-004：cross-layer-contracts.yaml 为契约注册表

- 格式：YAML，按 contract_id 索引
- 每个条目包含：contract_id / provider / consumers / interface_type / schema_version / status
- 消费者查找契约时，**仅从此注册表查询**，禁止扫描源码推测接口
- **生消流程**：人类/AI 在模块文件中定义契约 schema（IFC-001 六字段）→ 脚本 `validate_module_schema.py --sync-contracts` 将契约条目同步至注册表。注册表是"镜像"，禁止手动编辑——所有变更在源契约文件中进行
