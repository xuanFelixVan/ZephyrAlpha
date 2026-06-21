---
module_id: KE-1514
status: active
title: 14.2 安全关机 (逆序)
category: module_blueprint
---

# 14.2 安全关机 (逆序)

14.2 安全关机 (逆序)

```
stop信号:  P6→P5→P4→P3→P2→P1 (每步10s grace, 总≤60s)
强制关机:  P6→P1 同时 kill ——保存pending状态到wal
```

---
