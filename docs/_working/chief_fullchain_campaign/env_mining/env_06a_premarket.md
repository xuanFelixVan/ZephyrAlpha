---
ttl: task_bound
completes_when: 战役收尾（99_final_delivery 落账）后随役归档 archive/2026-10
---

# [BLUEPRINT] | docs/_working/chief_fullchain_20261006/env_mining/env_06a_premarket.md |
<!-- [MODULE]  -->
<!-- [STABILITY] evolving -->
<!-- [SAFETY] L -->

# ENV-06a 盘前段（05:30–09:30）挖矿作业簿（B1 批次，2026-10-06）

## §0 环节档案

- **真源锚**：FIG13 车道 `docs/_working/map_build/fig13_daycycle/`（00_skeleton.md §2 段 A + 簿01/02/03 + 13_consumers_scan_d13.csv）；机生图本体 `config/trading_day_cycle_map.yaml`（segments.A，generator=`scripts/governance/d5_architecture/generators/generate_trading_day_cycle_map.py`）。
- **现役挖掘 = st-fig13-bone-20261004**（簿件 frontmatter owner 记名 st-mapbuild-20260924 各车道 W-G/W-H/W-I，本簿按任务书口径以其为现役，不裁内部归属）。本簿对其领地只读，不重复挖矿；价值=①挂接收编 ②补代码消费面/字段面 ③本役三态裁定。
- **职责一句话**：一个交易日 05:30–09:30，补跑（catchup）→断供判新鲜（sentinel/coverage）→全球日历缝合（crypto/情绪窗）→撮合前提刷数（L0.5 五子源）→终端保活（QMT 看门狗）→就绪裁定（就绪门，名义）→竞价采集与模拟盘拉起。
- **节点与状态（图本体 2026-10-06 机生读数，13 节点）**：✅5（D13-04/07/08/11/12）｜🔨6（D13-01/02*/03*/05*/06/10；* 为 fig13 簿01/02 已实测升级 ✅、图本体 skeleton_status 镜像滞后）｜⬜2（D13-09 无主死结论、D13-G01 无产出证据态缺位）。任务书口径"✅5🔨7⬜1"与本读数差 1（🔨/⬜ 归属漂移），以机生图为准。

## §1 六向台账

| 向 | 内部反查发现（带路径） | 外部 | 判定 |
|---|---|---|---|
| 上（谁触发） | D13-01/02/03 三槽=APScheduler 特殊分支（`src/zephyr/data/scheduler.py:231/238/255`）；D13-04 双正门（槽 `nightly_sentiment` 08:20 + schtasks `ZephyrAlpha_NightlySentiment` 22:30 跑昨日窗，簿02 §1）；D13-07/12=机制 B（schtasks 08:45+12:55 / 09:25 `--if-trading-day`）；D13-08=调度器启动挂接非排班（`scheduler.py:2355-2362`，"日频"实为重启频率，09-12/09-19 缺档实证）；D13-09=零触发者 | fig13 触发机制三分（骨架 §2.1）为轴真源 | signal |
| 下（谁消费） | **本簿补充·代码消费面**：①撮合约束读 `stk_limit` PIT 行+`st_stock_list` 最近快照（`src/zephyr/ex_core/matching_engine.py:8` INVARIANTS 点名，禁第四份口径 #ARCH-DATA-020）→D13-06 三腿滞后=今日撮合价约束退化前缀推断；②`c1_market.suspend` **全仓零读数方**（簿02 §3 grep 实测）→断链直接后果=零，真实代价=名实不符；③failures/ 文件被仪表盘 datasrc 页消费（`src/zephyr/frontend/dashboard/api_server.py`+`web/features/datasrc/ds-page.js`），厂商外推通道 09-15 裁撤→没人开页=没收到 | 板块偏好重映射（丁线 owner_gate C1 乙档）吃 pre_open 复制产物 | signal |
| 内（子环节） | D13-06 五子源正名：limit_up_pool 属 daily_capital 槽非本槽（簿02 O-5' 纠偏骨架），真五源=stock_basic/stk_limit/suspend/index_constituent/st_stock_list，槽实挂 9 任务（O-8）；D13-09 三判据逐腿点名：C1=watchdog+paper-session 双替身（进程名分裂 XtItClient vs XtMiniQmt）、C2=人读 CLI 且"最近 SUCCESS"口径已被 stk_limit 假绿证伪、C3=自动探针无裁定——合成器零（簿03 §2 死结论） | 57 号归档 SOP（`docs/_archive/57_daily_cycle_sop.md:35-48`）为 C1/C2/C3 唯一真源 | signal |
| 旁（撞车面） | 三路兜底分工（catchup 档期/backfill 行数/integrity 只告警）真源= schedule.yaml 散文注释 L143-167，fig13 簿01 §1 已变三条边；哨兵 58 条目不覆盖 L0.5 五子源任何一表（簿01 O-4，两层哨兵共同盲区）；calendar_gate（开不开市）与 ready_gate（开不开得起）双字段禁合并（簿03 O-16） | 排班三表（resource_profile_registry/schedule_overview/schedule_consistency_reconciler）管争抢不管日序——硬让渡成立 | signal |
| 史 | D13-05"上线后从未自动跑成"已过期（幽灵池 09-16 治本，08:41:00 整×4 日三段时刻特征证据，簿02 §2）；57 号 SOP 已归档且"并入 55 号监控体系"承诺未兑现——现役接线无图可查即本图存在理由 | 普查 27 槽→实测 29→**2026-10-06 本簿复测 34 unique 槽**（见 §4 轮3，口径漂移登记） | signal |
| 新 | fig13 溢出 O-1~O-16 共 16 条已登记（catchup 分支无告警、重启风暴腰斩、告警冷却折叠 11 红 1 痕、哨兵盲区、SUCCESS 假绿面、suspend 双调度点每日 0 行 SUCCESS、QMTWatchdog 无 register ps1、双正门未成文、分钟漂移等）；**本簿补**：`emotion_index_pre_open` 08:34 FAILED（`cannot import name 'STAGE_AUCTION'`）与 D13-13 post_auction 同根（引用侧先行/常量未落），盘前-盘中接缝一处两症 | 无 | signal |

