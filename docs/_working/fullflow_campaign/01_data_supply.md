---
ttl: task_bound
completes_when: 全流通战役收官且最终交付报告落盘
---

# S1 数据供给链环节簿

> 挖掘时点：2026-10-08 01:50–02:10（只读调研 + CLI 实测）；挖掘代理 D。
> 证据真源：`src/zephyr/data/`（数据集成器 MOD-L00-004）、`config/data_supply_chain_map.yaml`（图12 DSCMAP-012，机生 as_of=2026-10-07，blood_stage=f2_done）、`docs/01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml`（REG-DATAFLOW-001 v1.9.9）、`src/zephyr/data/config/{tasks,schedule}.yaml`、OS 计划任务实查（Get-ScheduledTask）。
> 密钥纪律：`.env.clickhouse` / `.env.postgres` 只登记键名结构，值不入档。

## 一、输入面

- **外部源 23 家、在册任务 275 条**（tasks.yaml 实测计数）：miniqmt 56、akshare 100、akshare_alt 38、internal 26（内部衍生）、tushare 13、tqcenter 5、tdx 5、tickflow 4、hyperliquid 4、baostock 3、fred 3、eia 2、qweather 2、rss 2、qmt_bridge 2、irm 2、crypto_binance 2、cls 1、eastmoney_news 1、crypto_sentiment_panel 1、alt_fx_ecb 1、alt_regime_signal 1、backfill 1。
- **资产登记三实体**（data_asset_registry）：sources 18 / datasets 336 / jobs 122——与 tasks.yaml 枚举面并存，环节枚举四源纪律（tasks/schedule/scheduler 特殊槽/进程内写手）在案。
- **能力面 216 种 capability**：K 线全家族（日/周/月/1-60min/ETF/LOF/板块/港美/期货/期权/可转债）、财务三表、资金流、龙虎榜、两融、北交所、宏观（FRED/EIA/世界银行/中债/利率决议日历）、加密（Binance/Hyperliquid/OKX/onchain/恐惧贪婪）、另类（生猪/航运/台风/深圳统计局 22 族/和风天气/生猪现货）、新闻舆情（东财/央视/百度/RSS/研报）。
- **深史通道**：通道 A=QMT SDK `download_history_data`（服务器保留约 1 个月，miniQMT 清退后走大 QMT 沙箱，前提=终端开着）；通道 B=bdpan 百度网盘月度归档（2026-08-15 实证 3.19 亿行回补）；自有囤货=c1_market.tick_data 88 亿行（2025-01 起）。
- **输入侧已知带伤**：tushare provider 不可用（scheduler.log 尾部 ERROR：`news_tushare_incremental error=Provider tushare 不可用`）；miniQMT 已于 09-18 清退，tick 实时改走大 QMT/qmt_bridge。

## 二、输出面

- **ClickHouse c1_market**（172.24.30.100，Hyper-V Ubuntu VM）：目标表 197 张（机生 target_table_count）；读写链 TCP(9000)→HTTP(8123)→本地 TSV 落盘三级降级；批量写先落 local_fallback（78 个暂存域）再回灌。
- **存储分工一盘一责**（INFRA-STORE-003 / 宪法 §7）：CH=行情主库；PostgreSQL=depgraph/治理（config/.env.postgres，9 键：HOST/PORT/DB/USER/PASSWORD/READER_USER/READER_PASSWORD/WRITER_USER/WRITER_PASSWORD）；SQLite=运行态（data/integrator_jobs.db、integrator_progress.db、governance.db）；Redis H1 热缓存（同 VM :6379）；冷库=F:/zephyr_cold（实测在：00_manifest/10_inbox/20_raw/30_corpus/40_migration/50_archive/90_tmp）；备份总仓=G:/backup。旧 market.duckdb 已于 2026-07-05 删除。
- **CH 配置唯一真源**：config/.env.clickhouse（10 键：HOST/PORT/HTTP_PORT/USER/PASSWORD/DATABASE/READER_USER/READER_PASSWORD/WRITER_USER/WRITER_PASSWORD），经 `ch_config.py` fail-closed 加载（裁定 #ARCH-CH-017/#ARCH-CH-019，禁硬编码 IP 默认值）。
- **下游消费**：因子/形态/回测/仪表盘/策略引擎；run 态产物=scheduler.log、source_health_streaks.json、quality_sentinel/、sla/、metrics.prom、backup_state.json、rolling_archive_state.json。

## 三、入口面（命令 + 实测 + 一句说明）

