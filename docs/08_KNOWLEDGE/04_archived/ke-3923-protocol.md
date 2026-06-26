---
module_id: KE-3771------protocol-003
title: 1.3 实施策略：Protocol + 双实现（库化优先，按需服务化）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 1.3 实施策略：Protocol + 双实现（库化优先，按需服务化）

1.3 实施策略：Protocol + 双实现（库化优先，按需服务化）

**关键决策**：定义 `VectorMemoryProtocol` 抽象基类，两种实现共享同一签名，业务层永远依赖 Protocol 而非具体实现，升级时零重写。

```python
