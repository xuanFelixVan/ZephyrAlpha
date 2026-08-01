---
doc_type: audit_report
title: 候选模块清单 — D_MKT_DATA
version: "1.0"
status: active
date: auto-generated
owner: auto-generator
ttl: permanent
---

# D_MKT_DATA 候选模块清单

> [← 返回索引](index.md)

> 本域候选 **142** 条（原有 0 + harvest 142）。
> harvest 去重四态: likely_new=102 / likely_implemented=31 / likely_planned=2 / uncertain=7

## 完整清单

| ID | 名称 / Name | 大白话（干什么用） | 域 | 状态 | 四问卡点 | 优先级 | 触发信号摘要 | 下次复查 |
|------|------|------|------|------|------|:---:|------|------|
| CAND-HARVEST-0053 | Data Ingestion & Management 数据接入与管理 | C 001：数据接入与管理 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0252 | Connector 连接器 | / D-DATA-01 / Connector / ✅ / 项目内有蓝图编号MOD-MASTER-001已建设 / 数据源连接+智能下载调度 / | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0253 | Normalizer 归一化器 | / D-DATA-02 / Normalizer / ✅ / 项目内有蓝图编号MOD-MASTER-001已建设 / 数据标准化+脱敏+格式统一 / | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0254 | Storage 存储 | / D-DATA-03 / Storage / ✅ / 项目内有蓝图编号MOD-L02-001已建设 / 数据存储+冷热分层+Feature Store / | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0255 | Real-time Feed Manager 实时管理器 | / D-DATA-04 / Real-time Feed Manager / ❌ / 门禁：需Kafka/Flink实时管道基础设施，单人开发无法运维 / 实时行情推送管理 / | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0256 | PIT Manager 管理器 | / D-DATA-06 / PIT Manager / ✅ / / Point-in-Time正确性保证 / | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0257 | Data Permission Manager 管理器 | / D-DATA-13 / Data Permission Manager / ✅ / 项目有蓝图编号MOD-INF-018但是没建设 / RBAC/ABAC+数据分级+动态脱敏 / | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0259 | Tick Data Manager 管理器 | / D-DATA-20 / Tick Data Manager / ✅ / / Tick数据管理+回放引擎 / | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0260 | Data Observability Engine 可观测性引擎 | / D-DATA-23 / Data Observability Engine / ✅ / / 数据可观测性+新鲜度+Schema漂移 / | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0261 | A-Share Intraday Data Manager 管理器 | / D-DATA-31 / A-Share Intraday Data Manager / ✅ / / A股分时数据管理 / | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0262 | A-Share Auction Data Manager 管理器 | / D-DATA-32 / A-Share Auction Data Manager / ✅ / / A股集合竞价数据管理 / | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0263 | A-Share Alt-Data Source Manager 管理器 | / D-DATA-33 / A-Share Alt-Data Source Manager / ✅ / / A股龙虎榜/融资融券/大宗交易 / | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0264 | A-Share Order Flow Data Manager 管理器订单 | / D-DATA-34 / A-Share Order Flow Data Manager / ✅ / / A股Level-2行情/大单追踪 / | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0265 | AkShare Data Source Adapter 适配器 | / D-DATA-67 / AkShare Data Source Adapter / ✅ / / AkShare数据源适配器 / | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0298 | LLM API Unified Integration 集成 | / D-ML-39 / LLM API Unified Integration / ✅ 能建 / 📋 项目有蓝图编号MOD-INF-039但是没建设 / DeepSeek+GLM+Claude三API统一+降级 / | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0299 | M3 Code Generation Model Adapter 适配器模型 | / D-ML-46 / M3 Code Generation Model Adapter / ✅ 能建 / / M3代码生成适配DeepSeek-V4-Pro / | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0300 | M7 Deep Review Model Adapter 适配器模型视图 | / D-ML-47 / M7 Deep Review Model Adapter / ✅ 能建 / / M7深度审查适配GLM-5.1 / | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0308 | M8-S01 | M8 S01 血缘解析器 ✅ 能建 契约血缘解析，提取数据流转关系 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0309 | M8-S02 | M8 S02 静态分析器 ✅ 能建 代码/SQL静态分析提取血缘 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0310 | M8-S03 | M8 S03 动态采集器 ✅ 能建 运行时血缘动态采集 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0311 | M8-S04 | M8 S04 正向查询引擎 ✅ 能建 上游→下游血缘正向追踪 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0312 | M8-S05 | M8 S05 反向查询引擎 ✅ 能建 下游→上游血缘反向溯源 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0313 | M8-S06 | M8 S06 质量评分器 ✅ 能建 血缘节点数据质量评分 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0314 | M8-S07 | M8 S07 变更检测器 ✅ 能建 血缘变更检测与影响分析 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0315 | M8-NEW-01 | / M8-NEW-01 / OpenLineage集成 / ✅ 能建 / / OpenLineage标准血缘集成 / | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0316 | M8-NEW-02 | M8 NEW 02 列级血缘 ✅ 能建 列级粒度血缘追踪 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0317 | M8-NEW-03 | / M8-NEW-01 / OpenLineage集成 / ✅ 能建 / / OpenLineage标准血缘集成 / | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0318 | M8-NEW-04 | M8 NEW 04 实时血缘 ❌ 不能建 门禁：需Kafka | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0319 | M8-NEW-05 | / M8-NEW-01 / OpenLineage集成 / ✅ 能建 / / OpenLineage标准血缘集成 / | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0320 | M8-NEW-06 | M8 NEW 06 契约验证 ✅ 能建 数据契约自动验证 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0321 | M8-NEW-07 | / M8-NEW-01 / OpenLineage集成 / ✅ 能建 / / OpenLineage标准血缘集成 / | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0322 | M8-NEW-08 | M8 NEW 08 质量框架 ✅ 能建 数据质量规则框架 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0323 | M8-NEW-09 | M8 NEW 09 记录级追踪 ✅ 能建 记录级数据追踪 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0324 | M8-NEW-10 | M8 NEW 10 影响仿真 ❌ 不能建 门禁：需仿真平台 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0497 | miniQMT 主数据源 | 3秒Tick主数据源~5000只A股 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0498 | iFind 补充数据源 | 盘后日线衍生指标龙虎榜融资融券宏观数据 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0499 | AkShare 免费备用数据源 | iFind降级备选历史数据补充 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0500 | BaoStock 历史数据补充 | 历史K线财务数据回测交叉验证 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0501 | tushare 新闻快讯数据源 | 新闻快讯9源聚合历史数据待开通 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0505 | L0 数据接入与预处理层 Data Ingestion & Preprocessing Layer | 清洗+标准化+复权+缺失填补→CTR-001 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0517 | Hot 热存储层 Redis | <10ms盘中Tick实时因子值交易信号风控持仓 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0518 | Warm 温存储层 DuckDB+Parquet | <1s日线因子信号历史基本面宏观 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0519 | Cold 冷存储层 Parquet on SSD | ║  │ Hot (Redis)  │  │ Warm (DuckDB+Parquet)│  │ Cold (Parquet on SSD)        │  ║ | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0521 | Data Observability 数据可观测性 | ║  │ 🆕Data Observability五维度映射(Freshness/Volume/Schema/Distribution/     │  ║ | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0522 | AI驱动异常检测 AI Anomaly Detection | Isolation Forest+自适应阈值 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0524 | SQL AST解析器 SQL AST Parser | 自动采集列级血缘 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0527 | PIT一致性 Point-in-Time Consistency | 三条公理+三平面统一+AS OF JOIN+Embargo期 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0528 | 双时态建模 Bitemporal Modeling | system_time+business_time双时间轴 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0529 | HSTR Snapshot+Delta 历史状态重构 | 年报+季报Snapshot+公告Delta | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0530 | pit_consistency_test PIT验证测试框架 | CI/CD PIT一致性测试 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0531 | DuckDB性能校准 DuckDB Performance Calibration | ║  ║  DuckDB性能校准 (§7+§16)                                                  ║  ║ | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0532 | miniQMT 主数据源 A股全市场 | A股全市场~5000只3秒Tick | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0533 | iFind 补充数据源 盘后日线 | 盘后日线OHLCV衍生指标龙虎榜融资融券 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0534 | tushare 待开通数据源 | 新闻快讯9源聚合历史数据补充验证 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0535 | L0→L1 标准化流水线 L0→L1 Normalization Pipeline | 原始行情→格式校验→清洗去重→L1标准化行情 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0536 | 格式校验 Schema Validation | L0→L1流水线格式校验 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0571 | 三层存储架构 Three-tier Storage Architecture | Hot/Warm/Cold三层+容量规划+生命周期+备份 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0572 | 容量规划 Capacity Planning | Hot/Warm/Cold当前/1年/3年预估+扩展触发 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0573 | 生命周期管理 Lifecycle Management | 各数据类型Hot/Warm/Cold保留期+降级规则 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0575 | Redis RDB+AOF双开 Redis RDB+AOF | AOF保证RPO≈0 RDB保证恢复速度 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0576 | L0→L6全链路规格 L0→L6 Full-chain Spec | 数据从接入到消费全链路流动路径延迟预算 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0577 | 批流分离设计 Batch-Stream Separation | 流式路径盘中+批量路径盘后两种负载特征 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0584 | 完整性 Completeness | 数据记录和字段的缺失程度 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0585 | Financial Parser 财务报告解析器 | 年报/季报/快报PDF→结构化数据+XBRL解析 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0586 | 准确性 Accuracy | 数据值与真实值的偏差程度 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0587 | CrossSourceReconciler 跨源对账器 | 值偏差率量价逻辑违反率异常值检出率 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0588 | Corporate Actions Processor 公司行为处理 | 分红/拆股/合并/要约收购/复权因子计算 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0589 | 一致性 Consistency | 同一数据实体在不同系统/数据源间的口径一致性 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0590 | Data Schema Registry 数据Schema注册表 | Schema注册/验证/演化+兼容性检查 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0592 | 及时性 Timeliness | 数据从产生到可用的延迟 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0594 | Macro Data Manager 宏观数据管理器 | GDP/CPI/PMI/利率/汇率+多源采集 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0595 | 可用性 Availability | 数据可被查询和使用的比例 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0596 | SLA分级体系 SLA Tiered System | P0关键/P1重要/P2背景三级SLA分级 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0599 | Data Anomaly Alerter 数据异常告警器 | 多维度异常检测+告警分级+告警路由+告警抑制 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0601 | Trading Calendar Manager 交易日历管理 | 多市场日历引擎+交易日/结算日/交割日+财报披露窗口 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0603 | 盘中实时监控 Intraday Real-time Monitoring | 09:30-15:00 Tick延迟+因子新鲜度+信号可用性+风控数据 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0604 | 盘后一致性校验 Post-market Consistency Check | 15:00-17:00跨源对账+Quality Gate L1~L4+因子值一致性 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0615 | WAL Checkpoint Monitor SQLite WAL检查点监控器 | > **设计决策 DD-12-03**: Event Store使用Parquet append-only文件而非数据库。理由：事件是append-only的不可变数据，Parquet列式存储压缩比高（10:1），且与现有数据存储架构一致（ | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0616 | CQRS分离 CQRS Separation | 写端命令追加+读端物化视图查询分离 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0617 | 快照策略 Snapshot Strategy | 日快照+盘中5分钟增量快照两级策略 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0618 | Point-in-Time一致性保证 PIT Consistency | 三条公理+三平面统一+AS OF JOIN+Embargo期 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0619 | PIT三条公理 PIT Three Axioms | 因子值时间不可逆+财务数据公告日约束+幸存者偏差修正 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0620 | 三平面统一 Three-plane Unification | 训练平面+回测平面+推理平面PIT保证 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0621 | AS OF JOIN实现 AS OF JOIN Implementation | DuckDB QUALIFY ROW_NUMBER()实现PIT语义 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0622 | Embargo期 Embargo Period | 财务数据5个交易日Embargo覆盖更正公告窗口 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0623 | PIT校验规则 PIT Validation Rules | 因子时间戳+财务公告日+幸存者偏差+Embargo+跨平面一致性校验 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0629 | 可扩展性与演进性 Scalability & Evolution | 数据源接入流程+Schema演进+存储扩展+技术栈演进+ADR | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0630 | 数据源接入流程 Data Source Onboarding | 评估→审批→开发→验证→灰度→全量14天流程 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0631 | Schema演进 Schema Evolution | 新增列/删除列/修改列类型/重命名列/Schema版本向后兼容 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0632 | 存储扩展路径 Storage Expansion Path | AUM驱动阶段1 DuckDB/阶段2 ClickHouse/阶段3 Lakehouse | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0633 | 技术栈演进 Tech Stack Evolution | 热/温/冷存储+特征存储+事件存储+血缘+质量+契约+向量演进 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0637 | Data Version Manager 数据版本管理 | / D-DATA-11 / Data Version Manager / 数据版本管理(版本快照+分支/标签+增量Delta+版本回滚+PIT版本绑定) / ✅能建。与§13 HSTR Snapshot+Delta模式对齐，在Parquet | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0638 | Data Cost Tracker 数据成本追踪 | 用量计量+成本分摊+预算管控+ROI分析+供应商账单对账 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0639 | Data Retention Manager 数据保留策略 | 保留策略引擎+自动归档/删除调度+法律保留覆盖 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0643 | DuckDB AS OF JOIN PIT Query Engine PIT查询引擎 | 防幸存者偏差+查询构建/性能优化/结果缓存 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0644 | Multi-Source Data Priority Router 多数据源优先级路由器 | / D-DATA-77 / Multi-Source Data Priority Router / 多数据源优先级路由器(AkShare+iFind+BaoStock+优先级路由+降级切换+成本控制) / ✅能建。在D-DATA-01 Co | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0645 | Data Source Health Monitor 数据源健康度监控器 | 连接状态+数据延迟+数据完整性+自动切换 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0721 | §29.4 时序数据库与分层存储架构 TSDB & Tiered Storage | ### §16.18 A1§29.4 迁移内容：时序数据库与分层存储架构（历史参考） | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0722 | 4元组数据映射模型 4-tuple Data Mapping | 标的代码/时间戳/数据类型/数值统一映射 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0723 | ClickHouse 列存时序数据库 | 写入路径: L0数据接入 → 同时写Redis(热) + ClickHouse(温) | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0724 | TimescaleDB PostgreSQL时序扩展 | 备选温数据层PostgreSQL扩展SQL兼容 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0734 | PIT Consistency Guard PIT一致性守卫 | Point-in-Time一致性守卫AS OF JOIN三条公理 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1227 | Financial Knowledge Graph 金融知识图谱 | 实体/关系抽取+SPO三元组+图推理引擎+产业链KG+GraphRAG | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1228 | Knowledge Distiller 知识蒸馏器 | 从代码/日志/蓝图等提取结构化知识+LLM+规则混合提取 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1333 | Data Subscription Manager 数据订阅管理器 | 订阅注册/取消+QoS等级+推送调度+断点续传+订阅者健康监控 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1334 | Microstructure Analyzer 微观结构分析器 | 订单簿重建+买卖价差分解+成交量剖面+市场冲击模型+Kyle Lambda+Amihud非流动性 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1336 | Policy Event Factor Library 政策事件因子库 | 产业链关键词+政策事件因子+技术卡脖子因子+热度追踪 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1337 | Concept Factor Mapping Engine 概念因子映射引擎 | 概念-股票映射字典+逆向索引+质量校验 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1338 | High-Frequency Signal Enhancer 高频信号增强器 | 1分钟K线增强趋势转折信号+1min/5min融合分析 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1340 | Text Sentiment Factor Extractor 文本情感因子提取器 | NLP情感分析→IC测试→因子入库+舆情热度追踪 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1341 | Pydantic V2 Code Generator Pydantic V2代码生成器 | YAML→Pydantic V2 frozen dataclass代码生成+类型强制/序列化 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1343 | Data Isolation Manager 数据隔离管理器 | 治理数据与行情元数据隔离+隔离规则/校验/跨库查询协调 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1344 | Local File Auto-Parser 本地文件自动解析器 | 本地文件自动解析+格式识别+内容提取+知识结构化 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1345 | Web Data Crawler 网络数据爬虫 | 网络数据智能爬取+反反爬+数据清洗+质量校验 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1346 | Trading Decision Annotation Dataset 交易决策标注数据集 | 用户交易决策标注+画图标注+反馈数据采集+存储 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1347 | Research Report Collector 研究报告采集器 | 研究报告+新闻事件+宏观经济数据采集+NLP提取 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1348 | Training Dataset Manager 训练数据集管理器 | 多源训练数据集管理+数据版本+血缘+质量+分割+增强 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1350 | ClickHouse Analyzer ClickHouse分析器 | ClickHouse时序数据存储+高性能查询+列式存储+数据压缩 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1351 | Unified Data Portal 统一数据门户 | 统一界面访问所有数据+SQL查询+面向对象API+Jupyter集成 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1353 | Sector Factor Data Manager 板块因子数据管理器 | 板块分钟线+日线+成分股+板块轮动→统计因子 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1354 | Incremental Update Engine 增量更新引擎 | 仅更新变化的数据+变更检测+增量同步+一致性校验 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1355 | Great Expectations Governance Great Expectations治理 | GE自动化数据质量检查+修复+验证+质量闭环 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1359 | Sina+Tencent Real-Time 新浪+腾讯实时行情 | 新浪财经+腾讯财经免费实时行情API | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1360 | yfinance Adapter yfinance适配器 | yfinance雅虎财经历史行情+基本面数据 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1361 | Overseas Market Data Adapter 外盘数据适配器 | AkShare获取隔夜外盘数据+全球市场传导量化 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1362 | Vector DB Switch Manager 向量数据库切换管理器 | Chroma→FAISS/Milvus迁移策略+数据迁移+兼容性适配 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1803 | Dragon-Tiger List 龙虎榜 | 异常交易披露数据采集器(监管披露数据→统计因子) | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2300 | AkShare AkShare数据适配器 | / MVP替代方案 / 市场状态Agent消费隔夜外盘数据（通过D-DATA域AkShare适配器获取），不建独立跨资产域；A股+港股通通过miniQMT已有通道 / | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2606 | Industry Best Practice Benchmark 行业最佳实践对标 | NIST CSF+ISO 27001+数据安全法+个人信息保护法+JR/T 0197 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2607 | Design Decision Summary 设计决策汇总 | DD-14-01~04合规相关设计决策 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2620 | Dual Temporal Modeling 双时态建模 | / 双时态建模（system_time+business_time+HSTR Snapshot+Delta） / 运维监控（→A9） / | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2622 | Point in Time Consistency Point-in-Time一致性保证 | 三条公理+三平面统一+AS OF JOIN+Embargo期 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2623 | Tiered Storage Architecture 分层存储架构 | / 分层存储架构（Hot Redis/Warm DuckDB+Parquet/Cold Parquet SSD） / 治理机制（→A2） / | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3803 | Temp Query P5 模板查询p5 | data/asset_index/_temp_query_p5.py,module,'' | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4119 | Data Ingestion Process 数据接入进程 | A1迁移概念级进程P0 miniQMT连接iFind轮询事件总线不可崩溃 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4229 | Market Data Pipeline 行情数据管道 | 跨域混居应迁出GOV属于D-DATA行情管道是数据域核心 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4801 | Market Data Provider 行情数据提供商 | 外部契约-REST/WebSocket | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4869 | DDD Aggregate Root Lifecycle DDD聚合根与生命周期 | / 130~136 / DDD聚合根与生命周期 / 聚合根(MarketData/Instrument)生命周期管理+仓储接口+值对象(Bar/OHLCV/FinancialReport)+恢复演练验证+跨域保留归档策略协调+仿真回测数据生 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4913 | PIT Consistency Guarantee PIT一致性保证 | / — / PIT一致性保证 / 三公理(时间不可逆+公告日约束+幸存者偏差)+三平面统一(训练AS OF JOIN+回测事件回放+推理Redis) / ✅ / | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4914 | Bi-Temporal Modeling 双时态建模 | / — / 双时态建模 / system_time+business_time+HSTR+Delta / ✅ / | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4915 | FWT Retrieval Augmented Diffusion FWT检索增强扩散 | A股数据增强 | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5067 | CQRS Command Query Responsibility Segregation CQRS命令查询职责分离 | /  7  / 🟡建议 / CQRS命令查询职责分离              /  ❌域文档  / Martin Fowler CQRS | D_MKT_DATA | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |

## 按四问卡点分组（为什么没开发）

> 四问过滤：q1已实现 / q2需求驱动 / q3域活着 / q4 AI替代。任一问「否」即不进 depgraph 设计态，登记在候选库。

### 待评估（142 条）

| ID | 名称 | 大白话（干什么用） | 域 | 卡点理由 | 替代方案 |
|------|------|------|------|------|------|
| CAND-HARVEST-0053 | Data Ingestion & Management 数据接入与管理 | C 001：数据接入与管理 | D_MKT_DATA | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0252 | Connector 连接器 | / D-DATA-01 / Connector / ✅ / 项目内有蓝图编号MOD-MASTER-001已建设 / 数据源连接+智能下载调度 / | D_MKT_DATA | harvest待评估（likely_planned） |  |
| CAND-HARVEST-0253 | Normalizer 归一化器 | / D-DATA-02 / Normalizer / ✅ / 项目内有蓝图编号MOD-MASTER-001已建设 / 数据标准化+脱敏+格式统一 / | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0254 | Storage 存储 | / D-DATA-03 / Storage / ✅ / 项目内有蓝图编号MOD-L02-001已建设 / 数据存储+冷热分层+Feature Store / | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0255 | Real-time Feed Manager 实时管理器 | / D-DATA-04 / Real-time Feed Manager / ❌ / 门禁：需Kafka/Flink实时管道基础设施，单人开发无法运维 / 实时行情推送管理 / | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0256 | PIT Manager 管理器 | / D-DATA-06 / PIT Manager / ✅ / / Point-in-Time正确性保证 / | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0257 | Data Permission Manager 管理器 | / D-DATA-13 / Data Permission Manager / ✅ / 项目有蓝图编号MOD-INF-018但是没建设 / RBAC/ABAC+数据分级+动态脱敏 / | D_MKT_DATA | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0259 | Tick Data Manager 管理器 | / D-DATA-20 / Tick Data Manager / ✅ / / Tick数据管理+回放引擎 / | D_MKT_DATA | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0260 | Data Observability Engine 可观测性引擎 | / D-DATA-23 / Data Observability Engine / ✅ / / 数据可观测性+新鲜度+Schema漂移 / | D_MKT_DATA | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0261 | A-Share Intraday Data Manager 管理器 | / D-DATA-31 / A-Share Intraday Data Manager / ✅ / / A股分时数据管理 / | D_MKT_DATA | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0262 | A-Share Auction Data Manager 管理器 | / D-DATA-32 / A-Share Auction Data Manager / ✅ / / A股集合竞价数据管理 / | D_MKT_DATA | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0263 | A-Share Alt-Data Source Manager 管理器 | / D-DATA-33 / A-Share Alt-Data Source Manager / ✅ / / A股龙虎榜/融资融券/大宗交易 / | D_MKT_DATA | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0264 | A-Share Order Flow Data Manager 管理器订单 | / D-DATA-34 / A-Share Order Flow Data Manager / ✅ / / A股Level-2行情/大单追踪 / | D_MKT_DATA | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0265 | AkShare Data Source Adapter 适配器 | / D-DATA-67 / AkShare Data Source Adapter / ✅ / / AkShare数据源适配器 / | D_MKT_DATA | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0298 | LLM API Unified Integration 集成 | / D-ML-39 / LLM API Unified Integration / ✅ 能建 / 📋 项目有蓝图编号MOD-INF-039但是没建设 / DeepSeek+GLM+Claude三API统一+降级 / | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0299 | M3 Code Generation Model Adapter 适配器模型 | / D-ML-46 / M3 Code Generation Model Adapter / ✅ 能建 / / M3代码生成适配DeepSeek-V4-Pro / | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0300 | M7 Deep Review Model Adapter 适配器模型视图 | / D-ML-47 / M7 Deep Review Model Adapter / ✅ 能建 / / M7深度审查适配GLM-5.1 / | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0308 | M8-S01 | M8 S01 血缘解析器 ✅ 能建 契约血缘解析，提取数据流转关系 | D_MKT_DATA | harvest待评估（uncertain） |  |
| CAND-HARVEST-0309 | M8-S02 | M8 S02 静态分析器 ✅ 能建 代码/SQL静态分析提取血缘 | D_MKT_DATA | harvest待评估（uncertain） |  |
| CAND-HARVEST-0310 | M8-S03 | M8 S03 动态采集器 ✅ 能建 运行时血缘动态采集 | D_MKT_DATA | harvest待评估（uncertain） |  |
| CAND-HARVEST-0311 | M8-S04 | M8 S04 正向查询引擎 ✅ 能建 上游→下游血缘正向追踪 | D_MKT_DATA | harvest待评估（uncertain） |  |
| CAND-HARVEST-0312 | M8-S05 | M8 S05 反向查询引擎 ✅ 能建 下游→上游血缘反向溯源 | D_MKT_DATA | harvest待评估（uncertain） |  |
| CAND-HARVEST-0313 | M8-S06 | M8 S06 质量评分器 ✅ 能建 血缘节点数据质量评分 | D_MKT_DATA | harvest待评估（uncertain） |  |
| CAND-HARVEST-0314 | M8-S07 | M8 S07 变更检测器 ✅ 能建 血缘变更检测与影响分析 | D_MKT_DATA | harvest待评估（uncertain） |  |
| CAND-HARVEST-0315 | M8-NEW-01 | / M8-NEW-01 / OpenLineage集成 / ✅ 能建 / / OpenLineage标准血缘集成 / | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0316 | M8-NEW-02 | M8 NEW 02 列级血缘 ✅ 能建 列级粒度血缘追踪 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0317 | M8-NEW-03 | / M8-NEW-01 / OpenLineage集成 / ✅ 能建 / / OpenLineage标准血缘集成 / | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0318 | M8-NEW-04 | M8 NEW 04 实时血缘 ❌ 不能建 门禁：需Kafka | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0319 | M8-NEW-05 | / M8-NEW-01 / OpenLineage集成 / ✅ 能建 / / OpenLineage标准血缘集成 / | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0320 | M8-NEW-06 | M8 NEW 06 契约验证 ✅ 能建 数据契约自动验证 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0321 | M8-NEW-07 | / M8-NEW-01 / OpenLineage集成 / ✅ 能建 / / OpenLineage标准血缘集成 / | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0322 | M8-NEW-08 | M8 NEW 08 质量框架 ✅ 能建 数据质量规则框架 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0323 | M8-NEW-09 | M8 NEW 09 记录级追踪 ✅ 能建 记录级数据追踪 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0324 | M8-NEW-10 | M8 NEW 10 影响仿真 ❌ 不能建 门禁：需仿真平台 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0497 | miniQMT 主数据源 | 3秒Tick主数据源~5000只A股 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0498 | iFind 补充数据源 | 盘后日线衍生指标龙虎榜融资融券宏观数据 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0499 | AkShare 免费备用数据源 | iFind降级备选历史数据补充 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0500 | BaoStock 历史数据补充 | 历史K线财务数据回测交叉验证 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0501 | tushare 新闻快讯数据源 | 新闻快讯9源聚合历史数据待开通 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0505 | L0 数据接入与预处理层 Data Ingestion & Preprocessing Layer | 清洗+标准化+复权+缺失填补→CTR-001 | D_MKT_DATA | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0517 | Hot 热存储层 Redis | <10ms盘中Tick实时因子值交易信号风控持仓 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0518 | Warm 温存储层 DuckDB+Parquet | <1s日线因子信号历史基本面宏观 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0519 | Cold 冷存储层 Parquet on SSD | ║  │ Hot (Redis)  │  │ Warm (DuckDB+Parquet)│  │ Cold (Parquet on SSD)        │  ║ | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0521 | Data Observability 数据可观测性 | ║  │ 🆕Data Observability五维度映射(Freshness/Volume/Schema/Distribution/     │  ║ | D_MKT_DATA | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0522 | AI驱动异常检测 AI Anomaly Detection | Isolation Forest+自适应阈值 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0524 | SQL AST解析器 SQL AST Parser | 自动采集列级血缘 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0527 | PIT一致性 Point-in-Time Consistency | 三条公理+三平面统一+AS OF JOIN+Embargo期 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0528 | 双时态建模 Bitemporal Modeling | system_time+business_time双时间轴 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0529 | HSTR Snapshot+Delta 历史状态重构 | 年报+季报Snapshot+公告Delta | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0530 | pit_consistency_test PIT验证测试框架 | CI/CD PIT一致性测试 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0531 | DuckDB性能校准 DuckDB Performance Calibration | ║  ║  DuckDB性能校准 (§7+§16)                                                  ║  ║ | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0532 | miniQMT 主数据源 A股全市场 | A股全市场~5000只3秒Tick | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0533 | iFind 补充数据源 盘后日线 | 盘后日线OHLCV衍生指标龙虎榜融资融券 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0534 | tushare 待开通数据源 | 新闻快讯9源聚合历史数据补充验证 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0535 | L0→L1 标准化流水线 L0→L1 Normalization Pipeline | 原始行情→格式校验→清洗去重→L1标准化行情 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0536 | 格式校验 Schema Validation | L0→L1流水线格式校验 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0571 | 三层存储架构 Three-tier Storage Architecture | Hot/Warm/Cold三层+容量规划+生命周期+备份 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0572 | 容量规划 Capacity Planning | Hot/Warm/Cold当前/1年/3年预估+扩展触发 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0573 | 生命周期管理 Lifecycle Management | 各数据类型Hot/Warm/Cold保留期+降级规则 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0575 | Redis RDB+AOF双开 Redis RDB+AOF | AOF保证RPO≈0 RDB保证恢复速度 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0576 | L0→L6全链路规格 L0→L6 Full-chain Spec | 数据从接入到消费全链路流动路径延迟预算 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0577 | 批流分离设计 Batch-Stream Separation | 流式路径盘中+批量路径盘后两种负载特征 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0584 | 完整性 Completeness | 数据记录和字段的缺失程度 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0585 | Financial Parser 财务报告解析器 | 年报/季报/快报PDF→结构化数据+XBRL解析 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0586 | 准确性 Accuracy | 数据值与真实值的偏差程度 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0587 | CrossSourceReconciler 跨源对账器 | 值偏差率量价逻辑违反率异常值检出率 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0588 | Corporate Actions Processor 公司行为处理 | 分红/拆股/合并/要约收购/复权因子计算 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0589 | 一致性 Consistency | 同一数据实体在不同系统/数据源间的口径一致性 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0590 | Data Schema Registry 数据Schema注册表 | Schema注册/验证/演化+兼容性检查 | D_MKT_DATA | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0592 | 及时性 Timeliness | 数据从产生到可用的延迟 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0594 | Macro Data Manager 宏观数据管理器 | GDP/CPI/PMI/利率/汇率+多源采集 | D_MKT_DATA | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0595 | 可用性 Availability | 数据可被查询和使用的比例 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0596 | SLA分级体系 SLA Tiered System | P0关键/P1重要/P2背景三级SLA分级 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0599 | Data Anomaly Alerter 数据异常告警器 | 多维度异常检测+告警分级+告警路由+告警抑制 | D_MKT_DATA | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0601 | Trading Calendar Manager 交易日历管理 | 多市场日历引擎+交易日/结算日/交割日+财报披露窗口 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0603 | 盘中实时监控 Intraday Real-time Monitoring | 09:30-15:00 Tick延迟+因子新鲜度+信号可用性+风控数据 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0604 | 盘后一致性校验 Post-market Consistency Check | 15:00-17:00跨源对账+Quality Gate L1~L4+因子值一致性 | D_MKT_DATA | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0615 | WAL Checkpoint Monitor SQLite WAL检查点监控器 | > **设计决策 DD-12-03**: Event Store使用Parquet append-only文件而非数据库。理由：事件是append-only的不可变数据，Parquet列式存储压缩比高（10:1），且与现有数据存储架构一致（ | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0616 | CQRS分离 CQRS Separation | 写端命令追加+读端物化视图查询分离 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0617 | 快照策略 Snapshot Strategy | 日快照+盘中5分钟增量快照两级策略 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0618 | Point-in-Time一致性保证 PIT Consistency | 三条公理+三平面统一+AS OF JOIN+Embargo期 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0619 | PIT三条公理 PIT Three Axioms | 因子值时间不可逆+财务数据公告日约束+幸存者偏差修正 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0620 | 三平面统一 Three-plane Unification | 训练平面+回测平面+推理平面PIT保证 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0621 | AS OF JOIN实现 AS OF JOIN Implementation | DuckDB QUALIFY ROW_NUMBER()实现PIT语义 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0622 | Embargo期 Embargo Period | 财务数据5个交易日Embargo覆盖更正公告窗口 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0623 | PIT校验规则 PIT Validation Rules | 因子时间戳+财务公告日+幸存者偏差+Embargo+跨平面一致性校验 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0629 | 可扩展性与演进性 Scalability & Evolution | 数据源接入流程+Schema演进+存储扩展+技术栈演进+ADR | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0630 | 数据源接入流程 Data Source Onboarding | 评估→审批→开发→验证→灰度→全量14天流程 | D_MKT_DATA | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0631 | Schema演进 Schema Evolution | 新增列/删除列/修改列类型/重命名列/Schema版本向后兼容 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0632 | 存储扩展路径 Storage Expansion Path | AUM驱动阶段1 DuckDB/阶段2 ClickHouse/阶段3 Lakehouse | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0633 | 技术栈演进 Tech Stack Evolution | 热/温/冷存储+特征存储+事件存储+血缘+质量+契约+向量演进 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0637 | Data Version Manager 数据版本管理 | / D-DATA-11 / Data Version Manager / 数据版本管理(版本快照+分支/标签+增量Delta+版本回滚+PIT版本绑定) / ✅能建。与§13 HSTR Snapshot+Delta模式对齐，在Parquet | D_MKT_DATA | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0638 | Data Cost Tracker 数据成本追踪 | 用量计量+成本分摊+预算管控+ROI分析+供应商账单对账 | D_MKT_DATA | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0639 | Data Retention Manager 数据保留策略 | 保留策略引擎+自动归档/删除调度+法律保留覆盖 | D_MKT_DATA | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0643 | DuckDB AS OF JOIN PIT Query Engine PIT查询引擎 | 防幸存者偏差+查询构建/性能优化/结果缓存 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0644 | Multi-Source Data Priority Router 多数据源优先级路由器 | / D-DATA-77 / Multi-Source Data Priority Router / 多数据源优先级路由器(AkShare+iFind+BaoStock+优先级路由+降级切换+成本控制) / ✅能建。在D-DATA-01 Co | D_MKT_DATA | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0645 | Data Source Health Monitor 数据源健康度监控器 | 连接状态+数据延迟+数据完整性+自动切换 | D_MKT_DATA | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0721 | §29.4 时序数据库与分层存储架构 TSDB & Tiered Storage | ### §16.18 A1§29.4 迁移内容：时序数据库与分层存储架构（历史参考） | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0722 | 4元组数据映射模型 4-tuple Data Mapping | 标的代码/时间戳/数据类型/数值统一映射 | D_MKT_DATA | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0723 | ClickHouse 列存时序数据库 | 写入路径: L0数据接入 → 同时写Redis(热) + ClickHouse(温) | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0724 | TimescaleDB PostgreSQL时序扩展 | 备选温数据层PostgreSQL扩展SQL兼容 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-0734 | PIT Consistency Guard PIT一致性守卫 | Point-in-Time一致性守卫AS OF JOIN三条公理 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-1227 | Financial Knowledge Graph 金融知识图谱 | 实体/关系抽取+SPO三元组+图推理引擎+产业链KG+GraphRAG | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-1228 | Knowledge Distiller 知识蒸馏器 | 从代码/日志/蓝图等提取结构化知识+LLM+规则混合提取 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-1333 | Data Subscription Manager 数据订阅管理器 | 订阅注册/取消+QoS等级+推送调度+断点续传+订阅者健康监控 | D_MKT_DATA | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1334 | Microstructure Analyzer 微观结构分析器 | 订单簿重建+买卖价差分解+成交量剖面+市场冲击模型+Kyle Lambda+Amihud非流动性 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-1336 | Policy Event Factor Library 政策事件因子库 | 产业链关键词+政策事件因子+技术卡脖子因子+热度追踪 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-1337 | Concept Factor Mapping Engine 概念因子映射引擎 | 概念-股票映射字典+逆向索引+质量校验 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-1338 | High-Frequency Signal Enhancer 高频信号增强器 | 1分钟K线增强趋势转折信号+1min/5min融合分析 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-1340 | Text Sentiment Factor Extractor 文本情感因子提取器 | NLP情感分析→IC测试→因子入库+舆情热度追踪 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-1341 | Pydantic V2 Code Generator Pydantic V2代码生成器 | YAML→Pydantic V2 frozen dataclass代码生成+类型强制/序列化 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-1343 | Data Isolation Manager 数据隔离管理器 | 治理数据与行情元数据隔离+隔离规则/校验/跨库查询协调 | D_MKT_DATA | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1344 | Local File Auto-Parser 本地文件自动解析器 | 本地文件自动解析+格式识别+内容提取+知识结构化 | D_MKT_DATA | harvest待评估（likely_planned） |  |
| CAND-HARVEST-1345 | Web Data Crawler 网络数据爬虫 | 网络数据智能爬取+反反爬+数据清洗+质量校验 | D_MKT_DATA | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1346 | Trading Decision Annotation Dataset 交易决策标注数据集 | 用户交易决策标注+画图标注+反馈数据采集+存储 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-1347 | Research Report Collector 研究报告采集器 | 研究报告+新闻事件+宏观经济数据采集+NLP提取 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-1348 | Training Dataset Manager 训练数据集管理器 | 多源训练数据集管理+数据版本+血缘+质量+分割+增强 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-1350 | ClickHouse Analyzer ClickHouse分析器 | ClickHouse时序数据存储+高性能查询+列式存储+数据压缩 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-1351 | Unified Data Portal 统一数据门户 | 统一界面访问所有数据+SQL查询+面向对象API+Jupyter集成 | D_MKT_DATA | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1353 | Sector Factor Data Manager 板块因子数据管理器 | 板块分钟线+日线+成分股+板块轮动→统计因子 | D_MKT_DATA | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1354 | Incremental Update Engine 增量更新引擎 | 仅更新变化的数据+变更检测+增量同步+一致性校验 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-1355 | Great Expectations Governance Great Expectations治理 | GE自动化数据质量检查+修复+验证+质量闭环 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-1359 | Sina+Tencent Real-Time 新浪+腾讯实时行情 | 新浪财经+腾讯财经免费实时行情API | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-1360 | yfinance Adapter yfinance适配器 | yfinance雅虎财经历史行情+基本面数据 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-1361 | Overseas Market Data Adapter 外盘数据适配器 | AkShare获取隔夜外盘数据+全球市场传导量化 | D_MKT_DATA | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1362 | Vector DB Switch Manager 向量数据库切换管理器 | Chroma→FAISS/Milvus迁移策略+数据迁移+兼容性适配 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-1803 | Dragon-Tiger List 龙虎榜 | 异常交易披露数据采集器(监管披露数据→统计因子) | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-2300 | AkShare AkShare数据适配器 | / MVP替代方案 / 市场状态Agent消费隔夜外盘数据（通过D-DATA域AkShare适配器获取），不建独立跨资产域；A股+港股通通过miniQMT已有通道 / | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-2606 | Industry Best Practice Benchmark 行业最佳实践对标 | NIST CSF+ISO 27001+数据安全法+个人信息保护法+JR/T 0197 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-2607 | Design Decision Summary 设计决策汇总 | DD-14-01~04合规相关设计决策 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-2620 | Dual Temporal Modeling 双时态建模 | / 双时态建模（system_time+business_time+HSTR Snapshot+Delta） / 运维监控（→A9） / | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-2622 | Point in Time Consistency Point-in-Time一致性保证 | 三条公理+三平面统一+AS OF JOIN+Embargo期 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-2623 | Tiered Storage Architecture 分层存储架构 | / 分层存储架构（Hot Redis/Warm DuckDB+Parquet/Cold Parquet SSD） / 治理机制（→A2） / | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-3803 | Temp Query P5 模板查询p5 | data/asset_index/_temp_query_p5.py,module,'' | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-4119 | Data Ingestion Process 数据接入进程 | A1迁移概念级进程P0 miniQMT连接iFind轮询事件总线不可崩溃 | D_MKT_DATA | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4229 | Market Data Pipeline 行情数据管道 | 跨域混居应迁出GOV属于D-DATA行情管道是数据域核心 | D_MKT_DATA | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4801 | Market Data Provider 行情数据提供商 | 外部契约-REST/WebSocket | D_MKT_DATA | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4869 | DDD Aggregate Root Lifecycle DDD聚合根与生命周期 | / 130~136 / DDD聚合根与生命周期 / 聚合根(MarketData/Instrument)生命周期管理+仓储接口+值对象(Bar/OHLCV/FinancialReport)+恢复演练验证+跨域保留归档策略协调+仿真回测数据生 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-4913 | PIT Consistency Guarantee PIT一致性保证 | / — / PIT一致性保证 / 三公理(时间不可逆+公告日约束+幸存者偏差)+三平面统一(训练AS OF JOIN+回测事件回放+推理Redis) / ✅ / | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-4914 | Bi-Temporal Modeling 双时态建模 | / — / 双时态建模 / system_time+business_time+HSTR+Delta / ✅ / | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-4915 | FWT Retrieval Augmented Diffusion FWT检索增强扩散 | A股数据增强 | D_MKT_DATA | harvest待评估（likely_new） |  |
| CAND-HARVEST-5067 | CQRS Command Query Responsibility Segregation CQRS命令查询职责分离 | /  7  / 🟡建议 / CQRS命令查询职责分离              /  ❌域文档  / Martin Fowler CQRS | D_MKT_DATA | harvest待评估（likely_new） |  |

## 复查时间表

> 按 next_review_date 升序。复查时重新过四问，触发信号命中则晋升到 depgraph 设计态。

| 下次复查 | 复查频率 | ID | 名称 | 域 | 状态 | 上次复查结论 |
|------|------|------|------|------|------|------|
| 2026-11-30 | quarterly | CAND-HARVEST-0053 | Data Ingestion & Management 数据接入与管理 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0252 | Connector 连接器 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-0253 | Normalizer 归一化器 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0254 | Storage 存储 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0255 | Real-time Feed Manager 实时管理器 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0256 | PIT Manager 管理器 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0257 | Data Permission Manager 管理器 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0259 | Tick Data Manager 管理器 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0260 | Data Observability Engine 可观测性引擎 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0261 | A-Share Intraday Data Manager 管理器 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0262 | A-Share Auction Data Manager 管理器 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0263 | A-Share Alt-Data Source Manager 管理器 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0264 | A-Share Order Flow Data Manager 管理器订单 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0265 | AkShare Data Source Adapter 适配器 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0298 | LLM API Unified Integration 集成 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0299 | M3 Code Generation Model Adapter 适配器模型 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0300 | M7 Deep Review Model Adapter 适配器模型视图 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0308 | M8-S01 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-0309 | M8-S02 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-0310 | M8-S03 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-0311 | M8-S04 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-0312 | M8-S05 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-0313 | M8-S06 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-0314 | M8-S07 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-0315 | M8-NEW-01 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0316 | M8-NEW-02 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0317 | M8-NEW-03 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0318 | M8-NEW-04 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0319 | M8-NEW-05 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0320 | M8-NEW-06 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0321 | M8-NEW-07 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0322 | M8-NEW-08 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0323 | M8-NEW-09 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0324 | M8-NEW-10 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0497 | miniQMT 主数据源 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0498 | iFind 补充数据源 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0499 | AkShare 免费备用数据源 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0500 | BaoStock 历史数据补充 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0501 | tushare 新闻快讯数据源 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0505 | L0 数据接入与预处理层 Data Ingestion & Preprocessing Layer | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0517 | Hot 热存储层 Redis | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0518 | Warm 温存储层 DuckDB+Parquet | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0519 | Cold 冷存储层 Parquet on SSD | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0521 | Data Observability 数据可观测性 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0522 | AI驱动异常检测 AI Anomaly Detection | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0524 | SQL AST解析器 SQL AST Parser | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0527 | PIT一致性 Point-in-Time Consistency | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0528 | 双时态建模 Bitemporal Modeling | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0529 | HSTR Snapshot+Delta 历史状态重构 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0530 | pit_consistency_test PIT验证测试框架 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0531 | DuckDB性能校准 DuckDB Performance Calibration | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0532 | miniQMT 主数据源 A股全市场 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0533 | iFind 补充数据源 盘后日线 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0534 | tushare 待开通数据源 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0535 | L0→L1 标准化流水线 L0→L1 Normalization Pipeline | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0536 | 格式校验 Schema Validation | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0571 | 三层存储架构 Three-tier Storage Architecture | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0572 | 容量规划 Capacity Planning | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0573 | 生命周期管理 Lifecycle Management | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0575 | Redis RDB+AOF双开 Redis RDB+AOF | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0576 | L0→L6全链路规格 L0→L6 Full-chain Spec | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0577 | 批流分离设计 Batch-Stream Separation | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0584 | 完整性 Completeness | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0585 | Financial Parser 财务报告解析器 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0586 | 准确性 Accuracy | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0587 | CrossSourceReconciler 跨源对账器 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0588 | Corporate Actions Processor 公司行为处理 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0589 | 一致性 Consistency | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0590 | Data Schema Registry 数据Schema注册表 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0592 | 及时性 Timeliness | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0594 | Macro Data Manager 宏观数据管理器 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0595 | 可用性 Availability | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0596 | SLA分级体系 SLA Tiered System | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0599 | Data Anomaly Alerter 数据异常告警器 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0601 | Trading Calendar Manager 交易日历管理 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0603 | 盘中实时监控 Intraday Real-time Monitoring | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0604 | 盘后一致性校验 Post-market Consistency Check | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0615 | WAL Checkpoint Monitor SQLite WAL检查点监控器 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0616 | CQRS分离 CQRS Separation | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0617 | 快照策略 Snapshot Strategy | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0618 | Point-in-Time一致性保证 PIT Consistency | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0619 | PIT三条公理 PIT Three Axioms | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0620 | 三平面统一 Three-plane Unification | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0621 | AS OF JOIN实现 AS OF JOIN Implementation | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0622 | Embargo期 Embargo Period | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0623 | PIT校验规则 PIT Validation Rules | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0629 | 可扩展性与演进性 Scalability & Evolution | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0630 | 数据源接入流程 Data Source Onboarding | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0631 | Schema演进 Schema Evolution | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0632 | 存储扩展路径 Storage Expansion Path | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0633 | 技术栈演进 Tech Stack Evolution | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0637 | Data Version Manager 数据版本管理 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0638 | Data Cost Tracker 数据成本追踪 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0639 | Data Retention Manager 数据保留策略 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0643 | DuckDB AS OF JOIN PIT Query Engine PIT查询引擎 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0644 | Multi-Source Data Priority Router 多数据源优先级路由器 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0645 | Data Source Health Monitor 数据源健康度监控器 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0721 | §29.4 时序数据库与分层存储架构 TSDB & Tiered Storage | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0722 | 4元组数据映射模型 4-tuple Data Mapping | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0723 | ClickHouse 列存时序数据库 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0724 | TimescaleDB PostgreSQL时序扩展 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0734 | PIT Consistency Guard PIT一致性守卫 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1227 | Financial Knowledge Graph 金融知识图谱 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1228 | Knowledge Distiller 知识蒸馏器 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1333 | Data Subscription Manager 数据订阅管理器 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1334 | Microstructure Analyzer 微观结构分析器 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1336 | Policy Event Factor Library 政策事件因子库 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1337 | Concept Factor Mapping Engine 概念因子映射引擎 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1338 | High-Frequency Signal Enhancer 高频信号增强器 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1340 | Text Sentiment Factor Extractor 文本情感因子提取器 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1341 | Pydantic V2 Code Generator Pydantic V2代码生成器 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1343 | Data Isolation Manager 数据隔离管理器 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1344 | Local File Auto-Parser 本地文件自动解析器 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-1345 | Web Data Crawler 网络数据爬虫 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1346 | Trading Decision Annotation Dataset 交易决策标注数据集 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1347 | Research Report Collector 研究报告采集器 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1348 | Training Dataset Manager 训练数据集管理器 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1350 | ClickHouse Analyzer ClickHouse分析器 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1351 | Unified Data Portal 统一数据门户 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1353 | Sector Factor Data Manager 板块因子数据管理器 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1354 | Incremental Update Engine 增量更新引擎 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1355 | Great Expectations Governance Great Expectations治理 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1359 | Sina+Tencent Real-Time 新浪+腾讯实时行情 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1360 | yfinance Adapter yfinance适配器 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1361 | Overseas Market Data Adapter 外盘数据适配器 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1362 | Vector DB Switch Manager 向量数据库切换管理器 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1803 | Dragon-Tiger List 龙虎榜 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2300 | AkShare AkShare数据适配器 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2606 | Industry Best Practice Benchmark 行业最佳实践对标 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2607 | Design Decision Summary 设计决策汇总 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2620 | Dual Temporal Modeling 双时态建模 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2622 | Point in Time Consistency Point-in-Time一致性保证 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2623 | Tiered Storage Architecture 分层存储架构 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3803 | Temp Query P5 模板查询p5 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4119 | Data Ingestion Process 数据接入进程 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4229 | Market Data Pipeline 行情数据管道 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4801 | Market Data Provider 行情数据提供商 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4869 | DDD Aggregate Root Lifecycle DDD聚合根与生命周期 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4913 | PIT Consistency Guarantee PIT一致性保证 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4914 | Bi-Temporal Modeling 双时态建模 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4915 | FWT Retrieval Augmented Diffusion FWT检索增强扩散 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-5067 | CQRS Command Query Responsibility Segregation CQRS命令查询职责分离 | D_MKT_DATA | 候选待评（candidate） | harvest待评估（likely_new） |
