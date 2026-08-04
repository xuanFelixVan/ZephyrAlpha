---
doc_type: audit_report
title: 作战地图对齐报告
version: "1.0"
status: active
date: 2026-08-04
owner: auto-generator
ttl: permanent
---

# 作战地图对齐报告 (Battle Map Alignment Report)

- 生成时间: 2026-08-04 21:16:48
- 数据源: depgraph (PostgreSQL)
- 三表统计: steps=324 / anchors=468 / edges=119 / 叙事真源=285
- 业务域模块: 1770（BM-INV-007 扫描范围，业务域白名单内 depgraph 节点）
- 问题总数: 222
  - 孤儿环节（BM-INV-001，无锚点=悬空决策）: 28
  - 幽灵锚点（BM-INV-002，target_id 找不到）: 0
  - 缺失叙事（BM-INV-003，翻译真源无环节）: 39
  - 悬空边（edge 指向不存在环节）: 0
  - 域漂移（BM-INV-004，target domain 不在 flow_stage 允许列表）: 2
  - 父子嵌套问题（BM-INV-006，父不存在/跨阶段/成环/depth超限）: 0
  - 孤儿模块（BM-INV-007，业务域模块无作战锚点=造出来没用上）: 153

## 1. 孤儿环节（BM-INV-001：环节无锚点 = 悬空决策）

> 君子协定：每个 battle_map_steps 必须至少有一个 battle_map_anchors。无锚点环节 = 没有模块承载 = AI 写决策时凭记忆推断 = 幻觉风险。

| step_id | 环节名 | 阶段 | 设计成熟度 |
|---|---|---|---|
| BM-BT-08 | 试运行与验证 | backtest_validation | design |
| BM-BUY-10 | 合规技术深度 | buy_flow | design |
| BM-BUY-11 | 合规持续运营 | buy_flow | design |
| BM-BUY-12 | 硬边界裁定 | buy_flow | design |
| BM-BUY-13 | 合规裁定扩展-EU AI Act | buy_flow | design |
| BM-BUY-15 | 交易合规检测 | buy_flow | design |
| BM-MT-06 | 元学习与自我进化 | model_training | design |
| BM-MT-06-A | 元学习RSI四维度 | model_training | design |
| BM-MT-06-B | 学习效果反馈闭环 | model_training | design |
| BM-RES-08 | 知识清洗与结构化 | research_incubation | design |
| BM-RES-09 | 知识分类与策略提取 | research_incubation | design |
| BM-RES-10 | 模块映射与工厂匹配 | research_incubation | design |
| BM-RES-11 | 多模态知识采集 | research_incubation | design |
| BM-RES-08-A | 知识清洗流水线 | research_incubation | design |
| BM-RES-09-A | 知识类型分类体系 | research_incubation | design |
| BM-RES-10-A | 模块工厂架构 | research_incubation | design |
| BM-RES-11-A | 采集源分类与调度 | research_incubation | design |
| BM-RC-10 | 风险否决权 | risk_control | design |
| BM-RC-11 | 独立风险数据管道 | risk_control | design |
| BM-RC-12 | 极端事件与黑天鹅 | risk_control | design |
| BM-RC-10-A | 否决执行引擎 | risk_control | design |
| BM-RC-11-A | 独立风险指标计算 | risk_control | design |
| BM-RC-11-B | 风险报告生成 | risk_control | design |
| BM-RC-12-A | 黑天鹅模式库 | risk_control | design |
| BM-RC-12-B | 跨市场传导与传染模型 | risk_control | design |
| BM-RC-12-C | 流动性危机模拟 | risk_control | design |
| BM-SEL-26 | 决策可解释性与人机协作 | stock_selection | design |
| BM-SEL-27 | 盘中实时事件处理 | stock_selection | design |

## 2. 幽灵锚点（BM-INV-002：target_id 在目标图找不到）

> 君子协定：anchor.target_id 必须能在 target_graph 对应的图/仓库里找到。找不到 = 幽灵锚点 = 指向不存在的模块/候选/蓝图。

> ✅ 无幽灵锚点（或锚点表为空，无对象校验）。

## 3. 缺失叙事（BM-INV-003：翻译真源无对应环节）

> 君子协定：DB 每个环节必须在翻译真源 `battle_map_steps` 段有叙事（name_zh/plain_zh/mechanism_zh/indicators_zh）。缺失 = 生成器降级到 DB step_name。

