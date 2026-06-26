---
module_id: KE-540--------experimental-p0-000
status: active
title: 8A.5 日常巡检清单（experimental P0）
category: documentation
ttl: permanent
---

# 8A.5 日常巡检清单（experimental P0）

8A.5 日常巡检清单（experimental P0）

建议每日一次：

- [ ] FLE anomaly 累计 < 5 条（否则启动调查）
- [ ] LSG fail-closed 触发 < 10 次（否则检查策略表）
- [ ] Orc SQLite audit.db 大小 < 100MB（超阈值归档）
- [ ] VMS ChromaDB 持久化大小 < 500MB（TECH-04 upgrade_watchboard）
- [ ] `.runtime/logs/session/` 30 天内无新 incident 文件

---