| # | 入口 | 实测 | 说明 |
|---|------|------|------|
| 1 | `python -m zephyr.data --help` | 绿 | 主入口，8 子命令与宪法声明一致：status/list/run/rerun-failed/pause/resume/start/speed-test |
| 2 | `python -m zephyr.data status/list/run/rerun-failed/pause/resume/start/speed-test --help`（8 个逐一） | 绿 | 全部 argparse 正常出帮助；pause/resume=按源熔断，speed-test 支持 --source/--capability |
| 3 | `python -c "import zephyr.data"` | 绿 | 冒烟通过，Python 3.12.8 |
| 4 | `python -m zephyr.data.quality_sentinel --help` | 绿 | 质量哨兵，参数 --tables/--days/--config/--output-dir/--no-report/--no-alert |
| 5 | `python -m zephyr.data.onboarding_wizard --help` | 绿 | 新源接入向导，子命令 start/resume/confirm/status/checklist |
| 6 | `python -m zephyr.data.tick_subscriber --help` | 绿 | QMT 实时 Tick 订阅服务（--bridge，env=sim/real） |
| 7 | `python -m zephyr.data.consensus_crosscheck --help` | 绿 | 一致预期每日双向验证（--selftest 火警演习） |
| 8 | `python -m zephyr.data.macro_vintage --help` | 绿 | PIT 宏观工具面（--selftest/--print-ddl/--pit-sql AS_OF） |
| 9 | `python -m zephyr.data.ch_parts_monitor` | 绿 | 实跑返回"OK: 无表 active parts 超阈值(30)"——0 字节部件监视器在岗 |
| 10 | `scripts/governance/data_quality/check_tick_duplication.py --help` | 绿 | RULE-DATA-OPS 判重正门，--month/--market-type/--json（注意：图12 缺口台账记其查询路径 09-25 坏着，--help 绿≠查询绿） |
| 11 | `python -m zephyr.data.backfill_checker --help` | 红 | **无 argparse，--help 被忽略直接开跑 L10 周末补下载**并连上 CH writer——本次实测误触 25 秒后 timeout 截断；事后核验 scheduler.log（止于昨日 15:50）与 local_fallback/_manifest.jsonl（01:37，早于误触）均无本次写入痕迹 |
| 12 | `python -m zephyr.data.supply_sentinel --help` | 黄 | 设计上无 CLI 入口（源码自注"运维一次性巡检"），静默退出 0；由调度槽分派 |
| 13 | `python -m zephyr.data.{integrity_checker,source_health_check,storage_tiering,data_service}` | 黄 | 均无 --help 输出（库模块无 argparse 主入口），只能被调度器/上层调用 |
| 14 | OS 计划任务 `Get-ScheduledTask`（Zephyr 过滤） | 绿 | 实查约 45 个任务：**ZephyrAlpha_DataScheduler=Running**、ProcessReaper=Running、DailyBackup/CHHealthProbe/QMTWatchdog/PostSettlement/IndexMinuteEOD/IntradayFundFlow/BoardIndexRealtime/AltFxECB/RSSHub/SectorSnapshot/NightlySentiment/TickSubscriber/RESTORE-DRILL=Ready |
| 15 | `scripts/data/` 工具族（backfill_*/repair_*/synth_*/import_bdpan_tick_zip/onboard_source/source_health_patrol 等约 45 个） | 黄 | 未逐个实测；backfill_night.ps1 已实证修过"powershell -File 恒返 0"静默失败病（exit $LASTEXITCODE） |

## 四、模块面（module 清单：路径 + 一句职责）

