---
module_id: KE-3590
title: 4.4.3 Deferred Queue 机制（激活专用）
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# 4.4.3 Deferred Queue 机制（激活专用）

4.4.3 Deferred Queue 机制（激活专用）

| 属性 | 值 | 说明 |
|------|---|------|
| `max_wait_time` | 72h | 超时后转人工 |
| `retry_interval` | 1h | 每小时重试依赖检查 |
| `on_timeout` | `flag_for_manual_review` | Owner 手动裁定：强制激活 / 标为 BLOCKED / 丢弃 |
