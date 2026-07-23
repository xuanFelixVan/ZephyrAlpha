# 外部依赖图文档 — 数据库/数据架构设计审查报告

> **审查范围**: `tmp/external_review_docs/depgraph_docs/`（原路径 `D:\临时工作区\依赖图`）
> **审查重点**: 02-D-DATA-数据域.md、15-D-DATA-ENG-数据工程域.md、24-D-INFRA-RUNTIME-运行时基础设施域.md、25-D-INFRA-OPS-运维基础设施域.md、project-entity-depgraph.yaml、场内模块清单.csv
> **浏览范围**: 03-D-FACTOR、04-D-SIGNAL、11-D-RISK、12-D-ML-TRAIN、13-D-ML-SERVE、14-D-ALT-DATA、19-D-SIMULATION、20-D-RESEARCH、21-D-KNOWLEDGE、22-D-AUT-CORE、23-D-AUT-PERM、26-D-SECURITY、29-D-GOVERNANCE、30-D-OPS 等域的数据库相关段落
> **审查日期**: 2026-07-22
> **审查人**: AI-session (ext_01_depgraph_docs_review)
> **数据库实测**: ClickHouse 已连接实测（172.24.30.100）；PostgreSQL depgraph 已连接实测；SQLite governance.db 已连接实测

---

## 目录

