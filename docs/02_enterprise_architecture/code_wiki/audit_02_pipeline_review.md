---
module_id: AUDIT-DB-PIPELINE-REVIEW
title: "数据下载与集成管线深度审查"
doc_type: audit_report
rule_form: data
status: active
version: 1.0.0
date: 2026-07-23
owner: ZephyrAlpha-Owner
ttl: permanent
language: zh
created_by: agent
---

# 数据下载与集成管线深度审查（Audit-02 · Pipeline Review）

> 审查对象：`src/zephyr/data/`（数据源集成器 MOD-L00-004 + 冗余源 MOD-L00-005）
> 审查场景：**仅回测用途**（个人单用户量化系统，实盘交易后续再开发）
> 审查方式：静态代码审查 + ClickHouse/进度库只读实测（CH `172.24.30.100:8123/9000` 本次可达，实测成功）
> 审查日期：2026-07-22（CH 服务器时间 2026-07-22 15:32）

---

## 目录

- [1. 总体结论](#1-总体结论)
- [2. 机制评分总表](#2-机制评分总表)
- [3. 分机制详评](#3-分机制详评)
  - [3.1 断点续传 progress_store](#31-断点续传-progress_store)
  - [3.2 熔断与故障切换](#32-熔断与故障切换)
  - [3.3 重试与错误分类](#33-重试与错误分类)
  - [3.4 质量门 quality_gate](#34-质量门-quality_gate)
  - [3.5 去重 news_dedup 与库表层面](#35-去重-news_dedup-与库表层面)
  - [3.6 回填 backfill_checker](#36-回填-backfill_checker)
  - [3.7 完整性校验 integrity_checker](#37-完整性校验-integrity_checker)
  - [3.8 写入性能 buffered_writer / ch_writer / wal_writer](#38-写入性能-buffered_writer--ch_writer--wal_writer)
  - [3.9 监控告警 metrics / alerter / health_snapshots](#39-监控告警-metrics--alerter--health_snapshots)
  - [3.10 调度 scheduler](#310-调度-scheduler)
- [4. 实测数据现状（2026-07-22）](#4-实测数据现状2026-07-22)
- [5. 数据清单盘点与覆盖缺口](#5-数据清单盘点与覆盖缺口)
- [6. 问题清单（P0/P1/P2）](#6-问题清单p0p1p2)
- [7. 改进方向（回测场景优先级排序）](#7-改进方向回测场景优先级排序)

---

## 1. 总体结论

管线整体成熟度**高于同类个人项目**：拥有 128 个声明式任务（`src/zephyr/data/config/tasks.yaml`，grep 实测 task_id 计数 128）、12 档分层调度（`src/zephyr/data/config/schedule.yaml` L22-107）、SQLite 断点续传、主副源 failover、攒批写入、WAL 主动落盘、周末回填与每日巡检，且 ClickHouse 内实测行情数据量级巨大（tick_data 143.2 亿行、kline_1min 38.7 亿行，2026-07-22 实测 `system.tables`）。治理意识（SSoT 表名注册表、能力契约校验、裁定编号体系）在代码中真实落地。

但按专业回测系统标准衡量，存在**四个结构性短板**：

1. **数值级质量门缺失**：写入路径无任何 OHLC 合法性/异常值/停牌检测，`quality_flag` 恒为默认值 1（见 §3.4）。
2. **失败面偏大**：进度库实测 126 个任务中 25 个 FAILED、8 个卡死 RUNNING（见 §4），多数源于 QMT 不可用时无副源兜底 + akshare 接口漂移。
3. **fallback 配置覆盖率低**：128 个任务仅 8 处配置 `fallback_sources`（grep 实测），冗余源切换器（SourceSwitcher 等）仅服务实时 tick 链路，批下载链路无心跳级熔断。
4. **关键表存在空洞**：`c1_market.l2_tick` 表不存在但有任务引用；`edb_data`/`realtime_snapshot`/`sector_snapshot` 建表后 0 行；tick_data 昨日（2026-07-21）实测 0 行。

---

## 2. 机制评分总表

| # | 机制 | 评分 | 一句话结论 | 关键证据 |
|---|------|------|-----------|---------|
| 3.1 | 断点续传 | ✅（有小瑕疵） | SQLite WAL + UPSERT + 运行历史双表，线程安全设计严谨 | `progress_store.py` L8（INVARIANTS）、L77-118 |
| 3.2 | 熔断与故障切换 | ⚠️ | 任务级 failover 有但覆盖率 6%；源级熔断可用；实时链路切换器设计完整但仅 tick 链路消费 | `scheduler.py` L818-857；`redundant_source/` |
| 3.3 | 重试与错误分类 | ✅（有盲区） | 双层重试（provider 策略 + 任务级源切换）+ 关键词错误分类，但分类器盲区导致 unknown 错误处理模糊 | `error_classifier.py` L42-98；`provider_base.py` L241-294 |
| 3.4 | 质量门 | ❌ | 数据管线写入路径无质量门；真源存在但零消费 | `quality_gate.py` L17-27；grep 实测零调用方 |
| 3.5 | 去重 | ✅（表级依赖引擎） | 新闻 MD5 标题去重 + 库内 news_id 主键去重；行情靠 ReplacingMergeTree/写前 DELETE，实测近 3 日无重复 | `news_dedup.py` L124-198；`scripts/ch/apply_market_tables_ddl.py` L75-77 |
| 3.6 | 回填 | ✅（有阈值风险） | 查 CH 实际行数发现缺口、动态发现全表、精准补下载，设计优秀；tick 阈值硬编码 500 万行有风险 | `backfill_checker.py` L17-32、L53-54 |
| 3.7 | 完整性校验 | ⚠️ | 仅"当日行数 ≥ 历史 7 日均值×0.5"单维检查，无数值质量/日内缺口/跨表一致性 | `integrity_checker.py` L17-28 |
| 3.8 | 写入性能 | ✅ | 攒批写入（50000 行/30s）+ TCP→HTTP→本地落盘三级降级 + 实时链路主动 WAL，且经历过真实事故迭代 | `buffered_writer.py` L17-38；`wal_writer.py` L17-38 |
| 3.9 | 监控告警 | ⚠️ | Prometheus 指标 + /health /metrics /status 端点 + 失败冷却去重完善；但告警通道只有日志+文件（钉钉/邮件 NotImplemented），health_snapshots 仅 1 个陈旧文件 | `alerter.py` L28；`health_snapshots/` 仅 health_20260625005037.json |
| 3.10 | 调度 | ✅ | APScheduler + DAG + 交易日历守卫 + 能力契约启动校验 + 三个守护线程（CH 探活/落盘回灌/破损 part 隔离） | `scheduler.py` L1134-1247 |

图例：✅ 达标 / ⚠️ 可用但有明确缺陷 / ❌ 缺失或失效

---

## 3. 分机制详评

### 3.1 断点续传 progress_store

**评分：✅（有小瑕疵）**

- **协议清晰**（`src/zephyr/data/progress_store.py` L24-27）：任务启动取 `last_key` → 每批写完更新 → 中断后从 `last_key` 续跑。双表设计：`task_progress`（每任务最新状态）+ `task_runs`（每次运行明细，L82-115）。
- **线程安全处理有据可查**：`check_same_thread=False` + `threading.Lock` 串行化 + WAL 模式 + autocommit（L8、L68-81），注释明确指向修复过的 SQLITE_MISUSE 事故。
- **幂等**：`save_progress` 为 UPSERT（L186-194），`start_run` 每次插新行（L203-217）。
- **实测**（只读进度库 `data/integrator_progress.db`）：126 任务登记，近 7 天 8884 次 task_runs 记录，机制在真实运转。

**瑕疵：**

1. **卡死 RUNNING 状态**：实测 8 个任务 `last_status='RUNNING'` 且超 24 小时未更新（如 `daily_valuation_full_refresh` 2026-07-20 01:29 起、财报四任务 2026-07-21 18:02 起）。`save_progress` 在 `_fetch_and_write` 每批循环内以 RUNNING 写入（`scheduler.py` L1097-1100），进程崩溃后无人清理，RUNNING 永久残留，且无"卡死检测"逻辑。
2. **last_key 语义模糊**：`_compute_start_date`（`scheduler.py` L1013-1025）把 `last_key`（日期字符串）直接当作下次 `payload.start`，即**同一天会重复拉取**，幂等性依赖 MergeTree 写前 DELETE（L1045-1066）或 ReplacingMergeTree 引擎去重兜底。跨日部分写入失败时，`last_key` 已推进但当日数据不完整——缺口只能靠 L10 周末回填（按行数阈值）事后发现，粒度偏粗。
3. **fail-open 风险**：`get_last_key` 查询失败返回 None（L136-138），上层将其解释为"任务从未运行"→ 全量重拉。对 tick/K 线类大表，一次 SQLite 读失败可能触发不必要的全量下载。

### 3.2 熔断与故障切换

**评分：⚠️（分层看：源级熔断可用，任务级 failover 覆盖不足，链路级切换器未接入批管线）**

三层机制并存：

1. **任务级 failover（批管线主通道）**：`scheduler.run_task` 构造"主源 + fallback_sources"尝试列表（`scheduler.py` L818-826），不可恢复错误立即切副源（L845-856）。**但覆盖率极低**：grep 实测 128 任务仅 8 处 `fallback_sources` 配置。实测失败任务（§4）中 `shareholder/express_report/earnings_forecast/dividend/kline_weekly/kline_monthly/kline_index` 等 miniqmt 任务均无副源，QMT 不在线时整批失败。
2. **源级熔断**：`policy.enabled=False` 时任务跳过并告警（`scheduler.py` L1002-1009），配合 CLI `integrator pause <source>`；`alerter.check_quota_exhausted` 对 iFind -4318/-4309 配额耗尽发 CRITICAL 并建议暂停（`alerter.py` L218-242）。
3. **链路级切换器（redundant_source/）**：`SourceSwitcher`（PRIMARY→BACKUP→RECOVERY_WAIT 状态机 + 30s 稳定期防抖，`redundant_source/source_switcher.py` L69-199）、`HeartbeatMonitor`（tick 超时 10s + CH ping 连续 3 次失败判死，`heartbeat_monitor.py` L31-33）、`SQLiteFallback`（CH 不可达写本地，50 万行 FIFO 上限 + INSERT OR REPLACE 幂等，`sqlite_fallback.py` L32、L98）、`RecoveryManager`（CH 恢复后分批回灌 + 指数退避 2s→60s，`recovery.py` L29-33）。**设计完整但消费面窄**：grep 实测仅 `tick_subscriber.py` L195 可选接入 HeartbeatMonitor；批下载 scheduler 链路不使用这些组件。对回测场景这不是 P0，但说明"冗余源"子系统与"集成器"子系统是两套未打通的韧性体系。
4. **CH 写入侧降级**（属于故障切换的另一半）：`ch_writer` TCP(9000)→HTTP(8123)→本地 TSV 落盘三级降级，落盘文件由 scheduler 守护线程每 30 分钟回灌（`scheduler.py` L385-419），实测 `data/local_fallback/` 存在 `c1_market__kline_sector`、`c1_market__tick_data` 等待回灌目录——降级链真实被触发过且在运转。

### 3.3 重试与错误分类

**评分：✅（有盲区）**

- **双层重试**：
  - Provider 内层：`_call_with_policy`（`provider_base.py` L241-294）按策略重试，退避支持 exponential/fixed/jittered（L310-324），限流按 RPM 休眠（L296-307）。策略真源为 `architecture_model/data/data_sources_registry.yaml` 派生的 `config/policies.yaml`（L6-7 声明禁止手改），per-source 定义 max_retries/retry_on/backoff（如 ifind 3 次、akshare 5 次）。
  - 任务外层：重试耗尽后按错误分类决定是否立即切副源（`scheduler.py` L845-856）。
- **错误分类器**（`error_classifier.py`）：不可恢复（配额/-4318/-4309/废弃/401/403/auth，L42-58）→ 立即 fallback；可恢复（Timeout/ConnectionError/502/503，L61-76）→ 重试用完才 fallback；unknown → 按可恢复处理（L21 注释）。
- **实测盲区**：当前最高频失败错误"无法连接xtquant服务，请检查QMT-投研版或QMT-极简版是否开启"（进度库实测，见 §4）不匹配任何关键词 → 归为 unknown。对"QMT 进程未启动"这种**持续整个交易日的确定性故障**，unknown=可恢复语义会让任务在每个调度时段重复失败（实测同一任务 08:30/10:00/11:00 多次 FAILED），浪费重试预算且刷告警。akshare 接口漂移类错误（`module 'akshare' has no attribute ...`，实测 2 例）同样归为 unknown——这类实际是**不可恢复**（代码级缺陷），应归类后阻断而非反复重试。

### 3.4 质量门 quality_gate

**评分：❌（管线写入路径无质量门）**

这是本次审查发现的最大结构性缺口：

1. `src/zephyr/data/quality_gate.py` 仅 27 行，是 re-export 壳（L17-27），真源在 `zephyr/gov_enforcement/rule_enforcement/quality_gate.py`（含 `QualityReport` L68、`DataQualityGate` 抽象类 L81、行情质量评分/停牌涨跌停检测职责声明）。
2. **grep 实测消费方为零**：`src/zephyr/data/` 与 `src/zephyr/trading/` 下无任何模块调用质量门；唯一 import 来自一个测试（`tests/governance/trading/test_e2e_pipeline.py` L372）和卫星引擎的 `__init__`。scheduler 的 `_fetch_and_write`（L1068-1101）在写入前只做新闻去重，无任何数值校验。
3. **quality_flag 形同虚设**：DDL 中 tick_data/kline_daily 均有 `quality_flag UInt8 DEFAULT 1 COMMENT '质量标记'`（`scripts/ch/apply_market_tables_ddl.py` L72、L99），但 grep 实测所有 provider 要么不写该列（走 DEFAULT 1），要么无置 0 逻辑——**全库数据 quality_flag 恒为 1**，异常数据无任何标记通道。
4. 后果（回测场景敏感）：脏 tick/缺 OHLC 合法性校验的 K 线会直接进入回测，产生虚假信号。专业回测系统至少要求：价格非负、high≥low、volume≥0、时间戳在交易时段内、涨跌停边界校验、重复时间戳检测。

### 3.5 去重 news_dedup 与库表层面

**评分：✅（新闻双层去重可靠；行情依赖引擎去重，已吸取历史事故教训）**

- **应用层去重**（`news_dedup.py`）：标题 strip+lower 后 MD5（L124-131），查 CH 最近 7 天已有标题哈希 + 批内去重（L134-198），fail-open 设计（查询失败跳过去重不阻断写入，L27）。调度器对 11 个新闻任务统一生效（`scheduler.py` L1083-1085 按表名匹配 `news_data`）。
- **库表层去重**：
  - news_id = MD5(source+title+publish_time)（`news_dedup.py` L114-116），news_data 为 ReplacingMergeTree（实测 `system.tables`）。
  - 行情表全部 ReplacingMergeTree：tick_data `ORDER BY (market_type, symbol, trade_date, timestamp, price)`（`scripts/ch/apply_market_tables_ddl.py` L77——**price 已入排序键**，即 RULE-DATA-OPS 记载 #ARCH-CH-020 事故后的修复状态）；kline_daily `ORDER BY (symbol, trade_date)`（L108）。
  - 非 Replacing 的 MergeTree 表（restricted_shares/share_change/rights_issue/share_unlock/disclosure_plan/analyst_forecast/equity_pledge_detail，实测引擎列）靠写前 DELETE 幂等（`scheduler.py` L1045-1066），DELETE 条件含分区键 trade_date 类列，成本可控。
- **实测**（只读 CH，2026-07-22）：news_data 近 3 日 `count()=6509, uniqExact(news_id)=6509`，**零重复**；tick_data 当日 `count()=114596, uniqExact(全排序键)=114596`，**零重复**。
- **注意点**：ch_reader 查询自动注入 FINAL（`backfill_checker.py` L91 注释），实测 FINAL 在超大表（tick_data 143 亿行、kline_1min 38.7 亿行）上导致若干查询失败（本次审查中 tick_data 全表 max、kline_1min、income_statement 等查询 TCP+HTTP 均失败），巡检/回填脚本对大表的 FINAL 查询存在超时风险。

### 3.6 回填 backfill_checker

**评分：✅（设计优秀，阈值有硬编码风险）**

- **不依赖 last_key，直接查 CH 实际行数**（L17-32 设计理念，裁定 #ARCH-BACKFILL-001）——这是与 last_key 机制的关键互补，能发现"进度记录成功但数据实际缺失"的隐性缺口。
- **动态发现全表**：`_discover_backfill_tables`（L265-293）从 tasks.yaml 自动发现所有表，新表注册任务即自动纳入；日期列用 `DESCRIBE TABLE` 按优先级推断（L215-241），阈值 = 近 7 天日均行数 × 0.5（L244-262）。
- **分层补下载**：tick_data 走 QMT 专用通道（分 09:30-10:00 / 10:00-15:30 两时段 + 50 标的/批攒批，L416-511）；其他表通过 `scheduler.run_task(task_id)` 重跑（L568-578）。调度挂接在 L10 周末档（周一 02:00，`schedule.yaml` L86-90）。
- **实测印证其必要性**：tick_data 昨日（2026-07-21）实测 0 行（今日 114,596 行为盘中部分数据），正是 L10 机制要捕获的场景。
- **风险**：
  1. tick 缺失阈值硬编码 500 万行/日（L53-54），注释称正常约 2000 万行/日——若市场标的扩容或 tick 粒度变化，阈值失效；通用表阈值（7 日均值×0.5）在低基数表上噪声敏感。
  2. `_ch_insert_tsv` 重试 3 次×2s（L99-115），CH 长故障时回灌能力弱于 scheduler 主链路（后者有本地落盘兜底）。
  3. 通用表补下载只重跑任务，不验证重跑后缺口是否真正闭合（L568-578 无回填后复查；仅 tick 路径有验证 L533-537）。

### 3.7 完整性校验 integrity_checker

**评分：⚠️（单维度、行数级，非数值级）**

- 每日 23:00 盘后巡检（L11 档，`schedule.yaml` L92-96），复用 backfill 的动态发现，逐表检查"当日行数 ≥ 阈值"（`integrity_checker.py` L46-83），不达标走 alerter ERROR 告警 + 进度库记录（L115-140）。只检测不补下载，职责划分清晰（L17-28）。
- **覆盖盲区**：
  1. 只查"行数够不够"，不查"数据对不对"——无 OHLC 关系、价格连续性、时间戳分布、停牌日 0 行合理性等检查。
  2. 阈值为 0 的表（无 7 日历史的新表/低频表）直接跳过（L60-62），低频财务表（季报披露前长期无增量）天然不在巡检覆盖内。
  3. 只查 `today`，当日因节假日/数据源停更导致的"合理 0 行"与"故障 0 行"无法区分（虽有过滤 trading_day_only 任务的机制，但阈值推断不感知日历）。
- 与质量门（§3.4）缺失叠加，意味着**入库数据的正确性目前完全依赖数据源自身质量**。

### 3.8 写入性能 buffered_writer / ch_writer / wal_writer

**评分：✅（经历过真实事故迭代，架构成熟）**

- **攒批写入**（`buffered_writer.py`）：50000 行或 30 秒触发 flush（L53-55），将"1 股票=1 INSERT"（5204 个 data parts 打爆 CH merge，裁定 #ARCH-CH-001/003，L21-28 背景注释）收敛为个位数 INSERT。per-task buffer_max_seconds 可配（`scheduler.py` L920，新闻类配 300s 降 flush 频率 10×）。
- **三级降级**（`ch_writer.py` L8 INVARIANTS）：query/delete 走 TCP 9000，write_tsv 走 HTTP 8123 → 失败本地 TSV 落盘（`data/local_fallback/`）；TCP 失败 15s 冷却避免反复重连（L82-83）。`WriteOutcome` 三态（CH_COMMITTED/LOCAL_DURABLE/NOT_DURABLE，L95-112）明确区分"已提交"与"本地持久化待回灌"，scheduler 对 LOCAL_DURABLE 记 `DEFERRED_PERSISTENCE` 状态而非伪装成功（`scheduler.py` L927-942）——诚实性设计优秀。
- **实时链路主动 WAL**（`wal_writer.py` L17-38）：tick 订阅先落 WAL 段文件再由 drain 线程异步排空，CH 慢/不可达不阻塞生产者；WAL 容量 90% critical 背压阻断写入（L9）。与 BufferedWriter 的"失败才降级"形成互补。
- **列过滤与 schema 漂移容忍**：写入前按 CH 实际表列过滤多余列（`buffered_writer.py` L127-154），CH 不可用时落盘 None 待回灌时重建列子句（L146-148，#ARCH-CH-013 修复）。
- 实测 CH 侧 tick_data 当日 14:56 仍有 part 写入（`system.parts` modification_time），写入链路在运转。

### 3.9 监控告警 metrics / alerter / health_snapshots

**评分：⚠️（采集完善，告警通道单薄，快照机制名存实亡）**

- **指标**（`metrics.py`）：自实现 Prometheus 文本格式（不依赖 prometheus_client），6 核心指标（task_total/duration 直方图/rows_fetched/rate_limit/retry/uptime，L22-28），原子写 .prom 文件（tmp+replace，L211-226）。同时 `zephyr.shared.observability.metrics` registry 被 redundant_source/ch_writer/wal_writer 埋点共用（如 `zephyr_ch_write_total{outcome=...}`，`ch_writer.py` L123-127）。调度器暴露 `/metrics` `/health` `/status` 端点（端口 9100，`scheduler.py` L1358-1456），/health 走 30s 探活缓存避免阻塞（L339-381，#ARCH-CH-011），端口冲突时降级不崩（L1442-1453）。
- **告警**（`alerter.py`）：触发条件齐全（DEAD 即告/单日失败率>5%/连续 3 天失败/配额耗尽，L19-23）；失败文件冷却 300s 防 crash-restart 刷屏（L52-53，有 40 分钟刷 3000 文件的真实事故背景 L131-133）；所有方法不抛异常。**但通知通道只有日志 + failures/ JSON 文件**，钉钉/邮件为"阶段3+ 扩展点，当前 NotImplementedError"（L28）——个人单用户系统无人盯日志时，CRITICAL 告警（如配额耗尽、连续失败）实际不可达。实测 `data/failures/` 当日已有 5 个失败文件（news_rss/realtime_snapshot/rights_issue/sector_meta/shareholder）。
- **health_snapshots**：`src/zephyr/data/health_snapshots/` 仅 1 个文件 `health_20260625005037.json`（2026-06-25，近一个月前），快照机制未持续运行，无法支撑健康度趋势分析。
- **破损 part 自愈**（加分项，`scheduler.py` L421-589）：守护线程每 5 分钟查 system.text_log 的 CHECKSUM_DOESNT_MATCH，自动 STOP MERGES→DETACH PART→START MERGES 隔离 + 审计 jsonl + CRITICAL 告警——针对真实事故（CHECKSUM 失败 718 次循环）的治本机制。

### 3.10 调度 scheduler

**评分：✅（机制密度最高的模块，小瑕疵见下）**

- **12 档分层调度**（`schedule.yaml` L9-20 注释+L22-107）：L0 集合竞价 10s 高频 → L1/L2/L2.5 盘中实时/分钟/板块（独立 executor 隔离快慢任务）→ L3 事件驱动 15min → L4-L7 盘后分层 → L8 周末校准 → L9 月初静态 → L10 周末回填 → L11 每日巡检。执行器分 5 池（default 8/heavy 2/realtime 4/intraday_minute 4/intraday_sector 2，`scheduler.py` L1235-1241）。
- **DAG 依赖**：TaskQueue 管理依赖（adj_factor→kline_daily_hfq 等），就绪任务并行（最多 8）批次间串行（L186-243）；局部 TaskQueue 方案修复了并发调度互相覆盖事故（L79-83、L198-199，#ARCH-CH-016 v2）。
- **交易日历守卫**：非交易日自动跳过盘中/盘后时段（L100-124），miniqmt 任务缺 `trading_day_only` 时拼写防护告警（L168-177）。
- **启动校验**：capability 契约 ERROR 级违规 fail-closed 阻断启动（L638-696，#ARCH-CH-022），路由-meta 一致性 WARN；tasks.yaml 表名 ⊆ 品类真源 WARN 校验（L617-632，#ARCH-CH-024）。
- **job 持久化与防重**：SQLAlchemyJobStore + `replace_existing=True` + `max_instances=1` + `coalesce=True` + `misfire_grace_time=3600`（L1242-1246）；模块级回调函数规避 pickle RLock 问题（L86-97）。
- **实测在运行**：进度库当日（2026-07-22）11:00 UTC 仍有任务执行记录，近 7 天 8884 次运行。
- **瑕疵**：
  1. `_DEFAULT_TIMEOUT=600`（`ch_writer.py` L72）在部分运维查询上过长，虽有探活专用 timeout=3 的修正，但巡检/回填路径的 CH 查询对大表 FINAL 有超时风险（§3.5 实测）。
  2. 事件订阅（config_changed/shutdown/task_completed，L292-296）已具备，但策略热更新靠 60s 轮询 `maybe_reload`（L1513），非纯事件驱动。

---

## 4. 实测数据现状（2026-07-22）

> 来源：CH `172.24.30.100` 只读查询（system.tables / system.parts / 业务表 count/max）+ `data/integrator_progress.db` 只读查询 + `data/failures/` 目录列举。本次 CH 可达，以下为实测值。

**库表规模（system.tables，c1_market 76 表 / c3_fundamental 21 表 / c0_meta 1 表）**：

- 头部表：tick_data 143.2 亿行、kline_1min 38.7 亿行、kline_5min 9.8 亿行、kline_daily 3466 万行、news_data 1016 万行、restricted_shares 2279 万行。
- **空表（0 行，有表有任务或有表无数据）**：`c1_market.edb_data`、`c1_market.realtime_snapshot`、`c1_market.sector_snapshot`。
- **缺失表**：`c1_market.l2_tick` 不存在（system.tables count=0），但 tasks.yaml 有 `l2_tick_snapshot` 任务指向该表——写入必然失败或落入 fallback。

**关键表新鲜度（max 日期实测）**：

| 表 | 最新日期 | 评价 |
|---|---|---|
| tick_data | 2026-07-22（当日盘中 11.5 万行） | ⚠️ **昨日 2026-07-21 实测 0 行** |
| kline_daily | 2026-07-21 | ✅ 正常（今日未收盘） |
| news_data | 2026-07-22 | ✅ |
| money_flow | 2026-07-20 | ⚠️ 滞后 2 日 |
| margin_trading | 2026-07-17 | ⚠️ 滞后 5 日（T+1 源，应为 07-21） |
| daily_valuation | 2026-07-21 | ✅ |
| income_statement | report_period 2026-03-31 / announce 2026-06-04 | ⚠️ 中报季，需关注 8 月披露密度 |

**进度库健康（126 任务）**：SUCCESS 93 / **FAILED 25** / **卡死 RUNNING 8**（见 §3.1）。

**FAILED 归因聚类**（实测 error_msg）：

1. **QMT 不在线**（"无法连接xtquant服务…"）：shareholder/express_report/earnings_forecast/dividend/kline_futures/kline_weekly/kline_monthly/kline_index 等 ≥8 个 miniqmt 任务，均无 fallback_sources。
2. **akshare 接口漂移**（`module 'akshare' has no attribute ...`）：rights_issue、disclosure_plan 2 例——数据源上游 API 变更，代码未跟进。
3. **能力缺口**（设计性失败）：audit_opinion（"AKShare 暂无专用审计意见接口"）、kline_us_daily（"QMT 无美股板块，需手动指定 symbols+开通美股权限"）。

---

## 5. 数据清单盘点与覆盖缺口

### 5.1 项目实际拥有的数据类别（tasks.yaml 128 任务 + CH 实测表）

| 大类 | 覆盖内容 | 实测状态 |
|---|---|---|
| A股日K | 日/周/月 K 线（前复权+后复权）、复权因子、每日估值指标 | ✅ 运转中，kline_daily 至 07-21 |
| 分钟线 | A股/ETF/LOF × 1/5/15/30/60min（15 个任务） | ✅ kline_1min 38.7 亿行 |
| Tick | QMT 实时 tick（3 秒粒度快照，14 字段）+ 集合竞价 10s 五档快照（auction_snapshot/auction_book） | ⚠️ 主链路运转，昨日缺口待 L10 回填 |
| L2/逐笔 | l2_tick_snapshot 任务存在 | ❌ **表不存在，实际无 L2 逐笔数据** |
| 财务报表 | 三大报表+财务指标+主营构成+业绩快报+审计意见+盈利预测（10+ 表） | ✅ 至 2026Q1；2 个 akshare 任务接口漂移失败 |
| 股本股东 | 十大股东/流通股东/股东户数/股本变动/限售解禁/回购/质押/分红配股 | ✅ 基本齐全 |
| 新闻舆情 | 11 个新闻任务（akshare/cls/eastmoney/rss/tushare/百度/央视等）→ news_data | ✅ 日更，去重有效 |
| 研报 | research_report 任务 | ✅（analyst_forecast 11K 行） |
| 板块 | 行业分类/概念板块/880 板块 K 线（tdx TCP 直连）/板块成分/板块快照 | ⚠️ sector_snapshot 0 行；板块 K 线运转中 |
| 资金面 | 资金流向/龙虎榜/大宗交易/融资融券/沪深港通/限售解禁 | ⚠️ money_flow 滞后 2 日、margin 滞后 5 日 |
| 期货期权 | 期货 K 线/持仓/期限结构；期权 K 线/Greeks/IV 曲面；可转债 K 线/IV | ⚠️ 量级小（futures_position 492 行、option_greeks 8876 行），疑似边缘覆盖 |
| 港美股 | 港股日 K/股票列表/交易日历；美股日 K/指数 | ⚠️ kline_us_daily 任务失败（权限+symbols 缺失） |
| 宏观 | macro_data（iFind，28.5 万行）+ edb_data（Wind EDB 任务） | ⚠️ **edb_data 0 行**（配额或权限问题） |
| 日历/静态 | 交易日历（A股/港股）/股票列表/指数成分与权重/ETF/LOF/可转债列表/ST 名单 | ✅ |
| 另类数据 | satellite_geospatial_engine 目录存在 | ❌ 仅骨架（`__init__.py` 声明 Phase B 骨架），无实际数据 |

### 5.2 对照专业回测系统标准清单的缺口

| 数据类别 | 专业回测系统应有 | 本项目现状 | 缺口评级 |
|---|---|---|---|
| 日线/分钟线 | 全市场全历史+复权 | ✅ 齐全（15 分钟级任务+前后复权） | 无 |
| Tick/逐笔 | tick 快照 + 逐笔成交/逐笔委托（L2） | 仅 3 秒 tick 快照；L2 表缺失 | **P0（高频/微观结构回测不可做）** |
| 财务报表 | 三大表+指标，含**历史修订版（point-in-time）** | 表齐，但 ReplacingMergeTree 覆盖式更新，**无 PIT 快照**，存在前视偏差风险 | **P0（基本面回测有效性）** |
| 公告原文 | 巨潮/交易所公告原文+结构化事件 | ❌ 无公告原文表（news 为媒体新闻，非交易所公告） | **P1** |
| 新闻舆情 | 多源+去重 | ✅ 11 源+双层去重 | 无 |
| 板块/概念 | 行业+概念+成分历史变动 | ⚠️ 成分表有但**历史成分变动时点**（index_constituent 59K 行）颗粒度未验证；sector_snapshot 空 | P1 |
| 宏观 | 常用宏观序列（GDP/CPI/PMI/利率/汇率） | macro_data 28.5 万行；EDB 0 行 | P1 |
| 利率/债券 | 无风险利率曲线（国债收益率）、信用利差 | ❌ 未见债券/收益率曲线表 | **P1（回测贴现/股债轮动必需）** |
| 衍生品 | 期货/期权/可转债 | ⚠️ 有表但量级极小，覆盖度存疑 | P2 |
| 港美股 | 港股可用；美股失败 | ⚠️ | P2 |
| 另类数据 | 卫星/ESG/舆情热度 | ❌ 骨架 | P2（回测场景非必需） |
| 退市股票 | 含退市股的全历史 universe（防幸存者偏差） | ⚠️ stock_list 5534 行≈当前上市数，**未见退市股清单/退市 K 线专项** | **P0（回测偏差根源）** |

---

## 6. 问题清单（P0/P1/P2）

### P0 — 影响回测结论有效性

| # | 问题 | 证据 | 影响 |
|---|---|---|---|
| P0-1 | **写入路径无质量门**：OHLC 合法性/异常值/时间戳校验缺失，quality_flag 恒为 1 | `quality_gate.py` L17-27（re-export 壳）；grep 实测零消费方；provider 均不写 quality_flag | 脏数据直进回测，产生虚假信号，且无任何标记可过滤 |
| P0-2 | **基本面数据无 point-in-time 快照**：ReplacingMergeTree 直接覆盖，历史财报修订不可回溯 | `scripts/ch/apply_market_tables_ddl.py` L75-108 引擎策略；c3 表无 announce_date 维度快照机制 | 基本面因子回测存在前视偏差，结论不可信 |
| P0-3 | **退市股覆盖未证实**：stock_list 5534 行≈当前上市公司数，无退市股清单与退市股历史 K 线专项 | 实测 `c1_market.stock_list` total_rows=5534 | 幸存者偏差，回测收益系统性高估 |
| P0-4 | **L2/逐笔数据实际为空**：l2_tick 表不存在但任务引用 | 实测 system.tables 无 l2_tick；tasks.yaml `l2_tick_snapshot` | 微观结构/高频回测不可做；任务持续失败刷告警 |

### P1 — 数据完整性与管线可靠性

| # | 问题 | 证据 | 影响 |
|---|---|---|---|
| P1-1 | 25/126 任务 FAILED，其中 ≥8 个因 QMT 不在线且**无 fallback_sources**；fallback 覆盖率仅 8/128 | 进度库实测；`scheduler.py` L818-826 | QMT 停机日=成批数据缺口，靠 L10 周末才补，周内回测数据滞后 |
| P1-2 | 8 任务卡死 RUNNING 超 24h，无卡死检测/清理 | 进度库实测（如 daily_valuation_full_refresh 07-20 起） | 状态失真，影响 rerun-failed 等运维判断 |
| P1-3 | akshare 接口漂移 2 例（rights_issue/disclosure_plan）+ 能力缺口 2 例（audit_opinion/kline_us_daily）长期 FAILED | 进度库 error_msg 实测 | 对应数据类别停更 |
| P1-4 | 空表 trio：edb_data/realtime_snapshot/sector_snapshot 0 行；margin 滞后 5 日、money_flow 滞后 2 日；tick 昨日 0 行 | §4 实测 | 宏观/资金面/板块快照数据链断裂未被巡检捕获（阈值为 0 的表被跳过，`integrity_checker.py` L60-62） |
| P1-5 | 错误分类盲区：QMT 断连/akshare 属性缺失归为 unknown 反复重试 | `error_classifier.py` L42-98 vs §4 实测错误串 | 重试预算浪费、告警噪音、熔断决策错误 |
| P1-6 | 无公告原文数据（仅媒体新闻） | tasks.yaml 表清单 grep 实测 | 事件驱动回测缺公告维度 |
| P1-7 | 无债券/无风险利率数据 | 表清单实测 | 股债配置/贴现率类回测不可做 |

### P2 — 健壮性与运维

| # | 问题 | 证据 | 影响 |
|---|---|---|---|
| P2-1 | 告警通道仅日志+文件，钉钉/邮件 NotImplemented | `alerter.py` L28 | CRITICAL 告警不可达，故障发现依赖人工看日志 |
| P2-2 | health_snapshots 仅 1 个 2026-06-25 陈旧文件 | `health_snapshots/` 目录实测 | 无健康度趋势，容量/性能回归无感知 |
| P2-3 | ch_reader 对超大表自动注入 FINAL 导致部分查询失败 | 本次审查实测 tick_data/kline_1min/income_statement 查询 TCP+HTTP 均失败 | 巡检/回填/诊断脚本对大表存在超时风险 |
| P2-4 | tick 缺失阈值硬编码 500 万行/日；通用阈值对低频表噪声敏感 | `backfill_checker.py` L53-54、L244-262 | 阈值漂移后漏检/误报 |
| P2-5 | 通用表回填后无闭合验证（仅 tick 路径有） | `backfill_checker.py` L568-578 vs L533-537 | 补下载失败无声 |
| P2-6 | 冗余源切换器（SourceSwitcher/SQLiteFallback/RecoveryManager）仅 tick 订阅链路消费，批管线未接入 | grep 实测消费方仅 `tick_subscriber.py` L195 | 两套韧性体系未打通，批管线故障恢复粒度粗 |
| P2-7 | last_key=日期直接作为下次 start，依赖引擎/DELETE 幂等兜底 | `scheduler.py` L1013-1025 | 部分写入失败时当日数据不完整，发现粒度为周级 |

---

## 7. 改进方向（回测场景优先级排序）

1. **接入质量门（治 P0-1）**：在 `_fetch_and_write`（`scheduler.py` L1068-1101）写入前增加轻量校验层——价格非负/high≥low/volume≥0/时间戳合法/涨跌停边界；不合格行 `quality_flag=0` 写入而非丢弃（保真+可过滤），质量统计入 metrics。复用已有 `DataQualityGate` 抽象（`gov_enforcement/rule_enforcement/quality_gate.py` L81）而非另起炉灶。
2. **财报 point-in-time 化（治 P0-2）**：三大报表写入改为"announce_date 分区 + report_period 排序键 + 追加不覆盖"（新引擎或版本列），回测查询统一按 `announce_date <= 回测日` 过滤，消除前视偏差。属表结构变更，需按 RULE-DATA-OPS 三步验证执行。
3. **退市股 universe 补全（治 P0-3）**：通过 iFind/akshare 退市名单接口补退市股清单+历史日 K，stock_list 增加 `delist_date` 语义（注释中 1970-01-01 空值约定已有雏形，见 business_data_categories.yaml L15）。
4. **fallback 覆盖提升 + 错误分类扩充（治 P1-1/P1-5）**：为核心 miniqmt 任务补 akshare/baostock 副源（kline_daily 已有样板）；error_classifier 增加"无法连接xtquant"/"has no attribute"/"暂无专用"→ unrecoverable 规则，QMT 断连类接入源级熔断（policy.enabled）而非逐任务失败。
5. **卡死 RUNNING 治理（治 P1-2）**：启动时或每日巡检中将 `RUNNING 且 last_run_at 超过 N 小时` 的记录重置为 FAILED 并告警；task_runs 补充孤儿 run（RUNNING 无 finished_at）清理。
6. **空表/低频表巡检覆盖（治 P1-4）**：integrity_checker 对阈值为 0 的表按"调度频率 × 上次成功时间"推导应有数据时点，替代行数阈值；edf/realtime_snapshot/sector_snapshot 三个空表先定位是任务未跑还是源失败。
7. **告警可达性（治 P2-1）**：alerter 增加最简可达通道（如 Windows toast / SMTP / webhook 任一），CRITICAL 级必须出日志外通道。
8. **回填闭环（治 P2-5）**：通用表补下载后复查行数并记录闭合状态；tick 阈值改为相对历史分位数。
9. **大表查询去 FINAL（治 P2-3）**：ch_reader 对巡检/统计类查询提供 `final=False` 显式开关，配合 ReplacingMergeTree 的 `GROUP BY 排序键 + argMax` 或 OPTIMIZE 周期性收敛。

---

*审查边界声明：本次 CH/进度库可达，§4 全部为实测值；PostgreSQL 本地 5432 端口可达但未深入业务库（与本审查范围相关性低）；redundant_source 的 SourceSwitcher 运行态未实测（未发现常驻进程引用证据，仅代码静态审查）。*
