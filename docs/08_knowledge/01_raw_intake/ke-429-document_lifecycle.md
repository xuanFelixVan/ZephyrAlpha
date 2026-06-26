---
module_id: KE-388
status: active
title: 5. Document lifecycle / 文档生命周期
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 5. Document lifecycle / 文档生命周期

5. Document lifecycle / 文档生命周期

```
┌────────────────────┐     ┌───────────────────┐     ┌──────────────────┐
│ 19_workspace/      │ ──→ │ 19_workspace/     │ ──→ │ 02_enterprise    │
│ working-designs/   │Stabilize│ review-ready/ │Promote│ /03_modules       │
│ taskbooks/         │     │                   │     │ etc.（canonical）│
│ open-questions/    │     │                   │     │                  │
└────────────────────┘     └───────────────────┘     └─────────┬────────┘
                                                               │
                                                               │ Superseded / 失效替代
                                                               ↓
                                                     ┌──────────────────┐
                                                     │ 99_archive/      │
                                                     │ retired-docs/    │
                                                     └──────────────────┘
```

Status machine / 状态机：`draft → in_discussion → review_ready → active/accepted → superseded/deprecated`

Full status machine spec: `19_development_workspace/structure-and-mapping/discussion-document-standard.md §6.3`

完整状态机规范：`19_development_workspace/structure-and-mapping/discussion-document-standard.md §6.3`

---
