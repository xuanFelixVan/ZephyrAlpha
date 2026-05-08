---
module_id: KE-module_blu-1_2-004
title: 1.2 目标
category: module_blueprint
---

# 1.2 目标

1.2 目标

| # | 目标 | 可衡量标准 |
|---|------|-----------|
| 1 | **合并为一**：MOD-INF-003+004 + 两份场外草稿 + 历史裁定 = 一份自包含蓝图 | 蓝图文件数 3→1，两份旧蓝图 deprecated |
| 2 | **全链路贯通**：意图→草稿→蓝图→任务卡→双管线→脚本系统——每步有输入/输出/门禁 | 每个环节 Schema 完整 |
| 3 | **TaskCard 模型取最优**：基座继承 shared/schemas.py Task（31字段）+ 扩展防漂移 + 父子层级 + 回滚 + 自治字段 | 基座对齐 metadata-registry.md §7 真源——不留两套模型 |
| 4 | **task_id 格式统一为 `{NAMESPACE}-{SEQ}`** | ADR-001 / STD-005 / SRC-042——对标 Jira，自文档 |
| 5 | **路径合规创建**：MTH-013 原则——AI 不得自主决定目录层级 | 所有路径可追溯到索引 |
| 6 | **模型分工明确**：DeepSeek V4 Pro 主力 + GLM 深度审查 + Claude 特种救援 | 分工有基准数据支撑 |
| 7 | **Dogfooding**：任务系统用自身管理自身维护——MOD-INF-006 自身任务是任务卡驱动的 | 本蓝图的施工任务全部通过 task_repo.create() 注册 |
| 8 | **AI 自治边界五级**：定义 Owner 离线时 AI 的权限边界（supervised / semi_autonomous / autonomous / full_auto / emergency_only） | GOV-TASK-004 §AI自治 五级枚举 + 每级允许操作清单 |
| 9 | **全链路可观测**：每个 M 模块执行耗时/Token/成本可追踪，`zalpha status` 一键摘要 | events 表含 module_id + duration_ms，CLI 命令可工作 |
| 10 | **失败自愈**：失败模式自动匹配→应用已知 mitigation，避免同一问题失败两次 | FailurePattern 匹配引擎可用，匹配成功率 > 60% |
| 11 | **执行可靠性三层**：diff-plan 约束 + 并发冲突检测 + 幂等强制检查——在"审查"之前拦住错误 | G1 门禁增加 diff_plan_required / conflict_free / idempotent_check |
| 12 | **API 韧性**：断路器 + 指数退避 + 自动降级——DeepSeek 不可用时系统不卡死 | 断路器状态可查，自动降级延迟 < 5s |
| 13 | **跨模块聚合**：支持多个 Blueprint 的任务按 Phase/Epic 聚合为全局施工视图 | Phase/Epic 字段可用，跨模块查询 < 100ms |
| 14 | **Prompt 质量可追溯**：每个 M 模块的 prompt 有独立版本号，任务记录 prompt_version——出问题时能追溯到是 prompt 还是模型还是数据的问题 | `prompt_diff` / `prompt_rollback` 可用，prompt 变更历史完整 |
| 15 | **失败可精细补偿**：多步骤任务失败后按 Saga 补偿事务逆序撤销，不依赖全量快照 | compensation_steps 自动执行，补偿成功率 > 80% |
| 16 | **质量退化自动发现**：模型输出质量下降 15%+ 时自动检测并回退到上一个好的 snapshot | QualityBaseline 可用，退化检测延迟 < 1个任务周期 |