| step_id | 环节名 | 阶段 |
|---|---|---|
| BM-BT-08 | 试运行与验证 | backtest_validation |
| BM-BUY-09 | 信息合规 | buy_flow |
| BM-BUY-10 | 合规技术深度 | buy_flow |
| BM-BUY-11 | 合规持续运营 | buy_flow |
| BM-BUY-12 | 硬边界裁定 | buy_flow |
| BM-BUY-13 | 合规裁定扩展-EU AI Act | buy_flow |
| BM-BUY-15 | 交易合规检测 | buy_flow |
| BM-BUY-08-A | 四项必做清单自动化检测 | buy_flow |
| BM-BUY-08-B | 四项严禁自动化检测 | buy_flow |
| BM-MT-06 | 元学习与自我进化 | model_training |
| BM-MT-06-A | 元学习RSI四维度 | model_training |
| BM-MT-06-B | 学习效果反馈闭环 | model_training |
| BM-REC-03-D | 元级迭代与二阶优化 | reconciliation |
| BM-RES-08 | 知识清洗与结构化 | research_incubation |
| BM-RES-09 | 知识分类与策略提取 | research_incubation |
| BM-RES-10 | 模块映射与工厂匹配 | research_incubation |
| BM-RES-11 | 多模态知识采集 | research_incubation |
| BM-RES-08-A | 知识清洗流水线 | research_incubation |
| BM-RES-09-A | 知识类型分类体系 | research_incubation |
| BM-RES-10-A | 模块工厂架构 | research_incubation |
| BM-RES-11-A | 采集源分类与调度 | research_incubation |
| BM-RC-09 | AI/Agent风险治理 | risk_control |
| BM-RC-10 | 风险否决权 | risk_control |
| BM-RC-11 | 独立风险数据管道 | risk_control |
| BM-RC-12 | 极端事件与黑天鹅 | risk_control |
| BM-RC-10-A | 否决执行引擎 | risk_control |
| BM-RC-11-A | 独立风险指标计算 | risk_control |
| BM-RC-11-B | 风险报告生成 | risk_control |
| BM-RC-12-A | 黑天鹅模式库 | risk_control |
| BM-RC-12-B | 跨市场传导与传染模型 | risk_control |
| BM-RC-12-C | 流动性危机模拟 | risk_control |
| BM-SEL-26 | 决策可解释性与人机协作 | stock_selection |
| BM-SEL-27 | 盘中实时事件处理 | stock_selection |
| BM-SEL-02-J | 信号工厂子阶段流水线 | stock_selection |
| BM-SEL-02-K | 多策略投票与加权 | stock_selection |
| BM-SEL-02-L | 信号聚合器架构 | stock_selection |
| BM-SEL-05-D | 主力行为自迭代推演 | stock_selection |
| BM-SEL-05-E | 庄家行为识别与模拟 | stock_selection |
| BM-SEL-05-F | 多方博弈模拟 | stock_selection |

## 4. 悬空边（edge 指向不存在的环节）

> ✅ 无悬空边，所有流转边两端均为合法环节。

## 5. 域漂移（BM-INV-004：target domain 不在 flow_stage 允许列表）

> 君子协定：anchor 的 target module/candidate 的 domain 必须在 step.flow_stage 对应的允许域列表里。不在 = 域漂移 = 语义错位（如把卖出决策挂在买入流程）。规则真源：`docs/01_policies_and_standards/_registry/catalogs/battle_map_domain_policy.yaml`。

| anchor_id | step_id | flow_stage | target_graph | target_id | target_domains | 角色 |
|---|---|---|---|---|---|---|
| 513 | BM-REC-03 | reconciliation | depgraph | MOD-INF-014 | D_INTEGRATION | supplement |
| 514 | BM-RES-04 | research_incubation | depgraph | MOD-INF-013 | D_GOVERNANCE, D_INTEGRATION | supplement |

## 6. 父子嵌套问题（BM-INV-006：父不存在/跨阶段/成环/depth超限）

> 君子协定：parent_step_id 必须指向同 flow_stage 的已存在环节，depth≤3，parent 链不能成环。规则真源：battle_map_positioning.md §8.4。

> ✅ 无父子嵌套问题。

## 7. 孤儿模块（BM-INV-007：业务域模块无作战锚点 = 造出来没用上）

> 君子协定：业务域（battle_map_domain_policy.yaml 所有 flow_stage 的 allowed 域并集）内的 depgraph 模块，必须至少有一个 battle_map_anchors 指向它（target_graph=depgraph，target_id 命中其 blueprint_id 或 path）。无任何锚点指向 = 没有作战使命 = 造出来没用上 = 幻觉/浪费风险。非业务域（D_GOVERNANCE/D_GOV_SCRIPTS/D_FRONTEND 等基础设施/治理/工具）天然排除，不在此扫。

