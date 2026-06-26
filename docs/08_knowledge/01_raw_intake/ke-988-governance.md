---
module_id: KE-910
status: active
title: 4.3 前端与后端层的交互约定
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# 4.3 前端与后端层的交互约定

4.3 前端与后端层的交互约定

前端层通过 **L08 Human-AI Interface** 层与后端交互：

```
FE-L3 (API Client) ──HTTP/WS──→ L08 (API Gateway) ──→ L00-L07, L09-L13
```

在架构图中，前端与后端的交互边必须标注 L08 作为边界层。

---
