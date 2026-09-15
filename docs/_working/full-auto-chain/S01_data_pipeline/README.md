---
ttl: task_bound
title: S01 数据落地管线挖矿文档
session: st-fullauto-20260915
date: 2026-09-15
---
# S01 数据落地管线

> 挖矿定位：S01 已较成熟（16→21 时段常驻调度），本环节**轻挖**——重点是现状核验+在途欠账登记，不新增施工。挖矿方法=mining_sop_policy.md §2-§6。

## 1 现状盘点（自动化状态+file:line 证据）

### 1.1 调度核
- **IntegratorScheduler 常驻**：`src/zephyr/data/scheduler.py:536` class IntegratorScheduler。自证能力（实读构造器）：
  - 启动探针（live 网络探针/CH 探活/破损 part 检测，startup_probes 默认 True）；
  - 崩溃自愈：初始化时 `reap_stale_runs(max_age_hours=24)` 清理卡死 RUNNING 任务（scheduler.py:574 附近）；
  - per-source 自动熔断器：`CircuitBreakerRegistry`（连续失败 N 次/滑窗错误率→熔断 M 分钟→半开探针，scheduler.py:596 附近）；
  - DDL 前置校验告警去重（4h 窗口，scheduler.py:523-527）。
- **时段表**：`src/zephyr/data/config/schedule.yaml:23` 起，实数 **21 个时段**（线索口径 16 已过期，增长项=daily_crypto/event_driven/news_slow/consensus_crosscheck/auction_highfreq/catchup_guard）：
  pre_market(8:30) / intraday_realtime(盘中5min) / intraday_minute / intraday_sector / event_driven(3min) / news_slow(30min) / daily_crypto / daily_kline(16:30) / daily_capital(18:00) / daily_event(19:00) / research_nightly(20:30) / consensus_crosscheck(23:30) / nightly_financial(22:00) / weekend_calibration(周日3:00) / monthly_static(月初9:00) / weekend_backfill / daily_backfill(17:00) / integrity_check(2:00) / **catchup_guard(5:30，治本 cron 错过无补跑——9/1 调度器 10:37 才被拉起事故的修复)** / nightly_sentiment(8:20) / auction_highfreq(9:15-9:25 每10秒五档盘口，cron 6 段)。
- **任务 DAG**：`src/zephyr/data/config/tasks.yaml` 共 **3093 行**，227 个 source 任务。
- **计划任务守卫**：reaper 计划任务存活是写操作前提（宪法 RULE-GUARDIAN）。

### 1.2 数据源面（⑥数据字段向实测）
tasks.yaml source 分布（grep 实测）：akshare 104 / miniqmt 66 / akshare_alt 29 / internal 18 / tushare 12 / tqcenter 5 / tdx 5 / baostock 5 / tickflow 4 / fred 3 / rss 2 / qweather 2 / eia 2 / crypto_binance 2 / local_valuation 1。

### 1.3 与全链的挂接（②下游向实测）
- 数据调度器已带**策略管线唤醒钩子**：`src/zephyr/data/scheduler.py:628-631`（C6 策略管线唤醒，MOD-BT-190 wire_data_scheduler：轻 kind drain+翻译件积压扫描）→ `src/zephyr/strategy_pipeline/pipeline_events.py` journal→drain。即 S01 不仅是数据底座，还是 S04-S07 事件链的时钟源。

## 2 六向挖矿日志表

| 向 | 内部发现 | 外部发现(URL+年份) | 判定 |
|---|---------|-------------------|------|
| ①上游 | 数据源=Owner 一头（S00 边界）：14 种外部/内部源已在 tasks.yaml 登记；tick 来源经 bdpan 停更事故后切 xtdata（market-data-gap-report） | 无新增搜索（Owner 一头=账号/API/充值，属 S00 不施工） | signal |
| ②下游 | scheduler.py:628-631 已挂 pipeline_events 唤醒钩子——数据落地→C2/C4/C6 事件链自动消费；消费表=kline_daily_hfq/kline_index/kline_etf_daily/stk_limit/index_constituent（c4_batch_screen.py:249 数据清单实引） | — | signal |
| ③算法/机制 | 已有：熔断器/启动探针/僵尸任务收割/DDL 前置校验/integrity_check 时段 | Pico(Corvil) feed 质量监控=检测 feed gaps/stale prices/missing data（https://www.pico.net/products/corvil-analytics/market-data-analytics/ ，Pico，2025 在营）；数据可观测性六柱=freshness/volume/distribution/schema/lineage/semantic（https://www.atlan.com/know/ai-agent/data-for-ai/data-observability-for-ai-pipelines/ ，Atlan，2025）；"checks left"原则=入仓即校验（https://www.pantomath.com/data-pipeline-automation/data-quality-checks ，Pantomath，2025） | signal |
| ④后端 | integrity_check(2:00)+catchup_guard(5:30)+weekend_calibration 已覆盖缺口巡检/补跑/校准；check_tick_duplication.py 判重（宪法 RULE-DATA-OPS） | 开源观测工具（Great Expectations/Soda/Monte Carlo 类）——本仓已有自研对等物（integrity_check+告警去重），不引入 | signal |
| ⑤前端 | 仪表盘入口=`src/zephyr/frontend/dashboard/app_panel.py`（宪法 §7）；数据健康页深挖属 S13 前端班边界，本环节只登记 | — | signal（登记不施工） |
| ⑥数据字段 | 227 任务×14 源分布实测（§1.2）；tick 永久缺口 6 交易日已登记不可恢复（2026-09-14-market-data-gap-report.md"永久事实"节） | tick 数据质量控制学术处理（https://www.researchgate.net/publication/391971666 ，ResearchGate，2025）——印证本仓"缺数据登记不可恢复+判重"路线正确 | signal |

