---
module_id: KE-558-------experimental------be-000
status: active
title: 9.3 防篡改机制（experimental 轻量 → beta 加强）
category: documentation
ttl: permanent
---

# 9.3 防篡改机制（experimental 轻量 → beta 加强）

9.3 防篡改机制（experimental 轻量 → beta 加强）

- SQLite WAL + 周期全库哈希（每日 00:00 UTC 写入 `audit.db.sha256`）
- 哈希文件 git commit（形成外部锚点）

**beta（接入真实资金）**：

- 哈希链（每条事件 include 前一条事件哈希）
- 异地只读副本（beta upgrade_watchboard 触发）
