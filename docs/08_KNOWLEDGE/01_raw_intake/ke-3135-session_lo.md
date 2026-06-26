---
module_id: KE-3033
status: active
title: 6.3 文件系统契约
category: session_log
ttl: permanent
doc_type: knowledge_entry
---

# 6.3 文件系统契约

6.3 文件系统契约

```
.runtime/sessions/
├── session_carryover.json              # 主文件（最新一次 Session 结束时）
├── session_carryover.json.tmp          # 原子写入的临时文件（正常情况不应存在）
├── session_carryover.corrupted.<ts>.json  # 损坏归档
└── history/                             # （beta+ 可选）历史 carryover 归档
    └── sess-20260424-153000-a1b2c3.json
```

---
