# 03 · 数据源集成与下载机制（zephyr.data）

> 文档生成：2026-07-22 ｜ 范围：`src/zephyr/data/` 全目录静态审查 + ClickHouse 只读实测
> 蓝图真源：`docs/03_modules/_domain_data/data_source_integrator_blueprint.md`（MOD-L00-004）
> 冗余源蓝图：`docs/03_modules/_domain_data/redundant_source_blueprint.md`（MOD-L00-005）

## 目录

- [1. 模块总览](#1-模块总览)
- [2. "8 源 61 任务" 出处核实（重要纠偏）](#2-8-源-61-任务-出处核实重要纠偏)
- [3. 数据源清单](#3-数据源清单)
- [4. 任务清单结构（tasks.yaml）](#4-任务清单结构tasksyaml)
- [5. 下载器架构与七大韧性机制](#5-下载器架构与七大韧性机制)
- [6. 调度机制（是否事件驱动）](#6-调度机制是否事件驱动)
- [7. CLI 子命令用法](#7-cli-子命令用法)
- [8. 数据落盘格式与路径](#8-数据落盘格式与路径)
- [9. 实测验证记录](#9-实测验证记录)
- [10. 模块文件索引](#10-模块文件索引)

---

## 1. 模块总览

`zephyr.data` 是**数据源集成器**（Data Source Integrator，蓝图编号 MOD-L00-004），统一管理多数据源的自动下载：Provider 抽象层 → per-source 策略注册表 → APScheduler 调度编排 → ClickHouse 写入 → 进度/告警/指标统一管理。包入口 `src/zephyr/data/__init__.py` 暴露 `DataSourceBase / SourcePolicy / PolicyRegistry / IntegratorScheduler / get_integrator`（`__init__.py:14-40`）。

核心链路（`scheduler.py:_try_source`，`scheduler.py:859-988`）：

```
tasks.yaml 任务定义
  → IntegratorScheduler（APScheduler cron 触发，DAG 依赖排序）
    → PolicyRegistry 取 per-source 策略（限流/重试/退避）+ 熔断检查
      → ProgressStore 取断点 last_key → 构造 FetchPayload
        → Provider.fetch() 迭代器分批返回 FetchResult
          → （新闻走 news_dedup 去重）→ BufferedWriter 攒批
            → ch_writer 二级传输写 ClickHouse（HTTP TSV → 本地落盘兜底）
              → ProgressStore 记录进度 / Alerter 失败告警 / Metrics 指标落盘
```

包内另有三个**独立常驻/手动入口**，不经 scheduler cron：

- `tick_subscriber.py`：QMT 实时 Tick 订阅（`subscribe_quote` 推送 → WalWriter 主动 WAL → 异步 drain 到 CH），`python -m zephyr.data.tick_subscriber` 启动（`tick_subscriber.py:1-10`）。
- `sector_snapshot_collector.py`：880xxx 板块实时快照采集（tqcenter 推送 99 只 + 全量轮询 30 秒），盘前启动盘后停止（`sector_snapshot_collector.py:18-32`）。
- `sector_kline_downloader.py` / `kline_resampler.py` / `sector_ranking_engine.py`：880xxx 板块 K 线下载、15m/30m/60m 合成、5 因子动态排名，均为手动 `python -m` 触发（`sector_kline_downloader.py:22-26`、`kline_resampler.py:30-34`、`sector_ranking_engine.py:28-31`）。

`satellite_geospatial_engine/` 目前仅有 `__init__.py`（54 行），是 D_DATA 接入层的文档化骨架（re-export `DataSourceBase` 与治理层 `DataQualityGate`），**无独立实现代码**，蓝图指向 MOD-L00-001（`satellite_geospatial_engine/__init__.py:1-54`）。

---

## 2. "8 源 61 任务" 出处核实（重要纠偏）

AGENTS.md（L187）称集成器"统一管理 **8 源 61 任务**"。核实结论：**两个数字均已过时**。

**"61 任务"出处**：蓝图 `data_source_integrator_blueprint.md:25` ——"把当前 61 项'手动触发'数据全部纳入自动调度"，蓝图 `:910-912` 记录"61 任务全部接入 tasks.yaml 调度配置"。这是**蓝图立项时（阶段 4 验收）**的历史基线。

**"8 源"出处推断**：蓝图未直接写"8 源"，但 `policy_registry.py:92-137` 的 `DEFAULT_POLICIES` 恰好内置 **8 个源**（ifind/miniqmt/akshare/baostock/tushare/tickflow/tdx/rss），即集成器初版 Provider 数量。

**当前真实数量（2026-07-22 实测，`integrator list` 运行验证）**：

| 口径 | 数量 | 证据 |
|---|---|---|
| tasks.yaml 任务总数 | **128**（121 活跃 + 7 个 `extra.disabled` 退役） | `integrator list` 输出"已加载任务清单: 128 个任务"；`config/tasks.yaml` |
| 有 Provider 实现并被 scheduler 路由的源 | **10**（ifind/miniqmt/akshare/baostock/tushare/tickflow/tdx/rss/cls/eastmoney_news） | `scheduler.py:743-781` `_create_provider` |
| policies.yaml 策略条目 | **11**（10 Provider + tqcenter） | `config/policies.yaml`（本文件头部注明为派生物，真源在 `architecture_model/data/data_sources_registry.yaml`） |
| 数据源注册表（真源）条目 | **13**（active 11 + planned 1 + deprecated 2；含无 Provider 的 baiduyun、未实现的 newsapi，已废弃的 yfinance/stooq） | `architecture_model/data/data_sources_registry.yaml` v2.1.0 |
| 调度时段 | **13 档**（schedule.yaml 12 档 + tasks.yaml 独有的 manual_script 标签） | `config/schedule.yaml:22-107`；实测日志"已加载调度计划: 13 档时段" |

**注册表漂移发现**：`cls`（财联社）与 `eastmoney_news`（东方财富快讯）已有 Provider 实现和 tasks.yaml 任务，但**未登记**在 `data_sources_registry.yaml`（该文件 13 条中无此二者）——policies.yaml 于 2026-07-22 23:29 被并发会话补上这两个源后，派生物已先于真源更新，存在"派生物先于真源"的逆向漂移。

---

## 3. 数据源清单

实现文件均在 `src/zephyr/data/implementations/`。能力清单取自各 Provider 的 `meta: DataSourceMeta` 类属性（行号为 `meta =` 起始行）；"更新频率"由 tasks.yaml 中该源任务的 schedule 分布归纳。

| 源 | 类型/认证 | 数据覆盖（注册表口径） | 更新频率 | 任务数 | 实现文件 | 关键约束（known_issues / extra） |
|---|---|---|---|---|---|---|
| **miniqmt**（miniQMT 迅投） | 商业 / 账号 | A股实时行情/历史K线/交易接口 | 盘中 5min 轮询（Tick/分钟K/期权/期货）+ 盘后日K/财报/事件 | 57 | `miniqmt_provider.py:378` | 需 XtMiniQmt.exe 进程常驻；单线程串行；非交易日 QMT 服务器拒连（error 10061）→ `trading_day_only` 守卫 |
| **akshare**（免费开源） | 开源 / 匿名 | A股/港股/美股/期货/宏观/新闻 | 盘后资金/事件 + 事件层 15min 轮询（宏观/新闻/研报）+ 月初静态 + 周末校准 | 40 | `akshare_provider.py:169` | RPM 60；须断 VPN（`disconnect_vpn: true`）；部分接口被反爬 |
| **ifind**（同花顺 iFind） | 商业 / 用户名密码 | A股K线/Tick/板块/财务/宏观/研报 | 盘后估值/资金面 + 周末校准 + 月初静态 | 8（1 个 disabled：edb_data_incremental） | `ifind_provider.py:102` | 配额制（EDB 每周 50000 cell，周一重置）；月度配额错误码 -4318/-4309；thread_local 会话 24h |
| **tdx**（通达信 mootdx） | 开源 / 匿名 | A股K线/指数/880xxx/881xxx 板块K线与成分 | 盘中板块分钟K（独立执行器）+ 周末校准 | 7 | `tdx_provider.py:81` | 单线程串行；bestip 自动选服务器，失败回退 `_RELIABLE_SERVERS` |
| **tickflow** | 开源 / 匿名 | 美股日K/美股指数（ETF 替代） | 周末校准（周一 03:00） | 4 | `tickflow_provider.py:84` | 60 次/分钟限流 |
| **rss**（RSSHub） | 开源 / 匿名 | 财经新闻 RSS | 事件层 15min 轮询 | 2 | `rss_provider.py:84` | 依赖本地 RSSHub（D:\RSSHub）；遵守 robots.txt（per-domain 缓存） |
| **baostock** | 开源 / 匿名 | A股K线/财务/宏观 | 月初静态（交易日历/指数成分）+ kline_daily 的 fallback 源 | 2 | `baostock_provider.py:63` | 数据滞后约 1 周；thread_local 登录，会话 TTL 3600s |
| **cls**（财联社电报） | 开源 / 匿名 | 分钟级财经快讯 | 事件层 15min 轮询 | 1 | `cls_provider.py:67` | RPM 30；依赖本地 RSSHub 路由 `/cls/telegraph`（policies.yaml extra） |
| **eastmoney_news** | 开源 / 匿名 | 东方财富 7×24 快讯 | 事件层 15min 轮询 | 1 | `eastmoney_news_provider.py:65` | RPM 30；高频请求可能被限 |
| **tushare** | 商业 / token | A股K线/财务/板块/基金/期货 | 当前唯一任务已 disabled（news_tushare_incremental） | 1（disabled） | `tushare_provider.py:61` | 历史数据截止 2024-08；积分阈值告警 2000 |
| **tqcenter**（通达信 PYPlugins） | 商业 / 客户端 | 880xxx 板块指数K线/成分/实时快照（subscribe_hq 推送独有） | manual_script（独立脚本，不走 cron） | 4 | 非 Provider：`sector_kline_downloader.py` / `sector_snapshot_collector.py` | 非 pip 安装，需 `sys.path` 注入 `E:\tdx\PYPlugins\user`；依赖通达信客户端 |
| **backfill**（伪源） | — | L10 周末补下载编排占位 | 周一 02:00 | 1 | `backfill_checker.py` | 非真实数据源，run_schedule 特殊分发 |

注册表中另有：**baiduyun**（通达信板块分笔历史 Tick 一次性包，无 API 可持续更新，无 Provider）；**newsapi**（planned，未实现）；**yfinance / stooq**（deprecated）。

---

## 4. 任务清单结构（tasks.yaml）

真源文件：`src/zephyr/data/config/tasks.yaml`（53.6 KB，128 个任务）。字段结构（样例见 `tasks.yaml:23-35`）：

| 字段 | 含义 |
|---|---|
| `task_id` | 任务唯一标识（主键，ProgressStore 断点键） |
| `table` | 目标 ClickHouse 表（全限定名 `db.table`，启动时经 TableRegistry 与 `business_data_categories.yaml` 品类真源校验） |
| `source` | 数据源 runtime_id（对应 `_create_provider` 路由） |
| `schedule` | 所属调度时段（对应 schedule.yaml 键或 `manual_script`） |
| `incremental` | true=增量（从 last_key 续传）；false=全量刷新 |
| `date_col` | 幂等 DELETE 用的日期列（SSoT，避免硬编码猜错列名） |
| `dependencies` | 同时段内前置 task_id 列表（DAG） |
| `capability` | Provider 内 fetch 路由能力名，启动时与 `meta.capability_contracts` 机器校验 |
| `symbols` | 标的列表；`null`=全市场（需 capability 声明 `supports_symbols_null=True`） |
| `fallback_sources` | 副源列表 `[{source, capability}]`，主源失败后按序切换 |
| `extra` | 透传给 Provider 的专属参数 + `disabled`/`trading_day_only` 控制位 |

**任务分布（128 个）**：

- 按源：miniqmt 57 / akshare 40 / ifind 8 / tdx 7 / tickflow 4 / tqcenter 4 / rss 2 / baostock 2 / cls 1 / eastmoney_news 1 / tushare 1 / backfill 1
- 按时段：daily_capital 16 / daily_kline 15 / intraday_minute 15 / monthly_static 15 / event_driven 13 / intraday_realtime 12 / weekend_calibration 12 / daily_event 11 / nightly_financial 8 / intraday_sector 5 / manual_script 4 / auction_highfreq 1 / weekend_backfill 1
- 增量任务 100 个；配置 `fallback_sources` 的 4 个（kline_daily→baostock、daily_valuation→akshare、money_flow→akshare、l2_tick_snapshot→miniqmt，最后者已 disabled）
- 覆盖 102 张不同的 CH 表（c1_market 77 表 / c3_fundamental 23 表实测存在）

**DAG 依赖（10 条）**，典型链：`adj_factor_incremental → kline_daily_hfq_incremental / kline_weekly_hfq / kline_monthly_hfq`；`kline_daily_incremental → daily_valuation_incremental`；`kline_futures_incremental → futures_position / futures_term_structure`；`industry_class_refresh → kline_sector_incremental`；`kline_sector_880_incremental → kline_sector_880_resample`。

**结构问题发现（如实记录）**：

1. **task_id 重复**：`kline_us_daily_incremental` 出现 2 次（miniqmt/daily_capital 与 tickflow/weekend_calibration），而 `task_progress` 表以 task_id 为主键（`progress_store.py:84-94`），两任务共享同一断点 last_key，存在断点互相覆盖风险；目标表 `c1_market.kline_us_daily` 甚至被 3 个任务写入。
2. **`manual_script` 不在 schedule.yaml**：4 个 tqcenter 任务的 schedule 值无对应 cron 时段，永远不会被 APScheduler 触发，仅用于 `backfill_checker._discover_backfill_tables()` 的表发现与台账登记——属"账本式注册"，命名与语义易误导。
3. **7 个 disabled 任务**：edb_data_incremental、kline_5min_history_backfill、news_tushare_incremental、l2_tick_snapshot、margin_trading/dragon_tiger/block_trade_qmt_placeholder（QMT 占位任务，功能暂由 akshare 源承担）。

---

## 5. 下载器架构与七大韧性机制

### 5.1 Provider 抽象与策略注入

`provider_base.py` 定义统一契约（`provider_base.py:187-343`）：

- `DataSourceBase` 抽象基类：`connect/health_check/fetch/disconnect` 四方法；**Provider 只拉数据返回 `Iterator[FetchResult]`（每批含 columns/rows/last_key），不写 CH**（不变式见文件头 L8）。
- `FetchPayload`（`provider_base.py:52-69`）：table/symbols/start/end/incremental/extra。
- `CapabilityContract`（`provider_base.py:100-119`）：把能力行为（supports_symbols_null / supports_incremental / requires_date_range）升级为机器可执行契约（裁定 #ARCH-CH-022），启动时由 `capability_validator.py` 校验，ERROR 级违规 fail-closed 阻断启动（`scheduler.py:638-714`）；另有 AST 级"fetch 路由-meta 声明"一致性 WARN 校验（Phase 4.3）。
- 策略执行点 `_call_with_policy`（`provider_base.py:241-294`）：限流休眠 → 调用 → 按 `retry_on` 模式匹配重试 → `exponential/fixed/jittered` 三种退避（`_calc_backoff`，L309-324）。

### 5.2 限流与重试（per-source 策略）

`policy_registry.py` 的 `SourcePolicy`（`policy_registry.py:44-86`）：rpm / concurrency / max_retries / backoff / initial_wait_sec / retry_on / use_proxy / disconnect_vpn / session_ttl_sec / relogin_on_auth_error / **enabled（熔断开关）**。策略真源为 `architecture_model/data/data_sources_registry.yaml`，`config/policies.yaml` 是派生物（文件头 L5-8 注明"禁止手工修改"），`maybe_reload()` 按 mtime 热更新（`policy_registry.py:187-201`），常驻主循环每 60s 检查一次（`cli.py:286-291`）。RPM 限流在 `_rate_limit_sleep`（`provider_base.py:296-307`）：保证两次调用间隔 ≥ 60/rpm。

### 5.3 断点续传

`progress_store.py`（SQLite，默认 `data/integrator_progress.db`，WAL 模式，`progress_store.py:50,78-118`）：

- `task_progress`（主键 task_id）：last_key / last_status / rows_total / error_msg
- `task_runs`（自增 run_id）：每次运行的 started_at/finished_at/rows_fetched/rows_written
- 协议（`progress_store.py:24-27`）：启动 `get_last_key(task_id)` → 作为 payload.start（`scheduler.py:1013-1025`，增量取 last_key，全量取月初）→ 每批写完 CH 即 `save_progress` 更新（`scheduler.py:1097-1100`）→ 中断后下次从 last_key 继续。
- 线程安全：`check_same_thread=False` + `threading.Lock` 串行化全部读写（修复 SQLITE_MISUSE，`progress_store.py:29-33`）。

### 5.4 熔断

两层：

1. **手动熔断**：`integrator pause <source>` 把 `SourcePolicy.enabled` 置 False（`cli.py:211-229`）；执行前 `_validate_provider_and_policy` 检查 `policy.enabled`，熔断源任务直接跳过并告警（`scheduler.py:1001-1009`）。`resume` 恢复（`cli.py:232-250`）。
2. **自动主备切换（fallback）**：`run_task` 构造"主源 + fallback_sources"尝试链（`scheduler.py:818-857`），配合 `error_classifier.py`：不可恢复错误（配额/接口废弃/认证失败，关键词如 `-4318`/`-4309`/`quota`/`401`/`403`，`error_classifier.py:42-58`）**立即 fallback**；可恢复错误（超时/网络，`error_classifier.py:61-76`）**重试耗尽才 fallback**；未知错误按可恢复处理。

### 5.5 质量门

两个层面：

- `quality_gate.py` 仅是 re-export 壳（27 行）：`QualityReport` 真源在 `zephyr.gov_enforcement.rule_enforcement.quality_gate`（`quality_gate.py:17-27`）；`DataQualityGate` 由 `satellite_geospatial_engine/__init__.py` re-export，属治理层契约 CTR-ERR-001，**当前下载主链路未直接消费**。
- 实际运行的质量保障是 `integrity_checker.py`（L11 每日巡检）+ `backfill_checker.py`（L10 周末补下载），见 5.7。

### 5.6 去重与幂等写入

- **新闻去重** `news_dedup.py`：标题 strip+lower 后 MD5，与 CH 最近 7 天已有标题哈希比对 + 批内去重（`news_dedup.py:124-199`）；`news_id` = MD5(source+title+publish_time)（`build_news_row`，L82-121）；**fail-open**：查重异常时跳过去重不阻断写入。仅对表名含 `news_data` 的 FetchResult 生效（`scheduler.py:1082-1085`）。
- **幂等写入**（`scheduler.py:1045-1066`）：ReplacingMergeTree 表直接 INSERT（CH 后台合并去重）；普通 MergeTree 表写前按 `date_col` 逐日 `DELETE WHERE toDate(date_col) IN (...)`。
- **攒批写入** `buffered_writer.py`：≥50000 行或 ≥30 秒（per-task `buffer_max_seconds` 可调，新闻类 300s）触发一次 `write_tsv`，把"每股一次 INSERT"聚合为少数几次，根治 data parts 爆炸（裁定 #ARCH-CH-003，`buffered_writer.py:17-38,122-124`）；列过滤只插表中存在的列（`_init_columns`，L127-154）。
- **写入二级降级** `ch_writer.py`：query/delete 走 clickhouse-driver TCP(9000)；`write_tsv` 走 HTTP API(8123, FORMAT TSV) → 失败则 `local_replay.save_fallback` 本地落盘 TSV（裁定 #ARCH-CH-013，`ch_writer.py:8,489-541`）；`WriteOutcome/WriteDisposition` 区分 CH_COMMITTED / LOCAL_DURABLE / NOT_DURABLE，禁止把本地落盘伪装成 CH 已提交（`ch_writer.py:95-112`）。
- **回灌** `local_replay.py`：`data/local_fallback/<db__table>/*.tsv` + `_manifest.jsonl`，原子写（.tmp→rename）；scheduler 启动时 + 每 30 分钟自动回灌，单次上限 100 文件（`scheduler.py:385-419`）；回灌用 manifest 保存的 cols_clause，`create_fallback=False` 防重复落盘。
- **实时链路主动 WAL** `wal_writer.py`：tick_subscriber 专用——先主动落 local_fallback 段文件，后台 drain 线程异步回灌 CH，与 BufferedWriter 的"失败才降级"路径互补（`wal_writer.py:1-35`）。

### 5.7 回填与巡检

- **L10 周末补下载** `backfill_checker.py`（周一 02:00，`scheduler.py:134-138` 特殊分发）：**不依赖 last_key，直接查 CH 实际行数**发现真实缺口（`backfill_checker.py:17-27`）。流程：取过去 7 天交易日（trade_calendar 表，fallback 到 kline_daily distinct，L120-146）→ `_discover_backfill_tables()` 从 tasks.yaml 动态发现全表（新增任务自动纳入，L265-293）→ `DESCRIBE TABLE` 推断日期列 + 历史 7 天日均×0.5 推断阈值（L215-262）→ 逐日 `count()` 检测 → tick_data 走 QMT xtdata 专门补下载（50 标的/批，`_BATCH_SYMBOLS`，L60），其他表调 `scheduler.run_task(task_id)` 重跑（L566-579）→ 结果记 progress_store + alerter。
- **L11 每日完整性巡检** `integrity_checker.py`（23:00）：复用同一表发现机制，**只检测不补下载**，不达标表经 Alerter 告警、结果记 progress_store（`integrity_checker.py:86-159`）。

### 5.8 告警与可观测性

- `alerter.py`：四级（INFO/WARN/ERROR/CRITICAL）；触发条件——任务重试耗尽立即告警、单时段失败率 >5% 汇总告警（`check_daily_failure_rate`，`alerter.py:171-191`，调用点 `scheduler.py:241`）、连续 3 天失败升级 CRITICAL、iFind 配额 -4318/-4309 立即 CRITICAL 并建议暂停该源（`alerter.py:218-242`）。落地方式：日志 + `data/failures/{date}_{task_id}_{ts}.json`；同 task_id 300 秒冷却防 crash-restart 刷文件（`alerter.py:52-53,128-146`）。钉钉/邮件为未实现扩展点。
- `metrics.py`：不依赖 prometheus_client，手写 Prometheus 文本格式 6 指标（task_total / task_duration_seconds / rows_fetched_total / rate_limit_hits_total / retry_total / session_uptime_seconds）落盘 `data/metrics.prom`（`metrics.py:17-37`）。
- 监控 HTTP（仅 `python -m zephyr.data.scheduler` 入口启动，端口 9100）：`/metrics`（Prometheus）`/health`（JSON 健康，CH 状态读 30s 探活缓存保证 100ms 响应，裁定 #ARCH-CH-011，`scheduler.py:341-381`）`/status`；端口占用时降级为无 HTTP 不崩溃（`scheduler.py:1435-1456`）。
- 另有**破损 part 自动隔离守护线程**（每 5 分钟查 `system.text_log` 的 CHECKSUM_DOESNT_MATCH → STOP MERGES → DETACH PART → START MERGES → 审计 JSONL + CRITICAL 告警，冷却 10 分钟，裁定 #ARCH-CH-015，`scheduler.py:423-589`）。
- `health_snapshots/` 目录仅有一个内容为 `{}` 的快照文件（`health_20260625005037.json`），为早期占位，当前无写入方。

### 5.9 冗余源子包（MOD-L00-005）

`redundant_source/` 四组件（`__init__.py:1-28`）：`heartbeat_monitor`（tick 10s 超时判主源死、CH 连续 3 次 ping 失败判不可达）、`source_switcher`（PRIMARY→BACKUP→PRIMARY 状态机 + 30s 稳定期防抖）、`sqlite_fallback`（CH 不可达时写 `data/fallback.sqlite`，每表 50 万行 FIFO 上限）、`recovery`（CH 恢复后按 1000 行/批回灌，指数退避 2s→60s）。**实测发现：该子包在 src 内无任何外部消费者**（grep 仅自引用），是面向未来实盘 tick 链路的预建模块，与当前 scheduler 下载链路未接线。

---

## 6. 调度机制（是否事件驱动）

**结论：批量下载是 APScheduler cron 时间驱动，不是事件驱动；"event_driven" 只是 15 分钟轮询时段的名字。** 永久系统"禁止时间触发"铁律由文件头 `# noqa: m02-manual` 豁免注释覆盖（`scheduler.py:17`、`cli.py:17`）。事件机制仅用于内部扩展点：`subscribe(event, handler)` 支持 `config_changed`（策略热更新）/ `shutdown` / `task_completed` 三类（`scheduler.py:306-337`），外部事件源（如 EventBus）未接入。

实现要点（`scheduler.py:1225-1247`）：

- `BackgroundScheduler` + `SQLAlchemyJobStore`（`sqlite:///data/integrator_jobs.db`，重启不丢 job）；job 回调用模块级函数 `_run_schedule_callback` + 全局单例规避 pickle `_thread.RLock` 失败（`scheduler.py:86-97`）。
- job_defaults：`coalesce=True`（错过合并跑一次）、`max_instances=1`（同任务不并发）、`misfire_grace_time=3600`。
- 5 个执行器线程池：default 8 / heavy 2（iFind/QMT 串行源）/ realtime 4（盘中实时）/ intraday_minute 4 / intraday_sector 2。
- cron 支持 5 段与 6 段（含秒，供集合竞价 10 秒高频层，`scheduler.py:1172-1196`）；亦支持 interval trigger（代码保留，当前 schedule.yaml 未用）。

**13 档时段（schedule.yaml L22-107）**：

| 时段 | cron（分 时 日 月 周，APScheduler 0=周一） | 执行器 | 职责 |
|---|---|---|---|
| intraday_realtime (L1) | `*/5 9-15 * * 0-4` | realtime | Tick/L2/Greeks/IV/期货/涨跌停/港股K线 |
| intraday_minute (L2) | `*/5 9-15 * * 0-4` | intraday_minute | A股/ETF/LOF 分钟K线滚动 |
| intraday_sector (L2.5) | `*/5 9-15 * * 0-4` | intraday_sector | 880xxx 板块分钟K（mootdx TCP 直连） |
| event_driven (L3) | `*/15 * * * *` | default | 新闻/研报/EDB 宏观（7×24 轮询） |
| daily_kline (L4) | `30 16 * * 0-4` | heavy | 日/周/月K线+复权+估值+指标+ETF净值 |
| daily_capital (L5) | `00 18 * * 0-4` | default | 资金流向/龙虎榜/大宗/期货/股本/美股 |
| daily_event (L6) | `00 19 * * 0-4` | default | 分析师预期/财报快报/分红配股/质押 |
| nightly_financial (L7) | `00 22 * * 0-4` | heavy | 财报三表/财务指标/十大股东/融资融券(T+1) |
| weekend_calibration (L8) | `00 3 * * 0`（周一 03:00） | heavy | 全量校准/TDX板块/概念板块/美股全量 |
| monthly_static (L9) | `00 9 1 * *` | default | 股票列表/板块分类/指数成分/交易日历 |
| weekend_backfill (L10) | `00 2 * * 0`（周一 02:00） | heavy | 查 CH 行数精准补下载（特殊分发） |
| integrity_check (L11) | `00 23 * * 0-4` | default | 全表当日数据达标巡检（特殊分发） |
| auction_highfreq (L0) | `*/10 15-25 9 * * 0-4`（6 段含秒） | realtime | 集合竞价五档盘口 10 秒快照 |

调度周期内执行（`scheduler.py:186-243`）：每周期创建**局部 TaskQueue**（裁定 #ARCH-CH-016 v2，消除并发调度周期互相覆盖），DAG 就绪任务并行（最多 8 线程），批次间串行保证依赖；前置 FAILED → BLOCKED 不执行。前置守卫：交易日历 `is_trading_day()`（exchange_calendars XSHG 本地计算，未安装降级 weekday，`trading_calendar.py:1-20`）对盘中/盘后时段自动跳过非交易日；miniqmt 任务另靠 `extra.trading_day_only` 过滤并有拼写防护告警（`scheduler.py:147-183`）。

---

## 7. CLI 子命令用法

入口两种：`integrator`（pyproject `[project.scripts]` → `zephyr.data.cli:main`）或 `python -m zephyr.data`（`__main__.py` re-export，`__main__.py:1-27`）。启动时自动加载项目根 `.env` + `config/.env.clickhouse`（`cli.py:52-71`）。共 **8 个子命令**（蓝图 §8.4 的 7 个 + §8.5 的 speed-test；AGENTS.md 只列了 7 个）：

| 命令 | 作用 | 实现 |
|---|---|---|
| `integrator status [task_id]` | 调度器状态 + 最近 20 条运行记录 / 单任务断点详情 | `cli.py:110-143` |
| `integrator list [--source <src>]` | 列出 128 个任务（可按源过滤） | `cli.py:146-164` |
| `integrator run <task_id>` | 手动触发单任务（含 fallback 链） | `cli.py:167-180` |
| `integrator rerun-failed` | 重跑所有 last_status=FAILED 任务 | `cli.py:183-208` |
| `integrator pause <source>` | 熔断某源（enabled=False，该源任务全跳过） | `cli.py:211-229` |
| `integrator resume <source>` | 恢复熔断 | `cli.py:232-250` |
| `integrator start` | 启动常驻调度进程（SIGINT/SIGTERM 优雅关闭，60s 周期热更新策略） | `cli.py:260-295` |
| `integrator speed-test [--source] [--capability]` | 能力×源小样本测速（rows/sec、错误率），用于主备源选型 | `cli.py:253-257` → `speed_tester.py` |

独立模块入口（不经 integrator）：`python -m zephyr.data.scheduler`（常驻 + 9100 监控端口 + `tmp/scheduler_run.log` 轮转日志）、`python -m zephyr.data.tick_subscriber`、`python -m zephyr.data.sector_snapshot_collector [--poll-interval 30 --push-limit 99]`、`python -m zephyr.data.sector_kline_downloader [--period 1d|1m|5m|all --days N]`、`python -m zephyr.data.kline_resampler [--days N --period 15m]`、`python -m zephyr.data.sector_ranking_engine [--top 99 --json]`。

---

## 8. 数据落盘格式与路径

| 落盘位置 | 格式 | 内容 | 证据 |
|---|---|---|---|
| ClickHouse `c1_market.*`（实测 77 表）/ `c3_fundamental.*`（23 表） | HTTP `INSERT ... FORMAT TSV`（TSV body，`\N`=NULL）；查询走 TCP 9000 | 全部业务数据：K线/Tick/财务/新闻/板块/宏观等 102 种目标表 | `ch_writer.py:17-41,77`；实测行数见 §9 |
| `data/integrator_progress.db` | SQLite（WAL，synchronous=NORMAL） | task_progress 断点 + task_runs 运行流水 | `progress_store.py:50,78-115` |
| `data/integrator_jobs.db` | SQLite（SQLAlchemyJobStore） | APScheduler 持久化 job | `scheduler.py:61` |
| `data/local_fallback/<db__table>/YYYYMMDD_HHMMSS_<uid>.tsv` + `_manifest.jsonl` | TSV 文件 + JSONL 清单 | CH 不可达时的落盘数据，待回灌；原子写 .tmp→rename | `local_replay.py:23-36,75-100` |
| `data/local_fallback/corrupted_parts_audit.jsonl` | JSONL | 破损 part 隔离审计 | `scheduler.py:452` |
| `data/failures/{date}_{task_id}_{ts}.json` | JSON | 失败汇总（ERROR 及以上，300s 冷却） | `alerter.py:50,144-163` |
| `data/metrics.prom` | Prometheus 文本 | 6 项集成器指标 | `metrics.py:51` |
| `data/fallback.sqlite` | SQLite | redundant_source 的 CH 降级库（当前未接线） | `sqlite_fallback.py` |
| `tmp/scheduler_run.log` | 文本日志（RotatingFileHandler 10MB×5） | scheduler 常驻进程日志 | `scheduler.py:1476-1484` |
| `config/.env.clickhouse` | env 文件 | CH 连接配置唯一真源（CLICKHOUSE_HOST=172.24.30.100，TCP 9000 / HTTP 8123），禁止硬编码 IP（裁定 #ARCH-CH-017） | `ch_config.py:1-30` |

CH 表引擎幂等约定：ReplacingMergeTree 直接 INSERT 由后台合并去重；MergeTree 写前按 date_col DELETE（`ch_writer.py:32-35`、`scheduler.py:1045-1066`）。

---

## 9. 实测验证记录

2026-07-22 23:31（项目 Python 3.11，`PYTHONPATH=src`，cwd=/d/ZephyrAlpha）：

- `python -m zephyr.data list` 成功运行：加载策略 11 源、调度计划 13 档、任务 128 个、品类注册表 105 条，且"[TableRegistry] tasks.yaml 表名与品类真源一致"（0 处不一致）。
- ClickHouse 172.24.30.100:8123 `/ping` 返回 Ok；只读实测：`system.tables` 中 c1_market 77 表 / c3_fundamental 23 表；`c1_market.kline_daily` 34,664,504 行、`c1_market.tick_data` 14,324,240,136 行、`c3_fundamental.news_data` 10,161,482 行。
- PostgreSQL 未做连接探测（本模块链路不依赖 PG；depgraph 等治理库不在本文范围）。
- 审查期间发现 `policies.yaml` 于 23:29 被并发会话修改（新增 cls/eastmoney_news 策略），本文以 23:31 后最新版本为准；tasks.yaml（22:59）与 schedule.yaml（22:09）在审查窗口内未再变动。

---

## 10. 模块文件索引

| 文件 | 行数 | 职责 |
|---|---|---|
| `cli.py` | 400 | CLI 8 子命令 + 常驻 start 入口 |
| `scheduler.py` | 1519 | APScheduler 编排 / DAG 并行 / fallback 链 / 3 个守护线程（CH 探活、本地回灌、破损 part 隔离）/ 监控 HTTP |
| `provider_base.py` | 343 | Provider 抽象 + FetchPayload/Result + CapabilityContract + 限流重试退避 |
| `policy_registry.py` | 243 | SourcePolicy + yaml 热更新注册表 |
| `progress_store.py` | 328 | SQLite 断点续传 + 运行流水 |
| `task_queue.py` | 252 | DAG 依赖图 + 状态机（PENDING/RUNNING/SUCCESS/FAILED/BLOCKED/DEFERRED_PERSISTENCE） |
| `ch_writer.py` / `ch_reader.py` / `ch_config.py` | 754/176/138 | CH 写入（HTTP TSV+本地兜底）/ 读取（TCP，自动 FINAL）/ 连接配置单真源 |
| `buffered_writer.py` | 214 | 攒批聚合写入（50000 行/30s） |
| `wal_writer.py` + `wal_codec/` | 301 | tick 链路主动 WAL（段文件 + drain） |
| `local_replay.py` | 302 | 本地落盘 manifest + 自动回灌 |
| `error_classifier.py` | 108 | 可恢复/不可恢复错误分类（驱动 fallback 时机） |
| `news_dedup.py` | 199 | 新闻标题 MD5 去重（7 天窗口，fail-open） |
| `backfill_checker.py` | 669 | L10 周末补下载（查 CH 实际行数） |
| `integrity_checker.py` | 159 | L11 每日全表巡检 |
| `alerter.py` | 269 | 四级告警 + 失败文件汇总 |
| `metrics.py` | 249 | Prometheus 文本指标 |
| `capability_validator.py` | 429 | 启动时 capability 契约校验（fail-closed） |
| `table_registry.py` | 213 | 表名/品类真源消费层（business_data_categories.yaml） |
| `trading_calendar.py` | 99 | XSHG 交易日历守卫 |
| `speed_tester.py` | 566 | 源×能力测速选型 |
| `tick_subscriber.py` | 488 | QMT 实时 tick 订阅常驻服务 |
| `sector_kline_downloader.py` / `sector_snapshot_collector.py` / `sector_ranking_engine.py` / `kline_resampler.py` | 245/450/269/212 | tqcenter 880xxx 板块四件套（手动触发） |
| `implementations/`（10 Provider） | — | ifind 2066 / miniqmt 3759 / akshare 2787 / baostock 268 / tushare 227 / tickflow 247 / tdx 342 / rss 239 / cls 184 / eastmoney_news 202 行 |
| `redundant_source/` | — | MOD-L00-005 主备热切换 + SQLite 降级 + 回灌（当前无消费者） |
| `config/` | — | schedule.yaml（13 档）/ tasks.yaml（128 任务）/ policies.yaml（11 源，派生物） |
| `quality_gate.py` | 27 | re-export 壳（真源在 gov_enforcement） |
| `satellite_geospatial_engine/` | 54 | D_DATA 层文档骨架（无实现） |
| `health_snapshots/` | — | 仅一个 `{}` 占位快照 |
