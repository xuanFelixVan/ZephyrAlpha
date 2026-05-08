---
module_id: KE-module_blu-2__3_trace_spans-000
title: 2. 3 Trace Spans
category: module_blueprint
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
