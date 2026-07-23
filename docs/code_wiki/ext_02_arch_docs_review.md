# ext_02 · 外部架构文档数据库设计审查报告（架构图系列 · 数据架构.md 深读）

> **审查对象**：`tmp/external_review_docs/arch_docs/`（原路径 `D:\临时工作区\架构图`），主审 `数据架构.md`（v6.0，4371 行，2026-05-25/26 最后更新），辅审其余 9 份架构文档的数据库相关段落。`test_diagram/` 与 `test_output/` 为测试产物，按任务要求跳过。
> **审查方式**：只读静态审查 + 数据库只读实测（ClickHouse TCP/HTTP 与 PostgreSQL 均可连通，已实测；未执行任何写入/破坏性操作）。
> **审查日期**：2026-07-22

---

## 目录

- [1. 数据架构.md 数据库设计规格提取](#1-数据架构md-数据库设计规格提取)
- [2. 落地状态逐条核验](#2-落地状态逐条核验)
- [3. 关键分歧：文档 v6.0 选 DuckDB，项目落地 ClickHouse](#3-关键分歧文档-v60-选-duckdb项目落地-clickhouse)
- [4. 文档优于项目现有实现的设计点](#4-文档优于项目现有实现的设计点)
- [5. 其余 9 份文档数据库相关段落摘要](#5-其余-9-份文档数据库相关段落摘要)
- [6. 结论：落地缺口判定](#6-结论落地缺口判定)

---

## 1. 数据架构.md 数据库设计规格提取

### 1.1 数据源层（§0.1 / 第一部分 §1.1）

文档定义 5+2 个数据源（`数据架构.md` L49-61、L314-366）：

| 数据源 | 定位 | 文档状态 |
|--------|------|---------|
| miniQMT | 唯一高频主源，3 秒 Tick，A股全市场 ~5000 只 + ETF/LOF/可转债 + REITs + 指数 | 主用 |
| iFind | 盘后日线 OHLCV、衍生指标、龙虎榜、融资融券、宏观，QPS≤20 | 补充 |
| AkShare | 免费备用，iFind 降级备选 | 备用 |
| BaoStock | 历史 K 线/财务，回测历史数据/交叉验证 | 备用 |
| tushare | 新闻快讯 9 源聚合 + 历史数据 | **待开通**（L340-346） |
| Whisper ASR + ChromaDB | 舆情音频转写 + 向量语义检索 | 规划 |

### 1.2 L0→L1 标准化流水线（§1.2 / §1.3）

- miniQMT 3 秒 Tick 字段：symbol/price/volume/amount/bid1~5/ask1~5（L370-378）；Level-2 十档需额外权限、未开通（L376-378）。
- L0 不持久化原始推送（DD-P1-02，L420）；L1 统一为 **CTR-001 NormalizedMarketData** 契约，Schema 为 `trade_date | symbol | open | high | low | close | volume | amount | vwap | turnover | adj_factor | timestamp`（L394-396）。
- 质量门禁四条：OHLC 逻辑校验（P0）、涨跌幅偏差>0.01%（P1）、缺口检测缺失>0.1%（P0）、复权偏差>0.01%（P1）（L398-402）。
- Tick 仅保留近 3 个月，历史归档为分钟 K 线（DD-07-03/DD-P1-03，L421、L1125）。

### 1.3 三层存储架构（§7.1，核心选型）

文档 v6.0 的存储选型（L1037-1070）：

| 层 | 技术 | 延迟 | 内容 | 路径 |
|----|------|------|------|------|
| Hot | **Redis** | <10ms | 盘中 Tick / 实时因子值 / 信号 / 风控 / 持仓，~200MB | 内存 |
| Warm | **DuckDB + Parquet** | <1s | 日线/因子/信号历史/基本面/宏观，~50GB | `D:\zalpha\data\` |
| Cold | **Parquet on SSD** | <30s | 归档/审计/快照（交易≥7年/决策≥3年/系统≥1年） | `E:\zalpha\archive\` |

配套规格：
- **容量规划**（§7.2）：Hot ~200MB→1GB、Warm ~50GB→400GB、Cold ~20GB→300GB。
- **生命周期矩阵**（§7.3，L1080-1091）：盘中 Tick Hot 盘中→Warm 3 个月→Cold 分钟 K 线；日线/基本面 Warm 1 年→Cold ≥7 年；因子 Warm 2 年→Cold ≥7 年。
- **备份策略**（§7.4，L1097-1108）：小时增量 D→E（保留 7 天）、每日 15:30 日快照（RTO<1s/RPO=0）、周全量（4 周）、配置备份（7 年）；Redis AOF everysec + RDB 双开；交易时段 RTO<5 分钟、持仓 RPO=0。
- **DuckDB 性能校准**（§0.1 L155-159 / DD-07-01）：Comfort≤5M 行（窗口函数）/Workable≤20M 行（简单聚合）/Pushing 20-30M/Batch-Only>30M；升级触发：窗口函数>5M→分区裁剪、简单聚合>20M→ClickHouse、100GB+→Iceberg。

### 1.4 Feature Store 特征存储（§11）

- **双存储架构**（DD-11-01，L1972-2024）：离线 Parquet（按日分区，PIT 查询 ~100ms，训练/回测用）+ 在线 Redis Hash（`feature:{symbol}` / `{factor_name}:{version}` → value，<5ms，盘中信号/风控用）+ **Feature Registry（SQLite `feature_registry.db`，四维：元数据/血缘/质量/服务状态）**。
- 离线 Parquet Schema 7 列：`trade_date/symbol/factor_name/factor_value/factor_version/computed_at/quality_flag`（L2057-2067）。
- **训练-服务一致性**（§11.3）：单一定义原则（D-FACTOR Engine 为唯一计算逻辑 SSoT）、PIT 正确性、版本对齐（`model_version` 血缘）。
- 因子容量：运行上限 ≤64、设计容量 ≥200（§0.1 L72）；声明式 YAML DSL + `incremental_compute()` + `consistency_check()`（L73-75）。

### 1.5 Event Store 事件溯源（§12）

- **Parquet append-only 文件**（DD-12-03，L2822-2880），按 `year=/month=/day=` 分区，Snappy 压缩 ~10:1。
- **6 类业务事件**（§12.2，L2733-2818）：TickEvent / SignalEvent / DecisionEvent / ExecutionEvent / RiskEvent / SystemEvent，事件流 Tick→Signal→Decision→Execution，Risk 可中断任意阶段。
- 事件 Schema 10 列（§12.3.1）：`event_id/event_type/event_version/timestamp(μs)/aggregate_id/aggregate_type/payload(JSON)/metadata(JSON)/correlation_id/causation_id`；**幂等键 = SHA-256(aggregate_id+timestamp+event_type)**（DD-12-04，L2897-2918）。
- **CQRS 分离**（DD-12-05，§12.4）：写端事件追加、读端 DuckDB 物化视图。
- **快照策略**（§12.5）：每日收盘全量快照 + 盘中每 5 分钟增量快照，重建性能提升 60x（L2702-2728）。
- 容量（§12.3.3）：TickEvent 年 2.5TB 仅留 3 个月；非 TickEvent 7 年 <1.2GB。

### 1.6 PIT 一致性（§13）

- **三条公理**（L3343-3369）：①因子值时间不可逆（`computed_at ≤ as_of`）；②财务数据公告日约束（`announce_date ≤ as_of`）；③幸存者偏差修正（PIT 股票池每日截面快照 + 退市/ST 标记）。
- **三平面统一**（§13.2）：训练（DuckDB AS OF JOIN）/回测（事件回放）/推理（Redis 实时）。
- **AS OF JOIN 实现**（§13.3）：DuckDB `QUALIFY ROW_NUMBER() OVER (PARTITION BY symbol, factor_name ORDER BY computed_at DESC) = 1`。
- **Embargo 期**（DD-13-01，§13.4）：季报/年报 5 个交易日、业绩预告 3 日、限售解禁 1 日、指数成分调整 5 日。
- **PIT 校验规则**（§13.5）：5 条规则含跨平面一致性校验（训练 vs 推理偏差 ≤0.01%，P0 告警+重算）。

### 1.7 数据质量 SLA（§10）

- ISO 8000 五维度（完整性/准确性/一致性/及时性/可用性）+ BCBS 239 校准（§10.1）。
- **SLA 三级**：P0 关键（Tick/信号）、P1 重要（日线/因子）、P2 背景（宏观/另类）（§10.2）。
- 三段自动化检查流水线：盘前 08:00-09:15、盘中 09:30-15:00 实时监控、盘后 15:00-17:00 一致性校验（§10.3）。
- 违约闭环：Detect→Alert→Degrade→Repair→Verify（§10.4）；质量记分卡（§10.5）。

### 1.8 数据血缘（§9）

列级血缘 + OpenLineage 标准适配（§9.3）+ SQL AST 解析自动采集 + 成熟度四阶段（Reactive→Passive→Active→Governed）+ AI 治理血缘（feature→model→prediction→action）。

### 1.9 数据安全与合规（§14）

- **四级分类**：L1 公开（行情/财务）/L2 内部（因子/回测）/L3 机密（信号/决策/仓位）/L4 绝密（持仓/交易记录/策略代码/模型权重）（L3456-3490）。
- **RBAC 6 角色**（Trader/RiskMgr/Researcher/Admin/AI Agent/Compliance）× 4 级数据矩阵（§14.2）；B-011 约束：AI 禁止将持仓/交易/策略数据发外部 LLM API。
- **加密**：TLS 1.3 传输 + AES-256-GCM 存储（L3/L4）+ 字段级加密（策略/因子公式/权重）+ 备份加密 90 天轮换（§14.3）。
- **AI 脱敏管道**（§14.4）：L4 仅发统计摘要、L3 金额/标的泛化、L2 禁发原始因子值序列。
- **审计日志**（§14.5）：交易≥7年/决策≥3年/数据访问≥1年/AI 调用≥1年，事件溯源 append-only + SHA-256 校验链。

### 1.10 演进路径（§15）

- **AUM 驱动三阶段**（§15.3-15.4）：阶段1（AUM<200万，当前）Redis+DuckDB+Parquet → 阶段2（200-500万）Warm 升级 ClickHouse + Data Contract → 阶段3（>500万）ClickHouse Cluster + MinIO/NAS + Kafka。
- **ADR 8 条**（§15.5）：ADR-001 DuckDB 替代 ClickHouse（已采纳）、ADR-005 AUM>200万升级 ClickHouse（待决策，触发门禁三选一）。

---

## 2. 落地状态逐条核验

> 图例：✅ 已落地 / 🟡 部分落地 / ❌ 未落地 / ⚡ 已落地但形态与文档不同（被更新的内部设计替代）

### 2.1 数据源接入

| # | 文档设计 | 状态 | 证据 |
|---|---------|:----:|------|
| 2.1.1 | miniQMT 3 秒 Tick 主源 | ✅ | `src/zephyr/data/implementations/miniqmt_provider.py`；`src/zephyr/data/tick_subscriber.py`（常驻订阅进程，QMT callback→queue→WalWriter→ClickHouse tick_data，头注 L14-21） |
| 2.1.2 | iFind 盘后补充 | ✅ | `src/zephyr/data/implementations/ifind_provider.py` |
| 2.1.3 | AkShare 备用 | ✅ | `src/zephyr/data/implementations/akshare_provider.py` |
| 2.1.4 | BaoStock 历史补充 | ✅ | `src/zephyr/data/implementations/baostock_provider.py` |
| 2.1.5 | tushare 待开通 | ✅（超出文档） | `src/zephyr/data/implementations/tushare_provider.py` 已存在（文档 L345 标注"待开通"，项目已施工） |
| 2.1.6 | 多源统一接入调度 | ✅（超出文档） | 项目 Data Source Integrator（MOD-L00-004）统一管理 8+ 源：`src/zephyr/data/config/tasks.yaml` 含 akshare/baostock/cls/eastmoney_news/ifind/miniqmt/rss/tdx/tickflow 等 source；比文档多 tdx/cls/eastmoney_news/rss/tickflow |
| 2.1.7 | Whisper ASR 舆情音频 | ❌ | `src/zephyr/data/` 无 whisper/ASR 相关实现（`src/zephyr/data/satellite_geospatial_engine/` 为另一另类数据方向） |

### 2.2 L0→L1 标准化与 CTR-001 契约

| # | 文档设计 | 状态 | 证据 |
|---|---------|:----:|------|
| 2.2.1 | CTR-001 NormalizedMarketData 契约 | ✅ | `docs/02_enterprise_architecture/01_global_architecture_diagram/contract_catalog.md` L151-185（提供方 D_MKT_DATA，物理路径 `src/zephyr/shared/contracts/market_data.py`）。**字段差异**：项目版含 data_source/quality_score/is_suspended/idempotency_key/trace_context 等治理字段，文档版含 vwap/turnover/trade_date——项目版更厚 |
| 2.2.2 | L0→L1 四条质量门禁 | 🟡 | `src/zephyr/data/quality_gate.py`（re-export QualityReport）+ `src/zephyr/data/integrity_checker.py` + `src/zephyr/data/backfill_checker.py` 存在质量检查组件，但文档定义的四条规则（OHLC 逻辑/涨跌幅/缺口/复权偏差）未见逐条对应的完整实现，tick 层有 `quality_flag` 字段（见 2.3.2 DDL） |
| 2.2.3 | Tick 仅留 3 个月→分钟 K 线归档 | ⚡ 超出 | 项目未执行"仅留 3 个月"：实测 `tick_data` 存 2016-10-10 ~ 2026-07-22 近 10 年全量 143 亿行；分钟 K 线由 `src/zephyr/data/kline_resampler.py` 从 tick 合成（`kline_1min` 实测 38.7 亿行，另有 5/15/30/60min） |

### 2.3 三层存储架构（核心分歧区）

| # | 文档设计 | 状态 | 证据 |
|---|---------|:----:|------|
| 2.3.1 | Hot 层 Redis | ❌ | `src/zephyr/infrastructure/database_service.py` 头注 L36-37：「Redis H1 热缓存为预留接口（抛 NotImplementedError），待 P2 实盘需求触发施工（#ARCH-048 已裁决）」；`src/` 全仓 grep 无 `import redis` |
| 2.3.2 | Warm 层 DuckDB+Parquet（`D:\zalpha\data\`） | ⚡ 被替代 | `database_service.py` 头注 L38-40：「market.duckdb（旧 DuckDB 业务时序库）已于 2026-07-05 删除……业务行情数据已迁移至 ClickHouse c1_market」。**实测 ClickHouse `c1_market` 库 77 张表**：`tick_data`（14,324,240,136 行，ReplacingMergeTree，PARTITION BY toYYYYMM(trade_date)，ORDER BY 含 price —— ARCH-CH-020 修复）、`kline_daily`（34,664,504 行）、`auction_snapshot`/`index_quote`/`adj_factor`(21M)/`money_flow`(622K)/`dragon_tiger`(170K)/`margin_trading`(1.15M)/`macro_data`(285K)/`hk_connect_flow` 等全部有量 |
| 2.3.3 | Cold 层 Parquet on SSD（`E:\zalpha\archive\`，≥7 年） | 🟡 未能验证 | `scripts/database/backup/` 目录存在，但 `D:\zalpha`/`E:\zalpha` 路径体系未见于代码（grep 无命中）；7 年留存当前由 ClickHouse 全量保存替代承载。未能实测 E 盘归档 |
| 2.3.4 | D→E 小时增量/日快照/周全量备份 + RTO/RPO 表 | 🟡 | `scripts/database/backup/` 存在备份脚本目录；但文档 §7.4 的四级备份矩阵（小时增量 7 天/日快照 RPO=0/周全量 4 周/配置 7 年）未见成体系的调度配置证据 |
| 2.3.5 | 8 张行情表插拔式 DDL-as-Code | 🟡 | 文档未提此概念，系项目自创超越：`docs/03_modules/_cross_layer/database/sub_blueprints/c1_market_clickhouse.md` L62-73 定义 C1 仓库 8 表（tick_data/kline_daily/auction_snapshot/index_quote/option_iv_surface/futures_position/futures_term_structure/convertible_bond_iv），`construction_progress: partially_implemented`；实测 8 表在 c1_market 均已建表且有数据 |

### 2.4 Feature Store 特征存储（最大缺口）

| # | 文档设计 | 状态 | 证据 |
|---|---------|:----:|------|
| 2.4.1 | 离线存储 Parquet（按日分区，7 列 Schema，PIT 查询） | ❌ | `src/zephyr/factor/` 下无因子值 Parquet 持久化；grep `factor_value` 在 `src/zephyr/factor/`、`src/zephyr/market_data/` 无持久化命中；ClickHouse 的 `stock_indicator` 表（63,654 行）是 iFind/THS 下载的财务衍生指标，非 D-FACTOR 计算因子值 |
| 2.4.2 | 在线存储 Redis Hash（`feature:{symbol}`，<5ms） | ❌ | 同 2.3.1，Redis 未实现 |
| 2.4.3 | Feature Registry（SQLite feature_registry.db，元数据/血缘/质量/服务状态四维） | 🟡 | 仅内存版：`src/zephyr/factor/factor_base.py` L130 `class FactorRegistry`（单例 dict，`@register` 装饰器 + get/list_all/list_by_domain），无 SQLite 落盘、无血缘/质量/服务状态维度 |
| 2.4.4 | 训练-服务一致性（单一定义/版本对齐/跨平面偏差≤0.01% 校验） | ❌ | 契约目录 `contract_catalog.md` L187-194：CTR-002 FactorSignal **状态 = unresolved**；C2 指标仓库子蓝图未编写（`docs/03_modules/_cross_layer/database/sub_blueprints/` 仅 `c1_market_clickhouse.md` + `index.md`，母蓝图 child_modules 中 C2-INDICATOR-CH status=Pending） |
| 2.4.5 | 声明式 YAML DSL + 增量计算 + 一致性引擎 | ❌ | `src/zephyr/factor/` 仅 `factor_base.py`/`momentum_factor.py`/`alpha_signal_pipeline.py` 等代码式定义，无 YAML DSL |

### 2.5 Event Store 事件溯源

| # | 文档设计 | 状态 | 证据 |
|---|---------|:----:|------|
| 2.5.1 | 事件不可变存储 | ⚡ 形态不同 | 项目 RI-13 EventStore = **SQLite**（`src/zephyr/infrastructure/event_store.py` L23-28：「SQLite 不可篡改审计日志（WAL+SHA256 checksum）」，默认 `data/events.db`），非文档的 Parquet append-only；文档 DD-12-03 明确否决 SQLite WAL 方案（L2824「行情事件写入频率高会压垮 WAL checkpoint」），项目实际只用它记低频审计事件，规避了该问题 |
| 2.5.2 | 6 类业务事件 Schema（Tick/Signal/Decision/Execution/Risk/System） | ❌ | EventStore 的 StoredEvent 为通用审计事件（component/level/message 粒度），无 6 类业务事件分类体系与各自 payload 定义 |
| 2.5.3 | correlation_id/causation_id 因果链 | 🟡 | CTR-TRACE-001 TraceContext 已入契约目录（contract_catalog.md L176），事件级 correlation/causation 双 ID 未见落库 |
| 2.5.4 | CQRS 读端物化视图 | ❌ | 无对应实现 |
| 2.5.5 | 日快照+盘中 5 分钟增量快照、任意时点状态重建 | 🟡 | `src/zephyr/infrastructure/system_snapshot.py` 存在系统快照组件；事件回放重建任意时点状态（文档 §12.1.2 重建流程）未见实现 |

### 2.6 PIT 一致性（落地质量好）

| # | 文档设计 | 状态 | 证据 |
|---|---------|:----:|------|
| 2.6.1 | 三条公理 | ✅ | `src/zephyr/backtest/core/pit_manager.py` 头注 L8：`[INVARIANTS] PIT三公理;Embargo期;AS OF JOIN;pit_consistency_test` |
| 2.6.2 | AS OF JOIN | ✅（实现路径不同） | `pit_manager.py` L119 `def as_of_join(...)`——pandas 实现而非文档的 DuckDB QUALIFY；DuckDB 已删除，此替代合理 |
| 2.6.3 | Embargo 期（财务 5 交易日等分档） | ✅ | `pit_manager.py` L79 `embargo_days: int = DEFAULT_EMBARGO_DAYS`（默认 5）+ L182 `apply_embargo()`；文档的分档 Embargo（预告 3 日/解禁 1 日/指数 5 日）未见分档实现 |
| 2.6.4 | 幸存者偏差校验 | ✅ | `pit_manager.py` L317 `check_survivorship_bias()`；`src/zephyr/backtest/core/data_handler.py` L232「运行PIT铁律检查（一致性测试+幸存者偏差检测）」 |
| 2.6.5 | `pit_consistency_test()` CI 化 | ✅ | `pit_manager.py` L229 `pit_consistency_test()`；`data_handler.py` L97-117 PITManager 注入数据管道 |
| 2.6.6 | 双时态建模（system_time+business_time）、HSTR Snapshot+Delta | ❌ | ClickHouse 表 DDL 无 system_time 列；无 Snapshot+Delta 双时态结构 |

### 2.7 数据质量 SLA

| # | 文档设计 | 状态 | 证据 |
|---|---------|:----:|------|
| 2.7.1 | 五维度质量定义（ISO 8000） | 🟡 | `src/zephyr/data/quality_gate.py`（QualityReport re-export）+ `integrity_checker.py` 存在，未见五维度形式化定义 |
| 2.7.2 | P0/P1/P2 SLA 分级 | 🟡 | `src/zephyr/infrastructure/sla/sla_monitor.py` 存在（面向 RTO/RPO）；数据品类 SLA 三级（P0 Tick/P1 日线/P2 宏观）未见分级配置 |
| 2.7.3 | 盘前/盘中/盘后三段检查流水线 | 🟡 | `scripts/governance/data_quality/check_tick_duplication.py`（--month 全字段 GROUP BY 真重复校验，RULE-DATA-OPS 标准化工具）+ `backfill_checker.py` 为散点工具，未成三段定时流水线 |
| 2.7.4 | 质量记分卡（§10.5 评分模型） | ❌ | 未见实现 |

### 2.8 数据血缘

| # | 文档设计 | 状态 | 证据 |
|---|---------|:----:|------|
| 2.8.1 | OpenLineage 标准 + 列级血缘 + SQL AST 采集 | ❌ | `src/zephyr/infrastructure/pipeline/models.py` 仅出现 OpenLineage 字样，无采集器/SQL AST 解析实现 |
| 2.8.2 | （文档未覆盖）代码级依赖血缘 | ✅ 项目自创 | PostgreSQL depgraph 实测 5506 个 nodes、46 张治理表（`zephyr.governance.depgraph_schema`），比文档血缘设计更重的代码级体系——方向不同但能力超出 |

### 2.9 数据安全与合规

| # | 文档设计 | 状态 | 证据 |
|---|---------|:----:|------|
| 2.9.1 | 四级数据分类（L1-L4） | 🟡 | `src/zephyr/data_security/` 域存在；文档的四级分类矩阵未见对应的数据资产打标落库 |
| 2.9.2 | RBAC 6 角色 × 4 级矩阵 | 🟡 | `src/zephyr/security/access_control/` 存在（kill_switch 等）；面向数据行级/列级的 RBAC 矩阵未见（单用户系统，优先级低属合理） |
| 2.9.3 | AES-256-GCM 存储/字段加密 | ❌ | 数据层未见 AES-256-GCM 加密实现（grep 仅命中 `src/zephyr/security/access_control/adversarial_resilience.py` 与 LSG L6 数据流层的零星引用） |
| 2.9.4 | AI 脱敏管道（B-011） | ⚡ 形态不同且更强 | 项目落地为 LSG LLM 安全网关 L1-L8 十层纵深防御（`src/zephyr/security/llm_defense/llm_security/`，RULE-LSG-001 强制所有 LLM 调用必经安检），覆盖文档 L4→统计摘要/L3→泛化的脱敏目标，且含 MCP Triple Gate 等文档未有的机制 |
| 2.9.5 | 审计日志分级留存（交易≥7年等） | 🟡 | EventStore（SQLite WAL+SHA256）满足不可篡改；分级留存期未见配置化执行 |

### 2.10 向量存储与知识图谱

| # | 文档设计 | 状态 | 证据 |
|---|---------|:----:|------|
| 2.10.1 | ChromaDB 向量索引（语义检索） | ✅ | `src/zephyr/integration/vector_memory/bridge_layer.py` L174-177 `chromadb.PersistentClient`；ADR-008 记载 ChromaDB 治理层已采用 |
| 2.10.2 | （文档远期）Faiss GPU | ✅ 超出 | `src/zephyr/integration/vector_memory/faiss_collection_manager.py` 已存在（文档 §15.4 列为阶段2/3 评估项，项目已落地） |
| 2.10.3 | 知识图谱（Neo4j/NetworkX 五类图谱 + Graph+Vector 混合 RAG） | ❌ | `src/` 无 neo4j 引用；母蓝图 G2-KNOWLEDGE-NEO4J status=Pending（`business_data_architecture.md` frontmatter child_modules）；治理架构.md L1645 亦标注「待 FPGA 硬件升级+GPU 资源就绪+Neo4j/ArangoDB 部署」 |

---

## 3. 关键分歧：文档 v6.0 选 DuckDB，项目落地 ClickHouse

这是本审查最重要的发现——**文档的数据库核心选型已被项目正式否决并超越**：

1. **文档族内部决策轨迹**：`00-架构图总览与索引.md` L466 记载 A3 数据架构 v3.0→v6.0 的变更内容含「**ClickHouse→DuckDB**」——即 2026-05-26 的 v6.0 主动从 ClickHouse 降级为 DuckDB+Parquet（ADR-001，理由：AUM<200万单机 DuckDB 零部署更轻量，DD-07-01）。
2. **文档族内部不一致**：`交易决策架构.md` L105 仍写「分层时序存储(Redis热+**ClickHouse温**+Parquet冷)」，与数据架构.md v6.0 的 DuckDB 选型冲突——文档族自身未完全同步。
3. **项目的反向决策**：项目母蓝图 `docs/03_modules/_cross_layer/database/business_data_architecture.md`（2026-07-01，晚于文档 v6.0 一个月）frontmatter `references` 明确写「DD-07-01 …… DuckDB→ClickHouse升级门禁决策（**本架构提前触发**）」，且 `depends_on` 声明以「数据架构.md §1~§17」为设计输入——**项目承认文档为上游设计真源，但正式推翻了其 DuckDB 决策，提前触发 ADR-005 升级门禁直接上 ClickHouse**。
4. **落地实证**：ClickHouse C1 行情仓库 2026-07-01 部署（INFRA-DB-006，`database_service.py` 头注 L35-36）；旧 market.duckdb 2026-07-05 删除。实测 c1_market 77 表、tick 143 亿行——数据规模（Tick 单表 14.3B 行）已远超文档 DuckDB「Batch-Only >30M 行」边界 3 个数量级，**事后看项目推翻 DD-07-01 是正确的**：按文档设计 Tick 仅留 3 个月（~62.5GB 压缩），项目实际需求是近 10 年全量 Tick 回测，DuckDB 无法承载。

**结论**：核验落地状态时，不能以文档的 DuckDB/Redis/Parquet 三层选型为基准判"未落地"，而应以"存储分层能力是否实现"为基准——Warm 层能力 ✅（ClickHouse 替代 DuckDB，更强），Hot 层能力 ❌（Redis 未建，#ARCH-048 裁决缓建），Cold 层能力 🟡（由 ClickHouse 全量留存事实替代，Parquet 归档未验证）。

---

## 4. 文档优于项目现有实现的设计点

以下设计点在文档中有完整规格，而项目当前实现缺失或更弱，**值得吸收**（按价值排序）：

1. **Feature Store 训练-服务一致性三件套**（§11.3）：单一定义原则（同一 compute() 代码路径供训练/推理）+ 版本对齐（feature_version↔model_version 血缘）+ 跨平面偏差校验（≤0.01% P0 告警）。项目 CTR-002 仍 unresolved、因子值无持久化，回测与（未来）实盘推理的因子一致性目前无任何机制保障——**回测场景下这是最高优先缺口**。
2. **新鲜度检查点 CP-01~CP-07 + 延迟预算表**（§8.3，L1165-1177）：每个链路段定义 SLO+超限动作（如 CP-01 Tick→Redis ≤3秒超限→P0 告警+暂停信号生成）。项目 tick_subscriber 有 metrics 埋点（received/written/dropped），但无检查点级 SLO 判定与联动动作。
3. **L0→L1 四条具体质量门禁规则**（§1.3，L398-402）：OHLC 逻辑/涨跌幅偏差/缺口检测/复权校验，带阈值和告警级别。项目 quality_gate 组件存在但规则未成文化到该粒度。
4. **数据生命周期矩阵 + 备份 RTO/RPO 表**（§7.3/§7.4）：每类数据的 Hot/Warm/Cold 保留期 + 四级备份（小时/日/周/变更触发）+ 明确 RTO/RPO。项目有备份脚本目录但无成体系的矩阵化策略。
5. **Event Sourcing 业务事件因果链**（§12.2/§12.3.1）：6 类业务事件 + correlation_id/causation_id 双 ID，使"信号→决策→执行"全链路可回放对账（文档称对账工作量减 60%）。项目 EventStore 仅为通用审计日志，回测事故复盘时无法按因果链重建决策过程。
6. **数据质量记分卡**（§10.5）：五维度加权评分模型 + 按 SLA 分级更新频率——项目质量工具是散点脚本，无聚合评分视图。
7. **分档 Embargo 期**（§13.4）：按数据类型分 1/3/5 交易日。项目 PITManager 仅全局默认 5 日单一档。
8. **因子值窄表 7 列 Schema + 容量估算纪律**（§11.1.1）：每张大表先算"记录数/日×单条大小×保留期"再定存储——项目母蓝图已吸收此方法论（`business_data_categories.yaml` 106 个 category_id 插拔式注册），但因子值表本身未建。

反向地，项目优于文档的点（文档可反哺修订）：ClickHouse 替换 DuckDB（§3）；治理侧 LSG 十层 LLM 安检替代单薄脱敏管道；depgraph 代码级血缘（5506 节点）替代纯数据血缘；数据源覆盖更广（10 provider vs 5）；ChromaDB+Faiss 双轨已落地（文档列为远期）。

---

## 5. 其余 9 份文档数据库相关段落摘要

| 文档 | 数据库相关要点（含行号） | 与数据架构.md 关系 |
|------|------------------------|-------------------|
| 00-架构图总览与索引.md | L205 三层存储（Hot Redis/Warm DuckDB+Parquet/Cold Parquet SSD）；L310 运行时 Redis 13 命名空间；L466 v6.0 变更「ClickHouse→DuckDB+PIT三公理+OpenLineage+双时态」 | 索引层与数据架构一致（DuckDB 口径） |
| Agent架构.md | L133 记忆体系：工作记忆(Redis/会话)→情景记忆(Redis+SQLite/90天)→语义记忆(SQLite+Parquet/永久)→程序记忆(SKILL.md)；L756-758 JSON-RPC over Redis Pub/Sub、Agent Registry 存 Redis Hash | 依赖 Redis——项目 Redis 未建，此文档对应设计整体未落地 |
| 交易决策架构.md | L34 数据存储方案（Redis/ClickHouse/Parquet）→A3；L105「分层时序存储(Redis热+**ClickHouse温**+Parquet冷)」；L114 特征存储(离线PIT+在线Redis+血缘+质量+回填+Serving API) | **内部矛盾**：此处仍为 ClickHouse 口径，与数据架构 v6.0 DuckDB 冲突 |
| 合规架构.md | L170 决策溯源链=9 字段扁平化决策日志(SQLite/Parquet)；L172 合规证据图查询引擎(Neo4j)；L304 Crypto-Shredding | Neo4j 未落地（同 2.10.3）；决策溯源链部分对应 EventStore |
| 学习系统架构.md | L565-574 离线特征存储(DuckDB Parquet)+在线特征服务+PIT AS OF JOIN；明确 PIT 门控/Feature Store/PIT Manager 三者职责边界 | Feature Store 未落地（同 2.4）；项目 PITManager ✅ |
| 安全架构.md | L709 数据库级加密：SQLite SQLCipher 扩展 / PostgreSQL TDE | 项目未采用 SQLCipher/TDE（单用户本地库，未见落盘加密） |
| 治理架构.md | L1645 图数据库存储（M5）❌「待 FPGA 硬件升级+GPU 资源就绪+Neo4j/ArangoDB 部署」 | 自证未落地，与项目现状一致 |
| 运维架构.md | L22/L88-111 运行时 NSSM+5 进程+Redis 共享状态+GPU 调度+灾备 3-2-1-1-0（D→E 盘） | Redis 依赖未落地；D→E 灾备未验证 |
| 集成架构.md | L167/L207/L274/L562 交易消息 Redis Stream + 幂等 Key + At-Least-Once 消费（下单零重试 HB-07） | Redis Stream 未落地（实盘阶段事项，当前仅回测可缓） |
| 风险架构.md | L1793 VaR DuckDB Historical Simulation Query Builder「项目有蓝图编号 MOD-L04-001 但是没建设」；L1894 Risk Policy SQLite Schema 同状 | 文档自证 VaR 计算未建设，与 DuckDB 删除后的现状叠加——VaR 查询引擎需重定向到 ClickHouse |

---

## 6. 结论：落地缺口判定

**判定：架构图文档的数据库设计未全部落地落盘，存在明确缺口；但其中"存储选型"部分的未落地是项目主动决策的结果（DuckDB→ClickHouse 提前升级），不应计为欠账。**

按能力域汇总：

| 能力域 | 判定 | 一句话结论 |
|--------|:----:|-----------|
| 数据源接入 | ✅ 落地且超出 | 10 provider 超文档 5 源设计，tushare 已开通 |
| 行情存储底座（Warm） | ✅ 落地且超出 | ClickHouse c1_market 77 表实测有量，tick 143 亿行/近 10 年，远超文档"3 个月 DuckDB"设计 |
| CTR-001 契约 | ✅ 落地 | 契约目录登记 + 物理契约文件，字段比文档更厚 |
| PIT 一致性 | ✅ 核心落地 | 三公理/AS OF JOIN/Embargo/幸存者偏差/pit_consistency_test 均有实现（pandas 替代 DuckDB）；双时态、分档 Embargo 未落地 |
| 向量存储 | ✅ 落地且超出 | ChromaDB+Faiss 双轨（文档列为远期评估项） |
| Hot 层 Redis | ❌ 未落地 | #ARCH-048 裁决缓建（回测阶段无需求），集成/Agent/运维架构的 Redis Stream/Pub-Sub/共享状态设计随之整体悬空 |
| Cold 层归档/备份矩阵 | 🟡 部分 | 备份脚本存在；E 盘 Parquet 归档、7 年分级留存、RTO/RPO 矩阵未验证/未成体系 |
| **Feature Store** | ❌ **最大缺口** | 无离线因子值存储、无在线 serving、无 SQLite Registry、CTR-002 unresolved、C2 仓库蓝图未写——训练-服务一致性无机制保障 |
| Event Sourcing 业务事件体系 | 🟡 概念落地形态不同 | SQLite 审计 EventStore ✅，但 6 类业务事件/因果链/CQRS/快照重建未落地 |
| 数据质量 SLA 体系 | 🟡 散点工具 | 有查重/完整性/SLA 监控组件，无 P0/P1/P2 分级、三段流水线、记分卡 |
| 数据血缘（OpenLineage） | ❌ 未落地 | 项目以 depgraph 代码血缘替代（方向不同，能力不弱） |
| 数据安全（四级分类/RBAC/AES 加密） | 🟡~❌ | LSG 覆盖 AI 脱敏目标且更强；数据层分级打标/RBAC 矩阵/落盘加密未落地（单用户回测阶段优先级合理） |
| 知识图谱（Neo4j） | ❌ 未落地 | G2 蓝图 Pending，治理架构自证待硬件就绪 |

**给后续施工的建议优先级**（回测场景约束下）：①Feature Store 离线存储 + CTR-002 契约转正（回测可复现性刚需）；②Event 业务事件分类 + 因果链（回测复盘/归因刚需）；③新鲜度检查点与 L0→L1 质量门禁规则成文化（数据可信度）；④分档 Embargo（PIT 精细化）；⑤Redis/Neo4j/OpenLineage/数据加密均可在实盘阶段（P2）再启动，与 #ARCH-048 裁决一致。

---

### 附：本次实测记录

- ClickHouse（172.24.30.100:9000/8123）只读实测：77 表；tick_data 14,324,240,136 行（2016-10-10~2026-07-22）；kline_daily 34,664,504 行；kline_1min 3,867,233,437 行；adj_factor 21,055,920 行；money_flow 621,716 行；dragon_tiger 169,980 行；margin_trading 1,154,636 行；macro_data 285,322 行。全部只读 SELECT/SHOW，无任何写入。
- PostgreSQL（localhost:5432）只读实测：public schema 46 张治理表，depgraph nodes 5,506 行。
- 未能验证项：E 盘归档目录（`E:\zalpha\archive\`）存在性、备份调度实际运行记录、DuckDB 删除前的历史数据迁移完整性。
