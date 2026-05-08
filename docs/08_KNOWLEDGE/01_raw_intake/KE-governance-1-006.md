---
module_id: KE-governance-1-006
title: §1 本目录的责任
category: governance
---

# §1 本目录的责任

§1 本目录的责任

`governance/module/` 是 ZephyrAlpha 的**模块治理中心**。这里管的是一切与"模块怎么接入、怎么活着、怎么改、怎么退役"相关的规则。

**正向责任**（本目录管的事）：
1. 模块准入门禁——新增/变更/迁移模块必须满足的条件
2. AI 模型行为铁律——AI 在任何操作中必须遵守的 10 条铁律
3. 模块注入规则——模块注入系统的 YAML 格式规则
4. 模块接口契约——模块对外暴露接口的格式要求
5. 模块生命周期——模块从注册到退役的全过程管理
6. 多登记表同步——模块操作后的多登记表一致性维护
7. 模型上线前 10 条规则——新模型上线前的准入检查事项

**负向责任**（本目录不管的事，去对应目录找）：
- 架构治理（ADR、评审门控）→ `governance/architecture/`
- AI 自治权限注册表 → `governance/ai/ai-autonomy-authority-registry.md`
- 文档命名和路径规范 → `governance/document/`
- 代码实现的模块接口 Schema → `src/zephyr/shared/contracts/`

---
