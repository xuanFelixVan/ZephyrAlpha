---
module_id: KE-1601
status: active
title: 2. 3 Trace Spans
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2. 3 Trace Spans

2. 3 Trace Spans

```
pipeline_dispatch (root span)
├── module_execute:M3 (child span)
│   └── model_call:deepseek (leaf span)
├── module_execute:M7 (child span)
│   └── model_call:glm (leaf span)
└── ...
```
