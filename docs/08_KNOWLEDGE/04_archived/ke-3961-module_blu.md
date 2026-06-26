---
module_id: KE-3809
title: 11.1 施工策略
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 11.1 施工策略

11.1 施工策略

| 项目 | 内容 |
|------|------|
| 施工阶段 | 2 个 Phase（scaffold 善后 / experimental 补给——重写三个核心 .py） |
| 施工模式 | **重写型**——v0.2.0 代码（task_id格式/状态机/存储）与 v0.3.0 契约不兼容 |
| 核心风险 | 破坏性变更——core/models.py / blueprint_decomposer.py / task_manager_server.py 需同步重写 |
