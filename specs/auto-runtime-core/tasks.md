# AutoRuntime Core — 实施任务

> **蓝图**: ARC-0001 / spec.md
> **版本**: v4.0.0-complete
> **总任务数**: 11 Phase / 40 Task

---

## Phase 1: 基础结构搭建

### T-1.1 创建 runtime 包
- 创建 `src/zephyr/runtime/` 目录及 `__init__.py`
- 导出 `AutoRuntimeCore`
- **依赖**: 无
- **产出**: `src/zephyr/runtime/__init__.py`

### T-1.2 创建 runtime_config.py
- `RuntimeConfig` pydantic 模型，继承 `b_execution_model.yaml` + `PipelineOrchestratorConfig`
- 字段：`poll_interval`, `dashboard_enabled`, `night_shift_storage_path`, `auto_start_l2`, `auto_start_l3`, `trae_heartbeat_url`, `enable_dream_cycle`, `enable_feedback_loop`, `enable_stop_gate`, `enable_git_auto_commit`, `work_orchestrator_enabled`, `max_parallel_l1`, `max_parallel_l2`, `max_parallel_l3`, `enable_auto_onboarding`, `max_daily_l3_activations`, `ultimate_goal`
- **依赖**: 现有 `PipelineOrchestratorConfig`
- **产出**: `src/zephyr/runtime/runtime_config.py`

### T-1.3 创建 AGENTS.md（项目宪法）
- 项目根目录创建 `AGENTS.md`
- 内容：项目概述、核心系统入口、能力发现方法、关键路径、代码规范、禁止事项、**终极目标（全域接入）**
- **依赖**: 无
- **产出**: `AGENTS.md`

---

## Phase 2: 数据层（审计 + 登记 + 能力）

### T-2.1 创建 ai_audit_logger.py
- `AiAuditLogger` 类：全量 AI 行为审计
- 6 类日志：`log_inference()`, `log_embedding()`, `log_routing()`, `log_ambiguity()`, `log_health()`, `log_registration()`
- `has_pending_flush()` → Stop Gate 用
- 存储：追加式 JSONL → `data/audit_logs/ai_audit_{date}.jsonl`
- **依赖**: 无
- **产出**: `src/zephyr/runtime/ai_audit_logger.py`

### T-2.2 创建 capability_card.py + capability_registry.py
- `CapabilityCard` pydantic 模型：11 字段 + `examples`
- `CapabilityRegistry` 类：`register()`, `unregister()`, `discover()`, `list_all()`, `find_by_tags()`, `dump_snapshot()`
- 持久化路径：`data/capability_cards/{id}.yaml`
- **依赖**: T-2.1
- **产出**: `src/zephyr/runtime/capability_card.py`, `src/zephyr/runtime/capability_registry.py`

### T-2.3 创建 night_shift_queue.py
- `NightShiftQueue` 类：JSONL 持久化 + 线程安全
- `append()`, `pending()`, `resolve()`, `stats()`, `has_unresolved()`, `flush_all()`
- **依赖**: 现有 `NightShiftAmbiguityLogEntry`
- **产出**: `src/zephyr/runtime/night_shift_queue.py`

---

## Phase 3: 质量闸门 + 知识固化

### T-3.1 创建 stop_gate.py
- `StopGate` 类：被动质量闸门
- `initialize()`, `check()`, `can_stop()`, `acknowledge_shutdown()`
- **依赖**: T-2.1, T-2.3
- **产出**: `src/zephyr/runtime/stop_gate.py`

### T-3.2 创建 dream_cycle.py
- `DreamCycle` 类：情节记忆→语义记忆转化
- `trigger_archival()`, `needs_archival()`, `query_episodic()`, `query_semantic()`
- **依赖**: T-2.1
- **产出**: `src/zephyr/runtime/dream_cycle.py`

### T-3.3 创建 feedback_loop.py
- `FeedbackLoop` 类：登记表裁定→规则进化
- `analyze_pending()`, `generate_proposals()`, `apply_proposal()`
- **依赖**: T-2.3
- **产出**: `src/zephyr/runtime/feedback_loop.py`

---

## Phase 4: 健康 + 集成

### T-4.1 创建 health_monitor.py
- `HealthMonitor` 类：水平触发调和 + Liveness/Readiness Probe
- `probe()`, `probe_all()`, `reconcile()`, `auto_restart()`, `pressure_level()`, `pressure_response()`
- **依赖**: T-2.2
- **产出**: `src/zephyr/runtime/health_monitor.py`

### T-4.2 创建 integration_registry.py
- `IntegrationRegistry` 类：26 包集成点追踪
- `IntegrationPoint` pydantic 模型
- `register()`, `validate_all()`, `status_all()`
- **依赖**: 各目标系统的 import 路径
- **产出**: `src/zephyr/runtime/integration_registry.py`

