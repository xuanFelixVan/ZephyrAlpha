---
module_id: KE-4242
title: A. 任务模型与生命周期
category: module_blueprint
ttl: permanent
---

# A. 任务模型与生命周期

A. 任务模型与生命周期

##### 盲点 #1 — 缺少父子任务层级（Epic→Story→Sub-task）

| 属性 | 值 |
|------|-----|
| 严重性 | **高** |
| 当前状态 | `depends_on` 是扁平列表，无层级语义 |
| 为什么是盲点 | 蓝图拆解生成的 6 个 TASK-INF-XXXX 之间只有线性依赖，无法表达"这个大任务包含 5 个小任务"。父任务状态 = 聚合子任务状态是 Jira/Linear/Asana 的基线功能 |
| 解决状态 | ✅ **已在本蓝图 §3.2.1 解决**——TaskCard 新增 `parent_task_id: str \| None` + 父子状态聚合规则 |
| 约束编号 | §4.1 约束 #10 |

##### 盲点 #2 — 缺少任务执行前 Snapshot / 可执行回滚

| 属性 | 值 |
|------|-----|
| 严重性 | **高** |
| 当前状态 | `rollback_instructions` 是自由文本，AI 无法可靠执行 |
| 为什么是盲点 | bolt.new/Cursor/Replit Agent 都实现了 checkpoint→回退机制。自由文本回滚对 AI 来说不可执行 |
| 解决状态 | ✅ **已在本蓝图 §3.2.1 解决**——TaskCard 新增 `checkpoint_path: str \| None` + FAILED 时自动恢复 |
| 约束编号 | §4.1 约束 #15 |

##### 盲点 #3 — 缺少 SUSPENDED 暂停/恢复状态

| 属性 | 值 |
|------|-----|
| 严重性 | **中** |
| 当前状态 | 10 态状态机中没有暂停状态 |
| 为什么是盲点 | 1人+AI 场景下 Owner 可能中途暂停长任务、两个 AI session 之间需要交接。当前只能 FAILED→RETRY 再从头开始 |
| 解决状态 | ✅ **已在本蓝图 §3.2.1 解决**——状态机增加 SUSPENDED + `suspend_context_json` 字段 + 24h 自动超时 |
| 约束编号 | §4.1 约束 #20 |

##### 盲点 #4 — 缺少 Hook/事件系统

| 属性 | 值 |
|------|-----|
| 严重性 | **中** |
| 当前状态 | 状态变更后的行为硬编码在 PipelineOrchestrator 和 TaskRepository 中 |
| 为什么是盲点 | 无法声明式配置"状态变为 X 时自动做 Y"。所有联动逻辑散落在不同类的 `if status == X: do_Y()` 中 |
| 解决状态 | 🔲 **v0.5.0 规划**——引入 EventHook 声明式注册（`{trigger_status, action, module_id}`），替代硬编码 if-else |
| 约束编号 | 待新增 |
