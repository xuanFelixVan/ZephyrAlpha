---
ttl: task_bound
lane: M1 数据链
segment: D1 多源采集调度 + D2 源接入生命周期 + D3 Provider 源路由 + D10 行情订阅分发
mined_at: 2026-09-25
session: st-commitspeed-tbl-20260924
---

# 01_ingest — 采集段作业簿（D1/D2/D3/D10）

## 一、环节定义与边界

一句话：把 23 个主数据源 × 271 个注册任务 × 29 个时段槽位的原始数据按交易日历灌进 CH 热库，含 tick 实时订阅常驻链。
- **供料方**：外部 API（akshare/tushare/东财/新浪/QMT 沙箱桥/币安 vision 镜像等）+ 本地计算源（internal 24 任务，读 CH 自算）+ QMT 沙箱 tick 桥文件。
- **消费方**：02_cleaning（写前门禁）→ 03_ch_warehouse（落库）→ 04_cold_storage（分层）→ 05_tdm_crossaxis（dataset 引用）。

## 二、六向台账

| 向 | 内容与实证 |
|---|---|
| 上游输入 | ① 外部源 API；② QMT 沙箱桥文件 `E:\qmt_bridge_sim\ticks3.csv`（tick_subscriber.py:1456，尾读+字节 offset 增量+timetag 去重）；③ internal 本地计算（internal_compute_provider.py，读 CH 派生）；④ 币安公开镜像 binance.vision（免 key，Owner 2026-09-11 裁定，tasks.yaml:877 注） |
| 下游消费 | ch_writer 写前门禁（ch_writer.py:971-986）→ c0_meta.fetch_perf 性能记录（DatabaseService 实查 c0_meta 1 表）；进度真源 data/integrator_progress.db（data/ 根实测在盘，含 -wal/-shm） |
| 自动化触发 | **APScheduler 常驻**：ZephyrAlpha_DataScheduler 计划任务 **Running**（schtasks 实测 2026-09-25）；schedule.yaml 29 个时段槽位（L0.5 盘前~L13.5 日历 diff；文件头写"16 个槽位"=过期注释，实数 29）。**tick 常驻**：ZephyrAlpha_TickSubscriber **Running**（桥模式 TICK_SOURCE=bridge，tick_subscriber.py INARIANTS 行 8）。**熔断**：source_circuit_breaker.py（64号 Q17，连续失败 N 次熔断 M 分钟+半开探针）。**QMT 看门狗**：ZephyrAlpha_QMTWatchdog Ready |
| 真源与注册表 | 任务真源=src/zephyr/data/config/tasks.yaml（**271 任务**，yaml 实解析）；时段真源=config/schedule.yaml（29 槽）；源策略真源=PolicyRegistry（policy_registry.py，pause/resume 熔断态）；能力画像=config/resource_profile_registry.yaml（29 个 data_slot_*，与 schedule.yaml 逐槽对齐实核）；缺口真源=config/known_data_gaps.yaml（**63 条 gap**，grep 实数）；槽位→executor 映射 realtim(4线程)/intraday_minute(4)/default(8)/heavy(2)（schedule.yaml:6 注） |
| 门禁与质量尺 | speed-tester.py 测速选型主备源（CLI speed-test）；source_health_check.py 调度器启动时全 provider 连通测试；source_sla_tracker.py 可用率/P50/P99/失败分布（MOD-DATA-066）；fetch_perf 落 c0_meta（fetch_perf_recorder.py）；任务校验 table_registry.validate_tasks_yaml WARN 不阻断（table_registry.py:167-195） |
| 当前运行状态 | **绿（带 P1 疤痕）**。绿证：DataScheduler/TickSubscriber 双 Running（schtasks 实测）；CH 主表 max_date=2026-09-24（kline_etf_1min/tick 族实查）。疤痕：#ARCH-351 miniQMT 清退 24 任务无退路 status=open（architecture_issue_registry.yaml:22342-22360）；ZephyrAlpha_TradingWatchdog **Disabled**（schtasks 实测，gap report 遗留项仍未复活）；ZephyrAlpha_NightlySentiment Disabled（data/runtime/nightly_sentiment.disabled.by-st-data-fix-20260921.bak 改名停用痕迹在盘，现行=nightly_sentiment_llm.enabled） |