## §2 挖干自评

- **三扫收敛**：不适用本簿——三扫义务在 fig13 车道（骨架 §4 B6 路③外部对标已由 10_外部对标三扫.md 承接）。本簿为挂接+补面批，两向（代码消费面/字段面）补齐后增量趋零。
- **长尾**：D13-09 就绪门合成器是本段唯一"结构空位"（非断供），其 ready_gate 三源定义已被簿03 钉死待施工；stk_limit 水位化判据（期望键 vs 实际键比对件）为其施工前置（O-14）。
- **🌑 清点**：QMT 自动登录（券商客户端无此能力，Owner 裁定常开）、断网断电演练 RUN-05（物理操作须 Owner）——两项均骨架 §6 在册，本簿不消不加。

## §3 挖后自审闸三态裁定

**挂起排期**。
- 理由：①本段全部 13 节点已由 fig13 车道三簿挖透（六向齐+16 条溢出登记），本役再挖=重复劳动；②本役补的代码消费面/字段面两向无新增红条目（suspend 零读数方、哨兵盲区均为已登记项的再确认）；③D13-01 完成链断裂、D13-06 五子源假绿、D13-09 无主三项缺口的施工方案均已随 fig13 车道成文，等施工令而非等挖矿。
- 解锁条件：fig13 封矿（骨架 §6 判据①三扫路③跑完+作业簿 01-10 交付无新 D13 编号溢出）→ 图本体进施工批 → 本役 six 向台账并入施工输入；届时 D13-09 就绪门合成器为盘前段第一施工件。

## §4 挖矿日志

| 轮 | 矿脉 | 判定 | 产出 |
|---|---|---|---|
| 1 | 读 00_skeleton.md §0-§2 段 A + 簿01/02/03 全文 | 挂接完成：三簿判态与骨架状态分布差异（D13-02/03/05 升 ✅）收编入 §0 | §0 档案段 |
| 2 | 机生图 `config/trading_day_cycle_map.yaml` segments.A 解析（13 节点/skeleton_status/mining_recheck/availability） | signal：任务书"🔨7⬜1"与图本体"🔨6⬜2"漂移 1，以图为准 | §0 状态行 |
| 3 | 代码消费面 grep：matching_engine/suspend 读数方/api_server datasrc；schedule.yaml 结构复查 | signal：suspend 全仓零读数方（再确认）；**schedule.yaml 已从 29 槽漂移至 34 unique 槽且 8 槽键物理三写**（eod_reconciliation/sector_pre_open/sector_close_final/dloop_post/data_supply_sentinel/daily_alt_fx/calendar_coverage_check/auction_highfreq，598 行，PyYAML 后写生效、三写内容一致故行为无差，疑 09-23/24 合并残留）——结构性脏，登记交总包，本簿不修（热文件 CAS 纪律） | §1 史/新 向、env_15 复用 |
| 4 | 三态裁定自审 | 挂起排期成立：无本役独有可施工项 | §3 |
