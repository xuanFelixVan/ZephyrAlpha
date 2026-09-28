---
ttl: task_bound
---

# EC3 灌水运行体检台账（st-ec3-water，2026-09-27 03:0x 实测）

> 宪章=同目录 00_orchestration.md。基线=docs/_working/fullflow_mining/m5_scheduling/05_master_health_table.md（09-25 拍摄）。
> 本台账=22 行全行重探+新增件发现+红行修复+关键表灌水实证。探活全只读；修复=任务重指向(register script)/配置两处（claim 留痕）。
> 当日历法：09-25(周五)=节假日 is_open=0，09-26/27 周末；**最后交易日=09-24(周四)**，下一交易日=09-28(周一)。

## 一、健康表 22 行逐行现态（2026-09-27 02:41~03:20 探测）

| # | 行 | 现态 | 证据（摘要） | 处置 |
|---|---|---|---|---|
| 1 | belt 传送带 | 绿 | `--status`: heartbeat_age_s=10, pid 33160 活, pool_workers=4 | 绿 |
| 2 | belt 自启任务 | 绿 | ZephyrAlpha_BeltDaemon Running/267009, LastRun 02:41:28（PT1M 节拍实证） | 绿 |
| 3 | ProcessReaper | 绿 | last_run=02:31:28, scanned=20 whitelist_hits=10 killed=1; 任务 PT10M 在射 | 绿 |
| 4 | DataScheduler guard+child | 绿 | heartbeat 02:41:29 新鲜（15s 写频）; guard 21540(powershell)+child 29748(python -m zephyr.data.scheduler) 双活 | 绿 |
| 5 | TickSubscriber guard+child | 绿 | heartbeat 02:41:29; 34836/32180 双活 | 绿 |
| 6 | CHHealthProbe guard+child | 绿 | heartbeat 02:41:29; 22328/8240 双活; logs/ch_health_probe.log 02:42:34 仍追加（CH HTTP+TCP 连通 172.24.30.100） | 绿 |
| 7 | DeadmanSwitch | 绿 | 任务 PT5M LastRun 02:40:28 result 0; 告警日志末条=09-26 20:45:31（scheduler 心跳 parse error 瞬态，自愈），此后 6h+ 零告警 | 绿（瞬态已录） |
| 8 | WorktreeDriftWatchdog | 绿 | pythonw pid 17376 活; watchdog.jsonl mtime 02:41、state.json 02:31 新鲜; 任务补射实例以 #99 单例锁 skip 退出=设计内 | 绿 |
| 9 | write_audit_daemon | 绿 | pid 27916 活（python -m ...write_audit_daemon） | 绿 |
| 10 | AI-Wrapper-Inject | 绿 | PT1M LastRun 02:41:01 result 0（基线 Running=恰逢在射，Ready=两射间隙，同健康） | 绿 |
| 11 | order_daemon（未接线） | 绿（按判据） | `grep -rn "OrderDaemon(" src/ --include="*.py" | grep -v test` = 零命中 → 判据"保持不存在"成立 | 绿 |
| 12 | BoardIndexRealtime | 绿 | 09-26 09:20 exit 0; CH board_index_tick max(ingest_ts)=09-24 15:00 CST（最后交易日收盘），周末无 feed=预期 | 绿 |
| 13 | SectorSnapshot | 绿 | 09-26 16:40 exit 0; sector_constituent_snapshot max(snapshot_date)=2026-09-26，总量 570,744 | 绿 |
| 14 | SimBridgeExecute | 绿（S3 已消） | LastResult 09-26 13:05=**0**; 日志 09-25/26 四班全 SKIP: non-trading day（交易日闸正常留痕），末次实跑 09-23 exit 0。09-24 的 4294770688 未复现 | 绿（S3 销案：自愈/环境性） |
| 15 | PostSettlement | 绿（S1 已修结案） | 09-25(节假日仍触发) 15:30 exit 0，日志注记空快照最小输入诚实声明; 注册脚本 HEAD=conhost+cmd 良态（a0446129e3 回植 8f0e5feba9）→ 重注册不复断 | 绿 |
| 16 | DataScheduler 槽位面 | 绿 | tmp/scheduler_run.log 持续滚动至 02:43（research_report 回填 2400/5569 在飞）; 05:30 catchup 在岗 | 绿（catchup 6 失败注记见 §三） |
| 17 | dloop_post / secbuild 两槽 | 黄 | 总闸文件均不存在=启用态; Alerter 无槽级 ERROR; **但 kline_sector_intraday 停在 09-22 15:00**（09-23/24 交易日缺供），根因=tdx provider 09-24 10:5x "所有服务器均无法获取K线数据"（alerter ERROR 在案） | 黄→断供登记（§三 D3） |
| 18 | tilib 夜回填 | 红→**本役修（重指向落地）** | 09-27 02:30 仍 exit 1；根因=任务 Execute 仍指 untracked 遗留 bat（.gitignore:604 scripts/data/*，且 bat 重定向指已被 tmp 卫生清掉的 .runtime\tmp\tilib-probe）。HEAD 早已备妥 tracked 接棒件 scripts/data/backfill_night.ps1（#399 分片 runner，fe40146a2b 第一批）但任务未重指。**本役动作**：新增 scripts/register_tilib_backfill_task.ps1（镜像原任务语义：daily 02:30/InteractiveToken/IgnoreNew/电池守卫默认）幂等重注册 → 任务 ACTION 现指 ps1，NextRun 09-28 02:30 保位，STATE=Ready | 修（register script 重指向；exit 0 终验=09-28 02:30 后看 LastTaskResult，移交晨检） |
| 19 | 资源族 5 件 | 绿 | SamplerScan Running/267009（PT10M 在岗）; RegenCheck=3=检出漂移语义内; Writeback 05:40/ViewPublish 05:50/MorningReport 06:31 均 0（09-26） | 绿 |
| 20 | 备份族 | 绿 | DailyBackup 09-26 06:00=0; WeeklyVMBackup 09-26 06:00=0（补射形态）; LibraryLedgerBackup 09-26 03:30=0; 两 drill 267011=从未跑，首跑 10-01 预期内; CH-Optimize 下次 09-27 03:30 | 绿 |
| 21 | news_slow（30 分节拍） | 绿 | cron 17,47 在射：19:17 槽 23:30 完成 2 成功 0 失败；23:47 槽在飞（research_report 大回填致槽时长小时级——非失败）；RSS 去重正常 | 绿 |
| 22 | OllamaServe / RSSHub | 红→半修 | RSSHub: pm2 online pid 18120 uptime 2D 绿。Ollama: 进程曾亡+port 11434 死 → 经在册任务 ZephyrAlpha_OllamaServe 拉起（Start-ScheduledTask，pid 31688，端口 LISTENING），**API 40s 无响应**（serve 挂起/模型层问题），禁 kill 不再动 | 半修→移交 Owner/ML 面 |

## 二、新增件/基线外发现（09-25 挖矿后新入册）

| 件 | 现态 | 证据 | 处置 |
|---|---|---|---|
| ZephyrAlpha_EvaporationBlackbox | **红（僵死占位）** | 新任务（09-25 02:26 注册，PT5M，EV-01 行车记录仪=15 号文 Owner 批件）。实例 cmd 16024+python 5056 自 **09-25 23:26:01** 起挂死，blackbox.jsonl 停更 27h+（mtime 09-25 23:26）；IgnoreNew 拒后续射（LastResult=0x800710E0）→ 黑匣子整段失明 | **纪律禁 kill 常驻→只记录**。处置建议（归属 LANE-EV/AI 层）：Stop-ScheduledTask 或结束 5056/16024 后 PT5M 自愈；建议补 register 脚本+fail-dead 检测（jsonl mtime 进 deadman 判据） |
| ZephyrAlpha_NightlySentiment | 变更观察 | 基线 09-25=Disabled（由 schedule.yaml 槽替代）→ 现 Ready 且 09-26 22:30 exit 0；与 scheduler nightly_sentiment 槽（cron 20 8）形成双源 | 不代裁：请 Owner/数据链确认保单源（任务 vs 槽），防双跑 |
| ZephyrAlpha_DecisionChainSentinel | 绿 | 新任务 09-26 09:40 result 0 | 绿（他会话施工件，不触碰） |
| QMTWatchdog 路径损坏 | **黄→本役修** | exit 1=SKIP exe not found；data/runtime/qmt_terminal_path.txt 自 09-15 起含 0x08 退格（`\bin`→`\b` 转义吞噬）。**已修**：字节级重写真路径，经看门狗同款读路径验证 Test-Path=True | 修（runtime 配置，不入 git）；09-28 08:45 起看门狗恢复 LAUNCH 能力（B1 半自动=Owner 批设计） |
| cron 周约定实证 | 观察项 | APScheduler 实测 0=Mon（'0-4' 下一射=周一）→ 全部 `0-4` 槽=周一~五正确，无周五漏洞；weekend_backfill '0'=周一 02:00、weekend_calibration '1'=周二 03:00（S17 本意周一） | 记录不动；weekend_calibration 语义偏移留数据链评估 |

## 三、灌水实证（CH 只读查证，2026-09-27 02:5x）

**结论：行情/新闻/模拟三大干线在灌水，最后交易日=09-24 全部到位；三表从未供水+两处断供已定位。**

| 表 | 时间列 | 最新值 | 判定 |
|---|---|---|---|
| c1_market.kline_daily | trade_date | 2026-09-24（10,108,049 行） | 绿=最后交易日 |
| c1_market.kline_1min | trade_date | 2026-09-24（14.8 亿行） | 绿 |
| c1_market.tick_data | trade_date | 2026-09-24（89.5 亿行） | 绿 |
| c1_market.tick_depth_5 | trade_date | 2026-09-24（1.03 亿行） | 绿 |
| c1_market.board_index_tick | ingest_ts | 09-24 15:00 CST（796,293 行） | 绿=盘尾 |
| c1_market.technical_indicator | trade_date | daily→09-24 / weekly→09-15 / monthly→09-15 | 绿/黄：W/M 停 09-15=夜回填长期 exit 1 后果，#18 修后 09-28 02:30 应推进 |
| c1_market.sector_constituent_snapshot | snapshot_date | 2026-09-26 | 绿 |
| c1_market.sector_fund_flow | trade_date | 2026-09-26 | 绿 |
| c1_market.kline_sector / _880 | trade_date | 2026-09-24 | 绿 |
| c1_market.kline_sector_intraday | trade_date | **2026-09-22 15:00** | **红：断供起点 09-23**，根因 tdx provider 全服务器取 K 线失败（09-24 alerter ERROR 在案）；TCP 取证 3/6 服务器现存可达→或自愈，09-28 盘中观察，归属数据链 |
| c1_market.kline_index / stock_daily_basic / daily_valuation / index_quote | trade_date | 2026-09-24 | 绿 |
| c1_market.crypto_kline_daily | trade_date | 2026-09-25 | 绿 |
| c1_market.alt_fx_rate_ecb | trade_date | 2026-09-25 | 绿 |
| c3_fundamental.news_data | publish_time | 09-27 当日 12 行（26 日 1,140 / 25 日 944…连续） | 绿=新闻干线在灌 |
| c3_fundamental.news_sentiment_score | scored_at | 2026-09-24 07:48 UTC（773 万行，publish_time 追打历史中） | 绿=打分器活，历史回填推进 |
| c3_fundamental.research_report | ingest_ts | 2026-09-18（14.7 万行）；02:43 起回填 2400/5569 在飞 | 黄：主灌 09-12 回填+零星，回填进行中 |
| c1_backtest.sim_trade_log / sim_daily_report / decision_daily | trade_date/ingest_ts | 09-27 / 09-27 02:19 CST / 09-28(T+1 计划) | 绿=模拟链在灌 |
| c1_market.suspend | trade_date | 2026-09-23（36 行） | 黄：09-24 零行或为当日无停牌，无法证伪，留观察 |
| **断供/空表** | — | c1_market.edb_data=0 行（FRED 族 integrator 每周期"0 行"→从未供水）；c1_market.etf_benchmark=0 行（catchup 日日补跑失败）；c1_market.account_nav_daily=0 行（57 号文 GAP 族，PostSettlement 日志注记在案） | **红×3：登记 Owner/数据链**（非本役代码级可修） |

catchup_guard 09-26 18:15 对账：overdue=20 补跑=15 失败=6 顺延=19 截断=5，空表=[suspend, etf_benchmark]（data/failures/20260926_catchup_guard_101516.json 仅汇总无明细）。

## 四、修复落地袋与移交项

**本役修复（2 处，均 claim 留痕）：**
1. `scripts/register_tilib_backfill_task.ps1`（新建，纯 ASCII，PSParser 0 错）——S2 终章：任务重指向 HEAD 既有 tracked runner scripts/data/backfill_night.ps1（#399 分片件，fe40146a2b 第一批的激活步）。重注册已实跑生效（ACTION/NextRun/STATE 三验证）。注：bat=untracked 遗留件（.gitignore scripts/data/*），其收编/删除按 fe40146a2b 预案仍属 Owner 门位，本役不碰；weekly/monthly 期差=数据链 #399 分批 rollout 范畴（现 ps1 仅 --periods daily），非任务层问题。register 脚本含 PS5.1 电池参数差异处置（无 DisallowStartIfOnBatteries 开关=默认即守卫，注脚留痕）。
2. `data/runtime/qmt_terminal_path.txt`（不入 git）——0x08 退格修复（09-15 起损坏，看门狗 SKIP exe-not-found 根因），字节级重写真路径并经看门狗同款读路径 Test-Path=True 终验；09-28 08:45 起恢复 LAUNCH 能力（B1 半自动=Owner 批设计）。

**移交项（不代裁）：**
- EvaporationBlackbox 僵尸实例（禁 kill）→ LANE-EV/AI 层，处置法见 §二。
- ollama serve 挂起（进程活 API 死）→ Owner/ML 面。
- NightlySentiment 双源（任务+槽）→ Owner 定单源。
- kline_sector_intraday 断供（tdx）→ 数据链车道，09-28 盘中复测。
- edb_data / etf_benchmark / account_nav_daily 三空表 → 数据链/Owner（§三）。
- weekend_calibration '1'=周二语义偏移 → 数据链评估。
- S3 SimBridge 09-24 异常码未复现=环境性销案；若再现，按 04 册取证路径（任务计划程序操作通道）。

## 五、冷启动合规自证

- RULE-ENV Python 3.12.8 ✓；RULE-GUARDIAN reaper 活（02:31 last_run）✓；改前 claim ×2（bat+qmt 路径）✓；
- capability_lookup.find('tilib indicator night backfill bat', st-ec3-water)=空集留审计 ✓；查库全只读（ch_reader SELECT）✓；未 kill 任何进程（ollama 经 Start-ScheduledTask 拉起）✓；他会话在飞件零触碰 ✓。

## 六、SW5 夜战复测段（2026-09-29 04:1x-04:3x，CH 复活后六项；sid=st-nightsweep-sw5-20260929）

> 背景：CH 172.24.30.100:9000 复活（Owner 确认全线打通）；本段对 §三/§四 移交项做活体复测。查库全只读（DatabaseService admin 连接，SELECT/DESCRIBE/count 口径），未 kill 任何进程，禁改域（akshare_provider/realtime_snapshot/etf_benchmark 换源=zc9-lane-d）零触碰。

| # | 项 | 本夜读数 | 判读 |
|---|---|---|---|
| ① | tilib 晨检（09-28 02:30 后效果） | `c1_market.stock_indicator` max(trade_date)=**2026-09-28**（11,689,777 行）；`c1_market.technical_indicator` max=**2026-09-28**（369,080,208 行） | **绿：09-28 02:30 夜批效果已落**（前账 S2 终章重注册后首个验证晨） |
| ② | ollama 挂起 | tasklist 无 ollama 进程（grep rc=1）；端口 11434 探测=False | **挂起演进：前账"进程活 API 死"→现"进程不存在+端口不通"**。禁杀禁拉起（让日班/Owner，99_skipped #4 在案）；nightly_sentiment_llm.enabled 旗仍开（09-23 起），LLM 不可达时走 llm_fallback 规则腿 |
| ③ | kline_sector_intraday | max(trade_date)=**2026-09-22 15:00**（10,436,356 行），较前账（09-27 读数同值）未涨 | **红维持：tdx 断供未恢复**（本夜 CH 活条件下复测仍 09-22；与 tasks/供应链图"本车道复跑未涨"一致）；恢复腿归数据链车道（tdx/mootdx 通道死亡，known_data_gaps :726 在案） |
| ④ | 空表三件复测 | `c1_market.edb_data`=0（前账"etb_data"系本表笔误，CH 无 etb_data 表）；`c1_market.etf_benchmark`=0；`c1_market.account_nav_daily`=0 | **三 0 维持**。处置：account_nav_daily→**新增 known_data_gaps 条目** `account_nav_daily_writer_zero_caller`（写器零调用方=从未接线，无既有腿可开，禁新建源）；edb_data→已有条目在案（iFind 配额退役，替代源 macro_data 活）；**etf_benchmark 不动**——换源域归 zc9-lane-d 在途施工（避让图），禁开腿禁代修 |
| ⑤ | NightlySentiment 单源 | 基座=规则法单源（data_source: rule/llm_fallback 留痕）；nightly_sentiment_batch 最近读数：09-26 SUCCESS 3813s（疑 LLM 挂试）→09-27 SUCCESS 289s（规则速）；**09-28 08:20 槽位无运行读数**（调度器本体两日 2902 条活跃至 04:21） | **黄**：单源语义确认（规则法兜底成立，ollama 挂不阻塞主腿）；但 09-28 缺跑一日=新观察→**新增 known_data_gaps 条目** `nightly_sentiment_batch_missed_20260928`（根因未定位，只登记不妄断；.disabled 总闸确认为开） |
| ⑥ | EvaporationBlackbox 运行态 | `.runtime/evaporation_blackbox/blackbox.jsonl` mtime=**09-29 04:21**（395,900B，追加中），末条 ts_local=2026-09-29T04:21:01+08:00 branch=dev | **绿：黑匣子活体快照在飞**（前账"僵尸实例禁 kill"观察维持——快照正常产出即保留，处置仍归 LANE-EV/日班） |

**本段产出**：known_data_gaps.yaml 追加 2 条（CAS 留痕，YAML 校验过）；无代码/任务/进程变更。
**结论**：CH 复活后六项=①绿 ②红(演进) ③红(维持) ④三0维持(1 登记/1 在案/1 让路) ⑤黄(1 登记) ⑥绿——供水面恢复主力干线（tilib/新闻/模拟链/黑匣子），板块分钟线与三空表缺口维持登记态。
