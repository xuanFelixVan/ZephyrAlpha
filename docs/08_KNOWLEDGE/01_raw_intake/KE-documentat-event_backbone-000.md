---
module_id: KE-documentat-event_backbone-000
title: 触发条件（何时引入 Event Backbone）
category: documentation
---

# 触发条件（何时引入 Event Backbone）

触发条件（何时引入 Event Backbone）

- 系统需要支持 **实时 Tick 处理**（当前批处理已无法满足延迟要求）
- 多个消费方需要**同时订阅同一事件**，点对点调用变为扇形（fan-out）
- 引入多个**独立部署的微服务**（超出单进程/单节点范围）
