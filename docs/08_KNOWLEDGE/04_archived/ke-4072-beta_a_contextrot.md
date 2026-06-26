---
module_id: KE-3918--------contextrot--000
title: 15.1 beta a — 核心缺失：ContextRot + Provenance + Eviction
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 15.1 beta a — 核心缺失：ContextRot + Provenance + Eviction

15.1 beta a — 核心缺失：ContextRot + Provenance + Eviction

| 新增文件 | 职责 | 行数 |
|---|---|---|
| context_rot_model.py | n² attention 衰减数学模型 | ~200 |
| context_evictor.py | 三维逐出：优先级×新鲜度×相关性 | ~250 |

升级：context_injector.py 加 provenance、context_budget_tracker.py 接入动态阈值
