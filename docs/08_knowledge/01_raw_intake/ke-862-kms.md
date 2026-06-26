---
module_id: KE-784
status: active
title: 2.1 KMS 知识管道时间轴
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# 2.1 KMS 知识管道时间轴

2.1 KMS 知识管道时间轴

```
┌──────────────────────────────────────────────────────────────────────┐
│   外部文档进入 → 被分类 → 被评估 → 被激活 → 被提取成 KE → 入知识库      │
└──────────────────────────────────────────────────────────────────────┘
       │            │           │           │            │
       ▼            ▼           ▼           ▼            ▼
     [G1]         [G2]         [G3]        [G4]         [G5]
   Ingest      Triage      Evaluate    Activate      Extract
  （吸入）    （分流）    （评估）    （激活）    （提取）
```