## 三、子模块清单（两源交叉验证：tasks.yaml 源分布 × implementations/ 目录实列）

**源分布**（tasks.yaml 271 任务 yaml 解析实数）：akshare 100 / miniqmt 56（清退后存量待迁移）/ akshare_alt 36 / internal 24 / tushare 13 / tqcenter 5 / tdx 5 / tickflow 4 / hyperliquid 4 / baostock 3 / fred 3 / rss 2 / crypto_binance 2 / eia 2 / qmt_bridge 2 / irm 2 / qweather 2 / cls·eastmoney_news·backfill·crypto_sentiment_panel·alt_regime_signal·alt_fx_ecb 各 1。

**Provider 层**（src/zephyr/data/implementations/ 实列 **45 个 .py**，ls 交叉 provider_base.py 基类）：

| 模块 | 入口 | 状态 |
|---|---|---|
| akshare_provider / akshare_alt_provider | implementations/akshare_provider.py（100+36 任务主承载） | production；akshare_alt=东财 datacenter 族 |
| miniqmt_provider | implementations/miniqmt_provider.py | **清退残留**：56 任务登记 vs 2026-09-18 清退；#ARCH-351 在案 |
| qmt_bridge_provider | implementations/qmt_bridge_provider.py | 生产（大QMT 沙箱桥，2 任务+tick 桥） |
| tushare_provider | 13 任务主源（#ARCH-IFIND-FAILOVER 后转正，tasks.yaml:854 等 4 处注） | production |
| tqcenter_provider | 5 任务；2026-09-11 mootdx 通道退化换道入注（tasks.yaml:949） | production |
| tdx_provider | 5 任务（板块/880 族） | production |
| crypto_provider / okx / hyperliquid / onchain / crypto_profile / crypto_universe_selector | crypto 族 8 文件 | production（OKX DNS 阻断后 binance vision 主） |
| fred / eia / fx_ecb / qweather | 宏观另类 4 源 9 任务 | production |
| rss / cls / eastmoney_news / tushare_news_connector / announcement | 新闻族 5 文件 | production |
| internal_compute_provider | internal_compute_provider.py:97-124 `_INTERNAL_COMPUTE_CAPABILITIES` 18 项 | production（读 CH 自算，零外采） |
| tickflow / irm / sentiment_panel / northbound_hold / sector_* / breadth / limit_up_pool / tick_depth_backfill | 采集侧专用 | production |
| provider_base.py | 基类+capability 声明 | production |

**调度与韧性层**（src/zephyr/data/ 实列）：scheduler.py（2704 行，IntegratorScheduler+单实例锁 #SCHED-DUAL-INSTANCE cli.py:274）、task_queue.py、progress_store.py（integrator_progress.db）、policy_registry.py（熔断）、source_circuit_breaker.py、source_sla_tracker.py、source_health_check.py、error_classifier.py、speed_tester.py（29KB）、fetch_perf_recorder.py、alerter.py、alert_webhook_dispatch.py（39KB）、progress/catchup：backfill_checker.py（48KB，L10）、auto_backfiller.py（事件触发回填）、catchup_guard.py（L10.7 档期对账，治 2026-09-01 宕机 32h 盲区）。

**tick 实时链**：tick_subscriber.py（85KB，xtdata/bridge 双模式， WalWriter P0-1 主动落盘）、wal_writer.py（段文件+drain 线程）、buffered_writer.py、tick_redis_cache.py（H1 热缓存）、tick_depth_writer.py、local_replay.py（回灌）。

**接入生命周期 SOP**：sop/data_ops_sop/data_source_onboarding_sop（D2 真源，全网挖矿→报批→建表→接入→三查→路由→退役全链；本册只登记入口不重挖——治理侧归 M3）。

## 四、堵点与病灶

