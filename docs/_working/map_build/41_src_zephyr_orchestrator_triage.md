---
ttl: task_bound
completes_when: 孤儿分诊战役终裁落地（chief 终审+处置执行）后本册随 30/31 号转归档
title: 孤儿分诊证据包：src.zephyr.orchestrator（47 台）
owner: st-orphtriage-20261004
---

# 41 号·分诊证据包：src.zephyr.orchestrator（47 台）

> 宇宙口径=裁定#481；数据真源=30_attribution_table.yaml（join checker 机生）；处置=证据班建议，终裁归 GLM-5.3 chief，退役执行归 Owner 门位。
>
> tier 分布：suspect_orphan=3，wired=11，wired_by_header=32，wired_dynamic=1；初判汇总：dispute=3，mount=44

## 逐台证据（四字段+初判）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `src/zephyr/orchestrator/fault_tolerance/__init__.py` | fault_tolerance — orchestrator fault_tolerance subpackage. | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→GOMAP（编排域） ②retire→Owner 门位） |
| `src/zephyr/orchestrator/governance/__init__.py` | governance — orchestrator governance subpackage. | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→GOMAP（编排域） ②retire→Owner 门位） |
| `src/zephyr/orchestrator/quality/__init__.py` | quality — orchestrator quality subpackage. | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→GOMAP（编排域） ②retire→Owner 门位） |
| `src/zephyr/orchestrator/contracts/construction_guide.py` | 施工指南引擎（Construction Guide） | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（编排域）（活线在身未挂线） |
| `src/zephyr/orchestrator/contracts/contract_registry.py` | 集成契约注册表（Contract Registry） | 2026-09-16（18天） | in=2/out=0·wired | **mount**→GOMAP（编排域）（活线在身未挂线） |
| `src/zephyr/orchestrator/contracts/contract_router.py` | 契约路由（Contract Router） | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（编排域）（活线在身未挂线） |
| `src/zephyr/orchestrator/contracts/design_decisions.py` | （无文档头，按文件名语义：design_decisions） | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（编排域）（活线在身未挂线） |
| `src/zephyr/orchestrator/contracts/prompt_version.py` | AI Prompt 版本控制（CT-PROMPT-VERSION）——prompt template版本化+部署前diff。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（编排域）（活线在身未挂线） |
| `src/zephyr/orchestrator/core/__init__.py` | orchestrator.core — auto-generated package init. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（编排域）（活线在身未挂线） |
| `src/zephyr/orchestrator/core/task_queue.py` | ActiveTaskQueue — 后台任务轮询与自动分发 | 2026-09-16（18天） | in=2/out=0·wired | **mount**→GOMAP（编排域）（活线在身未挂线） |
| `src/zephyr/orchestrator/deferred_queue.py` | DeferredQueue: WAITING -> READY task scheduler. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（编排域）（活线在身未挂线） |
| `src/zephyr/orchestrator/execution/batch_orchestrator.py` | BatchOrchestrator — 多 Worker 批量任务协调器（MOD-INF-016） | 2026-09-16（18天） | in=0/out=0·wired_dynamic | **mount**→GOMAP（编排域）（活线在身未挂线） |
| `src/zephyr/orchestrator/execution/dispatch_table.py` | AI Agent 冷启动分派表（Dispatch Table） | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（编排域）（活线在身未挂线） |
| `src/zephyr/orchestrator/execution/dlq_manager.py` | DLQ 管理器（Dead Letter Queue Manager — CT-DLQ-001） | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（编排域）（活线在身未挂线） |
| `src/zephyr/orchestrator/execution/phase_executor.py` | Phase 执行引擎（Phase Executor） | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（编排域）（活线在身未挂线） |
| `src/zephyr/orchestrator/execution/task_context_builder.py` | CE 任务上下文构建器 — build_from_task() 消费者 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（编排域）（活线在身未挂线） |
| `src/zephyr/orchestrator/execution/wave_generator.py` | WaveGenerator — 根据 Task 依赖图生成执行 Wave（T-2-03） | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（编排域）（活线在身未挂线） |
| `src/zephyr/orchestrator/fault_tolerance/bulkhead_manager.py` | （无文档头，按文件名语义：bulkhead_manager） | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（编排域）（活线在身未挂线） |
| `src/zephyr/orchestrator/fault_tolerance/canary_manager.py` | 金丝雀发布管理器（CT-CANARY）——权重分流+指标对比+自动回滚。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（编排域）（活线在身未挂线） |
| `src/zephyr/orchestrator/fault_tolerance/chaos_engine.py` | Chaos 故障注入引擎（CT-CHAOS-001）——4注入点×月度执行。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（编排域）（活线在身未挂线） |
| `src/zephyr/orchestrator/fault_tolerance/chaos_hooks.py` | ChaosHook — integrates ChaosEngine with the orchestrator execution loop. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（编排域）（活线在身未挂线） |
| `src/zephyr/orchestrator/fault_tolerance/disk_guard.py` | （无文档头，按文件名语义：disk_guard） | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（编排域）（活线在身未挂线） |
| `src/zephyr/orchestrator/fault_tolerance/fault_types.py` | Fault type registry and preset templates for chaos engineering. | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（编排域）（活线在身未挂线） |
| `src/zephyr/orchestrator/fault_tolerance/network_partition.py` | 网络分区容忍（CT-NETWORK-PARTITION）——CAP定理CP优先+脑裂检测+quorum write。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（编排域）（活线在身未挂线） |
| `src/zephyr/orchestrator/file_task_mapper.py` | FileTaskMapper — 文件路径 ↔ Task N:N 映射器（#21 裁定重写） | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（编排域）（活线在身未挂线） |
| `src/zephyr/orchestrator/governance/autonomy_guard.py` | Owner 缺位分级自治（CT-AUTONOMY）——Owner离线->自动降级->最小安全运行。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（编排域）（活线在身未挂线） |
| `src/zephyr/orchestrator/governance/dependency_lock.py` | 外部依赖版本锁（CT-DEPS）——Python包版本锁定+hash验证+安全审计。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（编排域）（活线在身未挂线） |
| `src/zephyr/orchestrator/governance/model_registry.py` | （无文档头，按文件名语义：model_registry） | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（编排域）（活线在身未挂线） |
| `src/zephyr/orchestrator/governance/path_index.py` | （无文档头，按文件名语义：path_index） | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（编排域）（活线在身未挂线） |
| `src/zephyr/orchestrator/governance/risk_registry.py` | （无文档头，按文件名语义：risk_registry） | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（编排域）（活线在身未挂线） |
| `src/zephyr/orchestrator/governance/schema_migration.py` | 数据库 Schema 演化契约（CT-SCHEMA-MIGRATE）——向后兼容迁移+回滚脚本。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（编排域）（活线在身未挂线） |
| `src/zephyr/orchestrator/governance/version_manifest.py` | （无文档头，按文件名语义：version_manifest） | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（编排域）（活线在身未挂线） |
| `src/zephyr/orchestrator/hallucination_detector.py` | HallucinationDetector · Chain-of-Verification（CoVe）幻觉检测器 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（编排域）（活线在身未挂线） |
| `src/zephyr/orchestrator/quality/agent_quality.py` | AI Agent 质量反馈闭环（CT-AGENT-QUALITY）——task完成质量评分+agent绩效追踪。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（编排域）（活线在身未挂线） |
| `src/zephyr/orchestrator/quality/benchmark_runner.py` | （无文档头，按文件名语义：benchmark_runner） | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（编排域）（活线在身未挂线） |
| `src/zephyr/orchestrator/quality/blind_spot_closure.py` | （无文档头，按文件名语义：blind_spot_closure） | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（编排域）（活线在身未挂线） |
| `src/zephyr/orchestrator/quality/blueprint_scorer.py` | BlueprintScorer — 蓝图路由统一打分逻辑 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（编排域）（活线在身未挂线） |
| `src/zephyr/orchestrator/quality/ke_quality.py` | 知识质量评分契约（CT-KE-QUALITY）——KE完整性+准确性+时效性三维评分。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（编排域）（活线在身未挂线） |
| `src/zephyr/orchestrator/quality/knowledge_freshness.py` | 知识新鲜度废止管理器（CT-KNOWLEDGE-FRESHNESS）——KE过期标记+自动失效。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（编排域）（活线在身未挂线） |
| `src/zephyr/orchestrator/quality/lean_scanner.py` | 死代码/孤儿文件/僵尸引用三扫描（CT-LEAN）——三款扫描器+自动化清理建议。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（编排域）（活线在身未挂线） |
| `src/zephyr/orchestrator/quality/stability_guard.py` | API 稳定性守护（CT-STABILITY）——public API签名锁+breaking change检测。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（编排域）（活线在身未挂线） |
| `src/zephyr/orchestrator/resilience/__init__.py` | orchestrator.resilience — auto-generated package init. | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（编排域）（活线在身未挂线） |
| `src/zephyr/orchestrator/resilience/failure_matcher.py` | FailurePatternMatcher — 任务失败模式识别与纠正建议 | 2026-09-16（18天） | in=2/out=0·wired | **mount**→GOMAP（编排域）（活线在身未挂线） |
| `src/zephyr/orchestrator/rollback_manager.py` | RollbackManager — 仅调试用途的 DB-state 快照，不用于自动回滚。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（编排域）（活线在身未挂线） |
| `src/zephyr/orchestrator/task_orchestration_skill.py` | TaskOrchestrationSkill — 任务编排技能（MOD-ORCH-003）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（编排域）（活线在身未挂线） |
| `src/zephyr/orchestrator/task_queue.py` | ActiveTaskQueue — 后台任务轮询与自动分发 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（编排域）（活线在身未挂线） |
| `src/zephyr/orchestrator/voting_first_multi_agent.py` | 投票优先多智能体编排（MOD-INF-048）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（编排域）（活线在身未挂线） |
