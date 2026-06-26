---
module_id: KE-1143
status: active
title: IFC-006：模块必须通过契约一致性检查
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# IFC-006：模块必须通过契约一致性检查

IFC-006：模块必须通过契约一致性检查

provider 模块注入和变更时，必须通过契约一致性验证：

- 验证命令：`python scripts/governance/validate_module_schema.py --check-conformance {module_id}`
- 验证内容：
  1. provider 实际暴露的接口是否与契约声明的 schema 一致
  2. 所有 consumers 引用的接口版本是否 ≤ provider 当前版本
  3. 跨层调用的契约是否存在且 frozen
- 失败动作：注入暂停，等待 provider 修正实现或更新契约
