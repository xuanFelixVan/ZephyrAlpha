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

> **文档作用 / Purpose**: 一张图看完所有运行中服务/数据流/契约/数据源/数据源 API/配置的总览,共258项资产。AI接入新功能前必查此图确认可复用资产。

> 本文档由 generate_asset_catalog.py 从 depgraph (PostgreSQL) 自动生成
> 真源: data_sources_registry.yaml + data_source_apis_registry.yaml + service_registry.yaml + config/*.yaml + cross_layer_contracts.yaml

## 1. 统计概览

| 资产类型 | 数量 | 真源 |
|----------|------|------|
| 外部数据源 | 12 | data_sources_registry.yaml |
| 数据源 API | 124 | data_source_apis_registry.yaml |
| 服务资产 | 10 | service_registry.yaml |
| 基础设施组件 | 14 | infrastructure_components.yaml |
| 契约资产 | 65 | cross_layer_contracts.yaml |
| 配置项 | 33 | config/*.yaml |
| 数据流作业 | 63 | dataflow_graph_registry.yaml |
| 数据集 | 14 | dataflow_graph_registry.yaml |
| **合计** | **258** | |

## 2. 外部数据源资产

| ID | 名称 | 类型 | 类别 | 供应商 | 状态 | API数 | 覆盖范围 |
|----|------|------|------|--------|------|-------|----------|
| DS-BAIDUYUN | 百度云 | commercial | market_data | 百度 | active | 0 | 通达信板块分笔历史Tick数据(一次性包,无API可持续更新) |
| DS-IFIND | 同花顺iFind | commercial | market_data | 同花顺 | active | 70 | A股K线/Tick/板块/财务/宏观/研报 |
| DS-MINIQMT | miniQMT | commercial | market_data | 迅投 | active | 87 | A股实时行情/历史K线/交易接口 |
| DS-TUSHARE | Tushare | commercial | market_data | Tushare | active | 0 | A股K线/财务/板块/基金/期货 |
| DS-NEWSAPI | NewsAPI | commercial | news | NewsAPI.org | planned | 0 | 全球财经新闻 |
| DS-AKSHARE | AKShare | open_source | market_data | 开源社区 | active | 0 | A股/港股/美股/期货/宏观/新闻(部分接口被反爬) |
| DS-BAOSTOCK | Baostock | open_source | market_data | 开源社区 | active | 0 | A股K线/财务/宏观(数据有延迟) |
| DS-STOOQ | Stooq | open_source | market_data | Stooq.com | deprecated | 0 | 全球历史K线(已废弃) |
| DS-TDX | 通达信 | open_source | market_data | 通达信 | active | 0 | A股K线/指数K线/实时报价/分时/个股分笔(仅最近交易日)/本地文件/财务数据/港股/期货 |
| DS-TICKFLOW | TickFlow | open_source | market_data | 开源社区 | active | 0 | A股Tick数据 |
| DS-YFINANCE | yfinance | open_source | market_data | 开源社区 | deprecated | 0 | 美股/港股(已废弃,分类体系不兼容) |
| DS-RSS | RSS | open_source | news | 开源 | active | 0 | 财经新闻RSS源 |

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
| CT-TEL-001 | TelemetryMetrics / 遥测指标采集 | cross_layer | D_OPS | unresolved |
| CT-TEL-002 | TelemetryLogs / 遥测日志持久化 | cross_layer | D_OPS | unresolved |
| CT-TEL-003 | TelemetryTraces / 遥测链路追踪 | cross_layer | D_OPS | unresolved |
| CT-TEL-004 | TelemetryHealth / 遥测健康检查 | cross_layer | D_OPS | unresolved |
| CTR-001 | NormalizedMarketData / 标准化行情数据 | cross_layer | D_MKT_DATA | planned |
| CTR-002 | FactorSignal / 因子信号 | cross_layer | D_FACTOR | unresolved |
| CTR-003 | RiskLimits / 风险限额 | cross_layer | D_RISK | unresolved |
| CTR-004 | Order / 委托指令 | cross_layer | D_PF_CORE | design |
| CTR-005 | Fill / 成交回报 | cross_layer | D_EX_CORE | planned |
| CTR-006 | PositionSnapshot / 持仓快照 | cross_layer | D_EX_CORE | planned |
| CTR-BP-001 | BackpressurePause / 背压暂停信号 | cross_layer | D_FACTOR | unresolved |
| CTR-BP-002 | BackpressureThrottle / 背压降速信号 | cross_layer | D_FACTOR | unresolved |
| CTR-BP-003 | BackpressureResume / 背压恢复信号 | cross_layer | D_FACTOR | unresolved |
| CTR-ERR-001 | DataQualityError / 行情质量门禁不通过错误 | cross_layer | D_MKT_DATA | unresolved |
| CTR-ERR-002 | FactorComputationError / 因子计算失败错误 | cross_layer | D_FACTOR | unresolved |
| CTR-ERR-003 | SignalDegradationWarning / 信号质量下降警告 | cross_layer | D_SIGQC | unresolved |
| CTR-ERR-004 | RiskLimitViolationError / 风险限额突破错误 | cross_layer | D_RISK | unresolved |
| CTR-ERR-005 | ExecutionRejectionError / 执行拒绝错误 | cross_layer | D_EX_CORE | unresolved |
| CTR-ERR-006 | ContractViolationError / 契约违反错误 | cross_layer | D_SHARED | unresolved |
| CTR-P1-001 | FactorMonitorReport / 因子有效性监控报告 | cross_layer | D_FACTOR | unresolved |
| CTR-P1-002 | MacroFactorSignal / 宏观因子信号 | cross_layer | D_FACTOR | unresolved |
| CTR-P1-003 | CapitalAllocationResult / 资本配置结果 | cross_layer | D_ASHARE_SIGNAL | unresolved |
| CTR-P1-004 | ModelServingRequest / 模型推理请求 | cross_layer | D_ML_TRAIN | planned |
| CTR-P1-005 | ModelServingResponse / 模型推理响应 | cross_layer | D_ML_TRAIN | planned |
| CTR-P1-006 | StrategyLifecycleEvent / 策略生命周期事件 | cross_layer | D_PF_CORE | planned |
| CTR-P1-007 | ExecutionReport / 执行分析报告 | cross_layer | D_EX_CORE | unresolved |
| CTR-P1-008 | RiskDashboardSnapshot / 风险仪表板快照 | cross_layer | D_RISK | unresolved |
| CTR-P1-009 | PerformanceAttributionReport / 绩效归因报告 | cross_layer | D_TRADING | planned |
| CTR-P1-010 | SystemConfiguration / 系统配置 | cross_layer | D_INFRA_OPS | unresolved |
| CTR-P1-011 | RiskMetricsReport / 风险指标报告 | cross_layer | D_RISK | unresolved |
| CTR-P1-012 | ComplianceRule / 合规规则 | cross_layer | D_GOV_ENFORCEMENT | planned |
| CTR-P1-013 | TelemetryEmitter / 遥测发射器 | cross_layer | D_OPS | unresolved |
| CTR-P1-014 | ExperimentResult / 实验结论 | cross_layer | D_INTELLIGENCE | planned |
| CTR-P1-015 | SynthesizedSignal / 合成交易信号 | cross_layer | D_ASHARE_SIGNAL | unresolved |
| CTR-P1-016 | BacktestResult / 回测结果 | cross_layer | D_BACKTEST | unresolved |
| CTR-P1-017 | BacktestRunArtifact / 回测运行产物 | cross_layer | D_BACKTEST | unresolved |
| CTR-TRACE-001 | TraceContext / 全链路追踪上下文 | cross_layer | D_MKT_DATA | planned |
| OCP-002 | StrategyBase + StrategyRegistry / 策略扩展点 | cross_layer | D_SHARED | unresolved |
| OCP-003 | BrokerInterface / 券商扩展点 | cross_layer | D_SHARED | unresolved |
| CT-001 | config/context-rules.yaml | declarative | D_DATA_SEC | resolved |
| CT-002 | config/embedding_model_registry.yaml | declarative | D_DATA_SEC | resolved |
| CT-003 | config/session_state_machine.yaml | declarative | D_DATA_SEC | resolved |
| CT-004 | config/capabilities.yaml | declarative | D_DATA_SEC | resolved_as_not_supported |
| CT-005 | src/zephyr/orchestrator/execution/trigger_router.py + config/trigger_router.yaml | declarative | D_INTELLIGENCE | resolved |
| CT-006 | config/compression_policy.yaml | declarative | D_DATA_SEC | resolved |
| CT-007 | MOD-INF-005 §13.1 (script_system/blueprint.md V3.0.0) | declarative | D_GOV_SCRIPTS | resolved |
| CT-008 | MOD-INF-005 §13.2 (script_system/blueprint.md V3.0.0) | declarative | D_GOV_SCRIPTS | resolved |
| CT-009 | MOD-INF-005 §3.6 + §5.2 (script_system/blueprint.md V3.0.0) | declarative | D_GOV_SCRIPTS | resolved |
| CT-010 | MOD-INF-005 §5.2 (script_system/blueprint.md V3.0.0) | declarative | D_GOV_SCRIPTS | resolved |
| CT-011 | MOD-INF-005 §6.5 (script_system/blueprint.md V3.0.0) | declarative | D_GOV_SCRIPTS | resolved |
| AS-CT-DATA-001 | 市场数据→因子引擎（OHLCV/orderbook/tick） | domain_contract | D_FACTOR | unresolved |
| AS-CT-FACTOR-002 | Code-Dedup-Engine→去重后的因子值（唯一source_key） | domain_contract | D_FACTOR | unresolved |
| AS-CT-SIGNAL-001 | 信号数据帧→风控引擎 | domain_contract | D_ASHARE_SIGNAL | unresolved |
| AS-CT-VMS-001 | 因子嵌入向量存储（8 collections: signal-embeddings） | domain_contract | D_ASHARE_SIGNAL | unresolved |
| ME-CT-AB-001 | AB实验全流程：config→traffic_split→gate[eval]→analyst→deploy/rollback | domain_contract | D_ML_TRAIN | unresolved |
| ME-CT-BACKTEST-001 | 回测实验：ckpt→historical→PnL→Attribution→Report | domain_contract | D_ML_TRAIN | unresolved |
| ME-CT-CHECKPOINT-001 | 检查点导入（MODEL_CHECKPOINTS→AB/Backtest Experiment） | domain_contract | D_ML_TRAIN | unresolved |
| ME-CT-FEATURE-001 | 特征向量读取（ChromaDB collections: factor-signals, model-features） | domain_contract | D_ML_TRAIN | unresolved |
| ME-CT-SHADOW-001 | Shadow Mode：旁路预测→threshold→divergence alert→正式切流 | domain_contract | D_ML_TRAIN | unresolved |
| ME-CT-TRAIN-001 | 训练Pipeline Gate：数据→训练→验证→Sanity→发布 | domain_contract | D_ML_TRAIN | unresolved |
| CTR-009 | ExperimentConfig → D_ML_TRAIN ML Platform | layer_contract | D_SIMULATION | unresolved |
| CTR-010 | ExperimentMetric → D_RESEARCH Research | layer_contract | D_SIMULATION | unresolved |
| CTR-011 | ModelCheckpoint ← D_ML_TRAIN ML Platform | layer_contract | D_SIMULATION | unresolved |
| CTR-012 | ExperimentArtifact → INF-012 Database | layer_contract | D_SIMULATION | unresolved |
| EXT-DASHBOARD-FLE-001 | 消费 FLE fitness Facade | layer_contract | D_FRONTEND | unresolved |

## 6. 配置项清单(元数据)

> 仅记录元数据(文件名/大小/修改时间),不复制内容。内容真源为 config/*.yaml 文件本身。

| 文件路径 | 大小(KB) | 最后修改 |
|----------|---------|----------|
| `config/ai_capability_matrix.yaml` | 4.8 | 2026-07-02 |
| `config/ai_context_policy.yaml` | 1.0 | 2026-07-04 |
| `config/alert_rules.yaml` | 2.0 | 2026-07-02 |
| `config/asset_inventory.yaml` | 2.3 | 2026-07-04 |
| `config/auto_fix_cron.yaml` | 1.0 | 2026-07-05 |
| `config/blueprint_routing.yaml` | 23.1 | 2026-07-09 |
| `config/budget_policy.yaml` | 3.1 | 2026-06-12 |
| `config/capabilities.yaml` | 0.9 | 2026-06-12 |
| `config/capacity_params.yaml` | 7.2 | 2026-06-24 |
| `config/capacity_slo.yaml` | 4.6 | 2026-07-10 |
| `config/compression_policy.yaml` | 2.5 | 2026-07-04 |
| `config/context_rules.yaml` | 5.6 | 2026-06-29 |
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
| `config/sandbox_policy.yaml` | 1.5 | 2026-07-05 |
| `config/session_state_machine.yaml` | 5.1 | 2026-07-01 |
| `config/sla_targets.yaml` | 0.9 | 2026-07-08 |
| `config/sli_registry.yaml` | 2.8 | 2026-07-02 |
| `config/survivorship_policy.yaml` | 0.7 | 2026-07-04 |
| `config/tech_stack_manifest.yaml` | 4.6 | 2026-07-06 |
| `config/trigger_router.yaml` | 4.9 | 2026-07-04 |

## 7. 数据源 API 清单

> 共 124 个 API,按数据源分组。真源: `architecture_model/data/data_source_apis_registry.yaml`,参数坑/调用示例见 [data_source_operation_manual.md](../../03_modules/_domain_data/data_source_operation_manual.md)。

**测试状态图例**: ✅ verified | 🟡 partial | ⚠️ untested | ❌ deprecated

### 7.1 AKShare（`DS-AKSHARE`，34 API）

测试状态: ✅ 28 verified / 🟡 0 partial / ⚠️ 0 untested / ❌ 6 deprecated

| API ID | 函数名 | 类别 | 功能 | 频率 | 范围 | 状态 | 章节引用 |
|--------|--------|------|------|------|------|:----:|----------|
| `DS-AKSHARE-API-001` | `macro_china_gdp` | 中国宏观 | GDP季度数据 | — | 中国宏观 | ✅ | §7.3.1 |
| `DS-AKSHARE-API-002` | `macro_china_cpi` | 中国宏观 | CPI居民消费价格指数 | — | 中国宏观 | ✅ | §7.3.1 |
| `DS-AKSHARE-API-003` | `macro_china_ppi_yearly` | 中国宏观 | PPI工业品出厂价格指数 | — | 中国宏观 | ✅ | §7.3.1 |
| `DS-AKSHARE-API-004` | `macro_china_pmi` | 中国宏观 | PMI制造业采购经理指数 | — | 中国宏观 | ✅ | §7.3.1 |
| `DS-AKSHARE-API-005` | `macro_china_money_supply` | 中国宏观 | M0/M1/M2货币供应量 | — | 中国宏观 | ✅ | §7.3.1 |
| `DS-AKSHARE-API-006` | `macro_china_lpr` | 中国宏观 | LPR贷款市场报价利率 | — | 中国宏观 | ✅ | §7.3.1 |
| `DS-AKSHARE-API-007` | `macro_china_shrzgm` | 中国宏观 | 社融增量 | — | 中国宏观 | ✅ | §7.3.1 |
| `DS-AKSHARE-API-008` | `macro_usa_cpi_monthly` | 美国宏观 | 美国CPI月度 | — | 美国宏观 | ✅ | §7.3.1 |
| `DS-AKSHARE-API-009` | `macro_usa_unemployment_rate` | 美国宏观 | 美国失业率 | — | 美国宏观 | ✅ | §7.3.1 |
| `DS-AKSHARE-API-010` | `macro_usa_fed_interest_rate` | 美国宏观 | 美联储联邦基金利率 | — | 美国宏观 | ✅ | §7.3.1 |
| `DS-AKSHARE-API-011` | `stock_news_em` | 新闻 | 个股新闻(东方财富) | — | A股新闻 | ✅ | §7.3.2 |
| `DS-AKSHARE-API-012` | `stock_info_global_cls` | 新闻 | 财联社全球快讯(实时滚动) | — | 财经快讯 | ✅ | §7.3.2 |
| `DS-AKSHARE-API-013` | `stock_info_global_em` | 新闻 | 东方财富全球资讯 | — | 财经快讯 | ✅ | §7.3.2 |
| `DS-AKSHARE-API-014` | `stock_research_report_em` | 研报 | 东方财富个股研报 | — | A股研报 | ✅ | §7.3.2 |
| `DS-AKSHARE-API-015` | `stock_profit_forecast_ths` | 研报 | 同花顺一致预期EPS(替代iFind分析师预期) | — | A股研报 | ✅ | §7.3.2 |
| `DS-AKSHARE-API-016` | `news_eco_calendar` | 事件日历 | 财经事件日历(经济数据发布/央行决议) | — | 财经事件 | ✅ | §7.3.2 |
| `DS-AKSHARE-API-017` | `news_cctv` | 央视新闻 | 央视新闻联播文字稿(政策风向标) | — | 政策新闻 | ✅ | §7.1.2D |
| `DS-AKSHARE-API-018` | `stock_gdfx_top_10_em` | 股权穿透 | 十大股东 | — | A股股权 | ✅ | §7.1.3A |
| `DS-AKSHARE-API-019` | `stock_gdfx_free_top_10_em` | 股权穿透 | 十大流通股东 | — | A股股权 | ✅ | §7.1.3A |
| `DS-AKSHARE-API-020` | `stock_zh_a_gdhs_detail_em` | 股权穿透 | 股东户数明细(历史) | — | A股股权 | ✅ | §7.1.3A |
| `DS-AKSHARE-API-021` | `stock_zh_a_gdhs` | 股权穿透 | 全市场股东户数 | — | A股股权 | ✅ | §7.1.3A |
| `DS-AKSHARE-API-022` | `stock_gpzy_pledge_ratio_em` | 股权穿透 | 股权质押(全市场) | — | A股股权 | ✅ | §7.1.3A |
| `DS-AKSHARE-API-023` | `stock_ggcg_em` | 股权穿透 | 高管增减持(全市场) | — | A股股权 | ✅ | §7.1.3A |
| `DS-AKSHARE-API-024` | `stock_zygc_em` | 股权穿透 | 主营业务构成 | — | A股股权 | ✅ | §7.1.3A |
| `DS-AKSHARE-API-025` | `stock_individual_info_em` | 股权穿透 | 股票基础信息(董事长/总经理/注册资本) | — | A股 | ❌ | §7.1.3A |
| `DS-AKSHARE-API-026` | `stock_hold_control_cninfo` | 股权穿透 | 控股关系 | — | A股股权 | ❌ | §7.1.3A |
| `DS-AKSHARE-API-027` | `stock_history_dividend_detail` | 分红 | 分红明细(最可靠) | — | A股分红 | ✅ | §7.3.5 |
| `DS-AKSHARE-API-028` | `sw_index_first_info` | 产业链 | 申万一级行业(31个) | — | A股行业 | ✅ | §7.1.3C |
| `DS-AKSHARE-API-029` | `sw_index_second_info` | 产业链 | 申万二级行业(131个) | — | A股行业 | ✅ | §7.1.3C |
| `DS-AKSHARE-API-030` | `sw_index_third_info` | 产业链 | 申万三级行业(336个) | — | A股行业 | ✅ | §7.1.3C |
| `DS-AKSHARE-API-031` | `sw_index_third_cons` | 产业链 | 三级行业成分股 | — | A股行业 | ❌ | §7.1.3C |
| `DS-AKSHARE-API-032` | `stock_board_industry_name_em` | 产业链 | 东财行业板块 | — | A股行业 | ❌ | §7.1.3C |
| `DS-AKSHARE-API-033` | `stock_board_industry_cons_em` | 产业链 | 东财行业板块成分股 | — | A股行业 | ❌ | §7.1.3C |
| `DS-AKSHARE-API-034` | `stock_board_concept_name_em` | 产业链 | 东财概念板块 | — | A股概念 | ❌ | §7.1.3C |

### 7.2 百度云（`DS-BAIDUYUN`，1 API）

测试状态: ✅ 0 verified / 🟡 0 partial / ⚠️ 1 untested / ❌ 0 deprecated

| API ID | 函数名 | 类别 | 功能 | 频率 | 范围 | 状态 | 章节引用 |
|--------|--------|------|------|------|------|:----:|----------|
| `DS-BAIDUYUN-API-001` | `baidu_news_nlp` | 新闻NLP | 百度新闻情感分析 | — | 新闻NLP | ⚠️ | §7.1.1 |

### 7.3 Baostock（`DS-BAOSTOCK`，16 API）

测试状态: ✅ 8 verified / 🟡 0 partial / ⚠️ 7 untested / ❌ 1 deprecated

| API ID | 函数名 | 类别 | 功能 | 频率 | 范围 | 状态 | 章节引用 |
|--------|--------|------|------|------|------|:----:|----------|
| `DS-BAOSTOCK-API-001` | `query_history_k_data_plus` | K线 | 日/周/月/分钟K线 | d/w/m/5/15/30/60 | A股(1990至今,分钟近5年) | ✅ | §7.2.1 |
| `DS-BAOSTOCK-API-002` | `query_profit_data` | 季频财务 | 季频盈利能力(roeAvg/npMargin/gpMargin) | — | A股(2007至今) | ✅ | §7.2.1 |
| `DS-BAOSTOCK-API-003` | `query_balance_data` | 季频财务 | 季频资产负债(currentRatio/quickRatio) | — | A股(2007至今) | ✅ | §7.2.1 |
| `DS-BAOSTOCK-API-004` | `query_cash_flow_data` | 季频财务 | 季频现金流 | — | A股(2007至今) | ✅ | §7.2.1 |
| `DS-BAOSTOCK-API-005` | `query_growth_data` | 季频财务 | 季频成长能力(YOYEquity/YOYAsset/YOYNI) | — | A股(2007至今) | ✅ | §7.2.1 |
| `DS-BAOSTOCK-API-006` | `query_hs300_stocks` | 成分股 | 沪深300成分股(每周一更新) | — | A股指数 | ✅ | §7.2.1 |
| `DS-BAOSTOCK-API-007` | `query_trade_dates` | 交易日历 | 交易日历 | — | A股交易日 | ✅ | §7.2.1 |
| `DS-BAOSTOCK-API-008` | `query_operation_data` | 营运能力 | 营运能力 | — | A股 | ⚠️ | §7.2.1 |
| `DS-BAOSTOCK-API-009` | `query_dupont_data` | 杜邦分析 | 杜邦分析 | — | A股 | ⚠️ | §7.2.1 |
| `DS-BAOSTOCK-API-010` | `query_sz50_stocks` | 成分股 | 上证50成分股 | — | A股指数 | ⚠️ | §7.2.1 |
| `DS-BAOSTOCK-API-011` | `query_zz500_stocks` | 成分股 | 中证500成分股 | — | A股指数 | ⚠️ | §7.2.1 |
| `DS-BAOSTOCK-API-012` | `query_stock_industry` | 行业分类 | 行业分类 | — | A股 | ⚠️ | §7.2.1 |
| `DS-BAOSTOCK-API-013` | `query_all_stock` | 证券列表 | 全部证券列表 | — | A股 | ⚠️ | §7.2.1 |
| `DS-BAOSTOCK-API-014` | `query_stock_basic` | 股票基本信息 | 股票基本信息 | — | A股 | ⚠️ | §7.2.1 |
| `DS-BAOSTOCK-API-015` | `query_dividend_data` | 分红 | 分红数据 | — | A股 | ❌ | §7.2.5 |
| `DS-BAOSTOCK-API-016` | `bs.login` | 登录 | 匿名登录(无需注册) | — | — | ✅ | §7.2.2 |

### 7.4 同花顺iFind（`DS-IFIND`，15 API）

测试状态: ✅ 7 verified / 🟡 1 partial / ⚠️ 4 untested / ❌ 3 deprecated

| API ID | 函数名 | 类别 | 功能 | 频率 | 范围 | 状态 | 章节引用 |
|--------|--------|------|------|------|------|:----:|----------|
| `DS-IFIND-API-001` | `THS_HistoryQuotes` | 历史行情 | 日/周/月K线（OHLCV+涨跌幅+换手率） | D/W/M | A股 | ✅ | §2.4.2 |
| `DS-IFIND-API-002` | `THS_HighFrequenceSequence` | 高频序列 | 分钟K线/Tick（Interval参数控制频率） | 1m/5m/15m/30m/60m/tick | A股 | ✅ | §2.2 |
| `DS-IFIND-API-003` | `THS_RealtimeQuotes` | 实时行情 | 实时行情快照（含盘口/资金流向） | realtime | A股 | ✅ | §2.4.6 |
| `DS-IFIND-API-004` | `THS_BasicData` | 基础数据 | 估值PE/PB/PS + 股票基础信息 | — | A股 | ✅ | §2.4.3 |
| `DS-IFIND-API-005` | `THS_DateSerial` | 日期序列 | 财务数据时间序列（ROE/净利润/资产等） | D | A股 | ❌ | §2.4.4 |
| `DS-IFIND-API-006` | `THS_DataPool` | 数据池 | 指数成分股/行业板块成分股 | — | A股指数/板块 | ✅ | §2.4.5 |
| `DS-IFIND-API-007` | `THS_EDBQuery` | EDB经济库 | 宏观经济指标（CPI/M2/利率等，77909指标） | — | 中国宏观/全球宏观/利率/行业经济 | 🟡 | §2.4.8 |
| `DS-IFIND-API-008` | `THS_iwencai` | i问财 | 自然语言查询（最灵活接口，16类已验证） | — | A股聚合数据 | ✅ | §2.4.7 |
| `DS-IFIND-API-009` | `THS_iEvent` | 事件 | 事件查询 | — | A股事件 | ❌ | §2.3 |
| `DS-IFIND-API-010` | `THS_iResearch` | 研报 | 研究报告查询 | — | A股研报 | ❌ | §2.3 |
| `DS-IFIND-API-011` | `THS_Snapshot` | 快照 | 行情快照 | — | A股 | ⚠️ | §2.2 |
| `DS-IFIND-API-012` | `THS_realTimeValuation` | 实时估值 | 实时估值 | realtime | A股 | ⚠️ | §2.2 |
| `DS-IFIND-API-013` | `THS_DateQuery` | 交易日历 | 交易日历查询 | — | A股交易日 | ⚠️ | §2.2 |
| `DS-IFIND-API-014` | `THS_ReportQuery` | 报告查询 | 报告查询 | — | A股 | ⚠️ | §2.2 |
| `DS-IFIND-API-015` | `THS_iFinDLogin` | 登录 | 登录iFind（0=成功 -201=已登录） | — | — | ✅ | §2.4.1 |

### 7.5 miniQMT（`DS-MINIQMT`，36 API）

测试状态: ✅ 3 verified / 🟡 0 partial / ⚠️ 33 untested / ❌ 0 deprecated

| API ID | 函数名 | 类别 | 功能 | 频率 | 范围 | 状态 | 章节引用 |
|--------|--------|------|------|------|------|:----:|----------|
| `DS-MINIQMT-API-001` | `download_history_data` | 行情下载 | 下载历史K线/Tick到本地 | tick/1m/5m/15m/30m/1h/1d/1w/1mon | A股 | ✅ | §3.4.3 |
| `DS-MINIQMT-API-002` | `download_history_data2` | 行情下载 | 批量下载历史数据 | tick/1m/5m/15m/30m/1h/1d/1w/1mon | A股 | ⚠️ | §3.2 |
| `DS-MINIQMT-API-003` | `get_market_data_ex` | 行情获取 | 读取本地/服务器行情（主力K线接口） | 1m/5m/15m/30m/1h/1d/1w/1mon | A股 | ✅ | §3.4.2 |
| `DS-MINIQMT-API-004` | `get_market_data` | 行情获取 | 读取行情（旧版接口） | 1m/5m/15m/30m/1h/1d/1w/1mon | A股 | ⚠️ | §3.2 |
| `DS-MINIQMT-API-005` | `get_local_data` | 行情获取 | 读取本地行情数据 | 1m/5m/15m/30m/1h/1d/1w/1mon | A股 | ⚠️ | §3.2 |
| `DS-MINIQMT-API-006` | `get_full_tick` | 实时行情 | 实时Tick快照 | tick | A股 | ⚠️ | §3.2 |
| `DS-MINIQMT-API-007` | `subscribe_quote` | 实时行情 | 订阅行情推送 | realtime | A股 | ⚠️ | §3.2 |
| `DS-MINIQMT-API-008` | `subscribe_whole_quote` | 实时行情 | 订阅全市场行情推送 | realtime | A股 | ⚠️ | §3.2 |
| `DS-MINIQMT-API-009` | `get_l2_order` | Level-2 | 逐笔委托（需L2权限） | tick | A股 | ⚠️ | §3.2 |
| `DS-MINIQMT-API-010` | `get_l2_quote` | Level-2 | 逐笔成交（需L2权限） | tick | A股 | ⚠️ | §3.2 |
| `DS-MINIQMT-API-011` | `get_l2_transaction` | Level-2 | 逐笔行情（需L2权限） | tick | A股 | ⚠️ | §3.2 |
| `DS-MINIQMT-API-012` | `download_financial_data2` | 财务数据 | 下载11张财务报表 | — | A股 | ⚠️ | §3.2 |
| `DS-MINIQMT-API-013` | `get_financial_data` | 财务数据 | 读取财务数据 | — | A股 | ⚠️ | §3.2 |
| `DS-MINIQMT-API-014` | `get_option_list` | 期权 | 期权合约列表 | — | A股期权 | ⚠️ | §3.2 |
| `DS-MINIQMT-API-015` | `get_option_detail_data` | 期权 | 期权详情/Greeks | — | A股期权 | ⚠️ | §3.2 |
| `DS-MINIQMT-API-016` | `get_option_undl_data` | 期权 | 期权标的 | — | A股期权 | ⚠️ | §3.2 |
| `DS-MINIQMT-API-017` | `get_cb_info` | 可转债 | 可转债详情 | — | A股可转债 | ⚠️ | §3.2 |
| `DS-MINIQMT-API-018` | `download_cb_data` | 可转债 | 下载可转债数据 | — | A股可转债 | ⚠️ | §3.2 |
| `DS-MINIQMT-API-019` | `get_etf_info` | ETF | ETF详情 | — | A股ETF | ⚠️ | §3.2 |
| `DS-MINIQMT-API-020` | `download_index_weight` | 指数 | 下载指数权重 | — | A股指数 | ⚠️ | §3.2 |
| `DS-MINIQMT-API-021` | `get_index_weight` | 指数 | 读取指数权重 | — | A股指数 | ⚠️ | §3.2 |
| `DS-MINIQMT-API-022` | `get_divid_factors` | 复权 | 除权除息因子 | — | A股 | ⚠️ | §3.2 |
| `DS-MINIQMT-API-023` | `getDividFactors` | 复权 | 除权除息因子（旧版） | — | A股 | ⚠️ | §3.2 |
| `DS-MINIQMT-API-024` | `get_industry` | 行业 | 行业分类 | — | A股 | ⚠️ | §3.2 |
| `DS-MINIQMT-API-025` | `get_main_contract` | 期货 | 主力合约 | — | 期货 | ⚠️ | §3.2 |
| `DS-MINIQMT-API-026` | `download_history_contracts` | 期货 | 下载历史合约 | — | 期货 | ⚠️ | §3.2 |
| `DS-MINIQMT-API-027` | `get_trading_calendar` | 交易日历 | 交易日历 | — | A股交易日 | ⚠️ | §3.2 |
| `DS-MINIQMT-API-028` | `get_trading_dates` | 交易日历 | 交易日列表 | — | A股交易日 | ⚠️ | §3.2 |
| `DS-MINIQMT-API-029` | `get_holidays` | 交易日历 | 假日列表 | — | A股假日 | ⚠️ | §3.2 |
| `DS-MINIQMT-API-030` | `get_sector_list` | 板块 | 板块列表 | — | A股板块 | ⚠️ | §3.2 |
| `DS-MINIQMT-API-031` | `get_stock_list_in_sector` | 板块 | 板块成分股 | — | A股板块 | ⚠️ | §3.2 |
| `DS-MINIQMT-API-032` | `download_sector_data` | 板块 | 下载板块数据 | — | A股板块 | ⚠️ | §3.2 |
| `DS-MINIQMT-API-033` | `get_instrument_detail` | 股票详情 | 股票基础信息 | — | A股 | ⚠️ | §3.2 |
| `DS-MINIQMT-API-034` | `get_instrument_type` | 股票详情 | 股票类型 | — | A股 | ⚠️ | §3.2 |
| `DS-MINIQMT-API-035` | `get_stock_type` | 股票详情 | 股票类型（旧版） | — | A股 | ⚠️ | §3.2 |
| `DS-MINIQMT-API-036` | `xtdata.get_client` | 初始化 | 获取QMT客户端连接 | — | — | ✅ | §3.4.1 |

### 7.6 NewsAPI（`DS-NEWSAPI`，8 API）

测试状态: ✅ 8 verified / 🟡 0 partial / ⚠️ 0 untested / ❌ 0 deprecated

| API ID | 函数名 | 类别 | 功能 | 频率 | 范围 | 状态 | 章节引用 |
|--------|--------|------|------|------|------|:----:|----------|
| `DS-NEWSAPI-API-001` | `newsapi.get_everything` | 新闻 | 新闻搜索(全量) | — | 全球新闻 | ✅ | §7.1.1 |
| `DS-NEWSAPI-API-002` | `newsapi.get_top_headlines` | 新闻 | 头条新闻 | — | 全球新闻 | ✅ | §7.1.1 |
| `DS-NEWSAPI-API-003` | `eastmoney_kuaixun` | 国内直连 | 东方财富快讯 | realtime | 国内财经快讯 | ✅ | §7.1.2A |
| `DS-NEWSAPI-API-004` | `ths_kuaixun` | 国内直连 | 同花顺快讯 | realtime | 国内财经快讯 | ✅ | §7.1.2A |
| `DS-NEWSAPI-API-005` | `wallstreetcn_live` | 国内直连 | 华尔街见闻全球直播 | realtime | 全球财经(中文版) | ✅ | §7.1.2A |
| `DS-NEWSAPI-API-006` | `jin10_flash` | 国内直连 | 金十数据快讯 | realtime | 财经快讯+经济数据 | ✅ | §7.1.2A |
| `DS-NEWSAPI-API-007` | `cls_roll` | 国内直连 | 财联社电报(字段最丰富50+字段) | realtime | 国内财经电报 | ✅ | §7.1.2B |
| `DS-NEWSAPI-API-008` | `cninfo_announcement` | 国内直连 | 巨潮资讯网上市公司公告 | — | A股公告 | ✅ | §7.1.2C |

### 7.7 通达信（`DS-TDX`，13 API）

测试状态: ✅ 0 verified / 🟡 0 partial / ⚠️ 13 untested / ❌ 0 deprecated

| API ID | 函数名 | 类别 | 功能 | 频率 | 范围 | 状态 | 章节引用 |
|--------|--------|------|------|------|------|:----:|----------|
| `DS-TDX-API-001` | `client.bars` | 在线行情 | A股K线(全周期) | 0=5分/1=15分/2=30分/3=60分/5=周/6=月/7/8=1分/9=日 | A股 | ⚠️ | §8.3.1 |
| `DS-TDX-API-002` | `client.index` | 在线行情 | 指数K线 | 9=日 | A股指数 | ⚠️ | §8.3.1 |
| `DS-TDX-API-003` | `client.quote` | 在线行情 | 实时报价 | realtime | A股 | ⚠️ | §8.3.1 |
| `DS-TDX-API-004` | `client.minute` | 在线行情 | 分时数据 | — | A股 | ⚠️ | §8.3.1 |
| `DS-TDX-API-005` | `client.transaction` | 在线行情 | 个股分笔(最近交易日) | tick | A股 | ⚠️ | §8.3.1 |
| `DS-TDX-API-006` | `reader.daily` | 本地文件 | 日线数据(本地.day文件) | 1d | A股 | ⚠️ | §8.3.2 |
| `DS-TDX-API-007` | `reader.minute` | 本地文件 | 分钟线(本地.lc1文件) | 1m | A股 | ⚠️ | §8.3.2 |
| `DS-TDX-API-008` | `reader.fzline` | 本地文件 | 5分钟线(本地.lc5文件) | 5m | A股 | ⚠️ | §8.3.2 |
| `DS-TDX-API-009` | `reader.block` | 本地文件 | 板块分类(本地.dat文件) | — | A股板块 | ⚠️ | §8.3.2 |
| `DS-TDX-API-010` | `Affair.files` | 财务数据 | 可下载财务文件列表 | — | A股财务 | ⚠️ | §8.3.3 |
| `DS-TDX-API-011` | `Affair.fetch` | 财务数据 | 下载财务数据包 | — | A股财务 | ⚠️ | §8.3.3 |
| `DS-TDX-API-012` | `ExtQuotes.bars` | 扩展行情 | 港股/期货K线 | 5m/9=日 | 港股/期货 | ⚠️ | §8.3.4 |
| `DS-TDX-API-013` | `Quotes.factory` | 初始化 | 初始化客户端(bestip自动选最优服务器) | — | — | ⚠️ | §8.4.1 |

### 7.8 TickFlow（`DS-TICKFLOW`，1 API）

测试状态: ✅ 0 verified / 🟡 0 partial / ⚠️ 1 untested / ❌ 0 deprecated

| API ID | 函数名 | 类别 | 功能 | 频率 | 范围 | 状态 | 章节引用 |
|--------|--------|------|------|------|------|:----:|----------|
| `DS-TICKFLOW-API-001` | `tickflow.get_us_kline` | 美股行情 | 美股K线 | 1d | 美股 | ⚠️ | §7.4 |
