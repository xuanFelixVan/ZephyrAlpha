---
module_id: KE-2115
status: active
title: 3.4 #42: Vacation Mode
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 3.4 #42: Vacation Mode

3.4 #42: Vacation Mode

在 `D:\ZephyrAlpha\config\capacity\owner_offline_protocol.yaml` 中新增 vacation_mode 节：
- 触发：Owner设置 OR 连续72h无响应
- 核心原则：DO NOT BUILD / DO NOT DEPLOY / DO NOT SPEND / DO MONITOR / DO PERSIST
- 每日报告：健康评分/Error Budget消耗/Token消耗/P0告警/度假天数
- 最大14天，回来后24h warm-up期
