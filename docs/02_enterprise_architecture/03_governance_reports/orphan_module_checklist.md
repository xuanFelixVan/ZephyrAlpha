---
doc_type: audit_report
title: 作战地图孤儿模块排查清单
version: "1.0"
status: active
date: 2026-08-04
owner: auto-generator
ttl: permanent
---

# 作战地图孤儿模块排查清单 (Orphan Module Triage Checklist)

- 生成时间: 2026-08-04 23:25:04
- 数据源: depgraph (PostgreSQL) + candidate_module_registry.yaml + module_translation_registry.yaml
- 扫描范围: BM-INV-007 业务域白名单内 depgraph 节点（不限 node_type）且无 battle_map_anchors
- 孤儿节点总数: **135**（与对齐报告 BM-INV-007=135 一致）
  - 按 node_type: {'blueprint': 5, 'config': 3, 'database': 4, 'module': 116, 'script': 1, 'test': 4, 'test_module': 2}
  - 按 build_status: {'planned': 8, 'deprecated': 9, 'generated': 53, 'stable': 65}

## 分类总览

| 类别 | 数量 | 性质 | 处置原则 |
|---|---|---|---|
| **[A] 横切子文件误报** | 106 | `node_type=module` + `granularity=file` + 横切基础设施域（D_INFRA_RUNTIME/D_INTEGRATION/D_SECURITY/D_SHARED）的子文件 | **无需处置**——大模块 file 粒度子节点，天然不挂作战锚点 |
| **[B] deprecated 弃用** | 9 | `build_status=deprecated` 节点（module + blueprint目录 + test_module） | **走弃用流程第②步**——补/升级 candidate_registry rejected 条目 |
| **[C] 真实待决策(planned)** | 8 | `build_status=planned` 且 `node_type∈(module,blueprint)` | **逐个决策**——挂锚点 / 弃用 / 重分类 |
| **[D] 非 module 基础设施/配置/测试** | 12 | database/config/script/test 等非作战决策节点 | **无需处置**——基础设施/测试节点天然不入作战图 |
| **合计** | **135** | | |

## [A] 横切子文件误报（106 个）— 无需处置

> `node_type=module` + `granularity=file` + domain ∈ 横切基础设施域。auto_fix_engine / vector_memory / system_telemetry 等大模块的 file 粒度子节点，本质单文件非独立作战模块。

### 按父模块聚类（13 组）

| # | 子文件数 | 父模块路径 | 父模块ID | build_status分布 |
|---|---|---|---|---|
| 1 | 29 | `src/zephyr/infrastructure/auto_fix_engine` | MOD-INF-031 | {'generated': 8, 'stable': 21} |
| 2 | 23 | `src/zephyr/integration/vector_memory` | MOD-INF-011 | {'generated': 9, 'stable': 14} |
| 3 | 17 | `src/zephyr/integration/mcp` | MOD-INF-013 | {'generated': 5, 'stable': 12} |
| 4 | 15 | `src/zephyr/infrastructure/system_telemetry` | MOD-INF-015 | {'generated': 9, 'stable': 6} |
| 5 | 6 | `src/zephyr/shared/protocols` | MOD-SHARED-001 | {'generated': 6} |
| 6 | 5 | `src/zephyr/gov_drift` | MOD-INF-011 | {'generated': 5} |
| 7 | 3 | `src/zephyr/shared/maintenance` | SH-MAIN-001 | {'stable': 3} |
| 8 | 2 | `src/zephyr/infrastructure/script_system` | MOD-INF-005 | {'generated': 1, 'stable': 1} |
| 9 | 2 | `src/zephyr/shared/io` | MOD-SHARED-002 | {'generated': 2} |
| 10 | 1 | `src/zephyr/infrastructure` | MOD-INF-003 | {'stable': 1} |
| 11 | 1 | `src/zephyr/shared/observability` | MOD-INF-044 | {'stable': 1} |
| 12 | 1 | `src/zephyr/shared/utils` | MOD-SHR_CONVERTERS | {'stable': 1} |
| 13 | 1 | `src/zephyr/shared/blueprint_tools` | SH-MAIN-001 | {'stable': 1} |

