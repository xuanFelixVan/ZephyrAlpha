# 01 · 仓库布局与全模块清单

> 生成者：架构师_模块清单（只读静态审查） | 日期：2026-07-22
> 本文档基于只读静态审查（`__init__.py` 头部元数据注释、模块 docstring、`grep '^class '` 符号提取、文件名推断），未逐行阅读业务代码，未连接数据库实测。
> 所有路径相对于仓库根 `D:\ZephyrAlpha`（git-bash: `/d/ZephyrAlpha`）。

## 目录

- [1. 仓库顶层结构](#1-仓库顶层结构)
- [2. src/zephyr 总览统计](#2-srczephyr-总览统计)
- [3. 包清单（按职能分层）](#3-包清单按职能分层)
  - [3.1 运行时大脑与编排层](#31-运行时大脑与编排层)
  - [3.2 治理域（Governance 六包）](#32-治理域governance-六包)
  - [3.3 基础设施与共享层](#33-基础设施与共享层)
  - [3.4 安全域](#34-安全域)
  - [3.5 自治与智能层](#35-自治与智能层)
  - [3.6 数据域](#36-数据域)
  - [3.7 量化交易域（信号→因子→回测→组合→执行→风控→报告）](#37-量化交易域信号因子回测组合执行风控报告)
  - [3.8 前端](#38-前端)
  - [3.9 设计态骨架包（12 个，header-only）](#39-设计态骨架包12-个header-only)
- [4. scripts / tests / docs 概览](#4-scripts--tests--docs-概览)
- [5. 疑似异常模块清单（孤儿 / 重复职责 / 命名异常）](#5-疑似异常模块清单孤儿--重复职责--命名异常)

---

## 1. 仓库顶层结构

| 顶层条目 | 内容 | 规模/说明 |
|---|---|---|
| `src/zephyr/` | 全部业务与治理源码（src-layout） | 43 个包，2474 个 `.py`（`find src/zephyr -name "*.py" \| wc -l`） |
| `scripts/` | 治理/运维/诊断脚本 | 590 个 `.py`；含 `governance/`（apply_depgraph.py、apply_decisiongraph.py 等）、`pre_commit/`、`hooks/`、`ch/`、`migration/`、`ops/`、`mcp/` 等子目录 |
| `tests/` | 测试套件 | 2190 个 `.py`，79 个顶层测试目录（a2a/audit/autonomy/blueprint/chaos/capability…） |
| `docs/` | 文档体系 | `01_policies_and_standards/`（规则/裁定/registry）、`02_enterprise_architecture/`、`03_modules/`（按域分 20+ 个 blueprint 目录）、`08_knowledge/`、`code_wiki/`、`CODE_WIKI.md`（v2.1.0 旧版百科） |
| `data/`、`config/` | 能力卡（`data/capability_cards/`）、`config/mcp.json`、`config/trigger_router.yaml` 等 | 见 AGENTS.md |
| 根文件 | `pyproject.toml`（requires-python >=3.12）、`AGENTS.md`（247KB 接入宪法）、`docker-compose.yml`、`requirements*.txt` | — |

## 2. src/zephyr 总览统计

- **总包数：43**（含 `__init__.py` 的顶层目录，不含 `__pycache__`；另有配置文件 `src/zephyr/service_layer_owners.yaml` 直接位于包根）
- **总 `.py` 文件数：2474**（含 `src/zephyr/__init__.py`；各包分项合计 2473 + 根 `__init__.py` = 2474，交叉验证一致）
- **规模两极分化严重**：Top 7 包（feedback_loop 337 / infrastructure 315 / governance 284 / shared 266 / security 179 / gov_enforcement 167 / autonomy_core 113）合计 1661 文件，占 67%；另有 12 个包各仅 7 个文件且全为 header-only 骨架（见 §3.9）。
- 每个包 `__init__.py` 头部携带机器可读元数据注释（`[A_module] module_id=…`、`[BLUEPRINT]`、`[DOMAIN]`、`[MATURITY]`、`[STABILITY]`、`[SAFETY]`、`[AI_AUTONOMY]`），是治理体系的登记入口。

## 3. 包清单（按职能分层）

### 3.1 运行时大脑与编排层

| 包 | py 数 | 一句话职责 | 关键类与函数 |
|---|---|---|---|
| `trading` | 79 | **AutoRuntime Core 系统大脑**：三层运行时编排、启动接线、资源监控、Agent 运行时入口（`python -m zephyr.trading`） | `AutoRuntimeCore`（`auto_runtime_core.py`，主运行时编排器）；`register_boot_hooks()`（`boot_hooks.py`，事件钩子总注册）；`IdeHealthDaemon` 相关（`ide_health_daemon.py`）；`module_onboarding_scanner.py`、`work_orchestrator.py`、`conductor.py`、`dream_cycle.py`、`night_shift_queue.py`、`orphan_detector.py`、`resource_optimization.py` |
| `orchestrator` | 70 | **AgentOrchestrator**：Agent 生命周期/路由/容错/回滚（MOD-INF-039 blueprint） | `RoutingRole`/`RoutingStrategy`/`AgentProfile`/`RouteDecision`/`ToolCallRecord`/`OrchestrationResult`（`agent_orchestrator.py`）；`rollback_manager.py`、`hallucination_detector.py`、`task_queue.py`、`agent_health_monitor.py`；子包 `contracts/ execution/ fault_tolerance/ governance/ lifecycle/ quality/ resilience/` |
| `autonomy_core` | 113 | 自治核心：技能注册/RBAC、阶段规划、触发路由、渐进披露注入 | `SpecEngine`+`UpgradePhase`/`UpgradeResult`（`spec_engine.py`）；`PhasePlanner`/`Phase`（`phase_planner.py`）；`TriggerRouter`（`trigger_router.py`）；`skill_rbac_registry.py`、`progressive_disclosure_injector.py`、`file_autoregister.py`、`vibe_coding_quality_gate.py`；子包 `context/ integration/ models/ skills/` |

### 3.2 治理域（Governance 六包）

| 包 | py 数 | 一句话职责 | 关键类与函数 |
|---|---|---|---|
| `governance` | 284 | 治理总域：任务状态机、depgraph schema、29 个治理子域目录 | `TaskRepositoryError`/`InvalidTransitionError`/`P0InflationFrozenError` 等状态机异常（`persistence/task_repo.py`）；`capability_lookup.py`（能力反查）；`depgraph_schema.py`、`evidence_pack.py`、`integrity.py`；子包含 `engine/ persistence/ rollback/ escalation/ semantic_audit/` 等 29 个 |
| `gov_enforcement` | 167 | **治理执行域**：GitCommitGateway、session_worktree、85 个 commit gate | `GitCommitGateway` 相关 `CommitStatus`/`CommitResult`/`_GlobalCommitLock`（`rule_bridge/git_commit_gateway.py`）；`session_worktree_start/commit/merge/abort` 及 `StartResult` 等 TypedDict（`rule_bridge/session_worktree.py`）；`commit_gates/`（85 个 gate 文件）、`rule_enforcement/`、`behavioral_admission/` |
| `gov_drift` | 74 | **漂移检测**（MOD-INF-023）：66+ 检测器，5 聚合命名约定（ARCH-042 裁定不建物理子目录） | `load_detector_registry()`（`drift_engine.py`）；聚合模块 `_core.py`/`_drift.py`/`_scanners/`detector_core/`；`cascade_detector.py`、`contract_drift_detector.py`、`backcompat_checker.py`、`chaos_injector.py` 等 |
| `gov_audit` | 70 | 审计域（MOD-INF-020，SAFETY=H）：准入判定、事件存证、DORA 指标 | `audit_admission_controller.py`（AdmissionResult 唯一准入判定）；`event_store.py`、`evidence_pack.py`、`audit_schema.py`、`dora_metrics.py`、`code_archaeology.py`、`cli.py` |
| `gov_code_quality` | 66 | 代码质量治理域（D_GOV_CODE_QUALITY） | 顶层仅 `__init__.py`（`__all__` 为空）；实质内容在 `code_dedup/` 等子包 |
| `gov_rule` | 3 | 规则治理域（D_GOV_RULE） | 仅 `constitutional_update/` 子包，3 个文件，体量极小 |

### 3.3 基础设施与共享层

| 包 | py 数 | 一句话职责 | 关键类与函数 |
|---|---|---|---|
| `infrastructure` | 315 | 运行时基础设施：DB 唯一真源、事件存证、成本、A2A、修复引擎 | `DatabaseService`（`database_service.py`，ClickHouse/PostgreSQL 统一访问）；`EventStore`/`StoredEvent`（`event_store.py`，SQLite WAL+SHA256 审计）；`CostTracker`/`UsageRecord`（`cost_tracker.py`）；子包 `a2a_protocol/`（Agent 间通信）、`auto_fix_engine/`、`health_monitor/`、`sla/`、`observability/`、`rollback/`、`asset_inventory/` 等 20+ |
| `shared` | 266 | 共享层：事件总线单例、跨层契约、工具集 | `EventBus`/`EventType`/`DomainEvent`/`EventBusBackpressure`（`event_bus.py`，`bus` 单例）；`contracts/`（factor_signal、market_data、execution_report、llm_gateway_protocol 等 15+ 契约文件）；子包 `events/ database/ protocols/ resilience/ observability/ utils/` 等 30 个 |
| `integration` | 76 | 集成层：管线编排 M1-M11、LLM 桥、MCP 基类 | `PipelineOrchestrator` 实现（`pipeline_orchestrator.py`，含 `_process_module_artifacts` 等内部函数）；`LLMBridge`（`llm_bridge.py`）；`mcp/_base_server.py`（BaseMCPServer）；`get_asset_summary`（`mcp_server.py`）；子包 `behavioral_admission/ budget_enforcer/ local_model/ vector_memory/` |

### 3.4 安全域

| 包 | py 数 | 一句话职责 | 关键类与函数 |
|---|---|---|---|
| `security` | 179 | 安全总域（MOD-INF-018）：LSG 十层防御、访问控制、对抗验证 | `LSGSecurityGateway`/`ScanMode`/`ScanResult`（`llm_defense/llm_security/gateway.py`，L1-L8 安检）；子包 `access_control/`（KillSwitch SSoT）、`adversarial_validation/`、`core/ models/ services/` |
| `red_blue_validator` | 1 | 红蓝验证器——**纯 re-export shim** | `__init__.py` L8 自述 "re-export shim for zephyr.security.adversarial_validation"，L3 标注 `[DOMAIN] D_SECURITY`；无独立实现 |

### 3.5 自治与智能层

| 包 | py 数 | 一句话职责 | 关键类与函数 |
|---|---|---|---|
| `feedback_loop` | 337 | **反馈循环引擎**（MOD-FEEDBACK_LOOP，全仓最大包）：采集→检测→诊断→演化 | `FeedbackLoop`/`EvolutionProposal`（`core.py`）；`EvolutionEngine`/`evolve()`（`evolution_engine.py`）；`FeedbackLoopScheduler`（`scheduler.py`）；`DecisionEngine`（`decision_engine.py`）；子包 `actors/ collectors/ detectors/ diagnosers/ evolution/ forensic/ gates/ resilience/ security/ verifiers/` |
| `intelligence` | 43 | 模型能力考试/评测（MOD-INF-036） | `ModelDriftDetector`/`DriftResult`（`model_drift_detector.py`）；子包 `model_evaluation/ model_profiling/ core/ services/` |

### 3.6 数据域

| 包 | py 数 | 一句话职责 | 关键类与函数 |
|---|---|---|---|
| `data` | 50 | **数据源集成器**（MOD-L00-004）：8 源 61 任务下载/断点续传/熔断，ClickHouse 读写 | `DataSourceBase`/`DataSourceMeta`/`FetchResult`/`CapabilityContract`（`provider_base.py`）；`IntegratorScheduler`（`scheduler.py`）；`ch_reader.py`/`ch_writer.py`/`ch_config.py`；`quality_gate.py`、`integrity_checker.py`、`backfill_checker.py`、`cli.py`（7 子命令）；子包 `redundant_source/ satellite_geospatial_engine/ wal_codec/` |

（`market_data`、`alt_data`、`cross_asset`、`data_eng`、`data_governance`、`data_security`、`digital_twin` 为骨架包，见 §3.9。）

### 3.7 量化交易域（信号→因子→回测→组合→执行→风控→报告）

| 包 | py 数 | 一句话职责 | 关键类与函数 |
|---|---|---|---|
| `factor` | 11 | 因子域（MOD-L02-001）：因子基类+注册表+自动发现 | `FactorBase`/`FactorMeta`/`FactorRegistry`/`autodiscover_factors()`（`factor_base.py`）；`Momentum20d`（`momentum_factor.py`）；`ValueFactor`（`value_factor.py`）；`alpha_signal_pipeline.py`、`bus_factor_defense.py` |
| `signal_fundamental` | 24 | 基本面信号域（MOD-L03-001） | `AlphaSignalPipeline`/`PipelineStage`/`PipelineResult`（`pipeline.py`）；子包 `capital/ combiner/ gen/ strategy/ synth/` |
| `signal_quality` | 8 | 信号质量域（D_SIGQC，MOD-INF-040）：信号退化监控 | `DegradationMonitorBase`（`degradation_monitor_base.py`） |
| `backtest` | 25 | 回测域（MOD-BT-001）：引擎基类+向量化实现+IO | `BacktestEngineBase`/`BacktestResult`/`FactorDiscovery`（`core/engine_base.py`）；`DefaultBacktestEngine`/`BacktestConfig`（`implementations/vectorized_engine.py`）；`io/`（v1.3.0 新增，配合 Panel 重构） |
| `pf_core` | 9 | 组合核心（MOD-L05-001）：策略基类与默认股票策略 | `DefaultEquityStrategy`/`RebalanceMode`（`default_equity_strategy.py`）；`strategy_engine/`、`strategies/` 子包（均仅 `__init__.py`，偏骨架） |
| `pf_alloc` | 8 | 组合配置：策略生命周期事件 | `strategy_lifecycle_event.py`（唯一实质文件，`__all__ = ["strategy_lifecycle_event"]`） |
| `position` | 8 | 持仓域：持仓对账 | `PositionReconciler`（`position_reconciler.py`，唯一导出） |
| `ex_core` | 12 | 执行核心（MOD-L06-001）：算法执行引擎+订单管理 | `ExecutionEngine`/`AlgoType`/`ExecutionConfig`（`execution_engine.py`）；`OrderManager`/`OrderAction`（`order_manager.py`） |
| `risk` | 20 | 风控域（MOD-L04-001）：风险管理/校验/限额/止损 | `RiskManagerBase`（`risk_manager.py`）；`RiskValidator`（`risk_validator.py`）；`RiskLimitsCalculator`（`risk_limits.py`）；`StopLossResult`（`stop_loss.py`）；子包 `cross_asset/` |
| `compliance` | 15 | 合规域（MOD-L10-001，STABILITY=frozen / immutable_core） | 子包 `audit_orchestrator/ audit_trail/ behavioral_admission/ behavioral_auditor/ compliance_gate_a6/`（顶层无实质文件） |
| `reporting` | 10 | 报告域（MOD-L07-001）：归因+TCA 交易成本分析 | `AttributionEngineBase`/`TCAEngineBase`（`analytics_base.py`）；`DefaultAttributionEngine`（`default_attribution_engine.py`）；`DefaultTCAEngine`（`default_tca_engine.py`） |
| `simulation` | 10 | 仿真实验域（MOD-L13-001） | `ExperimentPipelineBase`/`ScoutAgentBase`/`ExperimentConfig`（`pipeline_base.py`） |
| `ml_train` | 11 | 模型训练域（MOD-L11-001） | `ModelTrainerBase`/`ModelRegistry`/`ModelMetadata`（`trainer_base.py`）；`InferenceEngineBase`（`inference_base.py`） |
| `research` | 1 | 研究创新核（MOD-L09-001）——**空壳 stub** | `__init__.py` L1 docstring + L3 `__all__ = []`，无任何实现 |

### 3.8 前端

| 包 | py 数 | 一句话职责 | 关键类与函数 |
|---|---|---|---|
| `frontend` | 24 | HMI 核心（MOD-L08-001）：Panel+HoloViz 仪表盘 | `app_panel.py`（`frontend/dashboard/`，v3.1.0 主入口，10 Tab）；`app.py`（旧 Streamlit 残留？）；`Notification`/`ApprovalRequest`（`interface_base.py`）；`dashboard/components/` |

### 3.9 设计态骨架包（12 个，header-only）

以下 12 个包结构完全同构（各 7 个 `.py`：`__init__` + `_extensions/ api/ core/ infrastructure/ models/ services/` 六个空子包 `__init__`），所有文件仅含元数据头注释（`[MATURITY] design`、`[INVARIANTS] none`），**无任何类/函数实现**，属 depgraph 设计态占位：

| 包 | 标注域 | 推定职责 |
|---|---|---|
| `alt_data` | D_ALT_DATA | 另类数据 |
| `cross_asset` | D_CROSS_ASSET | 跨资产 |
| `data_eng` | D_DATA_ENG | 数据工程 |
| `data_governance` | D_DATA_GOV | 数据治理 |
| `data_security` | D_DATA_SEC | 数据安全 |
| `digital_twin` | D_DIGITAL_TWIN | 数字孪生 |
| `ex_sor` | D_EX_SOR | 智能订单路由（SOR） |
| `execution_simulation` | D_EXEC_SIM | 执行仿真 |
| `market_data` | D_MKT_DATA | 行情数据（依赖 `zephyr.shared.contracts.market_data`） |
| `ml_serve` | D_ML_SERVE | 模型服务 |
| `sell_decision` | D_SELL_DECISION | 卖出决策 |
| `signal_ashare` | D_ASHARE_SIGNAL | A 股信号（BLUEPRINT 标注 MOD-INF-038） |

## 4. scripts / tests / docs 概览

- **scripts/（590 py）**：治理工具链为主体。`governance/` 下含 depgraph/decisiongraph 写入器（`apply_depgraph.py`、`apply_decisiongraph.py`、`apply_dataflowgraph.py`）、`generate_project_depgraph.py`、D1-D12 审计目录（`d1_structure/` … `d12_ai_hallucination/`）、`d8_doc_sync/`、`data_quality/check_tick_duplication.py` 等；顶层有 GitCommitGateway CLI（`git_commit.py`）、守护进程（`ide_health_service.py`、`lock_files.py`）、`scaffold.py`、`rollback.py`。多个 PowerShell 调度脚本（`start_scheduler.ps1` 等）。
- **tests/（2190 py，79 个顶层目录）**：按主题切分（`audit/`、`autonomy/`、`blueprint/`、`chaos/`、`cold/`（冷启动）、`capability/`、`agent_rbac/` 等），与治理域高度对应；`conftest.py` 在顶层。
- **docs/**：`01_policies_and_standards/`（规则真源 `rules/trae_*.yaml` + `_registry/catalogs/` 31 registry + `ruling_registry.yaml`）、`02_enterprise_architecture/`、`03_modules/`（20+ 域 blueprint 目录，与包元数据 `[BLUEPRINT]` 字段一一对应）、`08_knowledge/`、旧版 `CODE_WIKI.md`（v2.1.0，2026-07-22）与本 `code_wiki/` 目录并存。

## 5. 疑似异常模块清单（孤儿 / 重复职责 / 命名异常）

### 5.1 疑似孤儿 / 空壳

1. **`research`（1 文件）**：`__init__.py` 仅 docstring + `__all__ = []`（`src/zephyr/research/__init__.py` L1-L3），MOD-L09-001 "Research Innovation Core" 完全无实现——最典型孤儿。
2. **12 个 header-only 骨架包**（§3.9）：仅设计态登记，无实现；当前对孤儿率的贡献为"名义接入、实质空转"。其中 `signal_ashare`（MOD-INF-038）与 `signal_fundamental`/`signal_quality` 同属 `_domain_signal` blueprint 体系，预留迹象明显。
3. **`gov_rule`（3 文件）**：规则治理域仅 `constitutional_update/` 一个子包，与 284 文件的 `governance` 体量悬殊，疑似迁移中途态。
4. **`pf_alloc`（8 文件）**：唯一实质导出是 `strategy_lifecycle_event`，且头部 `module_id=MOD-UNK-pf_alloc`（UNK=未登记），疑未完成立项。

### 5.2 重复职责信号

5. **安全域三点重叠**：`security`（MOD-INF-018，179 文件）/ `data_security`（D_DATA_SEC 骨架）/ `red_blue_validator`（`__init__.py` L3 标注 `[DOMAIN] D_SECURITY`，L8 自述为 `security.adversarial_validation` 的 re-export shim）。**`red_blue_validator` 与 `security` 同域（D_SECURITY）却单独立包**，属"同一安全域两个入口"的命名/归属异常信号（对应任务提示的"24-D 与 26-D 安全域"类信号；depgraph 编号未实测验证）。
6. **审计三处并存**：`gov_audit`（70 文件，MOD-INF-020）vs `governance/audit-trail/` + `governance/audit/` vs `compliance/audit_trail/` + `compliance/audit_orchestrator/`——审计职责横跨 3 个包 4 个子目录。
7. **漂移检测双包**：`gov_drift`（74 文件，MOD-INF-023）vs `governance/drift-detector/`（连字符目录），且 `intelligence/model_drift_detector.py` 与 `gov_drift/contract_drift_detector.py` 均含 "drift detector" 命名。
8. **shared 与 infrastructure 子目录大面积同名**：`adaptation/ compensation/ dependency/ draft/ lifecycle/ events/ api/` 等在两包中同时存在（§3.3），共享层与基础设施层边界模糊。
9. **行情/数据域碎片化**：`data`（实质实现 50 文件）vs `market_data`/`alt_data`/`data_eng`/`data_governance`/`data_security`（全骨架）+ `governance/data_governance/`——"数据治理"在 `data_governance` 包与 `governance/data_governance/` 各出现一次。

### 5.3 命名 / 元数据异常

10. **BLUEPRINT ID 撞号（auto-injected 元数据错误）**：
    - `trading/__init__.py` L1 与 `pf_alloc/__init__.py` L1 同被 S4 reconciler 注入 `[BLUEPRINT] MOD-INF-016`——一包一号原则被破坏；
    - `orchestrator/__init__.py` L7 `[BLUEPRINT] MOD-INF-039` 与 `signal_fundamental/__init__.py` L1 `module_id=MOD-INF-039` 撞号（且 signal_fundamental 自身 L2 另标 `[BLUEPRINT] MOD-L03-001`，一头两号）；
    - `integration/__init__.py` L1 与 `shared/__init__.py` L1 均被注入 `[BLUEPRINT] MOD-GOVERNANCE`——与 `governance/__init__.py` L1 的正主标注冲突，明显的 reconciler 误注入。
11. **连字符 vs 下划线目录并存**（Python 不可导入形式与可导入形式混用）：`governance/agent-rbac/` 与 `governance/agent_rbac/`、`governance/agent-spec/` 与 `governance/agent_spec/` 各自成对存在；`governance/audit-trail/`、`budget-enforcer/`、`drift-detector/` 为连字符目录（无法被 `import` 直接引用）。
12. **scripts/ 清单文件双名 + 临时残留**：`scripts/script-manifest.yaml` 与 `scripts/script_manifest.yaml` 并存，且有孤儿临时文件 `scripts/script_manifest.yaml.4160.tmp`。
13. **配置文件混入包根**：`src/zephyr/service_layer_owners.yaml` 为 src 树中唯一顶层 YAML，与 src-layout 纯代码惯例不符。

---

### 统计复核

| 指标 | 数值 | 核验方式 |
|---|---|---|
| src/zephyr 顶层包数 | **43** | `ls src/zephyr/` 排除 `__pycache__` 与 `service_layer_owners.yaml` |
| src/zephyr 总 `.py` 文件数 | **2474** | `find src/zephyr -name "*.py" \| wc -l`；分包含计 2473 + 根 `__init__.py` = 2474 ✓ |
| 实质实现包 | 30 | 排除 12 骨架包 + `research` stub |
| 纯设计态骨架包 | 12 | §3.9，各 7 文件 header-only |
| scripts/ `.py` | 590 | `find scripts -name "*.py" \| wc -l` |
| tests/ `.py` | 2190 | `find tests -name "*.py" \| wc -l`，79 个顶层目录 |

> 局限：未运行 depgraph 查询实测孤儿率与蓝图编号（DB 连接未验证）；包职责推断基于头部元数据、docstring 与 `grep '^class '` 符号提取，未逐行核读。
