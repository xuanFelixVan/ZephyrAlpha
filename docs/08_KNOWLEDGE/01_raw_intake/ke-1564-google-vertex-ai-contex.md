---
module_id: KE-1474---vertex-ai-contex-004
title: 13.2 Google — Vertex AI Context Caching
category: module_blueprint
---

# 13.2 Google — Vertex AI Context Caching

13.2 Google — Vertex AI Context Caching

| 层级 | 特征 | TTL | 用途 |
|---|---|---|---|
| Hot | 高频复用 | 同 session | 当前任务规则 |
| Warm | 跨 session 共享 | 60min | 蓝图、架构 |
| Cold | 长期存储 | permanent | 全量 KE |