**src/zephyr/data/（约 95 个 .py，编组）**
- `__main__.py` / `cli.py` — 集成器 CLI 入口（8 子命令，get_integrator 单例）。
- `scheduler.py`（140KB）— 常驻调度器：按 schedule.yaml 25 档期槽派工，同槽进 TaskQueue。
- `provider_base.py` — Provider 契约：IngestProviderBase/FetchPayload/FetchResult/CapabilityContract；铁律=Provider 只拉数返回 list[tuple]，写 CH 归调度器。
- `implementations/`（44 个 provider）— 源实现：akshare/akshare_alt/miniqmt/qmt_bridge/tushare/baostock/tdx/tickflow/tqcenter/okx/okx_swap/hyperliquid/crypto/fred/eia/qweather/rss/cls/eastmoney/irm/fx_ecb/onchain/sentiment_panel 等；SDK 懒加载。
- `ch_config.py` — CH 配置唯一真源加载器（fail-closed）。`ch_reader.py`/`ch_writer.py` — 读写双通道（writer=TCP→HTTP→本地 TSV 三级降级）。`wal_writer.py`+`wal_codec/` — 先落盘再入库。`buffered_writer.py`/`tick_depth_writer.py`/`tick_redis_cache.py`/`table_registry.py` — 写侧配套。
- `redundant_source/`（6 文件）— 备胎体系：sina_tencent 备源/source_switcher/sqlite_fallback/heartbeat_monitor/backup_tick_poller/recovery。`source_circuit_breaker.py`/`source_health_check.py`/`source_sla_tracker.py`/`dual_source_guard.py` — 熔断/健康/SLA/双源守卫。
- `backfill_checker.py`/`auto_backfiller.py`/`c4_history_repair.py`/`event_calendar_filler.py`/`catchup_guard.py` — 缺口检测与回补族。
- `quality_sentinel.py`/`integrity_checker.py`/`supply_sentinel.py` — 三哨兵（业务新鲜度阈值/达标检测/供给巡检）。`cleaning_*`（5 文件）— 清洗规则/引擎/异常/期望托管。`purity_adjudicator.py`/`cross_source_validator.py`/`consensus_crosscheck.py`/`divergence_stats.py`/`quarantine_manifest.py`/`quality/`（SLA 燃烧率+违约预测）— 质量裁决面。`capability_{semantic_gate,symbol_gate,validator}.py` — 能力门。
- `macro_vintage.py`/`pit_query.py` — PIT 宏观与点时查询。`sector_*`（7 文件）— 板块管线。`news_*`（3）/`intraday_sentiment_loop.py` — 新闻情绪。`kline_resampler.py`/`multi_timeframe_fusion.py` — K 线重采样与融合。`storage_tiering.py`/`data_compression_archiver.py` — 分层与归档。`onboarding_wizard.py` — 新源接入。`calendar/`（ashare/crypto）+`trading_calendar.py` — 交易日历。`satellite_geospatial_engine/` — **空壳（仅 __init__.py）**。
- `config/`（tasks.yaml 275 任务、schedule.yaml 25 槽、policies.yaml、data_supply_sentinel.yaml、known_data_gaps.yaml 76 缺口条、manual_calendar_events_schema.yaml）。

**治理与基建**
- `config/data_supply_chain_map.yaml` — 图12 供给链图真源：43 节点（production 10 / built 13 / partial 13 / pending 17）、62 边、gap 节点 15、gaps_registered 71、unwired_or_hollow 9、五段 S1 采集→S2 入库→S3 衍生→S4 冷备→S5 对账修复。
- `docs/.../catalogs/data_asset_registry.yaml` — 数据资产唯一真源（18 sources/336 datasets/122 jobs）。
- `src/zephyr/infrastructure/database_service.py` — 统一连接管理（CH c1_market + PG depgraph + SQLite + Redis H1）。
- `scripts/governance/data_quality/check_tick_duplication.py` — tick 判重正门；`scripts/data/` 约 45 个回补/修复/合成工具。

## 五、自动化面（自动/手动/半自动，依据）

- **自动（实证在跑）**：OS 计划任务矩阵约 45 个，其中 DataScheduler=Running（常驻调度进程，25 档期槽：pre_market 9 任务/auction_highfreq 2/intraday_realtime 16/intraday_minute 16/intraday_sector 5/post_auction/daily_kline 38/daily_capital 44/daily_event 42/weekend_calibration 44/monthly_static 21/event_driven 11/daily_crypto 6/eod_reconciliation 1 等）；ProcessReaper=Running（本次实查）；DailyBackup、CHHealthProbe、PostSettlement、IndexMinuteEOD、IntradayFundFlow、BoardIndexRealtime、RSSHub、SectorSnapshot、NightlySentiment 均 Ready 挂防。产数留痕：local_fallback 78 域当日有暂存（alt_sz_air_quality_daily 22:56 等）。
- **半自动**：周末回补 L10（weekend_backfill 1 任务 + backfill_night.ps1 兜底，需 CH 可达）；restore_drill（ZEPHYR-RESTORE-DRILL 计划任务 Ready 在册，但图12 记"归档副本今天仍可还原"未证）；4 条任务 schedule=disabled（人工决定是否启用）；speed-test 选型、pause/resume 熔断=人触发机执行。
- **手动**：bdpan 深史 tick 回补（看门狗计划任务 BdpanTickWatch 已于 09-24 退役，known_data_gaps 自认"每日自动巡检缺口不再成立"）；新源接入 onboarding_wizard；known_data_gaps 缺口治理登记；清洗分歧（cleaning_disagreement_stats）出报告人裁决。

## 六、缺口面（每条：[色] 描述 + 处方）

