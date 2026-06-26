---
module_id: KE-2139
title: 3.6 契约版本
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 3.6 契约版本

3.6 契约版本

| 契约部分 | 兼容性 | 说明 |
|---------|:---:|------|
| TaskCard 新增字段 | ✅ 向后兼容 | 不影响已有任务卡 |
| TaskCard 删除/重命名字段 | ❌ 破坏性 | 需 Owner 审批 + 迁移 |
| TaskCard 基座切换（Task类） | ❌ 破坏性（与 v0.2.0） | v0.3.0 与 v0.2.0 TaskCard 不兼容——task_id格式/状态机/标签全变 |
| GateLevel 新增值 | ✅ 向后兼容 | 新门禁不破坏已有逻辑 |
| MCP Tool 新增 | ✅ 向后兼容 | 不影响已有消费者 |
| MCP 输入 Schema 修改 | ⚠️ 需通知 | 消费者需更新参数 |

**变更通知**：破坏性变更→Owner审批+蓝图minor+1。兼容性变更→AI自主+patch+1。

---