---

## Phase 5: 工作编排子系统（新增）

### T-5.1 创建 work_dag.py + work_item.py
- `WorkDAG` pydantic 模型：dag_id, nodes, edges, default_layer, max_parallelism
- `WorkNode` pydantic 模型：node_id, capability_id, work_type, params, layer_override
- `WorkEdge` pydantic 模型：from_node, to_node, condition
- `WorkItem` pydantic 模型：item_id, dag_id, node_id, capability_id, layer, priority, depends_on, status
- **依赖**: T-2.2 (CapabilityCard)
- **产出**: `src/zephyr/runtime/work_dag.py`, `src/zephyr/runtime/work_item.py`

### T-5.2 创建 work_orchestrator.py
- `WorkOrchestrator` 类：DAG 管理 + 执行 + 调度 + 并行控制
- `register_dag()`, `submit()`, `submit_dag()`, `schedule_next()`, `resolve_layer()`, `resolve_priority()`
- `acquire_slot()`, `release_slot()`, `available_slots()`
- 与 `TaskRepository` 衔接：submit→create, 完成→update
- 与 `TaskQueue` 衔接：schedule_next→dispatch
- **依赖**: T-5.1, 现有 `TaskRepository`, `TaskQueue`
- **产出**: `src/zephyr/runtime/work_orchestrator.py`

### T-5.3 创建 10 个预定义 DAG YAML
- `data/work_dags/daily_dream_cycle.yaml`
- `data/work_dags/daily_health_check.yaml`
- `data/work_dags/daily_code_dedup.yaml`
- `data/work_dags/daily_kb_maintenance.yaml`
- `data/work_dags/daily_compliance.yaml`
- `data/work_dags/daily_feedback_loop.yaml`
- `data/work_dags/pipeline_full_run.yaml`
- `data/work_dags/kb_ingest_pipeline.yaml`
- `data/work_dags/security_scan.yaml`
- `data/work_dags/model_drift_check.yaml`
- **依赖**: T-5.1
- **产出**: 10 个 YAML 文件

---

## Phase 6: 自动接入子系统（新增）

### T-6.1 创建 module_onboarding_scanner.py
- `ModuleOnboardingScanner` 类：主动扫描未注册模块
- `scan_filesystem()`, `scan_blueprints()`, `diff_registered()`, `watch_for_changes()`
- `ModuleDiscovery`, `UnregisteredModule` dataclass
- 全量扫描（Circadian 04:00）+ 增量扫描（文件系统 watcher）+ 蓝图扫描（Circadian 07:00）
- **依赖**: T-2.2 (CapabilityRegistry)
- **产出**: `src/zephyr/runtime/module_onboarding_scanner.py`

### T-6.2 创建 auto_integrator.py
- `AutoIntegrator` 类：临时启动 L3 高级模型分析是否接入
- `analyze_module()`, `should_integrate()`, `generate_card()`, `assign_work_type()`, `auto_register()`
- `IntegrationAnalysis` dataclass
- 临时 L3 激活：分析时启动 API，分析完回到待机
- 成本控制：每天最多 `max_daily_l3_activations` 次
- confidence >= 0.8 → 自动注册；< 0.8 → NightShiftQueue
- **依赖**: T-2.2, T-2.3, T-6.1
- **产出**: `src/zephyr/runtime/auto_integrator.py`

### T-6.3 创建 orphan_detector.py
- `OrphanDetector` 类：持续监控孤儿率
- `compute_orphan_rate()`, `find_orphans()`, `prioritize_orphans()`, `report()`, `is_goal_met()`
- `OrphanReport` dataclass
- 与 HealthMonitor.reconcile() 衔接：每次调和检查孤儿率
- **依赖**: T-2.2, T-6.1
- **产出**: `src/zephyr/runtime/orphan_detector.py`

### T-6.4 增强调和循环加入孤儿率检查
- `HealthMonitor.reconcile()` 新增步骤：OrphanDetector.compute_orphan_rate()
- 孤儿率 > 0 → 触发 ModuleOnboardingScanner → AutoIntegrator
- ReconciliationReport 新增 orphan_rate 字段
- **依赖**: T-4.1, T-6.1, T-6.2, T-6.3
- **产出**: 更新 `health_monitor.py`

---

## Phase 7: 生物钟

### T-7.1 创建 circadian_scheduler.py
- `CircadianScheduler` 类：14 定时 + 5 事件触发
- 定时任务与 WorkOrchestrator DAG 衔接：Circadian 触发 → `submit_dag()`
- `get_current_phase()`, `get_next_task()`, `register_event_listener()`, `save_state()`
- **依赖**: T-3.2, T-3.3, T-5.2, T-6.1
- **产出**: `src/zephyr/runtime/circadian_scheduler.py`