| # | 现象 | 根因 | 修法草案 | 工作量 | 本车道可修 |
|---|---|---|---|---|---|
| B1 | **#ARCH-351（open P1）**：9/18 miniQMT 清退命中 24 任务无可用退路（TF01 8 主源/TF02 16 全裸/TF10 ex_dividend_event 为 stk_limit 公式法唯一输入）；TF07 daban 日频消费←周频生产名义 DAG 边（周二至五装载上周事件） | 退役映射表缺位+跨时段 DAG 时窗校验缺失 | 落地裁定#376 退役映射表+时窗校验设计；逐任务走 D2 退役 SOP 换源（akshare/tushare 已有 100+13 任务先例） | 2-4 天/批 | 是（换源施工）+总筹裁优先序 |
| B2 | known_data_gaps 63 条缺口长期在册；bdpan tick 看门狗 OS 任务 2026-09-24 已退役（known_data_gaps.yaml 头部注），tick 深史缺口须人工触发 | 自动巡检任务退役后无替代触发器 | 挂 data_supply_sentinel 盲点腿或 catchup_guard 档期，禁裸人工记忆 | 0.5 天 | 是 |
| B3 | schedule.yaml 头注释"当前 16 个时段槽位"vs 实数 29；骨架册 D1 写"30 个槽位"vs resource_profile 29——三处三个数 | 手工维护散文计数违反宪法 §4.4（计数用字段不写死） | 头注释改为引用生成器计数或删数字 | 0.1 天 | 是 |
| B4 | TradingWatchdog/RestartMiniQmt 计划任务仍 Disabled（schtasks 实测+2026-09-14 gap report :18-19 同案） | miniQMT 清退后看门狗对象消失，未正式退役登记 | 走 D2 退役登记或换 QMT 桥版看门狗 | 0.5 天 | 是（登记）；复活=待裁 |
| B5 | 历史病灶闭环核验：①股东户数断供两月（2026-07 发现）→supply_sentinel 治本**已闭环**（supply_sentinel.py 诞生背景注+第一配置腿）；②ifind 退役→tushare/akshare 转正**已闭环**（4 处 #ARCH-IFIND-FAILOVER 注）；③东财反爬→tushare 升主**已闭环**（tasks.yaml:186/:1214/:1913/:2235）；④miniqmt→sina 快照族接管**已闭环**（tasks.yaml:1019 裁定#339 注） | — | — | — | — |

## 五、提速与合并机会

1. **pause/resume 与 source_circuit_breaker 双轨**：手动熔断（CLI）与自动熔断（滑窗）互不感知——可合并为一套熔断状态真源（policy_registry 已是单例，落点现成）。
2. **speed-tester（29KB）与 source_health_check（24KB）同域重复**：两者都做"源连通+延迟小样本"，可合并为同一探针宿主两档深度。
3. **tasks.yaml 271 任务无生成器**：手工 YAML 已现漂移（B3 同根因）；内收判据"静态清单禁手工维护"——table_registry.validate 已 WARN，可升级为生成器产出校验报告挂 integrity_check。
4. miniqmt_provider.py 仍 8000+ 行被 56 任务引用——清退迁移完成后整文件退役是最大单体净删。

## 六、自审闸三态

**挖干可施工**（D1/D3/D10 六向全实证；D2 生命周期 SOP 真源已锚定不重挖）。B1 换源施工可开工，退役映射表落地需裁定#376 细则（已有 related_adjudication，非新裁定）。

## 七、复核命令

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$PATH"
python -m zephyr.data --help                      # 8 子命令
python -c "import yaml;print(len(yaml.safe_load(open('src/zephyr/data/config/tasks.yaml',encoding='utf-8'))['tasks']))"  # 271
grep -c "^  [a-z_0-9]*:" src/zephyr/data/config/schedule.yaml   # 29 槽位
ls src/zephyr/data/implementations/ | wc -l        # 45 provider 文件
powershell -NoProfile -Command "Get-ScheduledTask |? {$_.TaskName -match 'DataScheduler|TickSubscriber|TradingWatchdog'} | ft TaskName,State"
sed -n '22342,22360p' docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml  # #ARCH-351
```
