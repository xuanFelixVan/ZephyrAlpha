---
module_id: KE-2218
title: 4.1 技术约束
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 4.1 技术约束

4.1 技术约束

| # | 约束 | 原因 |
|---|------|------|
| 1 | Python 3.12+ | Pydantic V2 最低要求 |
| 2 | Pydantic V2 BaseModel——禁止 dataclass | ADR-0040 |
| 3 | 绝对路径——所有路径含 `D:\` | AGENTS.md §5.1 原则 3 |
| 4 | SQLite 唯一持久化数据库 | ADR-0030 |
| 5 | 任务卡 .md + SQLite 双轨制——task_repo.create() 后同步 .md | 机器可查(SQL) + 人可读(md) |
| 6 | 门禁在状态转换前执行 | GOV-TASK-004 §门禁机制 |
| 7 | 任务卡编号 `{NAMESPACE}-{SEQ}`（ADR/CP/KE/STD/DW/SRC/OPS） | metadata_registry.yaml §7.10 |
| 8 | 蓝图 draft/review 状态不得拆卡 | 内容不稳定 |
| 9 | **MTH-013 路径合规创建**——AI 不得自主决定目录层级 | 零自主创建权——必须先查索引 |
| 10 | **TaskCard 模型强制继承 `shared/schemas.py` Task**——禁止独立定义 | SSoT 唯一——Task 类已被 ADR-0030/ADR-0038/task_repo.py 引用 |
| 11 | **WIP（在制品）上限**：同时 IN_PROGRESS 任务 ≤ 5（P0/P1 ≤ 2）——超过时 dispatch() 拒绝 | 防止上下文碎片化 + AI session 冲突——盲点 #6/#8 |
| 12 | **并发文件冲突检测**：dispatch() 前检查所有 IN_PROGRESS 任务的 `allowed_touch` 交集——有交集时拒绝执行，等待前序任务完成 | 防止两个 AI session 覆盖彼此的修改——盲点 #6 |
| 13 | **上下文窗口溢出保护**：M2 装配前计算 estimated_context_tokens，超过 context_window_limit * 0.8 时触发裁剪（优先保留 applicable_rules + blueprint，裁剪 upstream_files 非关键部分） | DeepSeek V4 Pro=128K 窗口，超出→截断→幻觉——盲点 #14 |
| 14 | **API 断路器（Circuit Breaker）**：同一模型连续失败 3 次→自动熔断 5 分钟，期间所有请求自动路由到 fallback_model | DeepSeek API 不稳定是常态——盲点 #15 |
| 15 | **Retry 指数退避**：RETRY→IN_PROGRESS 自动等待 base * 2^(retry_count-1) 秒，max_retries 默认 3 | 盲点 #13 |
| 16 | **diff-plan 强制**：P0/P1 任务的 `diff_plan_required` 强制为 True——M3 生成代码前必须先产出 ExecutionPlan，M2 验证通过后才能写文件 | 比"生成完再审查"更可靠的执行范式——盲点 #11 |
| 17 | **幂等性强制检查**：PENDING/READY→IN_PROGRESS 前检查 downstream_outputs 是否已存在且内容符合预期——若已满足则跳过执行直接 COMPLETED | idempotent 字段的实质化——盲点 #10 |
| 18 | **依赖拓扑排序**：BlueprintDecomposer.decompose() 必须输出拓扑序——检测循环依赖，存在时拒绝拆解 | 盲点 #5 |
| 19 | **优先级链上传播**：若 depends_on 中有 P0/P1，下游任务 effective_priority ≥ 上游最高优先级 | P3 任务阻塞 P0 任务 → P3 实际上是 P0——盲点 #7 |
| 20 | **SUSPENDED 超时自动失败**：SUSPENDED 超过 24h → 自动 FAILED + 通知 Owner | 防止暂停任务永久挂起——盲点 #3 |
| 21 | **Prompt 版本化管理**：M1-M11 的 prompt template 必须语义化版本存储于 `prompts/{module_id}_v{MAJOR}.{MINOR}.{PATCH}.yaml`，禁止硬编码在 Python 代码中。TaskCard.prompt_version 必须记录任务使用的 prompt 版本 | Prompt 是 AI 执行质量的原材料——盲点 #31 |
| 22 | **Saga 补偿事务**：任务执行失败时按 compensation_steps 逆序执行 undo_command。补偿失败→写入 DeadLetter + 通知 Owner。补偿超时（单步>30s）→放弃+通知 Owner | 多步骤任务需要精细补偿而非全量快照——盲点 #32 |
| 23 | **模型质量退化检测**：M7（GLM审查）完成后对比任务 score vs QualityBaseline——偏差>15% 触发 QualityRegressionAlert。连续 3 个任务退化→自动回退到上一个已知好的 model_snapshot | 模型可以"正常调用"但输出质量下降——盲点 #33 |
| 24 | **SLA 时限自动升级**：sla_deadline 超时→SLAWatchdog 自动按 sla_escalation_policy 升级优先级（original_priority 记录初始值）。最多升级到 max_escalation_priority | P4 任务不应被永久遗忘——盲点 #34 |
| 25 | **跨 Session AI 思考态持久化**：AI session 结束前自动保存 thinking_state_json。新 session 接手 IN_PROGRESS 任务时→先读取 thinking_state_json→从断点继续 | Vibe Coding 中 Session 切换是常态——盲点 #41 |
| 26 | **跨任务知识隔离**：PipelineOrchestrator 每个 dispatch() 必须在新的 context window 中启动。执行前注入 neutralization prompt。cross_task_learning 默认 False，只有 Owner 明确允许时才跨任务保留经验 | AI 存在"上下文惯性"——盲点 #35 |
| 27 | **紧急热修复快速通道**：emergency_mode=True 时跳过 G1/G2/G3/G4/G5，仅保留 G0+G6+G7。事后 24h 内自动补跑完整审计（M6-M11）。补充：emer
