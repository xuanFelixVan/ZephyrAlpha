---
module_id: KE-4443
title: 5.3 降级路径
category: session_log
---

# 5.3 降级路径

5.3 降级路径

| 场景 | 处理 |
|------|------|
| 文件不存在 | 正常（首次 Session 或已消费）|
| JSON 解析失败 | 写入 `.runtime/sessions/session_carryover.corrupted.<ts>.json`，从零启动 |
| schema_version 不匹配 | 尝试 `_migrate_schema()`；失败则降级到"部分恢复"（仅恢复 open_tasks）|
| 文件过期（`ended_at` > 7 天前）| 展示警告但仍加载；用户可选择清空 |

---
