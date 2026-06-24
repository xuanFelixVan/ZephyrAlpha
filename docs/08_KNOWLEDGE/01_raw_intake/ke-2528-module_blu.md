---
module_id: KE-2433
title: 7.2 攻击场景设计
category: module_blueprint
---

# 7.2 攻击场景设计

7.2 攻击场景设计

红方攻击场景必须覆盖修复后的系统边界：

| 攻击类别 | 攻击向量 | 期望蓝方响应 | 对应 Gate |
|---------|---------|-------------|----------|
| **孤儿注入** | 创建一个未注册的 .py 文件，试图通过 G0 Entry Gate | G0 拒绝（RED） | G0 |
| **僵尸复活** | 修改一个已删除的注册表条目，指向不存在的文件 | 注册审计检测到僵尸引用 | G6 |
| **规则漂移** | 修改 `project_rules.md` 中的 RULE 编号，使其与实际不符 | 语义审计检测到结构缺失 | DIM-SEMANTIC |
| **重复注入** | 创建一个与现有函数 95% 相似的新函数 | Code Dedup Engine 阻断 | G0 dedup check |
| **密钥泄露** | 在代码中插入伪密钥字符串 | Secret Leak Scan 阻断 | G0 secret check |
| **Owner 伪造** | 将文件 owner 字段改为不存在的实体 | Owner 唯一性审计检测 | DIM-FIELD |
| **注册表破坏** | 删除 `_registry.yaml` 中的一个条目 | 注册表一致性检测到不一致 | G6 |