<details>
<summary>展开全部 106 个 [A] 子文件明细</summary>

| blueprint_id | 名称 | domain | build_status | path |
|---|---|---|---|---|
| MOD-INF-031 | 主入口 | D_INFRA_RUNTIME | generated | `src/zephyr/infrastructure/auto_fix_engine/__main__.py` |
| MOD-INF-031 | 对齐同步器 | D_INFRA_RUNTIME | generated | `src/zephyr/infrastructure/auto_fix_engine/alignment_syncer.py` |
| MOD-INF-031 | 公共接口：parse_all | D_INFRA_RUNTIME | generated | `src/zephyr/infrastructure/auto_fix_engine/all_completer.py` |
| MOD-INF-031 | 只读：conflict_resolver | D_INFRA_RUNTIME | generated | `src/zephyr/infrastructure/auto_fix_engine/batch_fixer.py` |
| MOD-INF-031 | 只读：retention_days | D_INFRA_RUNTIME | generated | `src/zephyr/infrastructure/auto_fix_engine/compliance_auditor.py` |
| MOD-INF-031 | 公共接口：fix_trailing_whitespace | D_INFRA_RUNTIME | generated | `src/zephyr/infrastructure/auto_fix_engine/config_fixer.py` |
| MOD-INF-031 | 公共接口：normalize_code | D_INFRA_RUNTIME | generated | `src/zephyr/infrastructure/auto_fix_engine/dedup_extractor.py` |
| MOD-INF-031 | Dep版本修复器 | D_INFRA_RUNTIME | stable | `src/zephyr/infrastructure/auto_fix_engine/dep_version_fixer.py` |
| MOD-INF-031 | 漂移修复器 | D_INFRA_RUNTIME | stable | `src/zephyr/infrastructure/auto_fix_engine/drift_fixer.py` |
| MOD-INF-031 | 引擎 | D_INFRA_RUNTIME | stable | `src/zephyr/infrastructure/auto_fix_engine/engine.py` |
| MOD-INF-031 | Escalation桥接器 | D_INFRA_RUNTIME | stable | `src/zephyr/infrastructure/auto_fix_engine/escalation_bridge.py` |
| MOD-INF-031 | 只读：event_log | D_INFRA_RUNTIME | stable | `src/zephyr/infrastructure/auto_fix_engine/event_hooks.py` |
| MOD-INF-031 | 修复预算 | D_INFRA_RUNTIME | stable | `src/zephyr/infrastructure/auto_fix_engine/fix_budget.py` |
| MOD-INF-031 | 修复差异 | D_INFRA_RUNTIME | stable | `src/zephyr/infrastructure/auto_fix_engine/fix_diff.py` |
| MOD-INF-031 | 公共接口：check_config | D_INFRA_RUNTIME | stable | `src/zephyr/infrastructure/auto_fix_engine/fix_health_check.py` |
| MOD-INF-031 | 只读：db_path | D_INFRA_RUNTIME | stable | `src/zephyr/infrastructure/auto_fix_engine/fix_pattern_miner.py` |
| MOD-INF-031 | 只读：ttl | D_INFRA_RUNTIME | stable | `src/zephyr/infrastructure/auto_fix_engine/fix_reliability.py` |
| MOD-INF-031 | 只读：history | D_INFRA_RUNTIME | stable | `src/zephyr/infrastructure/auto_fix_engine/fix_report.py` |
| MOD-INF-031 | 只读：enabled | D_INFRA_RUNTIME | stable | `src/zephyr/infrastructure/auto_fix_engine/fix_safety.py` |
| MOD-INF-031 | 修复调度器 | D_INFRA_RUNTIME | stable | `src/zephyr/infrastructure/auto_fix_engine/fix_scheduler.py` |
| MOD-INF-031 | Import修复器 | D_INFRA_RUNTIME | generated | `src/zephyr/infrastructure/auto_fix_engine/import_fixer.py` |
| MOD-INF-031 | 只读：wal_dir | D_INFRA_RUNTIME | stable | `src/zephyr/infrastructure/auto_fix_engine/interrupt_guard.py` |
| MOD-INF-031 | 只读：secret_guard | D_INFRA_RUNTIME | stable | `src/zephyr/infrastructure/auto_fix_engine/llm_fix_adapter.py` |
| MOD-INF-031 | 模型 | D_INFRA_RUNTIME | stable | `src/zephyr/infrastructure/auto_fix_engine/models.py` |
| MOD-INF-031 | 从 script-manifest.yaml 加载已注册脚本路径集合 | D_INFRA_RUNTIME | stable | `src/zephyr/infrastructure/auto_fix_engine/scaffold_registrar.py` |
| MOD-INF-031 | SelfHeal代理 | D_INFRA_RUNTIME | stable | `src/zephyr/infrastructure/auto_fix_engine/self_heal_agent.py` |
| MOD-INF-031 | 影子Workspace | D_INFRA_RUNTIME | stable | `src/zephyr/infrastructure/auto_fix_engine/shadow_workspace.py` |
| MOD-INF-031 | 状态Machine | D_INFRA_RUNTIME | stable | `src/zephyr/infrastructure/auto_fix_engine/state_machine.py` |
| MOD-INF-031 | 移除 content 中指向不存在文件的僵尸引用，返回清理后的内容 | D_INFRA_RUNTIME | stable | `src/zephyr/infrastructure/auto_fix_engine/zombie_cleaner.py` |
| MOD-INF-003 | Git 命令批量化工具 | D_INFRA_RUNTIME | stable | `src/zephyr/infrastructure/git_batcher.py` |
| MOD-INF-005 | 发现 | D_INFRA_RUNTIME | stable | `src/zephyr/infrastructure/script_system/finding.py` |
| MOD-INF-005 | 门禁桥接器 | D_INFRA_RUNTIME | generated | `src/zephyr/infrastructure/script_system/gate_bridge.py` |
| MOD-INF-015 | 预算Telemetry桥接器 | D_INFRA_RUNTIME | generated | `src/zephyr/infrastructure/system_telemetry/_budget_telemetry_bridge.py` |
| MOD-INF-015 | 链路桥接器 | D_INFRA_RUNTIME | generated | `src/zephyr/infrastructure/system_telemetry/_trace_bridge.py` |
| MOD-INF-015 | AI 行为遥测事件管道 | D_INFRA_RUNTIME | generated | `src/zephyr/infrastructure/system_telemetry/ai_behavior/event_sink.py` |
| MOD-INF-015 | 冷存储归档管道 | D_INFRA_RUNTIME | generated | `src/zephyr/infrastructure/system_telemetry/archive/cold_stub.py` |
| MOD-INF-015 | 全自动遥测注入钩子 | D_INFRA_RUNTIME | stable | `src/zephyr/infrastructure/system_telemetry/auto_bootstrap.py` |
| MOD-INF-015 | 只读：sla_buffer | D_INFRA_RUNTIME | stable | `src/zephyr/infrastructure/system_telemetry/contract_metrics.py` |
| MOD-INF-015 | 系统遥测门面类 | D_INFRA_RUNTIME | generated | `src/zephyr/infrastructure/system_telemetry/facade.py` |
| MOD-INF-015 | 只读：snapshots | D_INFRA_RUNTIME | stable | `src/zephyr/infrastructure/system_telemetry/health_aggregator.py` |
| MOD-INF-015 | 5.55.1 修复：探针内部真实检查依赖状态，而非信任外部传入的 deps_ok | D_INFRA_RUNTIME | stable | `src/zephyr/infrastructure/system_telemetry/health_probes.py` |
| MOD-INF-015 | 结构化日志流 | D_INFRA_RUNTIME | stable | `src/zephyr/infrastructure/system_telemetry/logs/__init__.py` |
| MOD-INF-015 | 结构化日志管道 | D_INFRA_RUNTIME | generated | `src/zephyr/infrastructure/system_telemetry/logs/structured_sink.py` |
| MOD-INF-015 | 单次蓝图读取事件 | D_INFRA_RUNTIME | stable | `src/zephyr/infrastructure/system_telemetry/metrics/blueprint_metrics.py` |
| MOD-INF-015 | 指标桥接器 | D_INFRA_RUNTIME | generated | `src/zephyr/infrastructure/system_telemetry/metrics_bridge.py` |
| MOD-INF-015 | W3C TraceContext 分布式追踪管道 | D_INFRA_RUNTIME | generated | `src/zephyr/infrastructure/system_telemetry/traces/span_stub.py` |
| MOD-INF-015 | —互检+Panic Mode+Dead Man's Switch | D_INFRA_RUNTIME | generated | `src/zephyr/infrastructure/system_telemetry/watchdog.py` |
| MOD-INF-013 | 基础服务端 | D_INTEGRATION | stable | `src/zephyr/integration/mcp/_base_server.py` |
| MOD-INF-013 | MCP 全量工具调用审计日志 | D_INTEGRATION | stable | `src/zephyr/integration/mcp/audit_logger.py` |
| MOD-INF-013 | 蓝图Search服务端 | D_INTEGRATION | stable | `src/zephyr/integration/mcp/blueprint_search_server.py` |
| MOD-INF-013 | session_handoff MCP Server 实现 | D_INTEGRATION | stable | `src/zephyr/integration/mcp/doc_guard_server.py` |
| MOD-INF-013 | MCP 错误码集中注册 | D_INTEGRATION | stable | `src/zephyr/integration/mcp/error_codes.py` |
| MOD-INF-013 | 检查路径是否命中黑名单 | D_INTEGRATION | stable | `src/zephyr/integration/mcp/gate_engine_server.py` |
| MOD-INF-013 | MCP Gateway 集中式治理节点 | D_INTEGRATION | stable | `src/zephyr/integration/mcp/gateway_server.py` |
| MOD-INF-013 | —从 handoff 包恢复 AI session 上下文 | D_INTEGRATION | generated | `src/zephyr/integration/mcp/handoff_auto_loader.py` |
| MOD-INF-013 | 关闭 B3） | D_INTEGRATION | generated | `src/zephyr/integration/mcp/prompt_provider.py` |
| MOD-INF-013 | MCP Gateway 同步速率限制器 | D_INTEGRATION | stable | `src/zephyr/integration/mcp/rate_limiter.py` |
| MOD-INF-013 | 关闭 B2/B41） | D_INTEGRATION | generated | `src/zephyr/integration/mcp/resource_provider.py` |
| MOD-INF-014 | 规则发现服务端 | D_INTEGRATION | stable | `src/zephyr/integration/mcp/rule_discovery_server.py` |
| MOD-INF-013 | 关闭 B4） | D_INTEGRATION | generated | `src/zephyr/integration/mcp/sandbox_server.py` |
| MOD-INF-013 | Stage 1 关键词匹配，返回 | D_INTEGRATION | stable | `src/zephyr/integration/mcp/sentinel_server.py` |
| MOD-INF-013 | 任务管理器服务端 | D_INTEGRATION | stable | `src/zephyr/integration/mcp/task_manager_server.py` |
| MOD-INF-013 | 系统可观测性 MCP 接口 | D_INTEGRATION | stable | `src/zephyr/integration/mcp/telemetry_server.py` |
| MOD-INF-013 | 向量记忆服务端 | D_INTEGRATION | generated | `src/zephyr/integration/mcp/vector_memory_server.py` |
| MOD-INF-011 | 桥接器层 | D_INTEGRATION | stable | `src/zephyr/integration/vector_memory/bridge_layer.py` |
| MOD-INF-011 | Chunk策略路由器 | D_INTEGRATION | stable | `src/zephyr/integration/vector_memory/chunk_strategy_router.py` |
| MOD-INF-011 | 收集管理器 | D_INTEGRATION | stable | `src/zephyr/integration/vector_memory/collection_manager.py` |
| MOD-INF-011 | 收集Schemas | D_INTEGRATION | stable | `src/zephyr/integration/vector_memory/collection_schemas.py` |
| MOD-INF-011 | 上下文Ingest | D_INTEGRATION | generated | `src/zephyr/integration/vector_memory/context_ingest.py` |
| MOD-INF-011 | 跨收集Retriever | D_INTEGRATION | generated | `src/zephyr/integration/vector_memory/cross_collection_retriever.py` |
| MOD-INF-011 | 以 ``UnifiedMemoryAPI`` 为后端的 ``VectorMemoryBase`` 实现 | D_INTEGRATION | generated | `src/zephyr/integration/vector_memory/delegated_vector_memory.py` |
| MOD-INF-011 | 设计原则 | D_INTEGRATION | stable | `src/zephyr/integration/vector_memory/design_principles.py` |
| MOD-INF-011 | Faiss收集管理器 | D_INTEGRATION | generated | `src/zephyr/integration/vector_memory/faiss_collection_manager.py` |
| MOD-INF-011 | 混合检索器 | D_INTEGRATION | stable | `src/zephyr/integration/vector_memory/hybrid_retriever.py` |
| MOD-INF-011 | 只读：store_size | D_INTEGRATION | stable | `src/zephyr/integration/vector_memory/in_memory_fake_vms.py` |
| MOD-INF-011 | In记忆记忆后端 | D_INTEGRATION | stable | `src/zephyr/integration/vector_memory/in_memory_memory_backend.py` |
| MOD-INF-011 | In流程向量记忆 | D_INTEGRATION | stable | `src/zephyr/integration/vector_memory/in_process_vector_memory.py` |
| MOD-INF-011 | 索引Health监控器 | D_INTEGRATION | stable | `src/zephyr/integration/vector_memory/index_health_monitor.py` |
| MOD-INF-011 | 单条记忆条目""" | D_INTEGRATION | generated | `src/zephyr/integration/vector_memory/interface.py` |
| MOD-INF-011 | Chroma到FAISS迁移 | D_INTEGRATION | generated | `src/zephyr/integration/vector_memory/migrate_chroma_to_faiss.py` |
| MOD-INF-011 | 校验 WriteTrace 完整性 | D_INTEGRATION | stable | `src/zephyr/integration/vector_memory/provenance_enforcer.py` |
| MOD-INF-011 | 只读：long_tail | D_INTEGRATION | stable | `src/zephyr/integration/vector_memory/retrieval_feedback.py` |
| MOD-INF-011 | Sqlite元数据存储 | D_INTEGRATION | generated | `src/zephyr/integration/vector_memory/sqlite_metadata_store.py` |
| MOD-INF-011 | 向量桥接器 | D_INTEGRATION | generated | `src/zephyr/integration/vector_memory/vector_bridge.py` |
| MOD-INF-011 | VMS错误 | D_INTEGRATION | stable | `src/zephyr/integration/vector_memory/vms_errors.py` |
| MOD-INF-011 | —将 UnifiedMemoryAPI 的操作路由到 InProcessVectorMemory | D_INTEGRATION | generated | `src/zephyr/integration/vector_memory/vms_memory_backend.py` |
| MOD-INF-011 | VMS模式定义 | D_INTEGRATION | stable | `src/zephyr/integration/vector_memory/vms_schemas.py` |
| MOD-INF-011 | 分析 | D_SECURITY | generated | `src/zephyr/gov_drift/_analysis.py` |
| MOD-INF-011 | 核心 | D_SECURITY | generated | `src/zephyr/gov_drift/_core.py` |
| MOD-INF-011 | 漂移 | D_SECURITY | generated | `src/zephyr/gov_drift/_drift.py` |
| MOD-INF-011 | 基础设施 | D_SECURITY | generated | `src/zephyr/gov_drift/_infrastructure.py` |
| MOD-INF-011 | 扫描器 | D_SECURITY | generated | `src/zephyr/gov_drift/_scanners.py` |
| SH-MAIN-001 | 从任务描述行中拆出叙事文本与 ``depends_on`` 列表 | D_SHARED | stable | `src/zephyr/shared/blueprint_tools/blueprint_decomposer.py` |
| MOD-SHARED-002 | 对连接应用 KBG-0030 §4.3 PRAGMA 基线 | D_SHARED | generated | `src/zephyr/shared/io/sqlite_factory.py` |
| MOD-SHR_IO_YAML | vocabulary YAML 加载公共工具 | D_SHARED | generated | `src/zephyr/shared/io/yaml_utils.py` |
| SH-MAIN-001 | 只读：tasks | D_SHARED | stable | `src/zephyr/shared/maintenance/dogfooding.py` |
| SH-MAIN-001 | 维护手册 | D_SHARED | stable | `src/zephyr/shared/maintenance/handbook.py` |
| SH-MAIN-001 | 公共接口：check_python | D_SHARED | stable | `src/zephyr/shared/maintenance/zero_config.py` |
| MOD-INF-044 | Grafana 双数据源仪表盘模块 | D_SHARED | stable | `src/zephyr/shared/observability/dashboard/__init__.py` |
| MOD-SHARED-001 | A2A协调 | D_SHARED | generated | `src/zephyr/shared/protocols/a2a/a2a_coordination.py` |
| MOD-SHARED-001 | A2A协议 | D_SHARED | generated | `src/zephyr/shared/protocols/a2a/a2a_protocol.py` |
| MOD-SHARED-001 | A2A注册表 | D_SHARED | generated | `src/zephyr/shared/protocols/a2a/a2a_registry.py` |
| MOD-SHARED-001 | A2A模式定义 | D_SHARED | generated | `src/zephyr/shared/protocols/a2a/a2a_schemas.py` |
| MOD-SHARED-001 | D-INFRA 通过此接口获取 DB 连接和路径 | D_SHARED | generated | `src/zephyr/shared/protocols/ports.py` |
| MOD-SHARED-001 | 进程级单例服务注册表 | D_SHARED | generated | `src/zephyr/shared/protocols/registry.py` |
| MOD-SHR_CONVERTERS | 将空字符串转为 None，其他值原样返回 | D_SHARED | stable | `src/zephyr/shared/utils/converters.py` |
</details>

## [B] deprecated 弃用（9 个）— 走弃用流程第②步

> 弃用流程两步：①`apply_depgraph.py`软删除 `build_status→deprecated` ✅9个均已执行；②`candidate_module_registry.yaml`登记`rejected`条目（含否决理由，防未来误重新设计）

| blueprint_id | 名称 | domain | node_type | path | candidate状态 | 第②步动作 |
|---|---|---|---|---|---|---|
| — | 测试触发器A | D_ALT_DATA | test_module | `test_trigger_A.py` | 未登记(无bp) | 补/升级 rejected |
| — | 测试触发器B | D_ASHARE_SIGNAL | test_module | `test_trigger_B.py` | 未登记(无bp) | 补/升级 rejected |
| MOD-EX-015 | 执行报告 | D_EX_CORE | module | `src/zephyr/ex_core/execution_report.py` | 未登记 | 补 rejected 条目 |
| MOD-PF-004 | 最小方差策略 | D_PF_CORE | module | `src/zephyr/pf_core/strategies/min_variance_strategy.py` | deferred | 升级 deferred→rejected+补理由 |
| MOD-PF-005 | 风险平价策略 | D_PF_CORE | module | `src/zephyr/pf_core/strategies/risk_parity_strategy.py` | deferred | 升级 deferred→rejected+补理由 |
| MOD-RISK-001 | 回撤跟踪器 | D_RISK | blueprint | `src/zephyr/risk/drawdown_tracker/` | 未登记 | 补 rejected 条目 |
| MOD-RSK-009 | A股止损亏损规则引擎 | D_RISK | module | `src/zephyr/risk/ashare_stop_loss_rule_engine.py` | 未登记 | 补 rejected 条目 |
| MOD-RSK-010 | A股Systemic风险检测器 | D_RISK | module | `src/zephyr/risk/ashare_systemic_risk_detector.py` | 未登记 | 补 rejected 条目 |
| MOD-RSK-011 | 回撤Realtime跟踪器 | D_RISK | module | `src/zephyr/risk/drawdown_realtime_tracker.py` | rejected(reason空) | 补否决理由(reason空) |

> **处置清单**：
> - 补登记 rejected（含 MOD-RISK-001、test_trigger_A/B 等无 bp 的需先补 blueprint_id 再登记）
> - 升级 deferred→rejected（MOD-PF-004/005）
> - 补否决理由（MOD-RSK-011 reason 空）

## [C] 真实待决策（8 个 planned）— 逐个评估

> `build_status=planned` 且 `node_type∈(module,blueprint)`，非横切子文件、非 deprecated。

| blueprint_id | 名称 | domain | node_type | granularity | 文件状态 | 评估 | 建议 |
|---|---|---|---|---|---|---|---|
| MOD-L00-007 | 存储 | D_DATA | blueprint | directory | 目录(planned) | D_DATA存储待建 | D_DATA基础设施数据层,确认是否入作战图 |
| MOD-L00-008 | 缓存 | D_DATA | blueprint | directory | 目录(planned) | D_DATA缓存待建 | 同MOD-L00-007 |
| MOD-EX-004 | redis幂等性 | D_EX_CORE | blueprint | directory | 目录(planned) | redis幂等性待建 | D_EX_CORE待建,同MOD-EX-037评估 |
| MOD-EX-037 | 蓝图Implementer | D_EX_CORE | module | file | CODE不存在 | D_EX_CORE执行核心待建,不在8个gated-on-live列表 | 统一评估D_EX_CORE planned去留(实盘门禁阻塞?是→保留;否→弃用) |
| MOD-EX-051 | 值对象 | D_EX_CORE | module | file | CODE不存在 | D_EX_CORE值对象待建 | 同MOD-EX-037 |
| MOD-EX-052 | 工厂 | D_EX_CORE | module | file | CODE不存在 | D_EX_CORE工厂待建 | 同MOD-EX-037 |
| MOD-INF-011 | docs__03_modules___domain_knowledge__vector_memory__blueprint_md | D_KNOWLEDGE | module | file | DOC(blueprint.md) | ✅已处置(扫描排除) | 设计文档非可执行模块,scan排除docs/03_modules/*.md(见下) |
| MOD-ML-003 | 训练数据集管理器 | D_ML_TRAIN | blueprint | directory | 目录(planned) | 训练数据集管理器待建 | D_ML_TRAIN待建模块,确认是否挂model_training锚点 |

> **MOD-INF-011 处置记录（2026-08-04，已实施）**：
> 经调查推翻原"DB重分类"方案——`doc`非合法node_type,且30+其他blueprint.md均用
> `node_type=module`(项目约定,非误登记)。真因是 BM-INV-007 扫描SQL未排除设计文档路径。
> 治本：`align_battle_map.py` SQL_SELECT_BUSINESS_MODULES 增加
> `AND NOT (path LIKE 'docs/03_modules/%' AND path LIKE '%.md')`，
> 排除业务域内的 blueprint.md 设计文档节点(共3个:MOD-INF-011/MOD-INF-039/MOD-INF-034)。
> 孤儿模块数 135→134,业务域模块 1770→1767。无需 DB 写入,无需 backup_pg_architecture。

> **决策优先级**：
> 1. ~~MOD-INF-011（蓝图 doc 误判）→ 重分类~~ ✅已处置(扫描排除,见上)
> 2. MOD-EX-037/051/052/004（D_EX_CORE planned 未建）→ Owner 决策实盘门禁阻塞与否
> 3. MOD-ML-003/L00-007/L00-008（D_ML_TRAIN/D_DATA planned 目录）→ 确认是否入作战图

## [D] 非 module 基础设施/配置/测试（12 个）— 无需处置

> database/config/script/test 等节点，非作战决策模块，天然不入作战图。

| blueprint_id | 名称 | domain | node_type | build_status | path |
|---|---|---|---|---|---|
| — | 调度计划 | D_DATA | config | generated | `src/zephyr/data/config/schedule.yaml` |
| — | 策略 | D_DATA | config | generated | `src/zephyr/data/config/policies.yaml` |
| — | 任务 | D_DATA | config | generated | `src/zephyr/data/config/tasks.yaml` |
| — | zephyr-chroma-vector-db — database 节点 (ARCH-053) | D_INFRA_RUNTIME | database | stable | `docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml#INFRA-DB-002` |
| — | zephyr-sqlite-task-db — database 节点 (ARCH-053) | D_INFRA_RUNTIME | database | stable | `docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml#INFRA-DB-001` |
| — | zephyr-clickhouse-c1-market — database 节点 (ARCH-053) | D_INFRA_RUNTIME | database | stable | `docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml#INFRA-DB-006` |
| — | zephyr-depgraph-db — database 节点 (ARCH-053) | D_INFRA_RUNTIME | database | stable | `docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml#INFRA-DB-003` |
| MOD-OPS-018 | 开发环境一次性初始化 | D_OPS | script | generated | `scripts/setup_dev_env.py` |
| MOD-E2E-001 | —D-FACTOR → D-BACKTEST 数据流验证 | D_BACKTEST | test | generated | `tests/factor/test_backtest_factor_e2e.py` |
| MOD-TEST_STRATEGY_RUNNER_TICK | StrategyRunner.run_tick_backtest 单元测试 | D_PF_CORE | test | generated | `tests/pf_core/test_strategy_runner_tick.py` |
| MOD-TEST_SURGE_FALL_STRATEGY | IntradaySurgeFallStrategy 单元测试 | D_PF_CORE | test | generated | `tests/pf_core/test_intraday_surge_fall_strategy.py` |
| MOD-TEST_METRICS_SERVER | metrics_server 单元测试 | D_SHARED | test | generated | `tests/zephyr/shared/observability/test_metrics_server.py` |

## 处置汇总与下一步

| 动作 | 涉及节点数 | 责任 |
|---|---|---|
| 无需处置（横切子文件 + 非 module 基础设施） | 118 | —（建议 BM-INV-007 加 `node_type='module'` 过滤消除误报） |
| 走弃用流程第②步 | 9 | 补/升级 candidate_registry rejected 条目 |
| 逐个决策 | 8 | MOD-INF-011 重分类 + D_EX_CORE×4/D_ML_TRAIN/D_DATA×3 Owner 决策 |
| **合计** | **135** | — |

> **根因建议**：BM-INV-007 扫描当前含全部 node_type，导致 135 个里 118 个（87%）为非作战模块的误报。建议扫描加 `node_type='module' AND granularity!='file'`（或排除横切域 file 子节点），可收敛到真正需决策的 17 个节点。
