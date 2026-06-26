---
module_id: KE-2146
status: active
title: 3.7 #61: DualChannelAlertManager
category: module_blueprint
ttl: permanent
---

# 3.7 #61: DualChannelAlertManager

3.7 #61: DualChannelAlertManager

文件：`D:\ZephyrAlpha\src\zephyr\shared\dual_channel_alert.py`

- 三通道：primary(飞书Webhook) / secondary(本地文件持久化) / tertiary(终端唤醒)
- `send_and_verify(alert)`: 发送→本地持久化→终端唤醒→等待Owner确认
- `startup_unacknowledged_scan()`: 重启后扫描未确认本地告警
- 关键原则：网络不可靠→本地磁盘可靠