1. [红] **判重正门带伤在岗**：图12 缺口台账（as_of=10-07）明记"RULE-DATA-OPS 指定的判重唯一正门自身坏着：不得以工具跑过了当作删数据的许可"——本次 --help 实测绿但查询路径未经 CH 实弹验证。处方：按 DSC 台账修复 check_tick_duplication 查询路径并留 fail-visible 复跑证据，修复前冻结一切 tick 删重操作。
2. [红] **备份可还原性未闭**：archive_manifest.jsonl 只证明"导出与删除发生过"，不证明副本今天可还原；图12 记 restore_drill 证据链未闭合（计划任务虽 Ready）。处方：跑一轮 ZEPHYR-RESTORE-DRILL 实弹还原并把还原证据写回 DSC-TERMINUS 案卷。
3. [红] **研报明细停更**：09-25 定账 max(publish_date)=09-18 不涨，预期重建 max=09-14 仍落后上游（eastmoney 研报源）。处方：走 backfill_checker 定点回补前先修 eastmoney_news/研报 provider 抓取。
4. [黄] **tushare 源断供在案**：scheduler.log 尾 ERROR news_tushare_incremental Provider 不可用；13 条 tushare 任务与 rss 新闻链受牵连。处方：speed-test 复测 tushare 配额/令牌，不可用则 akshare_alt 38 任务的备源切换路径顶上并登记 fallback 留痕。
5. [黄] **四个消费方在等生产者**（图12 gap 节点）：净值序列（FAC-E8/E9+ops_alert_feed 在等）、ExecutionReport（等 qmt_file_bridge_integra...）、feature_store/factor_signal 落点（buffer.py/CH 侧未通）。处方：逐一挂 task_id 进 tasks.yaml 或明确降级为 detect_only 并登记缺口病历。
6. [黄] **tick 实时链依赖大 QMT 终端开着**：miniQMT 09-18 清退后通道 A 前提=终端在线；TickSubscriber 计划任务 Ready 但是否当日有产未证。处方：给 tick_subscriber 加"当日 tick 行数"新鲜度探针并入 supply_sentinel 阈值。
7. [黄] **bdpan 深史巡检自动化退役**：BdpanTickWatch 08:00 巡检任务 09-24 实证不存在，>1 个月深史缺口无人自动发现。处方：要么重建计划任务、要么把深史缺口巡检并入周末回补槽（二选一，禁悬空）。
8. [黄] **backfill_checker 无 argparse**：`--help` 即开跑补下载（本次实测踩中，25 秒截断，核验无写入痕迹）。处方：补 argparse 主入口 + `--dry-run` 默认安全档；在入口面文档标注"该模块禁裸跑"。
9. [黄] **supply_sentinel/integrity_checker/source_health_check 无 CLI 面**：只能被调度器调，人工无法单独验证。处方：统一补 `--selftest` 或 `--check-once` 只读档（对齐 macro_vintage 先例）。
10. [黄] **43 节点仅 10 个 production**：built 13/partial 13/pending 17，另有 unwired_or_hollow 9（含 satellite_geospatial_engine 空壳模块）。处方：pending 节点按骨架 §1 逐行升 ✅ 或降级摘除；空壳模块按内收铁律 w5_1 判退役。
11. [绿] **0 字节部件事故已闭环**：09-25 187×0 字节 parts 打死 system.* 枚举面的事故已有 _quarantine_20261001/03 隔离目录 + ch_parts_monitor 阈值监视（本次实测 OK）+ "探测失败必判红"纪律入法。处方：无需动作，保持监视器挂防。
12. [绿] **供给主链当日有产**：DataScheduler Running + local_fallback 当日暂存 + 图12 骨架 §1 十行 ✅（production 数==✅ 数双轴口径），链路不是断的。处方：无需动作。

## 七、自审闸

**裁定：黄（通道在、主链在跑，但保险丝未全闭）。**
一句版：数据供给链是全仓自动化程度最高的一段——23 源 275 任务 25 槽由 OS 级计划任务矩阵实跑（DataScheduler=Running 实证），CH 197 表、冷备/熔断/判重/哨兵四位一体在岗；但 production 验证面仅 10/43 节点，判重正门带伤、备份可还原性未证、tushare 断供三处保险未闭，按"production 必带 freshness_evidence"的铁律只能裁黄不能宣绿。

---

*附：挖掘过程事件披露——入口面 #11 实测 `backfill_checker --help` 时因该模块无 argparse 导致 L10 补下载启动约 25 秒后被 timeout 截断；事后核验 scheduler.log（止于前日 15:50）、local_fallback/_manifest.jsonl（01:37 早于误触）均无本次运行写入痕迹，判定停留在只读缺口检测阶段。此事件本身即缺口 #8 的实证。*
