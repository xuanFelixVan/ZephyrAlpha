---
module_id: KE-session_lo-6_3-000
title: 6.3 文件系统契约
category: session_log
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
