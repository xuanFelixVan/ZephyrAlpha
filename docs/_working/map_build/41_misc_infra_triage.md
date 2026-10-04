---
ttl: task_bound
completes_when: 孤儿分诊战役终裁落地（chief 终审+处置执行）后本册随 30/31 号转归档
title: 孤儿分诊证据包：小簇合并册 misc_infra（8 簇 62 台）
owner: st-orphtriage-20261004
---

# 41 号·小簇合并册：misc_infra（8 簇 62 台）

> 宇宙口径=裁定#481；数据真源=30_attribution_table.yaml；处置=建议非终裁。
>
> 合并初判汇总：dispute=2，mount=60

### 簇 scripts.data（5 台；初判 mount=5）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `scripts/data/pattern_catalog_sync.py` | REG-PAT-001 蜡烛条目实现同步生成器（MOD-SIG-145 P2-b）。 | untracked（未入库） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `scripts/data/pattern_event_backfill.py` | market_pattern_event 历史回填扫描器（MOD-SIG-145 W2）。 | untracked（未入库） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `scripts/data/pattern_event_incremental.py` | pattern_event 增量扫描入口（MOD-SIG-145 W4b，JOB-106）。 | untracked（未入库） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `scripts/data/pattern_evidence_backfill.py` | REG-PAT-001 evidence 字段回填生成器（MOD-SIG-145 W4a）。 | untracked（未入库） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `scripts/data/pattern_win_rate_materialize.py` | pattern_win_rate 胜率统计物化任务（MOD-SIG-145 W3）。 | untracked（未入库） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |

### 簇 src.zephyr.alt_data（11 台；初判 mount=11）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `src/zephyr/alt_data/__init__.py` | [DORMANT] 未启用占位模板，勿当实现引用；2026-08-22 STR-01 标注，架构审查报告 §3.2 | 2026-09-23（11天） | in=1/out=0·wired | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/alt_data/_extensions/__init__.py` | alt_data/_extensions | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/alt_data/alt_data_catalog.py` | AltDataCatalog — 另类数据目录（MOD-ALT-008）。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/alt_data/alt_data_compliance_reviewer.py` | AltDataComplianceReviewer — 另类数据合规审查器（MOD-ALT-015）。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/alt_data/alt_data_privacy_protector.py` | AltDataPrivacyProtector — 另类数据隐私保护器（MOD-ALT-012）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/alt_data/api/__init__.py` | alt_data/api | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/alt_data/core/__init__.py` | alt_data/core | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/alt_data/geopolitical_risk_analyzer.py` | GeopoliticalRiskAnalyzer — 地缘政治风险分析器（MOD-ALT-014）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/alt_data/infrastructure/__init__.py` | alt_data/infrastructure | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/alt_data/models/__init__.py` | alt_data/models | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/alt_data/services/__init__.py` | alt_data/services | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |

