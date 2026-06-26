---
module_id: KE-970
title: 6. 废弃级联
category: governance_rule
ttl: permanent
doc_type: knowledge_entry
---

# 6. 废弃级联

6. 废弃级联

| 级联类型 | 触发条件 | 处理方式 |
|---------|---------|---------|
| 依赖级联 | 被废弃规则引用了其他文件 | 依赖方需更新引用或同步废弃 |
| 编号级联 | 废弃规则的 module_id 被引用 | 引用方需更新 module_id |
| 注册表级联 | 废弃规则在注册表中 | 注册表自动更新 status |