外部搜索合计 1 轮（轻挖口径），无 429 受阻轮（子查询 429 均在轮内重试成功）。

## 3 业界与开源对照（四闸过滤后）

| 业界实践 | 本仓现状 | 四闸结论 |
|---------|---------|---------|
| 市场数据专用 feed 监控（Pico/Corvil：gap/stale/missing 全 venue） | integrity_check 时段+缺口报告+告警去重，已对等 | A 股适配✅；**不引入**（自研已覆盖，引入=为自动化而自动化） |
| 数据可观测六柱（freshness/volume/distribution/schema/lineage/semantic） | freshness=catchup_guard；volume=每日覆盖率 SQL（scheduler.py SQL_DAILY_COVERAGE）；schema=DDL 前置校验；lineage=run 档案 | 六柱中 4 柱已有自研对等；distribution/semantic 柱=长尾登记，非本班 |
| shift-left（入仓即校验） | 采集侧熔断+DDL 前置校验已属此路线 | 已达标 |

## 4 堵点与欠账清单

1. **防复发四件套待立项**（2026-09-14-market-data-gap-report.md 遗留①）：①miniqmt 日线车道补 920 段覆盖+标的数偏差>1% 告警；②ch_writer 表列缓存失效机制；③新表 DDL 前置校验（已有部分）；④TICK_SOURCE 切 xtdata 后桥模式降级确认（待 Owner/A22）。
2. **TradingWatchdog / RestartMiniQmt 计划任务仍 Disabled**（遗留②）——涉实盘/终端管理，等 Owner 裁定，至今未见。
3. **alt_sz_subject 2 件死信在途**（遗留③）：writer 写 `alt_sz_subject` 而 registry/DDL 为 `alt_sz_market_subject`，留 C-1 会话收口。
4. **备份表清理未确认**（遗留④）：`kline_1min_tzbak_20260914` 等系列，验证期后删。
5. **tick 永久缺口**（07-03/07-06~07-09/08-05/08-06，bdpan 停更+QMT retention）——已登记 accepted，非欠账是事实。
6. **线索核验不符两项**：①"mootoor 通道死亡四替代全灭"——全仓 grep（docs/src/md/yaml/py）零命中，仓内无此名记录，无法核实，登记为**会话内存线索待核**（不影响本环节结论）；②"估值全月窗重刷"——docs/_working 未检索到同名记录，同上待核。

## 5 施工项建议

**本班施工：无**（S01 成熟，骨架定位=挖矿+核验；上述欠账均有归属会话/Owner 门位，不代修）。

**挂起排期（登记）**：
- G-01 防复发四件套立项（解锁：缺口报告遗留① Owner 立项）；
- G-02 TradingWatchdog/RestartMiniQmt 启停（解锁：Owner 裁定）；
- G-03 alt_sz_subject 死信收口（解锁：C-1 会话）；
- G-04 备份表清理（解锁：验证期结束）；
- G-05 观测"distribution/semantic"两柱（解锁：出现分布漂移实际事故再立，防过度工程）。

## 6 封矿结论

- 六向全部 signal，无 noise 轮——但信号均为"现状健康+欠账已有归属"，**无新增可施工矿脉**。
- 算法/机制向与④后端向的外部对照全部落在"本仓已有自研对等物"，按挖后自审闸 §6 判：引入外部观测工具=自动化对象本就无人参与+终局无位置，**方案封矿**（不引入 Great Expectations/Monte Carlo 类）。
- S01 结论：**核验通过，欠账登记完毕，本环节挖矿终结**（时间盒内无长尾未挖矿脉）。