### 簇 src.zephyr.data（12 台；初判 dispute=2，mount=10）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `src/zephyr/data/connectors/__init__.py` | Data Connectors sub-package——外部数据源传输连接器（抽象 + 文件连接器实现）。 | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→图12（数据供给链） ②retire→Owner 门位） |
| `src/zephyr/data/normalizers/__init__.py` | Data Normalizers sub-package——原始记录到统一 schema 的归一化层（抽象 + OHLCV 实现）。 | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→图12（数据供给链） ②retire→Owner 门位） |
| `src/zephyr/data/connectors/connector_base.py` | 数据连接器抽象基类（MOD-L00-005 data/connectors/ 核心抽象）。 | 2026-09-16（18天） | in=2/out=0·wired | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/data/connectors/file_connector.py` | 文件连接器（MOD-L00-005 具体实现①）。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/data/data_compression_archiver.py` | DataCompressionArchiver — 行情数据压缩与归档编排器（MOD-DATA-064）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/data/normalizers/format_transformer.py` | Schema 驱动的多源格式转换器（CAND-DAT-010 / B1-00343 / D-INT-16 DataFormatTransformer）。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/data/normalizers/normalizer_base.py` | 数据归一化器抽象基类（MOD-L00-006 data/normalizers/ 核心抽象）。 | 2026-09-16（18天） | in=2/out=0·wired | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/data/normalizers/ohlcv_normalizer.py` | OHLCV 归一化器（MOD-L00-006 具体实现①）。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/data/quality/__init__.py` | D_DATA 质量子包 — SLA 违约预测 + F08 归档链 burn-rate 消费面。 | 2026-10-04（0天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/data/quality/archive_sla_burnrate.py` | F08 冷归档链 SLA burn-rate 消费面（T1-B1 融合接线，2026-09-30）。 | 2026-10-04（0天） | in=1/out=0·wired | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/data/quality/sla_breach_predictor.py` | QualitySlaBreachPredictor — 质量 SLA 违约预测器（MOD-DATENG-003）。 | 2026-10-04（0天） | in=2/out=0·wired | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/data/tick_redis_cache.py` | tick → Redis tick:{symbol}:latest 双写器（D-DATA → H1 集成适配器）。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→图12（数据供给链）（活线在身未挂线） |

### 簇 src.zephyr.ex_sor（15 台；初判 mount=15）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `src/zephyr/ex_sor/__init__.py` | 规划态占位（planning stub）：本域已在 architecture_model/index.yaml 登记为 D_EX_SOR (L2_domain)， | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/ex_sor/_extensions/__init__.py` | ex_sor/_extensions | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/ex_sor/api/__init__.py` | ex_sor/api — 券商API层 (限速器/连接器) | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/ex_sor/api/api_rate_limiter.py` | Exchange API Rate Limiter — 交易所 API 限速器 (MOD-XS-014) | 2026-09-16（18天） | in=4/out=0·wired | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/ex_sor/api/broker_api_connector.py` | Broker API Connector — 券商 API 连接器 (MOD-XS-013) | 2026-09-16（18天） | in=3/out=0·wired | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/ex_sor/core/algo_trading_engine.py` | Algo Trading Engine — 算法交易引擎 (MOD-XS-005) | 2026-09-16（18天） | in=5/out=0·wired | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/ex_sor/core/execution_route_policy.py` | D_EX_SOR — 执行路由策略（90 号 Phase1 项③：默认限价单 + 打板专用路径） | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/ex_sor/core/execution_scheduler.py` | Execution Scheduler — 执行调度器 (MOD-XS-004) | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/ex_sor/infrastructure/__init__.py` | ex_sor/infrastructure | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/ex_sor/models/__init__.py` | ex_sor/models | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/ex_sor/risk_redline.py` | risk_redline — 实盘红线分级引擎 v0（骨架 v1.1 §9 的规则执行纯函数）。 | 2026-09-17（17天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/ex_sor/services/rl_trainer/td3_agent.py` | TD3 agent（Fujimoto 2018 起步口径）：MLP actor/critic、双 Q、目标平滑、延迟更新。 | 2026-09-22（12天） | in=2/out=0·wired | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/ex_sor/services/slippage_analyzer.py` | Slippage Analyzer — 滑点分析器 (MOD-XS-017) | 2026-09-16（18天） | in=1/out=0·wired | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/ex_sor/services/t0_cost_model.py` | D_EX_SOR — 做T成本模型（90 号 Phase1 项①，注册表条目 CST-T0-001） | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/ex_sor/services/transaction_cost_optimizer.py` | Transaction Cost Optimizer — 交易成本优化器 (MOD-XS-019) | 2026-09-16（18天） | in=1/out=0·wired | **mount**→图12（数据供给链）（活线在身未挂线） |

### 簇 src.zephyr.infra_ops（1 台；初判 mount=1）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `src/zephyr/infra_ops/storage_cost_calculator.py` | StorageCostCalculator — 存储成本量化核算器（MOD-INF-086）。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→图12（基础设施段）（活线在身未挂线） |

### 簇 src.zephyr.infra_runtime（3 台；初判 mount=3）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `src/zephyr/infra_runtime/cold_plane_isolation.py` | ColdPlaneIsolator — Cold 平面（>1s）隔离器（MOD-INF-079）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图12（基础设施段）（活线在身未挂线） |
| `src/zephyr/infra_runtime/ml_pipeline_process.py` | MlPipelineProcess — P5 ML 管线进程编排（MOD-INF-078）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图12（基础设施段）（活线在身未挂线） |
| `src/zephyr/infra_runtime/runtime_admission.py` | runtime_admission — 运行时准入三件合一（P2-c / L-3）。 | 2026-09-17（17天） | in=0/out=0·wired_by_header | **mount**→图12（基础设施段）（活线在身未挂线） |

### 簇 src.zephyr.library（8 台；初判 mount=8）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `src/zephyr/library/__init__.py` | zephyr.library — 终极图书馆总账域（MOD-LIB-001）。 | 2026-09-22（12天） | in=1/out=0·wired | **mount**→图11（交付流水线）（活线在身未挂线） |
| `src/zephyr/library/collectors/fs_collector.py` | fs_collector — 文件系统采集器：白名单目录全量盘点（只读）。 | 2026-09-24（10天） | in=2/out=0·wired | **mount**→图11（交付流水线）（活线在身未挂线） |
| `src/zephyr/library/collectors/logs_collector.py` | logs_collector — 图书馆采集器（MOD-LIB-004，只读）：日志抽屉族级入册（ulib3 T10）。 | 2026-09-24（10天） | in=1/out=0·wired | **mount**→图11（交付流水线）（活线在身未挂线） |
| `src/zephyr/library/collectors/mcp_collector.py` | mcp_collector — MCP server/工具采集器（契约 SSOT + 注册配置双向核对）。 | 2026-09-22（12天） | in=1/out=0·wired | **mount**→图11（交付流水线）（活线在身未挂线） |
| `src/zephyr/library/collectors/store_collector.py` | store_collector — 图书馆第 7 采集器（MOD-LIB-004，只读）：F/G 冷储与备份资产入册。 | 2026-09-27（7天） | in=1/out=0·wired | **mount**→图11（交付流水线）（活线在身未挂线） |
| `src/zephyr/library/ledger_fingerprint.py` | ledger_fingerprint.py — 账本级世代指纹（世代水位）唯一读出件（MOD-LIB-001 常量层）。 | 2026-09-27（7天） | in=1/out=0·wired | **mount**→图11（交付流水线）（活线在身未挂线） |
| `src/zephyr/library/ledger_schema.py` | ledger_schema.py — 总账 DDL 常量与身份派生纯函数（MOD-LIB-001）。 | 2026-09-27（7天） | in=11/out=0·wired | **mount**→图11（交付流水线）（活线在身未挂线） |
| `src/zephyr/library/librarian.py` | librarian.py — 馆员（Librarian）：总账唯一写路径（MOD-LIB-002）。 | 2026-09-27（7天） | in=11/out=0·wired | **mount**→图11（交付流水线）（活线在身未挂线） |

### 簇 src.zephyr.market_data（7 台；初判 mount=7）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `src/zephyr/market_data/__init__.py` | NOTE(P1W16 2026-08-25): scaffold 注册器写入 eager import + 类名 append | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/market_data/_extensions/__init__.py` | market_data/_extensions | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/market_data/api/__init__.py` | mkt_data/api | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/market_data/core/__init__.py` | mkt_data/core | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/market_data/infrastructure/__init__.py` | mkt_data/infrastructure | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/market_data/models/__init__.py` | mkt_data/models | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
| `src/zephyr/market_data/services/__init__.py` | mkt_data/services | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→图12（数据供给链）（活线在身未挂线） |
