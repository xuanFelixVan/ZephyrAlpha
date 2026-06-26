---
module_id: KE-2032---h-005
status: active
title: 3.1 #55: External Watchdog + HeartbeatServer (M-42)
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 3.1 #55: External Watchdog + HeartbeatServer (M-42)

3.1 #55: External Watchdog + HeartbeatServer (M-42)

文件：`D:\ZephyrAlpha\src\zephyr\shared\heartbeat_server.py`

- 独立轻量 HTTP 心跳服务（端口 8899）
- `/health` endpoint: 返回 governance_loop_last_eval / error_budget_pct / memory_pct / timestamp
- 外部看门狗配置 `external_watchdog.yaml`：三个选项
  - Option A: 云函数（阿里云/AWS Lambda, 5min HTTP check）
  - Option B: 手机Termux（Python脚本, 5min check）
  - Option C: 死人开关（deadmansswitch.net, TTL=30min, 每5min续期）
- 强制项：Solo Coder场景下，无外部看门狗=系统死亡不会被发现
