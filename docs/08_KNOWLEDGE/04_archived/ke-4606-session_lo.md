---
module_id: KE-4440
title: 3.1 顶层字段
category: session_log
ttl: permanent
---

# 3.1 顶层字段

3.1 顶层字段

| 字段 | 必填 | 说明 |
|------|:----:|------|
| `schema_version` | ✅ | 版本号。`validate_ssot.py` 会强制校验 |
| `session_id` | ✅ | 唯一 ID，格式 `sess-YYYYMMDD-HHMMSS-<6-char hex>` |
| `started_at` | ⬜ | Session 开始时间（ISO 8601）|
| `ended_at` | ✅ | Session 结束时间 |
| `ended_reason` | ⬜ | 结束原因分类（5 种枚举值）|
| `ide_info` | ⬜ | 当前 IDE 环境信息 |
| `open_tasks` | ✅ | 未完成任务列表（可为空数组）|
| `blockers` | ⬜ | 阻塞事项 |
| `hallucination_events` | ⬜ | 本次 Session 记录到的幻觉事件 |
| `context_state` | ⬜ | Context Engine 运行时状态快照 |
| `token_budget` | ⬜ | Token 用量与余额 |
| `artifacts_pending_review` | ⬜ | 待人工审核的产物文件路径 |
| `user_intentions` | ⬜ | 从用户对话抽取的下一步意图（≤ 5 条）|
| `environment_snapshot` | ⬜ | Git / 测试 / Lint 状态 |
