---
module_id: KE-2081
status: active
title: 3.2 不覆盖（→ 去哪）
category: module_blueprint
ttl: permanent
---

# 3.2 不覆盖（→ 去哪）

3.2 不覆盖（→ 去哪）

- AI 审计守卫 → MOD-INF-001（capacity-assurance）
- 安全网关（LSG）→ MOD-INF-014（llm-security）
- 因子计算逻辑 → L02-L03 业务层
- 审计追踪链存储 → MOD-INF-020（audit-trail），RI-13 EventStore 提供事件级溯源，审计追踪链消费事件
- 回滚执行 → MOD-INF-021（rollback-system），RI-13 事件重放可配合回滚
- 任务门禁（G0-G7）→ MOD-INF-007（gate-engine）
- Shared Core 基础设施的实现细节 → MOD-INF-016（shared-core）——本蓝图定义需求，MOD-INF-016 承载实现

---
