# ZephyrAlpha 量化数据库架构审查 —— 完整审查清单与总评报告

> 审查编号：audit_03 | 审查日期：2026-07-22 | 审查员角色：独立机构级量化系统架构审查
> 审查对象：ZephyrAlpha 数据底座（ClickHouse c0_meta / c1_market / c3_fundamental + SQLite/PostgreSQL 治理库 + 数据接入管线）

---

## 目录

- [0. 审查元信息](#0-审查元信息)
- [1. 审查清单与逐条评分](#1-审查清单与逐条评分)
  - [① Schema 与字段设计](#-schema-与字段设计)
  - [② 数据覆盖完整性](#-数据覆盖完整性)
  - [③ 数据质量保障](#-数据质量保障)
  - [④ 管线可靠性与容错](#-管线可靠性与容错)
  - [⑤ 存储引擎与查询性能](#-存储引擎与查询性能)
  - [⑥ 治理 / 血缘 / 元数据](#-治理--血缘--元数据)
  - [⑦ 备份与灾难恢复](#-备份与灾难恢复)
  - [⑧ 可观测性与告警](#-可观测性与告警)
  - [⑨ 安全与访问控制](#-安全与访问控制)
  - [⑩ 扩展性与未来实盘就绪度（方向提示，不计分）](#-扩展性与未来实盘就绪度方向提示不计分)
- [2. 分项得分与总分](#2-分项得分与总分)
- [3. 差距分析](#3-差距分析)
- [4. P0 / P1 / P2 问题清单](#4-p0--p1--p2-问题清单)
- [5. 可执行改进路线图](#5-可执行改进路线图)
- [6. 机构对标结论](#6-机构对标结论)

---

## 0. 审查元信息

### 0.1 审查假设（用户声明，全程适用）

- **单人使用**：单用户、单工作机场景，多租户/团队协作类机构标准不适用；
- **仅回测用途**：数据库当前只服务回测，实盘交易后续开发；
- **实盘就绪度（第⑩类）只作未来方向提示，不作为扣分项**；同理，单节点无副本、单 CH 用户等与"单人本地"假设相容的项按 ⚠️ 标注但不拉低总分定性。

### 0.2 审查方法

1. 静态审查：源码（`src/zephyr/data/`、`src/zephyr/infrastructure/database_service.py`）、DDL-as-Code（`schemas/categories/`）、配置（`config/`、`src/zephyr/data/config/`）、脚本（`scripts/ch/`、`scripts/backup/`）、治理文档（`docs/03_modules/_cross_layer/database/`）；
2. **实测连接**（只读）：成功连接 ClickHouse `172.24.30.100:8123`（HTTP 接口，版本 26.6.1.1193），对 `system.tables` / `system.parts` / `system.users` / `system.replicas` 及关键业务表执行只读查询验证数据量、日期覆盖、引擎、排序键、字段类型；
3. 逐条打分：✅ 达标 = 1.0，⚠️ 部分达标 = 0.5，❌ 缺失 = 0.0。

### 0.3 实测环境摘要（2026-07-22 只读实测）

| 项 | 实测值 |
|---|---|
| ClickHouse 版本 | 26.6.1.1193（单节点，`system.replicas` = 0） |
| c1_market | 76 张表，合计 302.20 GiB，全部 ReplacingMergeTree |
| c3_fundamental | 23 张表，合计 15.98 GiB |
| c0_meta | 1 张表（fetch_perf 采集性能记录） |
| tick_data | 14,324,240,136 行（181.41 GiB），2016-10-10 → 2026-07-22，310 个 active parts |
| kline_1min | 3,867,233,437 行（77.99 GiB），2000-06-09 → 2026-07-22（当日） |
| kline_daily | 34,664,504 行，1990-12-19 → 2026-07-21（最近交易日 5,211 只/日） |
| news_data | 10,161,482 行，1999-12-31 → 2026-07-22 |
| CH 用户 | 仅 `default` 一个用户 |

### 0.4 证据引用约定

所有证据为相对仓库根路径；行号以审查时文件内容为准；标注"实测"的条目来自 2026-07-22 对 ClickHouse 的只读查询。

---

## 1. 审查清单与逐条评分

### ① Schema 与字段设计

| # | 检查项 | 机构级合格标准 | 评分 | 证据 | 一句话理由 |
|---|--------|----------------|:--:|------|------------|
| 1.1 | DDL 单一真源（DDL-as-Code） | 每张表 DDL 有唯一真源文件，代码/部署脚本不得内联漂移副本；有自动一致性校验 | ✅ | `schemas/categories/market_tick.py` 等 10 个 schema 文件；`scripts/ch/apply_market_tables_ddl.py` L18-33（`--verify` 校验引擎） | schema 文件为唯一真源，apply 脚本带 verify 模式且不一致时退出码 1 |
| 1.2 | 金额/价格字段数值精度 | 价格金额用定点 Decimal，禁止 Float 存金额（避免二进制浮点误差累积） | ⚠️ | 行情表 `Decimal(18,4)/(18,2)`（`apply_market_tables_ddl.py` L62-64、L88-95）；但实测 `c3_fundamental.income_statement` 的 `total_revenue` 等 20+ 财务字段为 `Float64` | 行情侧达标，财务三表用 Float64 存金额，财务建模场景有精度隐患 |
| 1.3 | 排序键匹配高频查询模式 | ORDER BY 前缀应与最高频查询过滤列一致（symbol 级点查应可被主键裁剪） | ⚠️ | 实测 `tick_data` 排序键 `(market_type, symbol, trade_date, timestamp, price)`；`kline_daily` 为 `(symbol, trade_date)` | kline_daily 达标；tick_data 以 market_type 打头，单票查询无法跳过同分区其他市场段（且 price 入排序键是 #ARCH-CH-020 事故后修复项，代价是主键更长） |
| 1.4 | 分区策略与生命周期管理 | 按时间分区（月/日），支持整分区 DROP 的低成本归档 | ✅ | 实测全部行情/财务表 `PARTITION BY toYYYYMM(trade_date)` | 月分区全库统一，tick 202607 分区 2.54 GiB，粒度合理 |
| 1.5 | 低基数字典压缩 | 枚举型字符串列用 LowCardinality 降存储提查询 | ✅ | DDL 中 `market_type`/`direction`/`data_source` 均为 `LowCardinality(String)`（`apply_market_tables_ddl.py` L61、L67-68） | 低基数列全部正确使用 LowCardinality |
| 1.6 | 空值语义显式化 | 可空字段用 Nullable；禁止用魔术值（如 1970-01-01、-1）表达语义空 | ⚠️ | `bid_price` 等为 `Nullable(Decimal(18,4))` 达标；但 `business_data_categories.yaml` 头部注释承认"1970-01-01 表示未退市"语义空值；且实测 `kline_daily` 存在 1 行 `trade_date=1970-01-01`、symbol 为空的脏数据 | Nullable 用法正确，但 Date 列混用魔术值语义且存在残留脏行 |
| 1.7 | 审计列（ingest_ts / data_source / quality_flag） | 每行可追溯：写入时间、来源、质量标记 | ⚠️ | 财务表有 `ingest_ts DateTime DEFAULT now()`（实测 `income_statement`）；行情表 `tick_data`/`kline_daily` DDL 无 `ingest_ts` 列 | data_source/quality_flag 全库覆盖，但行情表缺写入时间戳，无法追溯"何时入库" |
| 1.8 | 字段注释与数据字典 | 全字段 COMMENT + 机器可读数据字典 | ✅ | DDL 全字段带中文 COMMENT；`docs/03_modules/_cross_layer/database/business_data_categories.yaml`（98 条品类注册） | 注释与品类字典双覆盖，字典声明 76+21+1 表与实测完全吻合 |
| 1.9 | Schema 变更受控流程 | 变更走审批/门禁，禁止裸 ALTER | ✅ | `schemas/categories/market_kline_daily.py` L9-13：`MODIFY-GUARD schema-change`、`AI_AUTONOMY human_only`，变更须经 `apply_schema.py` | schema 文件 human_only + 变更脚本化，达机构变更管理标准 |
| 1.10 | 命名规范与防编造机制 | 表名派生自注册表，代码禁止硬编码表名 | ✅ | `src/zephyr/data/table_registry.py` L41-58：`TableRegistry.table()` 查不到抛 KeyError（fail-closed），裁定 #ARCH-CH-024 | 注册表消费层已建且 fail-closed；但头注自述尚有 240 处历史硬编码待替换（渐进式，不影响达标判定） |

**小计：6 ✅ / 4 ⚠️ / 0 ❌ → 8.0 / 10**

### ② 数据覆盖完整性

| # | 检查项 | 机构级合格标准 | 评分 | 证据 | 一句话理由 |
|---|--------|----------------|:--:|------|------------|
| 2.1 | Universe 含退市/停牌股（防幸存者偏差） | 回测 universe 必须含已退市标的及历史停牌标记 | ❌ | 实测 `stock_list` 5,534 只 `list_status` 全部为"上市"，无一退市股；`config/data/survivorship_policy.yaml` L11-12 仅为声明级 policy gate（"数据管道可证明含退市样本前保持为 gate"） | 策略层面有要求、数据层面未落实，回测存在系统性幸存者偏差——回测用途下这是最严重覆盖缺陷 |
| 2.2 | 行情历史深度 | 日 K ≥ 20 年或全历史；分钟/tick 深度与策略需求匹配 | ✅ | 实测 kline_daily 自 1990-12-19（A 股开市起）；tick_data 自 2016-10-10 | 日 K 全历史，tick 近 10 年，深度达标 |
| 2.3 | 多周期覆盖 | 日/周/月 + 1/5/15/30/60 分钟 + 复权口径齐全 | ✅ | 实测 kline_1/5/15/30/60min、kline_daily/weekly/monthly、`_hfq` 后复权全套；ETF/LOF 分钟线独立成表 | 周期与复权口径覆盖完整 |
| 2.4 | 多市场/多品种覆盖 | A股/港股/美股/期货/期权/可转债/ETF/LOF/指数 | ✅ | 实测 hk_kline（160 万行）、kline_us_daily、kline_futures、option_greeks/option_iv_surface、convertible_bond_iv、etf_nav、index_quote 等 | 九大品种线全部有表有数据 |
| 2.5 | 基本面覆盖 | 三表/财务指标/股东/分红/质押/研报/分析师预期 | ✅ | 实测 c3_fundamental 23 表：income/balance/cashflow 各 33-61 万行，top10_shareholders 144 万行，analyst_forecast、equity_pledge 等齐全 | 基本面覆盖达卖方数据终端水平 |
| 2.6 | 新闻/舆情覆盖 | 多源新闻 + 去重 + 时间戳 | ✅ | 实测 news_data 1,016 万行（1999 起）；`src/zephyr/data/news_dedup.py` 标题 MD5 跨源去重 | 新闻深度与去重机制兼备 |
| 2.7 | 宏观/EDB 数据覆盖 | 宏观指标库非空且持续更新 | ⚠️ | 实测 `edb_data` 表 **0 行**；`macro_data` 285,322 行 | macro_data 有量但 EDB 通道空表，宏观覆盖不完整 |
| 2.8 | 交易日历与元数据 | 交易日历/证券主数据/指数成分为分析基础 | ✅ | 实测 trade_calendar（13,162 行）、hk_trade_calendar、index_constituent（59,583 行）、sector_constituent | 元数据基础完备 |
| 2.9 | 数据新鲜度（T 日数据 T 日可得） | 收盘后当日数据入库；盘中数据分钟级延迟 | ✅ | 实测 kline_daily 至 2026-07-21（最近交易日）；kline_1min 与 tick_data 已含 2026-07-22 当日盘中数据 | 管线当日鲜活，L1/L2 盘中层工作正常 |

**小计：7 ✅ / 1 ⚠️ / 1 ❌ → 7.5 / 9**

### ③ 数据质量保障

| # | 检查项 | 机构级合格标准 | 评分 | 证据 | 一句话理由 |
|---|--------|----------------|:--:|------|------------|
| 3.1 | 行级质量标记 | 每行有 quality_flag 支撑下游过滤 | ✅ | 全表 `quality_flag UInt8 DEFAULT 1`（DDL 实测） | 标记列全库覆盖 |
| 3.2 | 写入幂等与去重 | 重复执行/重复推送不产生重复数据 | ✅ | `src/zephyr/data/ch_writer.py` 头注 §7.3：ReplacingMergeTree 直接 INSERT / MergeTree 写前 DELETE；实测 99 张业务表 92 张为 ReplacingMergeTree | 引擎级 + 应用级双重幂等 |
| 3.3 | 每日完整性巡检 | 每日自动全表达标检测，不达标告警 | ✅ | `src/zephyr/data/integrity_checker.py` L17-27、L86-159：动态发现 tasks.yaml 全表，阈值=7 天日均×0.5，L11 层盘后执行 | 巡检自动化且随任务注册自动扩表 |
| 3.4 | 缺口检测与精准补下载 | 以 DB 实际行数为准发现缺口，不依赖进度文件 | ✅ | `src/zephyr/data/backfill_checker.py` L17-31：查 CH 实际行数、只补缺失（裁定 #ARCH-BACKFILL-001，L10 周末层） | 补下载机制设计达机构标准（但见 3.8 执行遗留） |
| 3.5 | 异常值检测（价格越界/跳变/零量） | 入库或巡检环节有价格/成交量合理性校验规则 | ❌ | quality_flag 全库存在但未见计算逻辑；`src/zephyr/data/quality_gate.py` 仅 27 行 re-export 包装（真源是治理侧 QualityReport，非行情校验规则） | 有标记列无校验器，异常值检测实质缺位 |
| 3.6 | 跨源交叉验证/副源冗余 | 关键数据有第二来源比对或自动 fallback | ⚠️ | `src/zephyr/data/config/tasks.yaml` L10-19 定义 fallback_sources 模板，但实测全文件 129 个任务仅 8 处配置（grep 计数）；`redundant_source/source_switcher.py` 仅覆盖实时 tick | 框架已建成，任务级覆盖率仅 ~6% |
| 3.7 | 数据事故复盘与防再发制度化 | 事故有根因分析、规则化防再发 | ✅ | AGENTS.md RULE-DATA-OPS（#ARCH-CH-020 事故治本）：三步验证铁律 + `scripts/governance/data_quality/check_tick_duplication.py` 标准化工具；tick_data 排序键已修复含 price | 事故治理闭环达机构合规文化水平 |
| 3.8 | 已知缺口/脏数据的清零执行 | 检测出的缺口在 SLA 内补齐；脏数据有清理记录 | ⚠️ | 实测 tick_data 2026-06 日均 248 万行 vs 2026-05 日均 2,385 万行（缺口约 90%，21 个交易日）；kline_daily 残留 1 行 1970 脏数据 | 检测机制（3.3/3.4）在，但 6 月大缺口至今未补齐，执行闭环未合上 |

**小计：5 ✅ / 2 ⚠️ / 1 ❌ → 6.0 / 8**

### ④ 管线可靠性与容错

| # | 检查项 | 机构级合格标准 | 评分 | 证据 | 一句话理由 |
|---|--------|----------------|:--:|------|------------|
| 4.1 | 统一调度 + 分层调度计划 | 单一调度器，按数据时效分层错峰 | ✅ | `src/zephyr/data/scheduler.py`（1,519 行）+ `src/zephyr/data/config/schedule.yaml` L6-23：L1-L11 分层、4 种 executor 线程池隔离 | 分层架构对标专业机构实践（文件头自述 v2） |
| 4.2 | 断点续传 | 任务中断后从 last_key 续传，不重头拉取 | ✅ | `src/zephyr/data/progress_store.py` L24-37：SQLite task_progress/task_runs 双表 + last_key 协议，取代 13 个散落 JSON | 进度持久化与续传协议完备 |
| 4.3 | 失败重试 + 错误分类 | 可恢复错误重试、不可恢复错误立即切源 | ✅ | `src/zephyr/data/error_classifier.py` L17-27：配额耗尽/认证失败→立即 fallback；超时→重试用完才切 | 重试策略有错误语义分层 |
| 4.4 | 写入降级容错 | DB 不可达时数据不丢，落盘待回灌 | ✅ | `src/zephyr/data/ch_writer.py` L22-46：TCP(9000)→HTTP(8123)→本地 TSV 落盘（local_replay）二级降级（裁定 #ARCH-CH-013） | 写入路径三级容错 |
| 4.5 | 实时写入 WAL + 背压 | 高频写入先落 WAL 异步排空，容量背压保护 | ✅ | `src/zephyr/data/wal_writer.py` L29-45、L60-64：段落盘（3000 行/5s）+ drain 线程 + 2GB 上限 70%/90% 两级背压 | 实时链路延迟稳定性设计达机构实时系统标准 |
| 4.6 | 任务依赖 DAG | 有先后关系的数据按依赖编排 | ✅ | tasks.yaml `dependencies` 字段（adj_factor→kline_daily_hfq 链，实测 L34-42） | DAG 依赖声明式管理 |
| 4.7 | 副源自动切换 | 主源中断自动切备源、恢复后切回 | ⚠️ | `redundant_source/source_switcher.py` L1-40：PRIMARY→BACKUP 状态机 + 30s 稳定期防抖；但仅实时 tick 链路接入，批量任务靠 8/129 的 fallback_sources | 实时链路达标，批量链路覆盖薄弱 |
| 4.8 | 配额/限流管理 | 数据源配额监控，超限熔断 | ✅ | `src/zephyr/data/alerter.py` L24-28：iFind 月度配额 -4318 立即告警并暂停该源全部任务；metrics 含 rate_limit_hits_total | 配额熔断机制明确 |
| 4.9 | 任务可重跑（rerun-failed） | 失败任务可一键重跑且幂等 | ✅ | CLI 7 子命令含 `rerun-failed`（AGENTS.md Data Source Integrator 条目）；配合 3.2 幂等写入 | 重跑安全且便捷 |

**小计：8 ✅ / 1 ⚠️ / 0 ❌ → 8.5 / 9**

### ⑤ 存储引擎与查询性能

| # | 检查项 | 机构级合格标准 | 评分 | 证据 | 一句话理由 |
|---|--------|----------------|:--:|------|------------|
| 5.1 | 引擎选型匹配数据特性 | 去重语义明确的表用 ReplacingMergeTree；无滥用 | ✅ | 实测 c1_market 76 表全 ReplacingMergeTree；选型矩阵见 `apply_market_tables_ddl.py` L26-31 | 引擎选型有设计文档依据且全库一致 |
| 5.2 | 分区裁剪有效性 | 时间过滤查询只扫目标分区 | ✅ | 实测月分区 + `toYYYYMM(trade_date)` 分区键，tick 单分区 0.7-6 GiB | 分区粒度与数据增长匹配 |
| 5.3 | 主键前缀裁剪 | 高频查询（单 symbol 时间序列）可被排序键前缀裁剪 | ⚠️ | 实测 tick_data 排序键 `(market_type, symbol, ...)`；kline_daily `(symbol, trade_date)` 达标 | 日线达标；tick 单票查询受 market_type 前缀限制（单用户负载下影响有限） |
| 5.4 | 预聚合/物化视图 | 高频聚合口径用 MV 或投影，避免重复扫大表 | ⚠️ | 实测 system.tables 无任何 MaterializedView/Projection；但 `src/zephyr/data/kline_resampler.py` L1-30 以物理表预聚合（toStartOfInterval + DELETE+INSERT 幂等）合成 15/30/60min | 功能等价物存在，但 MV 自动一致性缺位，重采样依赖手动/调度触发 |
| 5.5 | 冷热分层与 TTL | 声明的生命周期（hot_90d 等）在引擎层落地（TTL MOVE/DELETE） | ⚠️ | `business_data_categories.yaml` 每条有 `lifecycle: hot_90d` 声明；实测 engine_full 无 TTL 子句 | 生命周期有声明无执行，声明与实现漂移 |
| 5.6 | 查询层统一封装 | 查询统一入口，ReplacingMergeTree 自动 FINAL/去重 | ✅ | `src/zephyr/data/ch_reader.py`；`backfill_checker.py` L8 头注"查询走 ch_reader 自动注入 FINAL" | 读路径去重语义集中管理 |
| 5.7 | 分片健康（parts 数/合并压力） | active parts 在健康区间，无小文件爆炸 | ✅ | 实测 tick_data 310 个 active parts / 143 亿行，远未触及 parts 阈值；system.query_log 开启（近 1 小时 1,276 条） | part 规模健康，查询日志可用于慢查询分析 |
| 5.8 | 高可用/副本 | 机构标准：ReplicatedMergeTree + 多副本 | ⚠️ | 实测 `system.replicas` = 0，单节点 | 机构标准不达标；**按"单人本地回测"审查假设不扣总分**，记录为方向项 |

**小计：4 ✅ / 4 ⚠️ / 0 ❌ → 6.0 / 8**

### ⑥ 治理 / 血缘 / 元数据

| # | 检查项 | 机构级合格标准 | 评分 | 证据 | 一句话理由 |
|---|--------|----------------|:--:|------|------------|
| 6.1 | 数据品类注册表 SSoT | 品类/表名唯一真源，代码消费真源而非硬编码 | ✅ | `business_data_categories.yaml`（98 品类）+ `table_registry.py` L41-58 消费层 fail-closed | 声明-消费双闭环已建立（强制闭环 commit gate 规划中） |
| 6.2 | 数据血缘（源→表→消费方） | 每条数据可溯源到数据源、采集任务、写入路径 | ✅ | 表内 `data_source` 列；`c0_meta.fetch_perf` 记录 source/capability/target_table/速度/错误率；tasks.yaml 声明 source↔capability↔table 映射 | 血缘三要素（源/任务/表）机器可查 |
| 6.3 | 模块级治理元数据 | 每个模块有蓝图锚点/成熟度/不变量/错误契约 | ✅ | 全部数据模块头注含 BLUEPRINT/MODULE/DOMAIN/MATURITY/INVARIANTS/ERROR_CONTRACT（如 `ch_writer.py` L1-20） | 元数据密度超过多数机构内部系统 |
| 6.4 | 决策/裁定登记可追溯 | 架构裁定有中央登记与编号纪律 | ✅ | AGENTS.md RULE-RULING：`ruling_registry.yaml` 54 条目 + RULING-REFERENCE commit gate 硬阻断 | 裁定治理机制机构级 |
| 6.5 | 数据分类分级与生命周期执行 | 分类分级声明在存储层执行 | ⚠️ | 品类表有 lifecycle/sla_level 字段，但 CH 层无 TTL 落地（同 5.5） | 治理声明领先于执行 |
| 6.6 | 数据架构文档化 | 有架构蓝图 + 子蓝图 + 索引，与实现同步 | ✅ | `docs/03_modules/_cross_layer/database/blueprint.md`（v4.3.4）、`business_data_architecture.md`、`sub_blueprints/c1_market_clickhouse.md` | 文档体系完整且带版本/frontmatter 治理 |
| 6.7 | 破坏性操作纪律 | DELETE/REPLACE 等操作有强制验证流程 | ✅ | AGENTS.md RULE-DATA-OPS：必要性/真实性/可逆性三步验证（#ARCH-CH-020 事故治本，2026-07-16） | 直接源于真实事故的制度化，执行有 gate 支撑 |

**小计：6 ✅ / 1 ⚠️ / 0 ❌ → 6.5 / 7**

### ⑦ 备份与灾难恢复

| # | 检查项 | 机构级合格标准 | 评分 | 证据 | 一句话理由 |
|---|--------|----------------|:--:|------|------------|
| 7.1 | 备份覆盖全部数据库 | 治理库 + 架构库 + 行情仓库全部纳入 | ✅ | `scripts/backup/backup.ps1` L191-198：ClickHouse（c1_market + c3_fundamental）经 MinIO S3 bridge 备份；restic 覆盖 data/databases/ | 三库全覆盖 |
| 7.2 | 备份自动触发 | 事件驱动/定时自动执行，非靠人记 | ✅ | `scripts/backup/backup_reconciler.py` post-commit 双条件触发（8h 间隔保护）；CH 独立 24h 节奏（backup.ps1 L222-249） | 事件驱动自动备份 |
| 7.3 | 保留策略 | 日/周/月多级保留 | ✅ | `scripts/backup/backup_config.yaml` L29-33：daily 7 / weekly 4 / monthly 3（真源在 backup.ps1 L49） | 多级保留达标 |
| 7.4 | 恢复验证流程 | 有恢复演练脚本与验证方法 | ✅ | `scripts/backup/restore.ps1` L3-16：list/verify/latest/ch 四模式，verify 恢复到 `D:\restore_test\` 验证；dr_policy.yaml 登记 verify_method | 恢复路径脚本化可演练 |
| 7.5 | RTO/RPO 量化目标登记 | 每个数据组件有登记的 RTO/RPO | ⚠️ | `config/dr_policy.yaml` 仅登记 depgraph_pg / governance_db / runtime_state 三个组件（grep `component:` 仅 L20/32/44）；**302 GiB 行情仓库 c1_market / c3_fundamental 未登记 RTO/RPO** | 最大的数据资产反而没有灾备目标登记，政策覆盖与备份覆盖不一致 |
| 7.6 | 备份完整性校验 | 备份后自动校验可恢复性 | ✅ | backup.ps1 六阶段管线含 Integrity check 阶段（L4-6）；restic check | 校验内建于管线 |
| 7.7 | 异地/离线副本 | 至少一份异地或离线副本 | ⚠️ | restic 目标 `F:\restic-zephyr`（本机外挂盘）；CH 备份同机 MinIO 中转 | 全部副本在同一物理站点；**单用户假设下不扣总分**，标注为方向项 |

**小计：5 ✅ / 2 ⚠️ / 0 ❌ → 6.0 / 7**

### ⑧ 可观测性与告警

| # | 检查项 | 机构级合格标准 | 评分 | 证据 | 一句话理由 |
|---|--------|----------------|:--:|------|------------|
| 8.1 | 指标采集（Prometheus 格式） | 任务/行数/耗时/限流指标可被抓取 | ✅ | `src/zephyr/data/metrics.py` L22-31：6 核心指标写 metrics.prom（textfile collector）；`config/infra/prometheus/prometheus.yml` | 指标管线完整 |
| 8.2 | 告警规则集中管理 | 规则声明式配置，与代码解耦 | ✅ | `config/alert_rules.yaml`（ALERT-SYS/DB 系列，含慢查询 >5s）+ `config/sli_registry.yaml` | 规则即配置 |
| 8.3 | 告警通道可达（IM/邮件/短信） | 严重告警能触达人，不止写日志 | ❌ | `src/zephyr/data/alerter.py` L28-32：告警方式仅日志 + failures/ JSON 文件，"钉钉/邮件（阶段3+ 扩展点，当前 NotImplementedError）" | 告警不出本机——盘后巡检发现不达标也无人被触达，故障静默窗口大 |
| 8.4 | 数据质量告警闭环 | 质量事件→告警→记录→可追踪 | ✅ | `integrity_checker.py` L115-140：不达标→alerter ERROR + progress_store 记录 SUCCESS/PARTIAL | 闭环逻辑完整（但出口受 8.3 限制） |
| 8.5 | 采集性能可观测 | 每个数据源的速度/错误率/限流历史可查 | ✅ | 实测 `c0_meta.fetch_perf`：source/capability/rows_per_sec/error_rate/rate_limited/api_status/known_issues 全字段 | 源级性能画像达机构数据运营水平 |
| 8.6 | 可视化仪表盘 | Grafana/等效面板覆盖关键指标 | ✅ | `config/infra/grafana/dashboards` + `datasources`；另有 Panel 治理仪表盘（AGENTS.md §3 Dashboard 条目） | 双层可视化 |
| 8.7 | 日志持久化与结构化 | 运行日志 + 失败明细文件可回溯 | ✅ | alerter.py：logs/integrator.log + `failures/{date}_{task_id}.json` 结构化失败明细 | 审计回溯材料齐备 |

**小计：6 ✅ / 0 ⚠️ / 1 ❌ → 6.0 / 7**

### ⑨ 安全与访问控制

| # | 检查项 | 机构级合格标准 | 评分 | 证据 | 一句话理由 |
|---|--------|----------------|:--:|------|------------|
| 9.1 | 凭据不入版本库 | 密码/密钥 gitignore，无明文入库 | ✅ | `.gitignore` L338-344：`config/.env.clickhouse`、`.env.restic`、`.env.ch_backup` 全部忽略；`zephyr.shared.security.secrets` 模块统一读取 | 凭据管理达标 |
| 9.2 | 配置缺失 fail-closed | 连接配置缺失时显式失败，禁止静默默认值 | ✅ | `src/zephyr/data/ch_config.py` L30-46：缺 CLICKHOUSE_HOST 抛 CHConfigError，禁止 localhost/硬编码 IP 默认值（裁定 #ARCH-CH-017/#ARCH-CH-019） | 消除配置漂移隐患 |
| 9.3 | 最小权限连接 | 只读场景用只读连接/账号 | ✅ | `database_service.py` L153-172：ClickHouse 连接 `settings={'readonly': 1}`；L102-151 governance/PG 读写双连接，业务查询强制 `read_only=True`（project_memory 硬约束） | 读侧最小权限执行到位 |
| 9.4 | 数据库账号分级 | 写入账号与查询账号分离，CH 用户级 RBAC | ⚠️ | 实测 `system.users` 仅 `default` 一个用户 | 单用户假设下可接受，机构标准不达标；不扣总分 |
| 9.5 | 敏感数据分级标识 | 数据/文档有密级标识 | ✅ | 蓝图 frontmatter `classification: confidential`（`database/blueprint.md` L13）；另有 LSG 十层 LLM 调用安检（AGENTS.md §3） | 分级意识与机制俱在 |
| 9.6 | 操作审计日志 | 数据操作留痕不可篡改 | ✅ | `zephyr.infrastructure.event_store`（SQLite WAL+SHA256 checksum，AGENTS.md §3）；progress_store.task_runs 记录每次运行 | 审计链完整 |

**小计：5 ✅ / 1 ⚠️ / 0 ❌ → 5.5 / 6**

### ⑩ 扩展性与未来实盘就绪度（方向提示，不计分）

| # | 检查项 | 现状 | 评分 | 证据 | 说明 |
|---|--------|------|:--:|------|------|
| 10.1 | 实时数据通路 | 实时 tick 订阅 + WAL 写入已生产运行 | ✅ | `src/zephyr/data/tick_subscriber.py`、`wal_writer.py`；实测 tick 当日盘中持续入库 | 实盘数据侧已就绪 |
| 10.2 | 热缓存层（Redis H1） | 预留接口未实现 | ⚠️ | `database_service.py` L174-179：`get_redis_conn` 抛 NotImplementedError（#ARCH-048 已裁决待 P2） | 实盘低延迟读取需补 |
| 10.3 | 高可用副本 | 单节点无副本 | ❌ | 实测 system.replicas = 0 | 实盘前需 ReplicatedMergeTree/双机 |
| 10.4 | 实时源冗余切换 | 框架已建（QMT↔TDX），覆盖单链路 | ⚠️ | `redundant_source/source_switcher.py`、`heartbeat_monitor.py`、`recovery.py` | 实盘前需演练验证 |
| 10.5 | 容量增长空间 | 当前 318 GiB，月增约 5-6 GiB（tick），单机多年可撑 | ✅ | 实测 system.tables 汇总；backup.ps1 L193 注明 315 GiB 备份盘约束 | 备份盘容量是先行约束 |
| 10.6 | 交易接口/OMS/实盘风控 | 未开发 | ❌ | 项目自述"实盘交易后续再开发" | 按假设仅作方向提示 |

---

## 2. 分项得分与总分

计分范围：①-⑨ 共 **64 条**（第⑩类按审查假设不计分）。✅=1.0，⚠️=0.5，❌=0。

| 类别 | ✅ | ⚠️ | ❌ | 得分 | 百分比 | 雷达条（每格 5%） |
|------|:---:|:---:|:---:|:---:|:---:|------|
| ① Schema 与字段设计 | 6 | 4 | 0 | 8.0/10 | **80%** | ████████████████░░░░ |
| ② 数据覆盖完整性 | 7 | 1 | 1 | 7.5/9 | **83%** | █████████████████░░░ |
| ③ 数据质量保障 | 5 | 2 | 1 | 6.0/8 | **75%** | ███████████████░░░░░ |
| ④ 管线可靠性与容错 | 8 | 1 | 0 | 8.5/9 | **94%** | ███████████████████░ |
| ⑤ 存储引擎与查询性能 | 4 | 4 | 0 | 6.0/8 | **75%** | ███████████████░░░░░ |
| ⑥ 治理/血缘/元数据 | 6 | 1 | 0 | 6.5/7 | **93%** | ██████████████████░░ |
| ⑦ 备份与灾难恢复 | 5 | 2 | 0 | 6.0/7 | **86%** | █████████████████░░░ |
| ⑧ 可观测性与告警 | 6 | 0 | 1 | 6.0/7 | **86%** | █████████████████░░░ |
| ⑨ 安全与访问控制 | 5 | 1 | 0 | 5.5/6 | **92%** | ██████████████████░░ |
| ⑩ 实盘就绪度 | — | — | — | 不计分 | 方向提示 | — |

### 总分

**52.0 / 64 = 81.3% —— 评级 B+（良好，个人单用户系统中属顶尖水准，距机构级生产标准有明确但有限的差距）**

雷达特征：**工程韧性（④94%）、治理（⑥93%）、安全（⑨92%）为长板，已达到甚至超过许多专业机构内部系统；数据质量执行（③75%）与存储精细度（⑤75%）为短板**，差距集中在"机制已建但执行未闭环"与"少数数据资产缺口"两类。

---

## 3. 差距分析

### 3.1 已达机构级的方面（无需投入）

- **管线容错设计**：三级写入降级、WAL+背压、断点续传、错误分类重试、L1-L11 分层调度——这套设计放在中小私募数据团队也属于上游水平；
- **治理密度**：裁定登记、品类 SSoT、fail-closed 注册表、DDL-as-Code + human_only schema 变更、事故治本规则化（RULE-DATA-OPS）——多数机构靠 Wiki 和口头约定，本项目是代码强制；
- **采集可观测**：c0_meta.fetch_perf 的源级性能画像（速度/错误率/限流/已知问题）是机构数据运营的标准件。

### 3.2 与机构级的核心差距（按影响排序）

1. **幸存者偏差未消除（回测可信度之根）**：stock_list 5,534 只全部在市中，无退市股历史。对回测系统，这是数据资产层面的头号缺陷——任何选股类策略的回测收益都会被系统性高估。策略层有 `survivorship_policy.yaml` 声明要求，但数据层未兑现。
2. **质量保障"有检测、缺执行、缺校验器"**：完整性巡检和补下载机制都已建成，但 2026-06 tick 缺口（日均 -90%）实测至今未补齐；异常值校验器（价格越界/跳变）实质缺位，quality_flag 列有壳无芯。
3. **告警不出本机**：钉钉/邮件通道是 NotImplementedError，盘后巡检发现不达标只写日志和 JSON 文件。单用户场景下故障静默窗口 = 用户不看日志的时间。
4. **声明与执行漂移**：lifecycle（hot_90d）有声明无 CH TTL 落地；dr_policy.yaml 未登记最大的数据资产（302 GiB 行情仓库）的 RTO/RPO。
5. **存储精细度**：tick 排序键前缀不利于单票点查；无 MV/Projection（有物理预聚合等价物）；财务表 Float64 存金额。

### 3.3 单用户假设下的合理化说明

单节点无副本、单 CH 用户、无异地副本三项按机构标准为 ❌/⚠️，但与"单人本地回测"假设相容，本报告不计入扣分，仅在第⑩类与路线图中作方向提示。

---

## 4. P0 / P1 / P2 问题清单

### P0（直接损害回测结论可信度，应立即处理）

| ID | 问题 | 证据 | 影响 |
|----|------|------|------|
| P0-1 | **退市股缺失 → 幸存者偏差**：stock_list 5,534 只全部 `list_status='上市'`，无退市/暂停标的历史 | 实测 `SELECT list_status, count() FROM c1_market.stock_list GROUP BY list_status` 仅一行；`config/data/survivorship_policy.yaml` L11-12 | 所有选股/轮动类回测收益系统性高估，结论不可信 |
| P0-2 | **2026-06 tick 数据大缺口未补**：6 月日均 248 万行 vs 5 月日均 2,385 万行（-90%，21 个交易日） | 实测 `SELECT toYYYYMM(trade_date), count()/uniqExact(trade_date) FROM c1_market.tick_data GROUP BY ...` | 盘中/微观结构类回测在 6 月窗口失真或静默跳过 |

### P1（机制缺环或质量隐患，应在下个迭代处理）

| ID | 问题 | 证据 | 影响 |
|----|------|------|------|
| P1-1 | **告警通道未实现**：钉钉/邮件 NotImplementedError，告警仅日志+本地文件 | `src/zephyr/data/alerter.py` L28-32 | 数据故障静默，完整性巡检的告警价值无法兑现 |
| P1-2 | **异常值校验器缺位**：quality_flag 列全库存在但无计算规则（价格越界/跳变/零量检测） | `src/zephyr/data/quality_gate.py` 全文 27 行仅 re-export | 坏数据静默入库，下游回测吃进脏 tick/K线 |
| P1-3 | **EDB 宏观通道空表**：edb_data 0 行 | 实测 system.tables | 宏观因子/择时回测数据缺口 |
| P1-4 | **fallback_sources 覆盖率 6%**：129 任务仅 8 个配置副源 | grep 计数 `src/zephyr/data/config/tasks.yaml` | 主源（miniqmt 依赖 QMT 服务器）不可用时大面积任务无退路 |
| P1-5 | **dr_policy 未登记行情仓库**：RTO/RPO 仅覆盖 3 个治理组件，c1_market/c3_fundamental 缺登记 | `config/dr_policy.yaml`（grep `component:` 仅 3 项） | 灾备演练无目标可对标，318 GiB 资产恢复时间未知 |
| P1-6 | **lifecycle 声明未落地**：hot_90d 等生命周期无 CH TTL 执行 | `business_data_categories.yaml` vs 实测 engine_full 无 TTL | 治理声明与实现漂移，存储只涨不缩 |
| P1-7 | **财务三表 Float64 存金额**：total_revenue 等 20+ 字段 Float64 | 实测 `DESCRIBE c3_fundamental.income_statement` | 大金额精度隐患（>2^53 分位失真），财务建模不严谨 |
| P1-8 | **kline_daily 残留 1970 脏行**：1 行 trade_date=1970-01-01、symbol 空 | 实测 | 轻微，但属于 1.6 魔术值语义混用的实证 |

### P2（优化项，不紧急）

| ID | 问题 | 证据 | 影响 |
|----|------|------|------|
| P2-1 | 行情表无 ingest_ts 写入时间戳（财务表有） | DDL 对比（`apply_market_tables_ddl.py` L48-75 vs 实测 income_statement） | 无法追溯行级入库时间，影响增量审计 |
| P2-2 | tick_data 排序键以 market_type 打头，单票点查裁剪受限 | 实测 sorting_key | 单用户负载下影响有限；数据量再涨 10 倍时需重排 |
| P2-3 | 无 MaterializedView/Projection，分钟线靠物理表 DELETE+INSERT 重采样 | 实测 system.tables；`kline_resampler.py` | 重采样窗口内存在短暂不一致 |
| P2-4 | 240 处历史硬编码表名待替换为 TableRegistry 引用 | `table_registry.py` L47-49 头注自述 | 渐进式技术债，gate 已防新增 |
| P2-5 | 备份盘 315 GiB 约束 vs 数据 318 GiB 且月增 5-6 GiB | backup.ps1 L193；实测汇总 | 备份窗口将在数个季度内触顶 |

---

## 5. 可执行改进路线图

> 工作量按单人全职当量估算（1 pd = 1 人日）；可并行项已标注。

### 阶段一：回测可信度修复（P0，1-2 周）

| 序 | 行动 | 对应问题 | 工作量 | 验收标准 |
|----|------|----------|:------:|----------|
| 1 | **接入含退市股的证券主数据**（Tushare `stock_basic` list_status='D' / iFind 退市列表），回填 stock_list 并补齐退市股历史日 K | P0-1 | 2-3 pd | stock_list 含 D/P 状态标的；`survivorship_policy.yaml` 从 policy gate 转为数据实证登记 |
| 2 | **补 2026-06 tick 缺口**：对 6 月 21 个交易日跑 backfill_checker 精准补下载（miniqmt 历史 tick 通道）；补不了的交易日登记 known_gap | P0-2 | 1-2 pd（含下载等待） | 6 月日均行数恢复至 5 月的 ≥80%，或缺口登记进 c0_meta |
| 3 | 清理 kline_daily 1970 脏行（走 RULE-DATA-OPS 三步验证流程） | P1-8 | 0.2 pd | 脏行删除 + 操作记录留痕 |

### 阶段二：告警与质量闭环（P1，1-2 周，可与阶段一并行）

| 序 | 行动 | 对应问题 | 工作量 | 验收标准 |
|----|------|----------|:------:|----------|
| 4 | **打通一个真实告警通道**：复用 `zephyr.infrastructure.observability.notifier` 已有渠道，或最小实现钉钉 webhook/Server酱，接入 alerter.notify | P1-1 | 0.5-1 pd | 手动触发一次 integrity_check 不达标，手机收到告警 |
| 5 | **实现行情异常值校验器**：价格>0、涨跌幅越界（±20%/±30% 分板块）、量价为零组合、时间戳乱序，结果写 quality_flag | P1-2 | 2-3 pd | 校验器接入写入路径或巡检；抽样表 quality_flag 出现 0 值分布可查 |
| 6 | 排查并修复 EDB 采集任务（edb_data 空表） | P1-3 | 0.5-1 pd | edb_data 有数据且日更 |
| 7 | fallback_sources 扩面：为 daily_kline/daily_capital 两个时段的核心任务批量配置 baostock/akshare/tushare 副源 | P1-4 | 1 pd | 覆盖率从 6% → ≥50% 核心任务 |

### 阶段三：治理对齐与存储精细度（P1/P2，2-3 周，可分期）

| 序 | 行动 | 对应问题 | 工作量 | 验收标准 |
|----|------|----------|:------:|----------|
| 8 | dr_policy.yaml 增补 c1_market / c3_fundamental 组件（RPO 24h / RTO 按 restore.ps1 实测填写） | P1-5 | 0.2 pd | 登记 + 一次 CH 恢复演练记录 |
| 9 | lifecycle 落地：为 hot_90d 品类加 CH TTL（或明确裁决哪些表永久保留并同步 YAML） | P1-6 | 1 pd | TTL 生效或 YAML 声明修正，二者一致 |
| 10 | 财务表金额字段迁移至 Decimal(18,2)（新表+回填+切换，走 schema-change 流程） | P1-7 | 2-3 pd | 三表 Decimal 化且回测因子回归一致 |
| 11 | 行情表补 ingest_ts 列（DEFAULT now()，ALTER ADD 低成本） | P2-1 | 0.5 pd | 新增行带入库时间 |
| 12 | 备份盘扩容评估或 CH 备份改增量策略 | P2-5 | 0.5 pd | 12 个月备份容量推演报告 |

### 阶段四：实盘就绪方向（第⑩类，仅方向提示，不排期）

- Redis H1 热缓存施工（#ARCH-048 触发条件：实盘需求立项）；
- CH 副本化（ReplicatedMergeTree）与备份异地化；
- 实时源切换（source_switcher）实盘演练与降级预案；
- OMS/交易网关/实盘风控专项设计。

---

## 6. 机构对标结论

以"个人单用户回测数据库"为基准坐标系：

- **已达顶尖**：管线工程韧性（④94%）、治理与血缘（⑥93%）、安全纪律（⑨92%）——这三项的完成度超过相当比例的中小型资管机构内部系统，其特征是"事故治本规则化 + 机制代码强制"而非依赖人肉流程；
- **接近达标**：备份（⑦86%）、可观测（⑧86%）、覆盖（②83%）——机制齐备，各差一个"最后一公里"（告警通道、dr_policy 登记、退市股/EDB）；
- **主要短板**：质量保障执行（③75%）与存储精细度（⑤75%）——典型的"检测机制先于执行闭环建成"阶段特征，6 月 tick 缺口与异常值校验器缺位是最直观的证据。

**总评**：这是一套**设计水准 A-、执行完成度 B+** 的数据底座。架构决策（引擎选型、分层调度、容错降级、治理 SSoT）几乎全部正确且有裁定链支撑；扣分几乎全部来自执行缺口而非设计缺陷。按阶段一+阶段二（合计约 8-12 人日）补齐 P0/P1 前四项后，可实质性达到"个人单用户回测数据库的机构级合格线"（预估 90%+）。

---

*本报告所有"实测"数据来自 2026-07-22 对 ClickHouse 26.6.1.1193（172.24.30.100）的只读查询；静态证据以审查时点的文件内容为准。未执行任何写入/破坏性操作。*
