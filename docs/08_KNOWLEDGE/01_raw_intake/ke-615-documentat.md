---
module_id: KE-553
status: active
title: 9.2 归档触发与流程
category: documentation
ttl: permanent
---

# 9.2 归档触发与流程

9.2 归档触发与流程

- **触发**：调度器按数据 `ts` 字段超过阈值时，移动到冷层，元数据登记到 archive index
- **可恢复性**：冷层数据必须可在 24h 内重建为温层可查（重测、合规调阅）
- **不可变性**：归档数据走 WORM（Write Once Read Many）存储，对应合规留痕要求