| blueprint_id | 名称 / Name | domain_id | build_status | path |
|---|---|---|---|---|
| None | SQLite 任务库 / SQLite Task DB | D_INFRA_RUNTIME | stable | docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml#INFRA-DB-001 |
| None | ChromaDB 向量数据库 / ChromaDB Vector DB | D_INFRA_RUNTIME | stable | docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml#INFRA-DB-002 |
| None | 依赖架构图库 / Depgraph PostgreSQL DB | D_INFRA_RUNTIME | stable | docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml#INFRA-DB-003 |
| None | ClickHouse 业务行情仓库 / ClickHouse Market Warehouse | D_INFRA_RUNTIME | stable | docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml#INFRA-DB-006 |
| MOD-ML-003 | 训练数据集管理器 / Training Dataset Manager | D_ML_TRAIN | planned | src/zephyr/ml_train/training_dataset_manager/ |
| MOD-DAT-fred_ingest | FRED宏观数据获取器 | D_DATA | generated | src/zephyr/data/implementations/fred_provider.py |
| MOD-EX-051 | 值对象 / Value Objects | D_EX_CORE | planned | src/zephyr/ex_core/value_objects.py |
| MOD-EX-029 | 停止亏损止盈利润执行器 / stop_loss_take_profit_executor | D_EX_CORE | planned | src/zephyr/ex_core/stop_loss_take_profit_executor.py |
| MOD-SIG-009 | 信号优先级路由器 / Signal Priority Router | D_FUNDAMENTAL_SIGNAL | planned | src/zephyr/signal_fundamental/router/signal_priority_router.py |
| MOD-POS-005 | 跨策略持仓合并器 / Cross Strategy Position Merger | D_POSITION | planned | src/zephyr/position/core/cross_strategy_position_merger.py |
| MOD-POS-011 | 协方差估计器 / Covariance Estimator | D_POSITION | planned | src/zephyr/position/core/covariance_estimator.py |
| MOD-H1_REDIS_HOT | H1因子源 / H1 Factor Source | D_INFRA_RUNTIME | deprecated | src/zephyr/infrastructure/h1_redis_hot/h1_factor_source.py |
| MOD-POS-015 | 持仓时间预算 / Position Time Budget | D_POSITION | planned | src/zephyr/position/core/position_time_budget.py |
| MOD-EX-012 | 执行交易成本分析 / Execution Tca | D_EX_CORE | planned | src/zephyr/ex_core/execution_tca.py |
| MOD-EX-021 | 部署一致性管理器 / Deployment Consistency Manager | D_EX_CORE | planned | src/zephyr/ex_core/deployment_consistency_manager.py |
| MOD-EX-036 | 性能监控器 / Performance Monitor | D_EX_CORE | planned | src/zephyr/ex_core/performance_monitor.py |
| MOD-L00-007 | 存储 | D_DATA | planned | src/zephyr/data/storage/ |
| MOD-EX-015 | 执行报告 / execution_report | D_EX_CORE | deprecated | src/zephyr/ex_core/execution_report.py |
| MOD-SIG-010 | 信号冲突解决器 / Signal Conflict Resolver | D_FUNDAMENTAL_SIGNAL | planned | src/zephyr/signal_fundamental/router/signal_conflict_resolver.py |
| MOD-EX-031 | 批次止盈利润执行器 / batch_take_profit_executor | D_EX_CORE | planned | src/zephyr/ex_core/batch_take_profit_executor.py |
| MOD-EX-032 | 拍卖偏差执行器 / auction_deviation_executor | D_EX_CORE | planned | src/zephyr/ex_core/auction_deviation_executor.py |
| MOD-RSK-009 | A股止损亏损规则引擎 / Ashare Stop Loss Rule Engine | D_RISK | deprecated | src/zephyr/risk/ashare_stop_loss_rule_engine.py |
| None | 测试触发器A / Test Trigger A | D_ALT_DATA | deprecated | test_trigger_A.py |
| MOD-EX-059 | 执行MCP服务端 / execution_mcp_server | D_EX_CORE | planned | src/zephyr/ex_core/execution_mcp_server.py |
| MOD-EX-042 | conditional订单管理器 / conditional_order_manager | D_EX_CORE | planned | src/zephyr/ex_core/conditional_order_manager.py |
| MOD-L00-008 | 缓存 | D_DATA | planned | src/zephyr/data/cache/ |
| None | 测试触发器B / Test Trigger B | D_ASHARE_SIGNAL | deprecated | test_trigger_B.py |
| MOD-RISK-001 | 回撤跟踪器 / Drawdown Tracker | D_RISK | deprecated | src/zephyr/risk/drawdown_tracker/ |
| MOD-PF-004 | 最小方差策略 / Min Variance Strategy | D_PF_CORE | deprecated | src/zephyr/pf_core/strategies/min_variance_strategy.py |
| MOD-INF-031 | Escalation桥接器 / Escalation Bridge | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/auto_fix_engine/escalation_bridge.py |
| MOD-INF-011 | 蓝图 / Blueprint | D_KNOWLEDGE | planned | docs/03_modules/_domain_knowledge/vector_memory/blueprint.md |
| MOD-PF-005 | 风险平价策略 / Risk Parity Strategy | D_PF_CORE | deprecated | src/zephyr/pf_core/strategies/risk_parity_strategy.py |
| MOD-EX-004 | redis幂等性 | D_EX_CORE | planned | src/zephyr/ex_core/redis_idempotency/ |
| MOD-EX-035 | 实盘仿真切换器 / live_simulation_switcher | D_EX_CORE | planned | src/zephyr/ex_core/live_simulation_switcher.py |
| MOD-POS-012 | 相关性状态监控器 / Correlation Regime Monitor | D_POSITION | planned | src/zephyr/position/core/correlation_regime_monitor.py |
| MOD-POS-013 | 持仓风险预算分配器 / Position Risk Budget Allocator | D_POSITION | planned | src/zephyr/position/core/position_risk_budget_allocator.py |
| MOD-POS-018 | 日内持仓约束 / Intraday Position Constraint | D_POSITION | planned | src/zephyr/position/core/intraday_position_constraint.py |
| MOD-POS-019 | 持仓行为分类器 / Position Behavior Classifier | D_POSITION | planned | src/zephyr/position/core/position_behavior_classifier.py |
| MOD-EX-052 | 工厂 / Factory | D_EX_CORE | planned | src/zephyr/ex_core/factory.py |
| MOD-EX-058 | MiniqmtChannel管理器 / Miniqmt Channel Manager | D_EX_CORE | planned | src/zephyr/ex_core/miniqmt_channel_manager.py |
| MOD-EX-037 | 蓝图Implementer / Blueprint Implementer | D_EX_CORE | planned | src/zephyr/ex_core/blueprint_implementer.py |
| MOD-EX-060 | Rl最优执行器 / Rl Optimal Executor | D_EX_CORE | planned | src/zephyr/ex_core/rl_optimal_executor.py |
| MOD-EX-061 | 微观结构建模器 / Microstructure Modeler | D_EX_CORE | planned | src/zephyr/ex_core/microstructure_modeler.py |
| MOD-RSK-011 | 回撤Realtime跟踪器 / Drawdown Realtime Tracker | D_RISK | deprecated | src/zephyr/risk/drawdown_realtime_tracker.py |
| MOD-RSK-010 | A股Systemic风险检测器 / Ashare Systemic Risk Detector | D_RISK | deprecated | src/zephyr/risk/ashare_systemic_risk_detector.py |
| MOD-EX-033 | 卖出优先级调度器 / sell_priority_scheduler | D_EX_CORE | planned | src/zephyr/ex_core/sell_priority_scheduler.py |
| MOD-INF-031 | 模型 / Models | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/auto_fix_engine/models.py |
| MOD-H1_REDIS_HOT | {symbol}:latest 双写器 / Tick Redis Cache | D_INFRA_RUNTIME | stable | src/zephyr/data/tick_redis_cache.py |
| MOD-INF-011 | 分析 / Analysis | D_SECURITY | generated | src/zephyr/gov_drift/_analysis.py |
| MOD-INF-011 | 核心 / Core | D_SECURITY | generated | src/zephyr/gov_drift/_core.py |
| MOD-INF-011 | 扫描器 / Scanners | D_SECURITY | generated | src/zephyr/gov_drift/_scanners.py |
| MOD-INF-011 | 漂移 / Drift | D_SECURITY | generated | src/zephyr/gov_drift/_drift.py |
| MOD-INF-011 | 基础设施 / Infrastructure | D_SECURITY | generated | src/zephyr/gov_drift/_infrastructure.py |
| MOD-INF-003 | Git 命令批量化工具 / Git Batcher | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/git_batcher.py |
| MOD-INF-031 | 对齐同步器 / Alignment Syncer | D_INFRA_RUNTIME | generated | src/zephyr/infrastructure/auto_fix_engine/alignment_syncer.py |
| MOD-INF-031 | 只读：conflict_resolver / Batch Fixer | D_INFRA_RUNTIME | generated | src/zephyr/infrastructure/auto_fix_engine/batch_fixer.py |
| MOD-INF-031 | 只读：retention_days / Compliance Auditor | D_INFRA_RUNTIME | generated | src/zephyr/infrastructure/auto_fix_engine/compliance_auditor.py |
| MOD-INF-031 | 公共接口：parse_all / All Completer | D_INFRA_RUNTIME | generated | src/zephyr/infrastructure/auto_fix_engine/all_completer.py |
| MOD-INF-031 | 公共接口：fix_trailing_whitespace / Config Fixer | D_INFRA_RUNTIME | generated | src/zephyr/infrastructure/auto_fix_engine/config_fixer.py |
| MOD-INF-031 | 公共接口：normalize_code / Dedup Extractor | D_INFRA_RUNTIME | generated | src/zephyr/infrastructure/auto_fix_engine/dedup_extractor.py |
| MOD-INF-031 | 引擎 / Engine | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/auto_fix_engine/engine.py |
| MOD-INF-031 | 公共接口：check_config / Fix Health Check | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/auto_fix_engine/fix_health_check.py |
| MOD-INF-031 | Dep版本修复器 / Dep Version Fixer | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/auto_fix_engine/dep_version_fixer.py |
| MOD-INF-031 | 修复预算 / Fix Budget | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/auto_fix_engine/fix_budget.py |
| MOD-INF-031 | 只读：event_log / Event Hooks | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/auto_fix_engine/event_hooks.py |
| MOD-INF-031 | 漂移修复器 / Drift Fixer | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/auto_fix_engine/drift_fixer.py |
| MOD-INF-031 | 修复差异 / Fix Diff | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/auto_fix_engine/fix_diff.py |
| MOD-INF-031 | 只读：ttl / Fix Reliability | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/auto_fix_engine/fix_reliability.py |
| MOD-INF-031 | 只读：db_path / Fix Pattern Miner | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/auto_fix_engine/fix_pattern_miner.py |
| MOD-INF-031 | 只读：wal_dir / Interrupt Guard | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/auto_fix_engine/interrupt_guard.py |
| MOD-INF-031 | 只读：history / Fix Report | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/auto_fix_engine/fix_report.py |
| MOD-INF-031 | Import修复器 / Import Fixer | D_INFRA_RUNTIME | generated | src/zephyr/infrastructure/auto_fix_engine/import_fixer.py |
| MOD-INF-031 | 修复调度器 / Fix Scheduler | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/auto_fix_engine/fix_scheduler.py |
| MOD-INF-031 | 只读：enabled / Fix Safety | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/auto_fix_engine/fix_safety.py |
| MOD-INF-031 | 从 script-manifest.yaml 加载已注册脚本路径集合 / Scaffold Registrar | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/auto_fix_engine/scaffold_registrar.py |
| MOD-INF-031 | SelfHeal代理 / Self Heal Agent | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/auto_fix_engine/self_heal_agent.py |
| MOD-INF-031 | 主入口 / Main | D_INFRA_RUNTIME | generated | src/zephyr/infrastructure/auto_fix_engine/__main__.py |
| MOD-INF-031 | 影子Workspace / Shadow Workspace | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/auto_fix_engine/shadow_workspace.py |
| MOD-INF-031 | 只读：secret_guard / Llm Fix Adapter | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/auto_fix_engine/llm_fix_adapter.py |
| MOD-INF-031 | 状态Machine / State Machine | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/auto_fix_engine/state_machine.py |
| MOD-INF-031 | 移除 content 中指向不存在文件的僵尸引用，返回清理后的内容 / Zombie Cleaner | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/auto_fix_engine/zombie_cleaner.py |
| MOD-H1_REDIS_HOT | 连接 D-FACTOR/SIGNAL/RISK 与 H1 热缓存 / H1 Integration | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/h1_redis_hot/h1_integration.py |
| MOD-H1_REDIS_HOT | 事件→Redis 物化视图投影器 / H1 Cqrs Projectors | D_INFRA_RUNTIME | generated | src/zephyr/infrastructure/h1_redis_hot/h1_cqrs_projectors.py |
| MOD-H1_REDIS_HOT | H1 Redis 热缓存 Key Schema / H1 Redis Schema | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/h1_redis_hot/h1_redis_schema.py |
| MOD-H1_REDIS_HOT | 盘中实盘/模拟盘 <5ms 因子截面在线存储 / Init | D_INFRA_RUNTIME | generated | src/zephyr/infrastructure/h1_redis_hot/__init__.py |
| MOD-H1_REDIS_HOT | 决策引擎 <5ms 在线特征查询 / H1 Redis Reader | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/h1_redis_hot/h1_redis_reader.py |
| MOD-H1_REDIS_HOT | D-FACTOR Engine 每 3 秒截面写入 Redis / H1 Redis Writer | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/h1_redis_hot/h1_redis_writer.py |
| MOD-INF-005 | 发现 / Finding | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/script_system/finding.py |
| MOD-INF-005 | 门禁桥接器 / Gate Bridge | D_INFRA_RUNTIME | generated | src/zephyr/infrastructure/script_system/gate_bridge.py |
| MOD-INF-015 | 只读：sla_buffer / Contract Metrics | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/system_telemetry/contract_metrics.py |
| MOD-INF-015 | 5.55.1 修复：探针内部真实检查依赖状态，而非信任外部传入的 deps_ok / Health Probes | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/system_telemetry/health_probes.py |
| MOD-INF-015 | 全自动遥测注入钩子 / Auto Bootstrap | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/system_telemetry/auto_bootstrap.py |
| MOD-INF-015 | 只读：snapshots / Health Aggregator | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/system_telemetry/health_aggregator.py |
| MOD-INF-015 | 指标桥接器 / Metrics Bridge | D_INFRA_RUNTIME | generated | src/zephyr/infrastructure/system_telemetry/metrics_bridge.py |
| MOD-INF-015 | 互检+Panic Mode+Dead Man's Switch / Watchdog | D_INFRA_RUNTIME | generated | src/zephyr/infrastructure/system_telemetry/watchdog.py |
| MOD-INF-015 | 链路桥接器 / Trace Bridge | D_INFRA_RUNTIME | generated | src/zephyr/infrastructure/system_telemetry/_trace_bridge.py |
| MOD-INF-015 | 系统遥测门面类 / Facade | D_INFRA_RUNTIME | generated | src/zephyr/infrastructure/system_telemetry/facade.py |
| MOD-INF-015 | 预算Telemetry桥接器 / Budget Telemetry Bridge | D_INFRA_RUNTIME | generated | src/zephyr/infrastructure/system_telemetry/_budget_telemetry_bridge.py |
| MOD-INF-015 | AI 行为遥测事件管道 / Event Sink | D_INFRA_RUNTIME | generated | src/zephyr/infrastructure/system_telemetry/ai_behavior/event_sink.py |
| MOD-INF-015 | 冷存储归档管道 / Cold Stub | D_INFRA_RUNTIME | generated | src/zephyr/infrastructure/system_telemetry/archive/cold_stub.py |
| MOD-INF-015 | 结构化日志管道 / Structured Sink | D_INFRA_RUNTIME | generated | src/zephyr/infrastructure/system_telemetry/logs/structured_sink.py |
| MOD-INF-015 | 单次蓝图读取事件 / Blueprint Metrics | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/system_telemetry/metrics/blueprint_metrics.py |
| MOD-INF-015 | 结构化日志流 / Init | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/system_telemetry/logs/__init__.py |
| MOD-INF-015 | W3C TraceContext 分布式追踪管道 / Span Stub | D_INFRA_RUNTIME | generated | src/zephyr/infrastructure/system_telemetry/traces/span_stub.py |
| MOD-INF-011 | 桥接器层 / Bridge Layer | D_INTEGRATION | stable | src/zephyr/integration/vector_memory/bridge_layer.py |
| MOD-INF-011 | Chunk策略路由器 / Chunk Strategy Router | D_INTEGRATION | stable | src/zephyr/integration/vector_memory/chunk_strategy_router.py |
| MOD-INF-011 | 跨收集Retriever / Cross Collection Retriever | D_INTEGRATION | generated | src/zephyr/integration/vector_memory/cross_collection_retriever.py |
| MOD-INF-011 | 上下文Ingest / Context Ingest | D_INTEGRATION | generated | src/zephyr/integration/vector_memory/context_ingest.py |
| MOD-INF-011 | 收集管理器 / Collection Manager | D_INTEGRATION | stable | src/zephyr/integration/vector_memory/collection_manager.py |
| MOD-INF-011 | Faiss收集管理器 / Faiss Collection Manager | D_INTEGRATION | generated | src/zephyr/integration/vector_memory/faiss_collection_manager.py |
| MOD-INF-011 | 收集Schemas / Collection Schemas | D_INTEGRATION | stable | src/zephyr/integration/vector_memory/collection_schemas.py |
| MOD-INF-011 | 设计原则 / Design Principles | D_INTEGRATION | stable | src/zephyr/integration/vector_memory/design_principles.py |
| MOD-INF-011 | 单条记忆条目 / Interface | D_INTEGRATION | generated | src/zephyr/integration/vector_memory/interface.py |
| MOD-INF-011 | 只读：store_size / In Memory Fake Vms | D_INTEGRATION | stable | src/zephyr/integration/vector_memory/in_memory_fake_vms.py |
| MOD-INF-011 | 索引Health监控器 / Index Health Monitor | D_INTEGRATION | stable | src/zephyr/integration/vector_memory/index_health_monitor.py |
| MOD-INF-011 | 混合检索器 / Hybrid Retriever | D_INTEGRATION | stable | src/zephyr/integration/vector_memory/hybrid_retriever.py |
| MOD-INF-011 | In记忆记忆后端 / In Memory Memory Backend | D_INTEGRATION | stable | src/zephyr/integration/vector_memory/in_memory_memory_backend.py |
| MOD-INF-011 | In流程向量记忆 / In Process Vector Memory | D_INTEGRATION | stable | src/zephyr/integration/vector_memory/in_process_vector_memory.py |
| MOD-INF-011 | 以 ``UnifiedMemoryAPI`` 为后端的 ``VectorMemoryBase`` 实现 / Delegated Vector Memory | D_INTEGRATION | generated | src/zephyr/integration/vector_memory/delegated_vector_memory.py |
| MOD-INF-011 | Chroma到FAISS迁移 / Migrate Chroma To Faiss | D_INTEGRATION | generated | src/zephyr/integration/vector_memory/migrate_chroma_to_faiss.py |
| MOD-INF-011 | VMS错误 / Vms Errors | D_INTEGRATION | stable | src/zephyr/integration/vector_memory/vms_errors.py |
| MOD-INF-011 | 只读：long_tail / Retrieval Feedback | D_INTEGRATION | stable | src/zephyr/integration/vector_memory/retrieval_feedback.py |
| MOD-INF-011 | 校验 WriteTrace 完整性 / Provenance Enforcer | D_INTEGRATION | stable | src/zephyr/integration/vector_memory/provenance_enforcer.py |
| MOD-INF-011 | 将 UnifiedMemoryAPI 的操作路由到 InProcessVectorMemory / Vms Memory Backend | D_INTEGRATION | generated | src/zephyr/integration/vector_memory/vms_memory_backend.py |
| MOD-INF-011 | Sqlite元数据存储 / Sqlite Metadata Store | D_INTEGRATION | generated | src/zephyr/integration/vector_memory/sqlite_metadata_store.py |
| MOD-INF-011 | 向量桥接器 / Vector Bridge | D_INTEGRATION | generated | src/zephyr/integration/vector_memory/vector_bridge.py |
| MOD-INF-011 | VMS模式定义 / Vms Schemas | D_INTEGRATION | stable | src/zephyr/integration/vector_memory/vms_schemas.py |
| SH-MAIN-001 | 从任务描述行中拆出叙事文本与 ``depends_on`` 列表 / Blueprint Decomposer | D_SHARED | stable | src/zephyr/shared/blueprint_tools/blueprint_decomposer.py |
| MOD-SHARED-002 | 对连接应用 KBG-0030 §4.3 PRAGMA 基线 / Sqlite Factory | D_SHARED | generated | src/zephyr/shared/io/sqlite_factory.py |
| MOD-SHR_IO_YAML | vocabulary YAML 加载公共工具 / Yaml Utils | D_SHARED | generated | src/zephyr/shared/io/yaml_utils.py |
| SH-MAIN-001 | 只读：tasks / Dogfooding | D_SHARED | stable | src/zephyr/shared/maintenance/dogfooding.py |
| SH-MAIN-001 | 维护手册 / Handbook | D_SHARED | stable | src/zephyr/shared/maintenance/handbook.py |
| SH-MAIN-001 | 公共接口：check_python / Zero Config | D_SHARED | stable | src/zephyr/shared/maintenance/zero_config.py |
| MOD-INF-044 | Grafana 双数据源仪表盘模块 / Init | D_SHARED | stable | src/zephyr/shared/observability/dashboard/__init__.py |
| MOD-SHARED-001 | D-INFRA 通过此接口获取 DB 连接和路径 / Ports | D_SHARED | generated | src/zephyr/shared/protocols/ports.py |
| MOD-SHARED-001 | A2A协议 / A2a Protocol | D_SHARED | generated | src/zephyr/shared/protocols/a2a/a2a_protocol.py |
| MOD-SHARED-001 | 进程级单例服务注册表 / Registry | D_SHARED | generated | src/zephyr/shared/protocols/registry.py |
| MOD-SHARED-001 | A2A注册表 / A2a Registry | D_SHARED | generated | src/zephyr/shared/protocols/a2a/a2a_registry.py |
| MOD-SHARED-001 | A2A模式定义 / A2a Schemas | D_SHARED | generated | src/zephyr/shared/protocols/a2a/a2a_schemas.py |
| MOD-SHARED-001 | A2A协调 / A2a Coordination | D_SHARED | generated | src/zephyr/shared/protocols/a2a/a2a_coordination.py |
| MOD-SHR_CONVERTERS | 将空字符串转为 None，其他值原样返回 / Converters | D_SHARED | stable | src/zephyr/shared/utils/converters.py |
| MOD-OPS-018 | 开发环境一次性初始化 / Setup Dev Env | D_OPS | generated | scripts/setup_dev_env.py |
| MOD-E2E-001 | D-FACTOR → D-BACKTEST 数据流验证 / Test Backtest Factor E2e | D_BACKTEST | generated | tests/factor/test_backtest_factor_e2e.py |
| MOD-TEST_SURGE_FALL_STRATEGY | IntradaySurgeFallStrategy 单元测试 / Test Intraday Surge Fall Strategy | D_PF_CORE | generated | tests/pf_core/test_intraday_surge_fall_strategy.py |
| MOD-TEST_STRATEGY_RUNNER_TICK | StrategyRunner.run_tick_backtest 单元测试 / Test Strategy Runner Tick | D_PF_CORE | generated | tests/pf_core/test_strategy_runner_tick.py |
| MOD-H1_REDIS_HOT | tick→Redis tick:{symbol}:latest 双写器 / Test Tick Redis Cache | D_INFRA_RUNTIME | generated | tests/zephyr/data/test_tick_redis_cache.py |
| MOD-RUNTIME_INTRADAY | IntradayRuntime 盘中编排器单元测试 / Test Intraday Main | D_INFRA_RUNTIME | generated | tests/zephyr/runtime/test_intraday_main.py |
| MOD-TEST_METRICS_SERVER | metrics_server 单元测试 / Test Metrics Server | D_SHARED | generated | tests/zephyr/shared/observability/test_metrics_server.py |
|  | 任务 / tasks | D_DATA | generated | src/zephyr/data/config/tasks.yaml |
|  | 调度计划 / schedule | D_DATA | generated | src/zephyr/data/config/schedule.yaml |
| MOD-RUNTIME_INTRADAY | 单进程串起 tick_subscriber + IntradayFactorLoop / Intraday Main | D_INFRA_RUNTIME | stable | src/zephyr/runtime/intraday_main.py |
|  | 策略 / policies | D_DATA | generated | src/zephyr/data/config/policies.yaml |
| MOD-BT-025 | 结果deployer / result_deployer | D_BACKTEST | planned | src/zephyr/backtest/services/result_deployer.py |

