---
module_id: KE-881
status: active
title: 检查项 4：依赖关系验证
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# 检查项 4：依赖关系验证

检查项 4：依赖关系验证

在声明任何模块依赖关系之前，必须确认依赖方向正确：

- [ ] 依赖方向符合项目分层架构（低层依赖高层是错误的）
- [ ] 我没有创建循环依赖
- [ ] 如果依赖关系不确定，我会标注置信度（L1/L2/L3）
