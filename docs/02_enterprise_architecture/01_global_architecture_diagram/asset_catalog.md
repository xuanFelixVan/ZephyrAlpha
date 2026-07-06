---
doc_type: architecture_view
title: 资产清单全景图
version: "1.0"
status: active
date: auto-generated
owner: auto-generator
ttl: permanent
---

# 资产清单全景图 / Asset Catalog

> **文档作用 / Purpose**: 一张图看完所有运行中服务/数据流/契约/数据源/配置的总览,共111项资产。AI接入新功能前必查此图确认可复用资产。

> 本文档由 generate_asset_catalog.py 从 depgraph (PostgreSQL) 自动生成
> 真源: data_sources_registry.yaml + service_registry.yaml + config/*.yaml + cross_layer_contracts.yaml

## 1. 统计概览

| 资产类型 | 数量 | 真源 |
|----------|------|------|
| 外部数据源 | 10 | data_sources_registry.yaml |
| 服务资产 | 10 | service_registry.yaml |
| 基础设施组件 | 14 | infrastructure_components.yaml |
| 契约资产 | 39 | cross_layer_contracts.yaml |
| 配置项 | 38 | config/*.yaml |
| 数据流作业 | 13 | dataflow_graph_registry.yaml |
| 数据集 | 14 | dataflow_graph_registry.yaml |
| **合计** | **111** | |

## 2. 外部数据源资产

| ID | 名称 | 类型 | 类别 | 供应商 | 状态 | API数 | 覆盖范围 |
|----|------|------|------|--------|------|-------|----------|
| DS-BAIDUYUN | 百度云 | commercial | market_data | 百度 | active | 0 | 通达信板块分笔历史Tick数据(一次性包,无API可持续更新) |
| DS-IFIND | 同花顺iFind | commercial | market_data | 同花顺 | active | 70 | A股K线/Tick/板块/财务/宏观/研报 |
| DS-MINIQMT | miniQMT | commercial | market_data | 迅投 | active | 87 | A股实时行情/历史K线/交易接口 |
| DS-NEWSAPI | NewsAPI | commercial | news | NewsAPI.org | planned | 0 | 全球财经新闻 |
| DS-AKSHARE | AKShare | open_source | market_data | 开源社区 | active | 0 | A股/港股/美股/期货/宏观/新闻(部分接口被反爬) |
| DS-BAOSTOCK | Baostock | open_source | market_data | 开源社区 | active | 0 | A股K线/财务/宏观(数据有延迟) |
| DS-STOOQ | Stooq | open_source | market_data | Stooq.com | deprecated | 0 | 全球历史K线(已废弃) |
| DS-TDX | 通达信 | open_source | market_data | 通达信 | active | 0 | A股K线/指数K线/实时报价/分时/个股分笔(仅最近交易日)/本地文件/财务数据/港股/期货 |
| DS-TICKFLOW | TickFlow | open_source | market_data | 开源社区 | active | 0 | A股Tick数据 |
| DS-YFINANCE | yfinance | open_source | market_data | 开源社区 | deprecated | 0 | 美股/港股(已废弃,分类体系不兼容) |

## 3. 服务资产

| ID | 名称 | 类型 | 域 | 端口 | 协议 | 状态 | 描述 |
|----|------|------|-----|------|------|------|------|
| SVC-CLICKHOUSE | ClickHouse c1_market | database | D_MKT_DATA | 9000 | clickhouse | planned | 业务行情仓库(C1),K线/指数/板块/财务数据 |
| SVC-DEPGRAPH | depgraph PostgreSQL | database | D_DATA_ENG | 5432 | postgresql | active | 全景图数据库(架构SSoT),40张表存储依赖/路径/数据流/决策流 |
| SVC-GOVERNANCE-DB | governance.db SQLite | database | D_GOVERNANCE | — | sqlite | active | 治理运行时(任务/审计/事件/门禁执行),34张表 |
| SVC-VECTORDB | Vector DB | database | D_KNOWLEDGE | — | file | provisioned | 向量数据库,知识库检索用 |
| SVC-BAIDUYUN | 百度云BOS | external_service | D_MKT_DATA | — | https | active | 百度云对象存储(通达信历史Tick数据包) |
| SVC-DEEPSEEK | DeepSeek API | external_service | D_INTELLIGENCE | — | https | active | 云端LLM推理服务(deepseek_chat) |
| SVC-IFIND | iFind Client | external_service | D_MKT_DATA | — | dll | active | 同花顺iFind客户端(同进程内调用THS_iFinDLogin) |
| SVC-MINIQMT | miniQMT Client | external_service | D_TRADING | — | dll | planned | 迅投miniQMT客户端(行情+交易) |
| SVC-OLLAMA | Ollama LLM | external_service | D_INTELLIGENCE | 11434 | http | active | 本地LLM推理服务(ollama_chat) |
| SVC-TELEMETRY | system_telemetry | service | D_INFRA_RUNTIME | — | inproc | active | 系统遥测门面(9子系统:metrics/logs/traces/ai_behavior/health/alerts/profiles/schema/archive) |

## 4. 基础设施组件

| ID | 类型 | 地址 | 状态 | SLA |
|----|------|------|------|-----|
| INFRA-CACHE-001 | cache | — | planned | 99.9% uptime, < 5ms GET p99 |
| INFRA-CACHE-002 | cache | in-process | planned | 缓存命中率 ≥ 90%，内存占用 < 512MB |
| INFRA-CFG-001 | config_center | — | planned | 99.9% uptime, < 100ms config read |
| INFRA-CI-001 | ci_pipeline | .github/workflows/governance.yml | connected | push/PR paths + workflow_dispatch；timeout 15m |
| INFRA-DB-001 | relational_db | .runtime/db/data/databases/governance.db | connected | persisted, ACID, < 30ms read p50 |
| INFRA-DB-002 | vector_db | data/vector_db/ | provisioned | < 200ms retrieval p95, index rebuild < 10 min |
| INFRA-DB-003 | relational_db | localhost:5432/depgraph | connected | ACID, MVCC, < 30ms read p50 |
| INFRA-DB-004 | cache | :memory: | connected | 内存模式，无持久化SLA；查询延迟 < 200ms p95 |
| INFRA-DB-006 | relational_db | localhost:9000/c1_market | connected | 持久化, 列式压缩, < 50ms write p95, < 200ms OLAP query p95 |
| INFRA-EVT-001 | event_bus | — | planned | 99.9% uptime, < 100ms publish-delivery |
| INFRA-MQ-001 | message_queue | — | planned | 99.5% uptime, < 5s task pickup delay |
| INFRA-PROC-001 | cache | in-process | planned | 进程复用率 ≥ 80%，启动延迟 < 500ms |
| INFRA-STORE-001 | object_storage | — | planned | 99.9% durability, < 100MB/s write |
| INFRA-SVC-001 | service_registry | — | planned | 99.9% uptime, < 50ms service lookup |

## 5. 契约资产

> 详细流向矩阵和字段定义见 [contract_catalog.md](contract_catalog.md)

| ID | 名称 | 类型 | 提供方 | 状态 |
|----|------|------|--------|------|
| CTR-001 | NormalizedMarketData / 标准化行情数据 | P0 | D_MKT_DATA | planned |
| CTR-002 | FactorSignal / 因子信号 | P0 | D_FACTOR | planned |
| CTR-003 | RiskLimits / 风险限额 | P0 | D_RISK | planned |
| CTR-004 | Order / 委托指令 | P0 | D_PF_CORE | design |
| CTR-005 | Fill / 成交回报 | P0 | D_EX_CORE | planned |
| CTR-006 | PositionSnapshot / 持仓快照 | P0 | D_EX_CORE | planned |
| CTR-BP-001 | BackpressurePause / 背压暂停信号 | P0 | D_FACTOR | planned |
| CTR-BP-002 | BackpressureThrottle / 背压降速信号 | P0 | D_FACTOR | planned |
| CTR-BP-003 | BackpressureResume / 背压恢复信号 | P0 | D_FACTOR | planned |
| CTR-ERR-001 | DataQualityError / 行情质量门禁不通过错误 | P0 | D_MKT_DATA | planned |
| CTR-ERR-002 | FactorComputationError / 因子计算失败错误 | P0 | D_FACTOR | planned |
| CTR-ERR-003 | SignalDegradationWarning / 信号质量下降警告 | P0 | D_SIGQC | planned |
| CTR-ERR-004 | RiskLimitViolationError / 风险限额突破错误 | P0 | D_RISK | planned |
| CTR-ERR-005 | ExecutionRejectionError / 执行拒绝错误 | P0 | D_EX_CORE | planned |
| CTR-ERR-006 | ContractViolationError / 契约违反错误 | P0 | D_SHARED | planned |
| CTR-TRACE-001 | TraceContext / 全链路追踪上下文 | P0 | D_MKT_DATA | planned |
| CT-TEL-001 | TelemetryMetrics / 遥测指标采集 | P1 | D_OPS | design |
| CT-TEL-002 | TelemetryLogs / 遥测日志持久化 | P1 | D_OPS | design |
| CT-TEL-003 | TelemetryTraces / 遥测链路追踪 | P1 | D_OPS | design |
| CT-TEL-004 | TelemetryHealth / 遥测健康检查 | P1 | D_OPS | design |
| CTR-P1-001 | FactorMonitorReport / 因子有效性监控报告 | P1 | D_FACTOR | planned |
| CTR-P1-002 | MacroFactorSignal / 宏观因子信号 | P1 | D_FACTOR | planned |
| CTR-P1-003 | CapitalAllocationResult / 资本配置结果 | P1 | — | planned |
| CTR-P1-004 | ModelServingRequest / 模型推理请求 | P1 | D_ML_TRAIN | planned |
| CTR-P1-005 | ModelServingResponse / 模型推理响应 | P1 | D_ML_TRAIN | planned |
| CTR-P1-006 | StrategyLifecycleEvent / 策略生命周期事件 | P1 | D_PF_CORE | planned |
| CTR-P1-007 | ExecutionReport / 执行分析报告 | P1 | D_EX_CORE | planned |
| CTR-P1-008 | RiskDashboardSnapshot / 风险仪表板快照 | P1 | D_RISK | planned |
| CTR-P1-009 | PerformanceAttributionReport / 绩效归因报告 | P1 | D_TRADING | planned |
| CTR-P1-010 | SystemConfiguration / 系统配置 | P1 | D_INFRA_OPS | planned |
| CTR-P1-011 | RiskMetricsReport / 风险指标报告 | P1 | D_RISK | planned |
| CTR-P1-012 | ComplianceRule / 合规规则 | P1 | D_GOV_ENFORCEMENT | planned |
| CTR-P1-013 | TelemetryEmitter / 遥测发射器 | P1 | D_OPS | planned |
| CTR-P1-014 | ExperimentResult / 实验结论 | P1 | D_INTELLIGENCE | planned |
| CTR-P1-015 | SynthesizedSignal / 合成交易信号 | P1 | — | planned |
| CTR-P1-016 | BacktestResult / 回测结果 | P1 | D_BACKTEST | planned |
| CTR-P1-017 | BacktestRunArtifact / 回测运行产物 | P1 | D_BACKTEST | planned |
| OCP-002 | StrategyBase + StrategyRegistry / 策略扩展点 | unknown | — | design |
| OCP-003 | BrokerInterface / 券商扩展点 | unknown | — | design |

## 6. 配置项清单(元数据)

> 仅记录元数据(文件名/大小/修改时间),不复制内容。内容真源为 config/*.yaml 文件本身。

| 文件路径 | 大小(KB) | 最后修改 |
|----------|---------|----------|
| `config/ai_capability_matrix.yaml` | 4.8 | 2026-07-02 |
| `config/ai_context_policy.yaml` | 1.0 | 2026-07-04 |
| `config/alert_rules.yaml` | 2.0 | 2026-07-02 |
| `config/asset_inventory.yaml` | 2.3 | 2026-07-04 |
| `config/auto_fix_cron.yaml` | 1.0 | 2026-07-05 |
| `config/blueprint_routing.yaml` | 23.1 | 2026-07-03 |
| `config/budget_policy.yaml` | 3.1 | 2026-06-12 |
| `config/capabilities.yaml` | 0.9 | 2026-06-12 |
| `config/capacity_params.yaml` | 7.2 | 2026-06-24 |
| `config/capacity_slo.yaml` | 4.6 | 2026-07-04 |
| `config/compression_policy.yaml` | 2.5 | 2026-07-04 |
| `config/context_rules.yaml` | 5.6 | 2026-06-29 |
| `config/data/survivorship_policy.yaml` | 0.7 | 2026-07-04 |
| `config/degradation_chain.yaml` | 1.3 | 2026-07-02 |
| `config/embedding_model_registry.yaml` | 3.5 | 2026-06-23 |
| `config/error_budget_config.yaml` | 1.6 | 2026-07-02 |
| `config/external_watchdog.yaml` | 0.9 | 2026-07-02 |
| `config/flags.yaml` | 2.0 | 2026-06-12 |
| `config/kb_parameters.yaml` | 3.2 | 2026-06-13 |
| `config/metrics_schema.yaml` | 2.6 | 2026-07-02 |
| `config/model_pricing.yaml` | 1.3 | 2026-06-12 |
| `config/nav_table_mapping.yaml` | 20.1 | 2026-07-01 |
| `config/owner_offline_protocol.yaml` | 1.0 | 2026-07-02 |
| `config/rbac_roles.yaml` | 1.1 | 2026-07-04 |
| `config/resource_optimization.yaml` | 1.6 | 2026-06-24 |
| `config/risk_params.yaml` | 1.3 | 2026-06-12 |
| `config/risk_register.yaml` | 9.1 | 2026-07-02 |
| `config/runtime/burn_rate_acceleration.yaml` | 1.2 | 2026-07-04 |
| `config/runtime/error_budget_state.yaml` | 1.9 | 2026-07-04 |
| `config/runtime/kill_switch_state.yaml` | 1.3 | 2026-07-04 |
| `config/runtime/script_retirement_state.yaml` | 1.4 | 2026-07-04 |
| `config/runtime/shadow_mode_state.yaml` | 1.4 | 2026-06-12 |
| `config/sandbox_policy.yaml` | 1.5 | 2026-07-05 |
| `config/session_state_machine.yaml` | 5.1 | 2026-07-01 |
| `config/sli_registry.yaml` | 2.8 | 2026-07-02 |
| `config/survivorship_policy.yaml` | 0.7 | 2026-07-04 |
| `config/tech_stack_manifest.yaml` | 4.6 | 2026-07-06 |
| `config/trigger_router.yaml` | 4.9 | 2026-07-04 |