---

## Phase 8: 生命周期

### T-8.1 创建 finalizer.py
- `Finalizer` 类：关闭前级联清理
- `register()`, `run()`
- **依赖**: T-2.1, T-2.2, T-2.3, T-3.2, T-4.1
- **产出**: `src/zephyr/runtime/finalizer.py`

### T-8.2 创建 lifecycle_manager.py
- `LifecycleManager` 类：22 步 Boot + 18 步 Shutdown
- Boot 含 WorkOrchestrator 初始化 + DAG 加载 + ModuleOnboardingScanner 首次全量扫描
- **依赖**: 所有 Phase 1-7 + T-8.1
- **产出**: `src/zephyr/runtime/lifecycle_manager.py`

---

## Phase 9: 核心编排

### T-9.1 创建 auto_runtime_core.py
- `AutoRuntimeCore` 主类：系统大脑唯一入口
- 新增 `work_orchestrator` property + `submit_work()` + `submit_dag()`
- 新增 `orphan_detector` property + `onboarding_scanner` property
- **依赖**: 所有 Phase 1-8
- **产出**: `src/zephyr/runtime/auto_runtime_core.py`

### T-9.2 创建 status_dashboard.py
- `StatusDashboard` 类：TUI + JSON API
- TUI 新增工作编排状态区 + 孤儿率指标
- **依赖**: T-2.3, T-3.2, T-3.3, T-5.2, T-6.3, T-7.1
- **产出**: `src/zephyr/runtime/status_dashboard.py`

### T-9.3 创建 __main__.py
- `python -m zephyr.runtime` 入口
- **依赖**: T-9.1
- **产出**: `src/zephyr/runtime/__main__.py`

---

## Phase 10: Windows Service

### T-10.1 创建 windows_service.py
- **依赖**: T-9.3
- **产出**: `src/zephyr/runtime/windows_service.py`

---

## Phase 11: 迁移 + 集成对接

### T-11.1 迁移 local_layer_daemon.py 为薄包装
- **依赖**: T-9.1
- **产出**: 更新 `local_layer_daemon.py`

### T-11.2 对接 NightShiftQueue 到 PipelineOrchestrator
- **依赖**: T-2.1, T-2.3
- **产出**: 更新 `pipeline_orchestrator.py`

### T-11.3 为现有组件生成 CapabilityCard
- 为 EmbeddingRouter, OllamaChat, Reranker, LocalModelScheduler, TaskRepository, TaskQueue, TaskScheduler 生成 YAML
- **依赖**: T-2.2
- **产出**: 7 个 YAML 文件

### T-11.4 对接 WorkOrchestrator 到 TaskRepository
- `submit()` → `TaskRepository.create()`
- `schedule_next()` → `TaskQueue` dispatch
- 完成回调 → `TaskRepository.update()` + 依赖解析
- **依赖**: T-5.2, 现有 `TaskRepository`, `TaskQueue`
- **产出**: 更新 `work_orchestrator.py`

### T-11.5 更新 b_execution_model.yaml
- **依赖**: 无
- **产出**: 更新 `architecture-model/layers/b_execution_model.yaml`

---

## Phase 12: 最终测试

### T-12.1 全链路端到端测试
- DEMO 7 任务 + tasks/ JSON 投递 → 全部自动完成
- WorkOrchestrator DAG 执行：daily_dream_cycle DAG 端到端跑通
- DAG 依赖解析：上游完成→下游自动 READY
- 并行控制：L2 同时跑 3 个嵌入任务
- 优先级抢占：P0 抢占 P2 槽位
- NightShiftQueue 写入/读取/裁定
- CircadianScheduler 14 定时任务触发
- Dream Cycle / Feedback Loop / Stop Gate / Finalizer
- ModuleOnboardingScanner 全量扫描发现孤儿
- AutoIntegrator 临时启动 L3 分析后自动注册或登记
- OrphanDetector 孤儿率计算正确
- `ruff check --select F` 零新增
- **依赖**: 所有 Phase
- **产出**: 测试通过日志

---

## 依赖关系图

```
P1: 基础结构 → P2, P5, P9
P2: 数据层 → P3, P4, P5, P6, P8, P11
P3: 闸门+固化 → P7, P8
P4: 健康+集成 → P6, P8
P5: 工作编排 → P7, P9, P11
P6: 自动接入 → P7, P8, P9
P7: 生物钟 → P8
P8: 生命周期 → P9
P9: 核心编排 → P10, P11
P10: Windows Service
P11: 迁移+集成
P12: 最终测试 ← 全部
```

---

> **下一步**: 按 `checklist.md` 逐项验收。
