---
module_id: KE-2575
title: C. AI 执行可靠性
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# C. AI 执行可靠性

C. AI 执行可靠性

##### 盲点 #10 — 幂等性没有强制保证

| 属性 | 值 |
|------|-----|
| 严重性 | **高** |
| 当前状态 | `idempotent: bool` 字段存在但无任何代码检查 |
| 为什么是盲点 | 真正的幂等保证 = 执行前检查产物是否已存在且符合预期，存在则跳过。不实现等于假字段 |
| 解决状态 | ✅ **已在本蓝图 §4.1 解决**——约束 #17：执行前检查 downstream_outputs，幂等跳过 |
| 约束编号 | §4.1 约束 #17 |

##### 盲点 #11 — 缺少 diff-plan 的结构化约束

| 属性 | 值 |
|------|-----|
| 严重性 | **高** |
| 当前状态 | M3 直接生成代码写入文件，依赖 M7 事后审查 |
| 为什么是盲点 | Cursor/v0 的实践表明：AI 先产出 diff plan（"我要改哪些文件，怎么改"）→ 人类/AI 审核通过 → 再实际写入——比"生成完再审查"可靠得多 |
| 解决状态 | ✅ **已在本蓝图 §4.1 解决**——约束 #16：P0/P1 强制 `diff_plan_required=True`，M2 验证 ExecutionPlan → M3 写入 |
| 约束编号 | §4.1 约束 #16 |

##### 盲点 #12 — 缺少执行超时后的自动清理/回滚

| 属性 | 值 |
|------|-----|
| 严重性 | **高** |
| 当前状态 | 超时检查存在，但超时后任务仍是 IN_PROGRESS，已修改的文件处于半完成状态 |
| 为什么是盲点 | 超时不自动处理 → Owner 需要手动 FAILED + 手动回滚 → 1人+AI 维护不可接受 |
| 解决状态 | ✅ **已在本蓝图 §9 解决**——风险 #16：超时→自动 FAILED + checkpoint_path 恢复 + 通知 Owner |
| 约束编号 | §9 风险 #16 |

##### 盲点 #13 — 缺少指数退避 Retry 策略

| 属性 | 值 |
|------|-----|
| 严重性 | **中** |
| 当前状态 | RETRY→IN_PROGRESS 是手动调用，无自动退避 |
| 为什么是盲点 | 专业系统（AWS SDK/Retry Pattern）的标准做法：指数退避（1→2→4→8min）+ 最大重试次数 + 不可重试错误分类 |
| 解决状态 | ✅ **已在本蓝图 §3.2.1 解决**——TaskCard 新增 `retry_count`/`max_retries`/`retry_backoff_seconds` + §4.1 约束 #15 |
| 约束编号 | §4.1 约束 #15 |

##### 盲点 #14 — 缺少上下文窗口溢出保护

| 属性 | 值 |
|------|-----|
| 严重性 | **极高** |
| 当前状态 | 无任何检查 upstream_files + applicable_rules + pipeline prompt 的总 token |
| 为什么是盲点 | DeepSeek 128K 窗口。5 个大 upstream_files + pipeline system prompt 很容易溢出。溢出 = 截断 = 关键信息丢失 = 你以为 AI 读了实际没读——比不读更危险 |
| 解决状态 | ✅ **已在本蓝图 §3.2.1 解决**——TaskCard 新增 `estimated_context_tokens`/`context_window_limit` + §4.1 约束 #13 + M2 裁剪策略 |
| 约束编号 | §4.1 约束 #13 |

##### 盲点 #15 — 缺少 API 断路器（Circuit Breaker）

| 属性 | 值 |
|------|-----|
| 严重性 | **高** |
| 当前状态 | fallback_model 存在但需手动切换 |
| 为什么是盲点 | DeepSeek API 不稳定是常态。自愈系统的基线要求：连续失败 N 次 → 自动熔断 → 期间全部路由 fallback → 半开探测恢复 → 关闭熔断 |
| 解决状态 | ✅ **已在本蓝图 §3.2.1 解决**——TaskCard 新增 `circuit_breaker_open` + §4.1 约束 #14 + §9 风险 #4 |
| 约束编号 | §4.1 约束 #14 |