## 8. 处置建议

- 孤儿环节：用 `apply_battle_map.py --add-anchor` 为环节挂载承载模块/候选/蓝图（草图 §12 迁移第二批「锚点」）
- 幽灵锚点：修正 target_id 指向真实存在的模块/候选，或删除该锚点
- 缺失叙事：在 `module_translation_registry.yaml` §battle_map_steps 段补齐环节叙事（name_zh/plain_zh/mechanism_zh/indicators_zh）
- 悬空边：修正 edge 的 from/to step_id，或删除孤立边
- 域漂移：① 确认锚点是否挂错环节（如 D_SELL_DECISION 不应在 buy_flow）；② 若挂错，迁移到正确环节或删除；③ 若认为该 domain 应被允许，修改 `battle_map_domain_policy.yaml` 的 `flow_stage_allowed_domains` 段（真源在 YAML，禁止改代码）；④ target_domains 含多个 domain 时，任一在允许列表即通过（跨域蓝图如 MOD-INF-002 含 80+ 子模块跨 8 domain）
- 孤儿模块：① 确认该模块是否该挂到某作战环节——若是，用 `apply_battle_map.py --add-anchor --target-graph depgraph --target-id <blueprint_id>` 挂到对应 step；② 若确无作战使命（造出来用不上），走弃用流程——`apply_depgraph.py` 软删除（build_status→deprecated）+ 在 `candidate_module_registry.yaml` 记 rejected 条目（含否决理由，防未来误重设）；③ build_status=planned 的孤儿 = 设计了却没想好挂哪，优先评审其作战归属再决定建/弃