- [§1 外部文档概览](#1-外部文档概览)
- [§2 数据库/数据架构设计规格提取](#2-数据库数据架构设计规格提取)
  - [§2.1 存储选型与分层架构](#21-存储选型与分层架构)
  - [§2.2 表设计与Schema](#22-表设计与schema)
  - [§2.3 数据流与管线](#23-数据流与管线)
  - [§2.4 接口契约](#24-接口契约)
  - [§2.5 数据治理与质量](#25-数据治理与质量)
  - [§2.6 备份与灾备](#26-备份与灾备)
  - [§2.7 事件存储与审计](#27-事件存储与审计)
- [§3 逐项落地核验](#3-逐项落地核验)
  - [§3.1 存储选型核验](#31-存储选型核验)
  - [§3.2 表设计核验](#32-表设计核验)
  - [§3.3 数据流核验](#33-数据流核验)
  - [§3.4 接口契约核验](#34-接口契约核验)
  - [§3.5 数据治理核验](#35-数据治理核验)
  - [§3.6 备份灾备核验](#36-备份灾备核验)
  - [§3.7 事件存储核验](#37-事件存储核验)
- [§4 更优设计识别](#4-更优设计识别)
- [§5 结论](#5-结论)

---

## §1 外部文档概览

外部文档是一套完整的 **30 域 DDD 架构设计**（00-总览与索引.md §1），包含 31 份域文件 + 1 份总览 + 1 份跨域交叉点分析 + 1 份项目级实体依赖图 YAML + 1 份场内模块清单 CSV。文档体系的核心特征：

| 维度 | 内容 |
|------|------|
| 架构范式 | DDD 业务域视角（非 TOGAF 分层），30 个域按价值链逻辑编号 01-31 |
| 数据架构核心 | D-DATA（数据域）+ D-DATA-ENG（数据工程域）双域协同——D-DATA 管"数据有什么"，D-DATA-ENG 管"数据怎么流"（15-D-DATA-ENG §0） |
| 存储选型 | 冷热三层：热(Redis <10ms) / 温(DuckDB+Parquet <1s) / 冷(归档Parquet <30s)（02-D-DATA §6 设计决策） |
| 依赖图 YAML | 28 个 domain 节点 + 138 条边（91 import_depends + 47 event_depends），scope=domain 粒度（project-entity-depgraph.yaml L7-21） |
| 场内模块清单 | 2435 个模块条目，格式为 `路径,类型,blueprint_id`（场内模块清单.csv L1-4） |
| 文档成熟度 | 所有域文件标注 `DRAFT`，成熟度从 `⬜ 空白` 到 `🔒 已开发` 不等（00-总览与索引.md §1） |

**关键定位差异**：外部文档是一套**场外草稿区**的设计文档（project-entity-depgraph.yaml L12: `generated_by: generate_depgraph_yaml.py (场外草稿区)`），其设计规格与项目实际实现之间存在显著差距。项目实际实现已在外部文档之后经历了多轮架构迭代（DuckDB→ClickHouse 迁移、治理体系建立等）。

---

## §2 数据库/数据架构设计规格提取

### §2.1 存储选型与分层架构

#### D1: 冷热三层存储架构

**来源**: 02-D-DATA-数据域.md §6 设计决策记录（2026-05-12）+ §1 子模块清单(03 Storage)

| 层级 | 存储 | 数据 | 访问延迟 | 淘汰策略 |
|:----:|------|------|:-------:|:-------:|
| 热 | Redis | 盘中Tick/实时因子值/交易信号/风控指标/持仓状态(~200MB) | <10ms | TTL管理 |
| 温 | DuckDB + Parquet | 日线/因子/信号历史/基本面/宏观(D:\zalpha\data\) | ~10ms | 无 |
| 冷 | 归档 Parquet（SSD） | 历史归档/事件历史/审计日志/快照历史/模型版本(E:\zalpha\archive\) | ~100ms | 无 |

**容量规划**: 热~200MB→1GB / 温~50GB→400GB / 冷~20GB→300GB（02-D-DATA §1 冷热分层详细设计）

**设计决策**: "冷热温三级存储架构"（02-D-DATA §6, 2026-05-12）

#### D2: 存储扩展路径（AUM驱动三阶段）

**来源**: 15-D-DATA-ENG-数据工程域.md §14.3 存储扩展路径

| 阶段 | AUM | 热存储 | 温存储 | 冷存储 |
|:----:|:----:|--------|--------|--------|
| 1 | <200万 | Redis (~200MB) | DuckDB + Parquet (D盘731GB) | Parquet on SSD (E盘931GB) |
| 2 | 200~500万 | Redis (~500MB) | ClickHouse (替代DuckDB) | Parquet on SSD |
| 3 | >500万 | Redis (~1GB) | ClickHouse + 分布式 | MinIO/NAS |

**升级触发条件**: DuckDB查询延迟>200ms 或 因子数量>500 或 AUM>200万（15-D-DATA-ENG §14.5 ADR-005）

#### D3: 技术栈演进矩阵

**来源**: 15-D-DATA-ENG-数据工程域.md §14.4

| 组件 | 阶段1 | 阶段2 | 阶段3 |
|------|:-----:|:-----:|:-----:|
| 热存储 | Redis | Redis | Redis Cluster |
| 温存储 | DuckDB+Parquet | ClickHouse | ClickHouse Cluster |
| 冷存储 | Parquet on SSD | Parquet on SSD | MinIO/NAS |
| 特征存储 | 自建(Parquet+Redis) | 自建+Feast YAML参考 | 自建/评估Feast迁移 |
| 事件存储 | Parquet append-only | Parquet+Kafka | Kafka+EventStoreDB |
| 血缘追踪 | SQLite | SQLite+OpenLineage | OpenLineage+Marquez |
| 质量检查 | 自建 | 自建+Great Expectations | Great Expectations |
| 向量存储 | ChromaDB+Faiss GPU(双轨) | ChromaDB+Faiss GPU+Qdrant评估 | Qdrant/Chroma(独立服务) |

#### D4: 双数据库文件隔离

**来源**: 02-D-DATA-数据域.md §6 设计决策（2026-05-12）+ ADR-DAT-004

- `zalpha_metadata.db`（治理数据，SQLite WAL模式）
- `zalpha_market_data.db`（行情元数据，SQLite WAL模式）
- 隔离理由："行情写入频率压垮WAL checkpoint影响治理数据；备份策略不同"

### §2.2 表设计与Schema

#### D5: CTR-001 NormalizedMarketData 契约

**来源**: 02-D-DATA-数据域.md §3 CTR-001接口定义

```python
@dataclass(frozen=True)
class NormalizedMarketData:
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    amount: float
    frequency: str
    source: str
    quality_score: float
    asof_ts: datetime
    trace_id: str
```

**定位**: "全系统唯一数据契约"（02-D-DATA §6），Pydantic V2 frozen dataclass 实现

#### D6: Feature Store Schema（离线+在线双存储）

**来源**: 03-D-FACTOR-因子域.md §11 特征存储架构

**离线存储 Parquet Schema**: 因子值窄表（因子ID/标的/时间戳/值/版本/计算时间）
**在线存储 Redis**: Key=`feature:{symbol}`, Field=`{factor_name}:{version}`, Value=`{factor_value}`, TTL=盘中无/盘后3600s
**Feature Registry**: SQLite 元数据（四维索引：因子名/版本/依赖/状态）

**设计决策**: "窄表存储因子值——Schema稳定，新增因子不改变表结构"（03-D-FACTOR DD-P3-01）

#### D7: Feature Store 接口契约

**来源**: 02-D-DATA-数据域.md §1 Feature Store 接口

| 接口 | 签名 | 说明 |
|------|------|------|
| get_features | `(feature_names, symbols, start, end, as_of=None) → pd.DataFrame` | ML训练和推理共享特征数据 |
| register_feature | `(feature_name, description, compute_logic_ref) → None` | 注册新特征 |
| get_feature_lineage | `(feature_name) → list[dict]` | 查询特征血缘 |

**特征生命周期**: PROPOSED→EXPERIMENTAL→PRODUCTION→DORMANT→REACTIVATED→DEPRECATED→RETIRED（02-D-DATA §1）

#### D8: Event Store 设计（CQRS + Event Sourcing）

**来源**: 02-D-DATA-数据域.md §6 设计决策（2026-05-12）

- 写端：Parquet 追加写入（不可变序列）
- 读端：DuckDB 视图（CQRS 读端）
- 日快照 + 5分钟增量快照
- 幂等写入
- 设计决策："Event Store+CQRS——写端Parquet追加+读端DuckDB视图+最终一致性；事件不可变序列支持故障恢复/审计/回测"

#### D9: UFL 确定性事实层

**来源**: 02-D-DATA-数据域.md §6 设计决策（2026-05-12）

- Feature Store 子集 `is_deterministic=True`
- 财务/交易/宏观数据不含 ML 预测
- 追加式不可修改
- 对标 VeNRA

### §2.3 数据流与管线

#### D10: 批流分离设计

**来源**: 15-D-DATA-ENG-数据工程域.md §13.2

| 维度 | 流式路径(盘中) | 批量路径(盘后) |
|------|:-------------:|:-------------:|
| 触发 | miniQMT 3秒Tick | iFind盘后数据(15:00-15:30) |
| 写入 | Redis Hot (<10ms) | Parquet Warm (DuckDB) |
| 计算 | D-FACTOR Engine增量 (<5秒) | D-FACTOR Engine批量 (全量重算) |
| 延迟预算 | Tick→信号 ≤15秒 | 15:30-17:00 (90分钟) |
| 存储 | Redis+Parquet异步追加 | Parquet+Feature Store Offline |
| 质量检查 | 实时监控(延迟/缺失/心跳) | 全量校验(对账/Quality Gate) |

#### D11: 新鲜度检查点体系（CP-01~CP-07）

**来源**: 15-D-DATA-ENG-数据工程域.md §13.3

| 检查点 | 数据品类 | 新鲜度SLO | 延迟预算 | 超限动作 |
|--------|---------|:---------:|:-------:|---------|
| CP-01 | miniQMT Tick→Redis | ≤3秒 | <10ms | P0告警+暂停信号生成 |
| CP-02 | Redis因子值→信号 | ≤5秒 | <5ms | P1告警+使用上一批次 |
| CP-03 | 信号→决策 | ≤10秒 | <100ms | P0告警+暂停新开仓 |
| CP-04 | 决策→风控→执行 | ≤1秒 | <1秒 | P0告警+触发保命轨 |
| CP-05 | iFind盘后数据→Parquet | ≤30分钟 | 15:00-15:30 | P1告警+使用T-2数据 |
| CP-06 | 因子批量计算→Feature Store | ≤2小时 | 15:30-17:00 | P1告警+推迟训练任务 |
| CP-07 | 跨源对账完成 | ≤2小时 | 15:30-17:00 | P1告警+标记差异 |

#### D12: L0→L6 全链路数据流

**来源**: 15-D-DATA-ENG-数据工程域.md §13.1

从 L0(miniQMT Tick) → L1(CTR-001) → L2(因子/信号/市场状态/知识图谱) → L3(策略决策) → L3.5(仓位裁决) → L4(风控审批) → 执行 → L5(闭环优化) → L6(可解释性)，每段有明确延迟预算和存储层分配。

#### D13: D-DATA-ENG 骨架6子模块

**来源**: 15-D-DATA-ENG-数据工程域.md §1

| ID | 名称 | 职责 | 优先级 |
|----|------|------|:------:|
| D-DATA-ENG-01 | ETLPipeline | ETL管线+增量同步+断点续传 | P0 |
| D-DATA-ENG-02 | PipelineOrchestrator | 管线编排+DAG调度+依赖管理+重试 | P0 |
| D-DATA-ENG-03 | FeatureStore | PIT查询+特征版本+特征服务API+在线/离线存储 | P0 |
| D-DATA-ENG-04 | DataQualityMonitor | 6维质量评分+Great Expectations+异常检测+质量门禁 | P1 |
| D-DATA-ENG-05 | DataLineageTracker | 端到端血缘+列级溯源+变换算子注册+影响分析 | P1 |
| D-DATA-ENG-06 | StreamProcessingEngine | 实时计算+窗口聚合+事件时间对齐+水位线+背压控制 | P1 |

### §2.4 接口契约

#### D14: CTR-001 数据契约

详见 §2.2 D5。契约实现要求：Pydantic V2 frozen dataclass（02-D-DATA §6, 2026-05-12）

#### D15: Feature Store 接口

详见 §2.2 D7。

#### D16: 数据目录结构

**来源**: 02-D-DATA-数据域.md §1 数据目录结构

```
data/
├── zalpha_metadata.db      ← 治理数据（SQLite WAL）
├── zalpha_market_data.db   ← 行情元数据（SQLite WAL）
├── market_data/            ← 行情数据文件
│   ├── daily/              ← 日线 Parquet（按年分区）
│   ├── intraday/           ← 分钟线 Parquet（按月分区）
│   └── cache/              ← 热数据内存映射
├── events/                 ← Event Store（Parquet追加写入）
├── features/               ← Feature Store（离线Parquet+Registry SQLite）
└── shard_00/               ← 现有分片
E:/backup/                  ← E盘双副本备份
├── redis/                  ← Redis AOF+RDB
├── data/parquet/           ← Parquet增量备份
├── data/models/            ← 模型文件备份
└── integration/baselines/  ← 契约基线快照
```

### §2.5 数据治理与质量

#### D17: Quality Gate 四级检查体系

**来源**: 02-D-DATA-数据域.md §1 Quality Gate 分级

| 级别 | 检查项 | 通过条件 | 不通过动作 |
|:----:|--------|---------|-----------|
| L1 格式检查 | 字段完整性/类型/null率 | null率 < 5% | 拒绝入库 |
| L2 逻辑检查 | OHLC关系/涨跌幅范围/停牌标记 | 无逻辑矛盾 | 标记可疑 + 告警 |
| L3 统计检查 | 异常值检测/分布漂移 | Z-score < 4σ | 标记异常 + 降权使用 |
| L4 血缘检查 | 数据来源可追溯 | 有 CTR-TRACE-001 | 拒绝无血缘数据 |

#### D18: 数据质量6维评分

**来源**: 02-D-DATA-数据域.md §1 子模块清单(10 Data Quality Scorer)

完整性/准确性/一致性/时效性/唯一性/有效性 + BCBS 239 数据聚合原则（准确性/完整性/时效性/适应性/独立性）

#### D19: 数据血缘追踪

**来源**: 02-D-DATA-数据域.md §1 子模块清单(05 Data Lineage Tracker) + 15-D-DATA-ENG §11.1

- OpenLineage 标准对接
- 追踪范围：数据源→特征→因子→信号→策略→交易→PnL 全链路
- 列级血缘（SQL AST 解析器）
- 影响分析引擎
- 内容指纹（SHA-256）

#### D20: Schema 演进策略

**来源**: 15-D-DATA-ENG-数据工程域.md §14.2

| 演进类型 | 处理方式 | 向后兼容 |
|---------|---------|:-------:|
| 新增列 | Parquet天然支持新增列 | ✅ |
| 删除列 | 保留列但标记deprecated | ✅ |
| 修改列类型 | 新增列+迁移+旧列标记deprecated | ✅ |
| 重命名列 | 新增列+映射+旧列保留 | ✅ |
| Schema版本 | factor_version字段区分 | ✅ |

核心原则："Schema演进必须向后兼容。破坏性变更通过新增列+版本号实现，旧列保留≥1年"

#### D21: 数据版本管理

**来源**: 02-D-DATA-数据域.md §1 子模块清单(11 Data Version Manager)

- 版本快照（时间戳+哈希）
- 分支/标签
- 增量 Delta 存储
- 版本回滚
- PIT 版本绑定
- 知识版本管理（Git-like 变更 diff + 回退生效指针）

### §2.6 备份与灾备

#### D22: RTO/RPO 分级表

**来源**: 25-D-INFRA-OPS-运维基础设施域.md §8.1.1

| 数据/服务等级 | RTO目标 | RPO目标 | 数据内容 | 恢复策略 |
|-------------|:-------:|:-------:|---------|---------|
| L1 交易核心 | <5min | ≤1s | 持仓/订单/账户/风控状态 | Redis AOF + D→E双副本 |
| L2 策略状态 | <10min | ≤1min | 策略状态机/信号缓存/市场状态 | Redis RDB + 配置文件 |
| L3 因子数据 | <30min | ≤5min | 因子值/因子元数据 | Parquet文件双副本 |
| L4 模型文件 | <60min | ≤1hour | 模型权重/配置 | 文件双副本 |
| L5 历史数据 | <120min | ≤1hour | 行情历史/回测结果 | Parquet文件双副本 |
| L6 日志数据 | <240min | ≤24hour | 系统日志/审计日志 | 日志归档 |

#### D23: D→E 双副本策略

**来源**: 25-D-INFRA-OPS §8.1.3 + 15-D-DATA-ENG §8.2

| 数据类型 | 同步方式 | 同步频率 | 一致性校验 | 保留策略 |
|---------|---------|:--------:|-----------|---------|
| Redis AOF | 文件复制 | 实时(每秒fsync) | 文件MD5 | 保留最近7天 |
| Redis RDB | 文件复制 | 每小时 | 文件MD5 | 保留最近30天 |
| Parquet数据 | robocopy增量 | 每小时 | 文件大小+行数 | 保留最近90天 |
| 模型文件 | robocopy增量 | 每小时 | 文件MD5 | 保留最近10个版本 |
| 配置文件 | robocopy镜像 | 每次变更 | 文件MD5 | 保留最近30个版本 |
| 日志文件 | robocopy增量 | 每2小时 | 文件大小 | 保留7年(合规) |

#### D24: 备份黄金律 3-2-1-1-0

**来源**: 25-D-INFRA-OPS §8.1.4 + 15-D-DATA-ENG §8.2

- **3** 份副本：D:盘(生产) + E:盘(本地副本) + Git(配置第三副本)
- **2** 种介质：⚠️部分满足（D:SSD+E:SSD为同介质）
- **1** 份离线：❌不能建（约束二单机部署）
- **1** 份不可变：✅ E:盘关键目录设置Windows只读ACL
- **0** 错误：✅ 灾备演练验证

### §2.7 事件存储与审计

#### D25: 审计链哈希链 + Merkle 树

**来源**: 02-D-DATA-数据域.md §1 子模块清单(28 Data Access Auditor) + 10-D-REPORTING-报告域.md

- L1: SHA-256 哈希链事件完整性
- L2: Merkle 树集合完整性（每日/周/月批量证明）
- 5类日志分级存储：交易≥7年/决策≥3年/合规≥7年/模型≥5年/系统≥1年
- 决策溯源9字段标准

#### D26: Crypto-Shredding

**来源**: 02-D-DATA-数据域.md §7.2

解决 GDPR 被遗忘权与 MiFID II 记录留存的监管悖论——每个数据主体用独立密钥加密个人数据，收到被遗忘权请求时销毁对应密钥。当前适用性：单人使用不触发 GDPR，GATE-004/GATE-006 激活后需要。

---

## §3 逐项落地核验

### §3.1 存储选型核验

| # | 设计项 | 判定 | 证据 |
|---|--------|:----:|------|
| D1-热层 | Redis 热缓存 (<10ms) | ❌未落地 | `src/zephyr/infrastructure/database_service.py` L33: "Redis H1 热缓存为预留接口（抛 NotImplementedError），待 P2 实盘需求触发施工"。全项目 `grep "import redis"` 无实际 Redis 客户端导入 |
| D1-温层 | DuckDB + Parquet 温层 | 🟡部分落地 | DuckDB 已被 ClickHouse 替代——`database_service.py` L35: "market.duckdb（旧 DuckDB 业务时序库）已于 2026-07-05 删除"。ClickHouse c1_market 已部署 77 张表（实测 `system.tables`），kline_daily 34,664,504 行，tick_data 14,324,240,136 行。但 data/ 目录下无 .parquet 文件（`find data -name "*.parquet"` 结果为空） |
| D1-冷层 | 归档 Parquet 冷层 | ❌未落地 | data/ 目录下无 Parquet 归档文件。data/audit_trail/ 下有 cold/warm/hot 子目录但非 Parquet 格式 |
| D2 | 存储扩展路径（AUM驱动） | 🟡部分落地 | 阶段1设计为 DuckDB+Parquet，实际已提前跳到阶段2的 ClickHouse（2026-07-01 部署，INFRA-DB-006）。但扩展路径的触发条件（AUM>200万）和后续阶段未实现 |
| D3 | 技术栈演进矩阵 | 🟡部分落地 | ClickHouse 已替代 DuckDB（✅），ChromaDB+Faiss GPU 双轨已采用（`src/zephyr/integration/vector_memory/faiss_collection_manager.py`）。但 Feast/Great Expectations/OpenLineage/Kafka/EventStoreDB 均未实现 |
| D4 | 双数据库文件隔离 | 🟡部分落地 | governance.db 存在（SQLite WAL，实测 38 张表），但名称为 governance.db 而非 zalpha_metadata.db。zalpha_market_data.db 不存在。隔离原则已实现（治理 vs 业务分离），但文件命名不同 |

### §3.2 表设计核验

| # | 设计项 | 判定 | 证据 |
|---|--------|:----:|------|
| D5 | CTR-001 NormalizedMarketData | 🟡部分落地 | 无统一的 frozen dataclass 契约类。`src/zephyr/governance/data_governance/akshare_provider.py` 有类似数据结构但非统一契约。CTR-001 作为概念在跨层契约治理中存在（`src/zephyr/governance/audit/cross_layer_contract_signature_reconciler.py`），但无 Pydantic V2 frozen dataclass 实现 |
| D6 | Feature Store Schema | ❌未落地 | ClickHouse c2_indicator 数据库为空（实测 `system.tables WHERE database='c2_indicator'` 返回空）。无因子值窄表、无 Feature Registry SQLite。因子计算结果不持久化到 Feature Store |
| D7 | Feature Store 接口 | ❌未落地 | 全项目 `grep "feature_store\|FeatureStore"` 无实现代码。get_features()/register_feature()/get_feature_lineage() 接口不存在 |
| D8 | Event Store (CQRS) | 🟡部分落地 | `src/zephyr/infrastructure/event_store.py` 实现了 EventStore 类，但基于 SQLite（非 Parquet+CQRS）。EVENT_STORE_SCHEMA 定义了 events 表（id/event_id/timestamp/level/component/event_type/payload/metadata/checksum），有 checksum 字段但非 CQRS 读写分离架构 |
| D9 | UFL 确定性事实层 | 🟡部分落地 | `src/zephyr/gov_audit/replay_engine.py` L52 有 `is_deterministic` 字段，L148 有 `is_deterministic=True`。但无完整的 UFL 层实现（非 Feature Store 子集，无追加式不可修改保证） |

### §3.3 数据流核验

| # | 设计项 | 判定 | 证据 |
|---|--------|:----:|------|
| D10 | 批流分离设计 | 🟡部分落地 | 盘后批量已实现：`src/zephyr/data/scheduler.py` 实现 APScheduler 5 档 cron 时段调度（盘后日K 16:30/盘后资金 17:00/盘后事件 18:00/周末财务 周六10:00/静态数据 月初09:00），tasks.yaml 配置 129 个任务。但盘中流式路径（miniQMT 3秒Tick→Redis→信号≤15秒）未实现——`src/zephyr/data/tick_subscriber.py` 存在但依赖 Redis 作为热层 |
| D11 | 新鲜度检查点 CP-01~CP-07 | ❌未落地 | 无 CP-01~CP-07 检查点实现。`src/zephyr/data/metrics.py` 有 IntegratorMetrics 但非新鲜度 SLO 检查点体系 |
| D12 | L0→L6 全链路数据流 | 🟡部分落地 | L0→L1 已实现（数据源→ClickHouse）。L1→L2 因子计算有部分实现（`src/zephyr/factor/`）。L2→L3→L4→L5→L6 链路未完整实现（无盘中实时决策链路） |
| D13 | D-DATA-ENG 骨架6子模块 | ❌未落地 | `src/zephyr/data_eng/` 目录下仅有 `__init__.py` 空文件（实测 models/、services/、core/、api/、infrastructure/ 子目录全部为空）。6 个骨架子模块（ETLPipeline/PipelineOrchestrator/FeatureStore/DataQualityMonitor/DataLineageTracker/StreamProcessingEngine）均无实现 |

### §3.4 接口契约核验

| # | 设计项 | 判定 | 证据 |
|---|--------|:----:|------|
| D14 | CTR-001 Pydantic V2 frozen | ❌未落地 | 无 Pydantic V2 frozen dataclass 的 CTR-001 实现。项目使用标准 Python dataclass 而非 Pydantic V2 |
| D15 | Feature Store 接口 | ❌未落地 | 同 D7 |
| D16 | 数据目录结构 | 🟡部分落地 | data/ 目录存在且有 governance.db、integrator_jobs.db、integrator_progress.db。但无 market_data/、events/、features/ 子目录（外部文档设计的 Parquet 目录结构），无 E:/backup/ 双副本结构 |

### §3.5 数据治理核验

| # | 设计项 | 判定 | 证据 |
|---|--------|:----:|------|
| D17 | Quality Gate 四级检查 | 🟡部分落地 | `src/zephyr/gov_enforcement/rule_enforcement/quality_gate.py` 有 QualityReport 和 DataQualityGate ABC。`src/zephyr/gov_enforcement/rule_enforcement/default_quality_gate.py` 有 DefaultQualityGate 实现。但无 L1格式→L2逻辑→L3统计→L4血缘的四级分级体系 |
| D18 | 数据质量6维评分 | 🟡部分落地 | `src/zephyr/feedback_loop/collectors/data_quality_validator.py` 有 DataQualityValidator。`src/zephyr/feedback_loop/gates/data_quality_gate.py` 有 DataQualityGate。但无完整的 6 维评分体系（完整性/准确性/一致性/时效性/唯一性/有效性）和 BCBS 239 原则实现 |
| D19 | 数据血缘追踪 | ❌未落地 | 无 OpenLineage 标准对接。无列级血缘（SQL AST 解析器）。无全链路追踪（数据源→特征→因子→信号→策略→交易→PnL）。depgraph 有模块级依赖追踪但非数据级血缘 |
| D20 | Schema 演进策略 | 🟡部分落地 | `src/zephyr/data/table_registry.py` 实现了 TableRegistry 消费层（business_data_categories.yaml 为表名/品类唯一真源，106 条品类记录）。但无完整的 Schema 演进策略（新增列/删除列/修改列类型/重命名列的处理规则） |
| D21 | 数据版本管理 | ❌未落地 | 无版本快照（时间戳+哈希）、无分支/标签、无增量 Delta 存储、无版本回滚、无 PIT 版本绑定 |

### §3.6 备份灾备核验

| # | 设计项 | 判定 | 证据 |
|---|--------|:----:|------|
| D22 | RTO/RPO 分级表 | 🟡部分落地 | `src/zephyr/infrastructure/sla/sla_monitor.py` 有 SLAMonitor 实现。`config/sla_targets.yaml` 存在。但无 L1~L6 六级 RTO/RPO 分级表，无交易核心 RPO≤1s 的硬约束实现 |
| D23 | D→E 双副本策略 | ❌未落地 | data/databases/backups/ 目录仅有 depgraph_backup_20260721_220004.sql 一个文件。无 robocopy 增量同步脚本，无 E: 盘备份目录结构，无 Redis AOF/RDB 备份 |
| D24 | 备份黄金律 3-2-1-1-0 | ❌未落地 | 无 3 份副本机制，无 E: 盘只读 ACL 设置，无灾备演练计划（25-D-INFRA-OPS §8.1.7 的月度/季度/半年演练） |

### §3.7 事件存储核验

| # | 设计项 | 判定 | 证据 |
|---|--------|:----:|------|
| D25 | 审计链哈希链+Merkle树 | 🟡部分落地 | `src/zephyr/infrastructure/event_store.py` 有 checksum 字段（SHA-256）。data/audit_trail/ 目录有 merkle_batches/ 和 merkle_hourly/ 子目录，表明 Merkle 树实现存在。但无完整的 5 类日志分级存储（交易≥7年/决策≥3年/合规≥7年/模型≥5年/系统≥1年）和决策溯源 9 字段标准 |
| D26 | Crypto-Shredding | ❌未落地 | 无日志独立加密基础设施，无密钥销毁预留接口。外部文档也标注"❌不能建"（GATE-004/GATE-006 激活后才需要） |

---

## §4 更优设计识别

以下外部文档中的设计**在当前项目实现中没有对应物**，且对系统有明确价值。按价值高低排序：

### 4.1 Feature Store（高价值缺口）

**外部设计**: 02-D-DATA §1 + 03-D-FACTOR §11 + 15-D-DATA-ENG §9.1

- 离线 Parquet（PIT/训练/回测，~100ms）+ 在线 Redis（实时查询 <5ms）+ Feature Registry（SQLite 元数据）
- PIT 正确性保证：`as_of` 参数通过 DuckDB AS OF JOIN 实现
- 特征生命周期管理（PROPOSED→EXPERIMENTAL→PRODUCTION→...→RETIRED）
- 训练-服务一致性：回测 Sharpe 与模拟盘 Sharpe 偏差 <15%

**当前状态**: ❌ 完全未实现。ClickHouse c2_indicator 为空库，无因子值持久化机制。

**优在哪**: 当前项目因子计算结果不持久化，每次回测/推理都需重新计算。Feature Store 可以：
1. 消除训练-服务偏差（15-25% 的生产 bug 来源，15-D-DATA-ENG §9.1）
2. 支持增量因子计算（避免全量重算）
3. 提供 PIT 正确的历史特征快照
4. 因子血缘追踪（从哪个因子/数据源计算）

**但需注意**: 外部设计基于 DuckDB+Parquet+Redis，项目已迁移到 ClickHouse。Feature Store 的存储引擎需要重新选型（ClickHouse 可替代 DuckDB 作为离线存储，但 Redis 在线存储仍需部署）。

### 4.2 数据血缘追踪（高价值缺口）

**外部设计**: 02-D-DATA §1(05 Data Lineage Tracker) + 15-D-DATA-ENG §11.1

- OpenLineage 标准对接
- 全链路追踪：数据源→特征→因子→信号→策略→交易→PnL
- 列级血缘（SQL AST 解析器）
- 影响分析引擎（数据源变更→自动评估受影响的下游模块）
- 内容指纹（SHA-256）

**当前状态**: ❌ 完全未实现。depgraph 有模块级依赖追踪但非数据级血缘。

**优在哪**: 当前项目无法回答"这个因子值是从哪些原始数据计算的？"和"如果这个数据源出问题，哪些下游模块受影响？"。血缘追踪是数据治理的核心能力，也是外部文档 Quality Gate L4 的前置条件。

### 4.3 Quality Gate 四级检查体系（中高价值缺口）

**外部设计**: 02-D-DATA §1 Quality Gate 分级

- L1 格式检查 → L2 逻辑检查 → L3 统计检查 → L4 血缘检查
- 贯穿 Connector→Normalizer→Storage 全流程
- 关键路径 ≤1ms / 非关键 ≤10ms / 默认阻断

**当前状态**: 🟡 有基础质量检查（QualityReport/DataQualityGate ABC/DefaultQualityGate），但无四级分级体系。

**优在哪**: 四级分级提供了渐进式数据质量保障——L1 快速过滤格式错误，L2 检查业务逻辑，L3 统计异常检测，L4 血缘追溯。当前项目仅有一层质量检查，无法区分"格式错误"（应拒绝入库）和"统计异常"（应降权使用）。

### 4.4 数据版本管理（中价值缺口）

**外部设计**: 02-D-DATA §1(11 Data Version Manager)

- 版本快照（时间戳+哈希）
- 增量 Delta 存储
- PIT 版本绑定
- 知识版本管理（Git-like 变更 diff + 回退生效指针）

**当前状态**: ❌ 未实现。

**优在哪**: 数据版本管理是回测可复现性的基础——"用哪个版本的数据做的回测？"当前项目无法回答。ClickHouse ReplacingMergeTree 提供了行级去重但非版本管理。

### 4.5 新鲜度检查点体系（中价值缺口）

**外部设计**: 15-D-DATA-ENG §13.3 CP-01~CP-07

7 个检查点覆盖从 Tick→Redis→因子→信号→决策→执行→盘后批量→跨源对账的全链路新鲜度 SLO。

**当前状态**: ❌ 未实现。有 IntegratorMetrics 但非 SLO 检查点体系。

**优在哪**: 数据新鲜度是量化系统的生命线——"数据多旧了？"当前项目无法系统性回答。CP 体系提供了数据流管道中的质量检查点位置和延迟预算。

### 4.6 D→E 双副本自动备份（中价值缺口）

**外部设计**: 25-D-INFRA-OPS §8.1.3 + 15-D-DATA-ENG §8.2

- robocopy 增量同步（每小时）
- 文件 MD5 一致性校验
- 分级保留策略

**当前状态**: ❌ 未实现。仅有一个手动 depgraph 备份。

**优在哪**: 当前项目数据全部在 D: 盘，单点故障风险高。ClickHouse tick_data 有 143 亿行，一旦磁盘故障恢复困难。

### 4.7 UFL 确定性事实层（中低价值）

**外部设计**: 02-D-DATA §6 设计决策

- Feature Store 子集 is_deterministic=True
- 财务/交易/宏观数据不含 ML 预测
- 追加式不可修改

**当前状态**: 🟡 有雏形（replay_engine.py 的 is_deterministic 字段）。

**优在哪**: 区分"确定性事实"和"ML 预测"是数据治理的重要概念，防止 ML 预测污染基础事实数据。

### 4.8 CTR-001 统一数据契约（中低价值）

**外部设计**: 02-D-DATA §3

- Pydantic V2 frozen dataclass
- 全系统唯一数据契约
- 含 quality_score/asof_ts/trace_id 字段

**当前状态**: 🟡 有概念但无统一实现。

**优在哪**: 统一契约消除了"每个 Provider 返回不同格式"的问题，是数据标准化的基础。但项目通过 ClickHouse 表结构隐式实现了类似效果（所有数据都写入统一 Schema 的表），因此价值相对较低。

---

## §5 结论

### 总体判定

外部文档中的数据库/数据架构设计**远未全部落地**。在 26 项提取的设计规格中：

| 判定 | 数量 | 占比 |
|:----:|:----:|:----:|
| ✅已落地 | 0 | 0% |
| 🟡部分落地 | 15 | 58% |
| ❌未落地 | 11 | 42% |

### 核心发现

1. **存储引擎已完成 DuckDB→ClickHouse 迁移，但外部设计的配套机制未跟进**。ClickHouse c1_market（77 表）+ c3_fundamental（23 表）已替代外部设计的 DuckDB+Parquet 温层，且数据量已达生产级（kline_daily 3460 万行，tick_data 143 亿行）。但外部设计围绕 DuckDB+Parquet 构建的 Feature Store、Event Store CQRS、数据版本管理等配套机制完全未实现。

2. **数据工程域（D-DATA-ENG）是最大缺口**。`src/zephyr/data_eng/` 目录完全为空（仅有 `__init__.py`），外部设计的 6 个骨架子模块（ETLPipeline/PipelineOrchestrator/FeatureStore/DataQualityMonitor/DataLineageTracker/StreamProcessingEngine）和 5 个增强子模块均无实现。数据源集成器（MOD-L00-004）在 `src/zephyr/data/` 下实现了 ETL 管线的核心能力（Provider 抽象 + APScheduler 调度 + 断点续传 + 告警），但这是作为 D-DATA 域的连接器实现的，而非独立的 D-DATA-ENG 域。

3. **Redis 热层完全缺失，限制了盘中实时能力**。外部设计的冷热三层架构中，Redis 热层是盘中实时计算的基础（<10ms 延迟）。当前 Redis 仅为预留接口（NotImplementedError），导致 tick_subscriber.py 的实时 Tick 推送、因子实时计算、信号实时生成等盘中链路无法实现。项目当前定位为"回测数据库"（非实盘），因此这一缺口在当前阶段影响有限。

4. **ClickHouse 替代 DuckDB 是正确决策，但需注意外部设计中 DuckDB 特有的能力在 ClickHouse 中的映射**。外部设计大量使用 DuckDB AS OF JOIN 实现 PIT 查询（02-D-DATA §5 P1 就绪条件、03-D-FACTOR §11.2、15-D-DATA-ENG §9.1）。ClickHouse 不原生支持 AS OF JOIN，需要自行实现 PIT 语义（当前 backtest/core/pit_manager.py 已用纯 pandas 实现，但未与 ClickHouse 集成）。

5. **项目治理体系（depgraph/governance.db/commit gates）远超外部文档设计，但在业务数据治理（血缘/质量分级/版本管理）方面落后于外部设计**。项目已建立了完善的代码治理体系（depgraph 5506 节点/7592 边、38 张治理表、commit gates），但业务数据治理仍停留在基础水平。

### 高价值未落地设计缺口（建议优先级排序）

| 优先级 | 缺口 | 理由 |
|:------:|------|------|
| P0 | Feature Store（D6/D7） | 因子值不持久化是回测可复现性和训练-服务一致性的根本缺陷 |
| P1 | 数据血缘追踪（D19） | 无法追溯数据来源和影响范围，是数据治理的核心能力 |
| P1 | Quality Gate 四级体系（D17） | 数据质量保障需要从单层检查升级为分级检查 |
| P2 | 数据版本管理（D21） | 回测可复现性需要"用哪个版本的数据"的记录 |
| P2 | D→E 双副本备份（D23） | 单点故障风险，143 亿行 tick 数据无自动备份 |
| P3 | 新鲜度检查点体系（D11） | 盘中实时监控的前置条件（当前回测阶段可延后） |
| P3 | UFL 确定性事实层（D9） | 区分事实与预测，防止数据污染 |

### 外部文档 vs 项目实现的架构哲学差异

| 维度 | 外部文档设计 | 项目实际实现 |
|------|------------|------------|
| 存储引擎 | DuckDB+Parquet（嵌入式分析） | ClickHouse（列式数据库） |
| 热层 | Redis（内存缓存） | 无（预留接口） |
| 架构风格 | DDD 30 域完整设计 | 按需实现，治理优先 |
| 数据契约 | Pydantic V2 frozen dataclass | ClickHouse 表结构隐式契约 |
| 质量保障 | Quality Gate 四级贯穿 | 基础质量检查 + commit gates |
| 血缘追踪 | OpenLineage 全链路 | depgraph 模块级依赖 |
| 备份策略 | D→E 双副本 + 3-2-1-1-0 | 手动 depgraph 备份 |
| 事件存储 | Parquet CQRS | SQLite EventStore |

外部文档是一套**理想态的完整设计**，覆盖了大量当前阶段（个人单用户、回测为主、无实盘）尚不需要的能力。项目实现采取了**务实路线**——优先建立治理体系和核心数据采集能力，延后了 Feature Store、血缘追踪、实时监控等高级能力。这种"治理先行、业务跟随"的策略与外部文档的"全量设计、分阶段实施"策略在方向上一致，但在 Feature Store 和数据血缘两个 P0/P1 级能力上存在明显缺口，建议在回测引擎进入高频迭代阶段前补齐。

---

*本报告基于 2026-07-22 的代码状态和数据库实测。ClickHouse (172.24.30.100) 和 PostgreSQL depgraph 已连接实测，SQLite governance.db 已连接实测。Redis 未部署，DuckDB 已删除。*
