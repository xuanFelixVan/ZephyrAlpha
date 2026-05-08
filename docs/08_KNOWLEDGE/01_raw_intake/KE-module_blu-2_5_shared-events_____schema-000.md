---
module_id: KE-module_blu-2_5_shared-events_____schema-000
title: 2.5 shared-events（事件体 Schema）
category: module_blueprint
---

# 2.5 shared-events（事件体 Schema）

2.5 shared-events（事件体 Schema）

> **修复 B6/B10 盲点**——observer.py 的 emit() 接受裸 dict，消费者不知道 payload 结构。

| 文件 | 职责 |
|------|------|
| `events/event_schemas.py` | **5 个 EventType 对应的 Pydantic V2 frozen Schema** + EVENT_PAYLOAD_MAP |
