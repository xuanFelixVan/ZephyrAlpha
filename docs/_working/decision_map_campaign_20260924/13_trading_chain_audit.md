---
ttl: task_bound
title: 13 · 交易链八环节运转审计（排班/盘前/盘中/执行/风控/模拟盘/日循环/实盘门）
created: 2026-09-25
sid: st-audit-chain-20260924（决策地图战役交易链审计班）
lane: decision_map_campaign
status: final（只读挖掘+只读探针+本文件一个交付件；禁 commit；CREATE-GUARD 由总指挥统一登记）
doc_version: v1.0
related: 09_link_skeletons.md（骨架与缺口登记真源——本文与其重叠处一律引用不重复）
doc_type: audit_report
---

# 13 · 交易链八环节运转审计

> **一句话**：09 号文回答"骨架有什么、缺什么"；本文回答"装了的那些**通不通、自动不自动、
> 谁在值班、坏了谁知道**"。按 Owner 八环节切分逐环节给六项：现状组件+路径 / 已知缺陷与断链 /
> "全不全"（该有没有的）/ "通不通"（上下游接线实证）/ 自动吗 / 施工项（TRD-A 编号）。
> 证据=文档真源+代码头注+**只读探针**（`schtasks /query` 实测 2026-09-25 00:22 快照、
> data/runtime 文件存在性实查、模块 grep 消费方实查）。实盘相关结论一律保守：有疑点标**待实查**，
> 本文不断言任何"实盘安全"。

## §0 结论速览

| 环节 | 一句话 | 自动吗 | 最重的一根刺 |
|---|---|---|---|
| ①排班调度 | 24 数据槽全在+守护任务实测存活；但**决策链在排班表里只有 4 个正式槽位**，且周末校准槽 day-of-week 两处注释语义互相矛盾（疑似修错日，待实查） | 数据全自动/决策半自动 | weekend_calibration 疑似错日 |
| ②盘前 | 预案由 T-1 16:45 备好；**T 日 08:00-09:15 晨间重评窗只有一个生产编排件且零接线**（premarket_workflow），dloop 的 premarket 段不在 T 日晨跑 | 盘前段半自动 | 晨间窗无人上班 |
| ③盘中 | 盘中监控=60min bar 事件链五态行+心跳死探；**价格/仓位级告警 4 条已注册零消费代码**，盘中持仓风控环无 runner | 事件链自动/告警哑 | THD-TRD 有尺无人用 |
| ④信号→下单 | sim 实单腿 09-23 首次全通（10:42 成交@4.604）；但**信号→订单映射表 Owner 未批**（仅防御=空仓一行合法）、L4-14 成本反馈断链（09 D34）、桥客户端两缺陷未闭环 | 半自动（桥执行腿双触发） | 隔夜单静默丢弃 |
| ⑤风控 | 两套五级并存且各自半接电：TDM 熔断 L0-L4（盘前门快照消费）/ 交易五级熔断（逐单闸+落盘已建）；**落盘重臂 rebuild_from_disk 零调用方** | 熔断自动/重臂未接 | 重启=熔断失忆窗口 |
| ⑥模拟盘 | 09-23 起历史首次全自动闭环（45 钱包 58.06M fresh=1）；**G4"连续绿 N 日"无机械计数器**，检查器仍是设计稿 | 全自动（自 09-23） | 绿天数靠人眼 |
| ⑦日循环 | dloop 总扳手 16:45 自动圈+E2E 双圈实证绿（09 号文"编排器不存在/warroom 零调用"结论已被 09-21 后进展**部分刷新**）；计划 vs 实际核对全史仍未实装 | 盘后自动/盘中事件链 | 复盘核对占位 |
| ⑧实盘门 | 四禁+三道锁在位（实测配置与代码）；七红中 3 红已闭合（S-1/S-2 登记册/S-3 落盘）、**4 红未闭（P1/P2/M4/K1）**；O-2~O-9 与档案 O-1..O-7 编号漂移 | 锁自动/批文人工 | K1 密钥轮换未办 |

---

## 环节① 排班与调度

### 现状组件+路径
- **排班真源**：`src/zephyr/data/config/schedule.yaml`（24 槽位，cron=APScheduler 语义，头注明示
  executor 分池）+ `src/zephyr/data/config/tasks.yaml`（271 任务，槽位分布：daily_event 42 /
  weekend_calibration 40+4 注 / daily_capital 39 / daily_kline 29 / monthly_static 20 /
  intraday_minute 15 / intraday_realtime 12 / event_driven 10 / 其余个位数；4 任务 disabled）。
- **调度器本体**：`src/zephyr/data/scheduler.py`（单实例文件锁防双 guard 竞态 :90-93、CH 探活线程
  :885、卡死任务 reap :971、本地回灌 :1024、破损 part 隔离 :1068、监控 HTTP :2602）。
- **交易日守卫**：`src/zephyr/data/trading_calendar.py:151-163` TRADING_DAY_GUARDED_SCHEDULES
  九槽（intraday_realtime/intraday_minute/daily_kline/daily_capital/daily_event/nightly_financial/
  daily_backfill/integrity_check/auction_highfreq）。
- **守护任务族**（`scripts/register_guard_tasks.ps1:46-52,113`）：DataScheduler/TickSubscriber/
  CHHealthProbe/DeadmanSwitch/TradingWatchdog 五件；死探 `scripts/deadman_switch.ps1`（心跳超阈
  告警并给出重启命令行 :193-200）；进程收割 `ZephyrAlpha_ProcessReaper`
  （`scripts/register_process_reaper_task.ps1`，keep 清单 data/runtime/process_reaper_keep.txt）。
- **只读探针实测**（2026-09-25 00:22 `schtasks /query`）：DataScheduler/TickSubscriber/
  CHHealthProbe/ProcessReaper/BeltDaemon **正在运行**；DeadmanSwitch/QMTWatchdog(08:45)/
  PaperSession(**就绪**，next 09:25)/SimBridgeExecute(09:35+13:05)/PostSettlement(15:30)/
  BoardIndexRealtime(09:20)/IndexMinuteEOD(15:10)/SectorSnapshot(16:40) **就绪**；
  TradingWatchdog 与 NightlySentiment **已禁用**。RULE-GUARDIAN 前提满足。

### 已知缺陷与断链
1. **day-of-week 语义矛盾（疑似修错日，待实查）**：`schedule.yaml:121-128` weekend_calibration
   修复注记称"crontab 0=周日"故 0→1（=周一意图）；同文件 :136-139 weekend_backfill 注记却称
   "APScheduler 0=周一，非周日"。requirements.txt:42 锁 apscheduler>=3.10,<4.0——3.x 语义
   0=mon..6=sun，按此 **"1"=周二**，修复疑似把周一错挪成周二。09-20 周窗未 firing 的观察与
   0=mon 语义自洽，与"0=周日"的诊断注记矛盾。**禁凭记忆断言，待实测（观测下个触发日或查
   APScheduler JobStore）后修正**。此族曾致 daban 断供 5 日（同文件 :125-128 自述），属数据链上游真金白银级风险。
2. **决策链正式槽位稀缺**：schedule.yaml 里属于交易决策链的槽只有 4 个——dloop_post(16:45) /
   sector_close_final(15:10) / sector_pre_open(09:15) / eod_reconciliation(15:40)。其余 20 槽全为
   数据摄取。盘前计划生成、盘中监控评估、风控巡检均**无独立槽位**（盘中靠事件链补位，见环节③）。
3. **收班巡检任务状态矛盾**：08_watch_and_risks.md §二"f18d34c8（18:00 收班巡检自动化）
   completed/runCount=31 但 nextRunAt 指向当日"——不重建防双发、本班兜底亲跑，病灶未除。
4. **NightlySentiment 双通道疑云（待实查）**：schedule.yaml:178-181 nightly_sentiment 槽
   （08:20，DataScheduler 内）在产；独立 Windows 任务 ZephyrAlpha_NightlySentiment 实测
   **已禁用**——疑似旧通道退役残骸，须确认无职责真空。
5. TradingWatchdog 按 D3 裁定禁用（`scripts/start_trading.ps1` 头注：2026-08-22 实证当日无常驻
   交易生产进程，启用看门狗=生产行为变更，禁用保一键恢复）——**这是裁定不是故障**，但意味着
   "交易主进程守护"当前是空位，paper 会话靠 ZephyrAlpha_PaperSession（09:25 拉起）+keepalive。

### 全不全（该有没有的）
- 有"数据断供哨兵"（data_supply_sentinel 06:50/quality_sentinel/calendar_coverage_check 07:10/
  catchup_guard 05:30/integrity_check 23:00 五件套，schedule.yaml:215-241）——**没有"决策链断供
  哨兵"**：dloop_post 圈失败仅 ERROR 告警（schedule.yaml:249-253），无"连续 N 日未出 decision_daily
  行"级的巡检条目（alert_threshold_registry.yaml 42 条中无此类，v1.6.0 注）。
- 有 Slot 级 catchup（错档补跑）——**没有 Slot 级"该跑没跑"对 T 日 09:15 硬约束链的守门**
  （见下"09:15 链"）。对标 469 样板问法："排班表 24 槽 vs 骨架九环节需要的触发面"逐格对，
  决策链触发面格子大多写着"事件链"而不是槽位——事件链正门合法（宪法 §9.3），但**缺一张
  槽位×触发面×守卫者的对账表**，谁也不签收这个映射（本文即为首张，见 §1 附表）。

### 通不通
- 上游（Owner 日历/交易日历）→ DataScheduler：通（trading_calendar 守卫+catchup_guard 对账）。
- DataScheduler → 数据表：通（271 任务+五件哨兵实测在岗，07 号文 B 段 881xxx 缺口除外）。
- DataScheduler → 决策链：通但仅 16:45 一班（dloop_post→run_daily_loop(None)，
  scheduler.py:362-396 实码）；09:35/13:05 桥执行腿走**独立计划任务**不走 DataScheduler
  （delivery_report_20260923 §2"tasks.yaml 为数据摄取清单，sim 链硬塞=滥用"）。
- 全环节：调度器单点无灾备演练记录（仓内未见 DataScheduler 故障切换/双机预案——"仓内未见"如实注）。

### 自动吗
数据层全自动（含补跑/哨兵自愈）；决策链=盘后自动、盘前半自动、盘中事件自动+执行腿定时自动。
**值班纪律**：Owner 晨间 ritual（XtMiniQmt 登录）仍是 sim 链硬前置（sim_launch 台账 R2：
09-17/18 SKIP 因 ritual 未做；delivery_report_20260923 前提"Owner 已登录终端"）——**人对机器的
依赖未消除**。

### 附：09:15 硬约束链逐环实证（本环节专项）
| 时点 | 环节 | 证据 | 状态 |
|---|---|---|---|
| 08:20 | 夜间情绪窗闭合后 20min 起跑 | schedule.yaml:178-181 | 通 |
| 08:34 | 盘前元数据 pre_market（universe/涨跌停/停复牌/ST） | schedule.yaml:28-31 | 通 |
| 09:15 | sector_pre_open（T 日 close_final 复制+偏好重映射） | schedule.yaml:263-267 | 通 |
| 09:15-09:25 | auction_highfreq 每 10s 五档盘口 | schedule.yaml:183-192 | 通 |
| 09:15-09:25 | 集合竞价**不接单**（L-003，从 09:30 连续竞价放行） | src/zephyr/ex_core/pre_execution_checker.py:114-117 | 通 |
| 09:15 | 盘后复盘纪律截止线（POST_MARKET 次日 09:15） | src/zephyr/compliance/discipline_must_do_checker.py:88,221 | 通 |
| 09:15-09:30 | **隔夜单黑洞实证窗**：预市场落单 09:15 竞价+09:30 开盘柜台零收录 | docs/_working/sim_launch/delivery_report_20260923.md §4 缺口② | **断（未闭环，TRD-A10）** |
| 09:15-15:00 | GPU/LLM 交易时段保护窗（训练 0GB） | config/gguf_vram_budget.yaml:35-36 | 通 |
| 09:25 | PaperSession 拉起（就绪实测） | schtasks 探针+register_paper_session_task.ps1:88-89 | 通（禁用→已启用，谁启用的无登记，**待实查**） |

**施工项**：TRD-A01（槽位×触发面对账表+决策链哨兵）、TRD-A02（周末校准日核查）。

---

## 环节② 盘前流程（盘前计划/warroom）

### 现状组件+路径
- 决策侧盘前件（`src/zephyr/plan_engine/`）：daily_plan.py（MOD-PLAN-030 晨间预案，
  judgment_daily_plan 三场景树）、next_day_forecaster（MOD-PLAN-029）、llm_premarket_analysis
  （LSG 网关 infer("premarket_analysis")，daily_loop_master_switch.py:249-261）、
  premarket_workflow.py+premarket_workflow_engine.py（MOD-PLAN-021，08:00-09:15 三段式
  分钟级 DAG：数据就绪→分析→就绪确认，mandatory 失败→blocked+人工接管点，头注 :20-45）、
  premarket_constraint_loader、overnight_boundary_reviser。
- warroom：daily_warroom_pipeline.py（MOD-PLAN-018，production）盘前 compute_and_record +
  盘后 outcome 回写两段；判定台账标准=trading_vision/2026-09-16-judgment-ledger-standard.md。
- 数据侧盘前槽：pre_market 08:34（universe 元数据）、nightly_sentiment 08:20、sector_pre_open 09:15。

### 已知缺陷与断链
1. **MOD-PLAN-021 零接线**：premarket_workflow 的 CONSUMERS 自注"运行时装配批（conductor 执行
   DAG）"，全仓 grep 生产消费方仅 `plan_engine/__init__.py` 导出与 `trading/work_dag.py` 相邻件——
   **production 级编排件无人装配**。而 dloop 的 premarket 段（daily_loop_master_switch.py:338
   STAGE 序 data_readiness→regime_freshness→warroom→daily_plan→llm_premarket）**不走**
   MOD-PLAN-021——两套盘前编排并存一套在岗一套休眠，与"查重铁律④/复用禁平行实现"张力待治理。
2. **T 日晨间窗真空**：dloop_post 在 T-1 16:45 以 phase=full 跑（scheduler.py:375 run_daily_loop(None)
   默认 phase="full"，daily_loop_master_switch.py:372），预案于 T-1 盘后备妥；**T 日 08:00-09:15
   无任何自动重评/重申动作**（隔夜外盘、竞价快照不回灌预案；数据槽只供数不决策）。
   09:15-09:25 竞价原料（auction_highfreq 60 次快照）产出后，消费它的是情绪 auction 档
   （post_auction 09:30）而非盘前计划。
3. warroom 三任务中"盘中实时走势分析"无自动化主体（09 号文环节 9 引 addendum 三任务节——
   本文不重复登记，只指出：现役自动化只有盘后 outcome 回写+盘后备预案两段，**第三任务
   （盘中实时）没有触发面**）。

### 全不全
- 有晨间预案生成（T-1 备）——没有 T 日 09:00 前的**预案有效性复核**（regime 快照是 T-1 的；
  若 T 晨出现跳空级隔夜信息，无机制触发预案重估。owner_gate_list.md 丁线接电面同口径：
  姿态→订单映射只有防御一行合法，见环节④）。
- 有就绪确认工序定义（readiness_confirm mandatory 人工在环）——没有它的**运行实例**
  （模块未接线=确认点在现实里不存在，盘前"就绪"当前由 dloop 数据就绪门 fail-closed 兼任）。

### 通不通
数据槽→judgment_daily_plan：通（E2E 实证，daily_loop_campaign/e2e_manual_run_report.md §2
16:52 自动链 [DAILY-DECISION] 拍板 target=09-22 cap=60.00%）；预案→盘中归类：通（60min bar
事件链五态行，E2E §2a 四拍全过）；预案→订单：**仅防御行**（环节④）。MOD-PLAN-021→任何
conductor：**断（零装配）**。

### 自动吗
半自动：T-1 自动备预案，T 日晨人工/无动作；llm_premarket 走 LSG 但失败降级不阻断（dloop 头注）。

**施工项**：TRD-A04（MOD-PLAN-021 复用或退役裁定+晨间重评窗立项/显式豁免）、TRD-A05
（warroom 盘中第三任务触发面，引用 09 环节 9 缺口不重复）。

---

## 环节③ 盘中监控

### 现状组件+路径
- 事件链盘中面：pipeline_events.py:45-46 maybe_track_intraday_state 挂 60min bar 入库 SUCCESS
  自然唤醒（bar_key 查重幂等）+ scenario_classifier 盘中五态归类——E2E 实证四拍
  （10:35/11:35/14:05/15:05）全过（e2e_manual_run_report.md §2a）。
- 计划偏差监控：plan_deviation_monitor.py（production，2σ 判偏+计划外强信号三重闸，
  头注 INVARIANTS）——消费方=daily_decision_orchestrator（拍板时点用，**非盘中连续**）。
- 心跳死探：deadman_switch.ps1 live_strategy_biz 通道（盘中 09:30-15:00 心跳 stale>10min 告警，
  :140-180）+ tick_subscriber_biz 无数据告警（:110-125）。
- 执行腿窗口监控：SimBridgeExecute 09:35/13:05 wrapper 内 XtItClient 活性守卫+quote 新鲜度闸
  （delivery_report_20260923 §2-§3）。
- 仪表盘：src/zephyr/frontend/dashboard/components/position_monitor.py（人工面，只读构造点已改
  read_only，交付报告 §3）+ warroom.py 组件（**全通道 fail-open 自注**，live_admission_checklist M5）。

### 已知缺陷与断链
1. **THD-TRD-001..004 零消费**：alert_threshold_registry.yaml:20-22,961-1023 四条交易级告警
   （位置超限/日亏-3%/断路器断连/心跳丢失）v1.6.0 已登记但自注"status=design 代码未落"；
   grep src/ 零消费方实证——**尺子进了注册表，没有人拿尺子量**。盘中价格/仓位异常当前
   只能靠五级熔断（触发即重动作）与人工看盘。
2. **盘中持仓风控环缺位**：BM-RC-04 盘中持仓风控监控（VaR/回撤/暴露/流动性）在 battle_map 为
   production 域件，但无盘中 runner（仓内未见调度或事件挂接——如实注）；TDM 熔断 L0-L4 状态机
   的盘中评估挂 daily_gate_snapshot（盘前门快照，src/zephyr/strategy_pipeline/daily_gate_snapshot.py:29-47），
   盘中级别变化无自动播报。
3. warroom 组件 fail-open（M5）：监控自身失效不拦交易——语义已知情登记（A4"告警是尽力而为，
   保命靠熔断与人工巡检"），但**人工巡检无排班**（无 Owner 盘中巡检 SOP 时点表落档，仓内未见）。

### 全不全
- 有执行腿死桥守卫——没有**持仓级**盘中守卫（如"持仓市值越界"仅 sim 观察档有预警线
  CAND-5301/6a6e/9987 三条，日刊哨兵，交付报告 §7；真实现役钱包的盘中回撤/集中度告警=零）。
- 有 60min 五态归类——没有**分钟级异常**（急拉急砸/成交量异常）探针；对标骨架，这是
  09 环节 9"warroom 盘中实时走势分析"的缺口，引用不重复。

### 通不通
数据(60min bar)→五态行：通（事件链实证）；五态→执行腿：通（防御→卖出 510300 实单，09-23）；
熔断→逐单闸：通（trading_session.py:457-492 kill_switch_probe 自动反查接线）；阈值→告警：**断**
（THD-TRD 零消费）。

### 自动吗
事件链自动（五态/结算）；告警面半瞎（有熔断无阈值告警）；人工巡检无排班。

**施工项**：TRD-A06（THD-TRD 消费面落地）、TRD-A07（盘中持仓风控环 runner 或显式降级人工+排班）。

---

## 环节④ 信号→下单执行（在 09 号文环节 7 基础上深挖，重叠处只引用）

### 现状组件+路径
- sim 实单腿（09-23 首通）：sim_daily_runner bridge-execute——日计划姿态→env=sim 桥真单；
  仓位真源=柜台实持（read_only broker 直读）、限价=下单时点盘口（quote mtime>900s 拒单）、
  窗口闸 09:30-11:25/13:00-14:55、幂等=signal_batch+orders_sim.csv idem 预扫
  （delivery_report_20260923 §3，全参数路径在案）。首单：10:42 卖 510300 1100 股成交@4.604，
  台账 bridge_fill_check=1.0。
- 下单管线（production 件，09 号文 SKL5"下半段通电"判定引用）：OrderManager（cancel 传本地
  order_id 修，同报告 §4）、qmt_file_bridge_broker（read_only+sysid 回填修）、
  pre_execution_checker 四级闸（trading_session.py:63 A1 注+:318,360,472 注入）。
- 桥真源：docs/_working/2026-09-08-qmt-bridge-migration-ledger.md（结案判定=**未结案保留**，
  3 条未完成：大QMT 沙箱同等权限 Owner 验证 9/18 期限已过无闭环记录、下单/取价/桥监控三件
  勾选空、§8 待办族）。
- 执行模板：BT-P2-055 底仓+日内回转模板=**裁定不立项挂起**（#331 砍向，激活前置=窄考试立项；
  archive/2026-09/kimi_audit/adjudications/p7a_ac_family_rulings.md:148-149 亲验 backlog
  untested）——09 号文"模板缺"实为"有裁定地缺"。

### 已知缺陷与断链（本班新证，09 已登的 D34/LK-12 只引用）
1. **桥客户端缺陷两枚（sim 实弹复现，呈 Owner 未闭环）**：①隔夜单静默丢弃——预市场落单
   客户端重登后本地 #DONE+ack(SENT) 而柜台永不收录（delivery_report_20260923 §4 缺口②，
   09-18 c3 同型复现；治理建议=客户端应拒单并 #FAIL）；②submit→cancel<5s 竞态触发同 remark
   反复重提交，36 合同冻结 16,203.40（无害但暴露客户端无终态原子性；containment=终态原子改写）。
   **两枚都是"真金白银安全"级行为异常，且都在唯一实弹过的下单腿上**。
2. **信号→订单映射表未批**：plan_order_mapping_proposal.md（sim_launch/）逐行呈批
   （S1_attack 买入参数 P/R、S3_oscillation A/B、低迷/亢奋处置、SIM-PLAN-001 钱包），
   批复栏全空；现役合法动作仅"防御=空仓"。delivery_report_20260923 §3 称 _plan_decision
   参数（不追高 1.5%/30% 额度）系"Owner 09-22 委托裁定"——**委托裁定与提案文件的批准范围
   是否同一口径，仓内无对账记录（待实查）**。
3. **台账勾选滞后**：qmt-bridge-migration-ledger §1"下单链路 QmtFileBridgeBroker [ ]"未勾，
   而 09-23 已有柜台合同 4820 实单成交——同一仓库两文矛盾，按"文档矛盾=事故"条款登记勘误欠账。
4. PositionStatics.csv 13 天未更红旗（ledger §1 ⚠️，09-08 时点）后续无复核记录——**待实查**。

### 全不全（对标 469 问法）
- 有卖出腿实弹——没有**买入腿实弹记录**（桥 smoke 买腿为撤单型烟测，成交买腿仓内未见）。
- 有幂等预扫——没有**对账级**闭环：T6b 撤单终态不产 execution_report 行（交付报告 §6 移交③，
  producer 语义待勘）——撤了但账上看不见。
- 有窗口闸/盘口闸——没有**资金占用/购买力闸**（bridge-execute 依赖柜台仓位真源，但仓内未见
  购买力校验件；如实注，禁断言缺失即风险）。

### 通不通
信号（五态/姿态）→plan-execute/bridge-execute：通（sim 实证）；执行→回报→台账：通
（sysid 回填修后 1573/1800/4820 三合同验证）；执行→成本反馈→选型：**断**（09 D34 断链实证
引用+LK-12 逐笔 TCA 欠账引用——本文不重复，施工化见 TRD-A08）。

### 自动吗
执行腿定时自动（09:35/13:05）+事件链 observe 自动；但每笔合法动作的**语义空间**=Owner 批准
映射表的行数，当前 4 行里批了 1 行。

**施工项**：TRD-A08（L4-14 闭环施工）、TRD-A09（映射提案批复接线）、TRD-A10（桥客户端两缺陷治理）、
TRD-A11（BT-P2-055 保持挂起+激活前置登记，非施工）。

---

## 环节⑤ 风控（kill_switch/五级熔断/THD 卡）

### 现状组件+路径
- **系统级 KillSwitch**：src/zephyr/security/access_control/kill_switch.py（MOD-INF-018，
  production，宪法 §7 在册）；告警链消费其态（alert_webhook_dispatch.py:362、intake_events.py:131）。
- **交易五级熔断**：src/zephyr/trading/trading_contracts/risk/trading_kill_switch.py:60-113
  （POSITION_LIMIT/DAILY_LOSS(-3%AUM)/CIRCUIT_BREAKER/SECOND_LEVEL/API_TIMEOUT，带
  cooldown+auto_reenable）；**持久化已建**：kill_switch_state_store.py（MOD-INF-016 testing，
  data/runtime/trading_kill_switch_state.json 原子写+rebuild_from_disk 重臂设计）——**探针实测
  state 文件存在**（2026-09-23T02:43Z 全 false，机制已走过真实写路径）。
- **TDM 熔断 L0-L4**（日级：警戒 2%/禁开仓 4%/减仓 6%/保命 25%，迟滞解除）：MOD-RK-049
  drawdown_state_machine.py（src/zephyr/risk/core/）；消费方=daily_gate_snapshot（L5 门读态）+
  defensive_asset_whitelist + drawdown_session_persistence（grep 实证三件）。
- **THD 卡**：THD-DRAWDOWN-001/002/003（0.05 预警等，alert_threshold_registry.yaml:64-102，
  TDM X-R1 threshold_refs 挂接 config/trading_decision_map.yaml:3177,3212）+THD-TRD-001..004
  （环节③已述零消费）。
- **crisis_gate**：config/crisis_gate.yaml enabled=true、warning_theta=0.5（O1/O-5 待 Owner 校准）；
  告警失败不阻断、crisis_gate_log 0 行（sim 台账 §1，无 crisis 日，正常）。
- **纸面/实盘物理锁**：paper_hedge real_channel_locked=true（config/paper_hedge.yaml:42），
  演练计数 0 次（live_admission_checklist R7）。
- 逐单闸接线：pre_execution_checker 闸门 1 熔断探针+闸门 1.5 live 档阻断
  （pre_execution_checker.py:176-206,259-274），trading_session 注入（:318,360,472）。

### 已知缺陷与断链
1. **rebuild_from_disk 零调用方**：grep 全仓仅 store/主件自引——state_store 头注自认消费面
   "交易会话启动侧 rebuild_from_disk（G2b/G5 sim 部署接线点）"=**接线点未到**。现状语义：
   交易进程重启后 DAILY_LOSS"当日不再恢复"靠落盘文件在，但**无人读它重臂**——重启即失忆窗口
   实存（store 建成把风险从"状态蒸发"降为"状态休眠"，非零）。
2. **两套五级无互认**：交易五级（执行秒级）与 TDM L0-L4（组合日级）各自独立状态机，阈值口径
   不一致（-3% AUM vs 日亏 6% 减仓），仓内未见映射/升级关系定义——**同日双触发时的仲裁序
   未立法**（如实注，待 Owner 裁定，禁臆断）。
3. R1-03 护盘白名单 proposed、BM-RC-10 风险否决权 design——09 号文 LK-14 已登，引用不重复。
4. kill_switch 触发复位=Owner 专属（qmt_e2e_runbook.md 禁区段"kill_switch 触发属 Owner 复位项"）；
   trading_kill_switch.reset(level) 代码面无权限闸（任何调用方可 reset）——**代码无门位、纪律靠
   约定**（如实注；系统级 KillSwitch 的权限面未在本班实测范围，待实查）。

### 全不全
- 有熔断动作定义——没有**熔断演练台账**（G5 要求 sim 完成 HALT 拒单演练，进度 0；
  live_admission_checklist R7 演练 0 次）。
- 有回撤阈值卡——没有熔断级别流转全史物化表（09 环节 8⑥ 已如实注，引用）。

### 通不通
熔断→逐单拒单：通（探针自动反查+闸门 1 fail-closed，R2 黄项"未实弹"仍真——演练 0）；
触发→落盘：通（state 文件实测）；落盘→重启重臂：**断（零调用方）**；触发→告警：通（系统级
A3 绿）；THD-TRD→任何监控：断（环节③）。

### 自动吗
触发/落盘/逐单拦截自动；重臂断；解除人工（Owner）。

**施工项**：TRD-A12（rebuild_from_disk 会话启动接线+演练）、TRD-A13（双五级仲裁序裁定呈 Owner）、
TRD-A14（crisis θ 校准 O-5，Owner 门位）。

---

## 环节⑥ 模拟盘（sim 平台/成绩台账/准入条件）

### 现状组件+路径
- 平台四件（sim_launch/00_campaign_ledger.md §1 验活）：sim_trade_log（23→**51 行终态**：48
  e4_replay+1 platform+2 plan_bridge，未结算 0/unresolvable 1=09-19 疤行）、sim_pocket_daily、
  sim_platform_journal（**45 钱包 58,063,421.64，fresh=1 degraded=0 首次全绿**，交付报告 §7）、
  strategy_screen（51 个 oos_tested candidate）；另有 sim_deviation_report 43 行、
  sim_attribution/sim_governance/sim_promotion_memo、crisis_gate_log。
- 自动化三腿：事件链 sim_observe_daily 挂 daily_kline SUCCESS（FIFO=账本→观察面→日刊→归因，
  pipeline_events.py:142 SIM_DAILY_KINDS+交付报告 §7 修正）；桥执行腿计划任务 09:35/13:05
  （实测就绪）；结算链 15:30 尾挂日刊（交付报告 §6④）。**09-23 起零人工闭环实证**。
- 卫兵：FIX-2 注册表 SSOT 卫兵（幽灵钱包拒开，08:43 自然实验 PASS）；NaN 价格卫兵；观察档
  市值越界预警（110 万线，三条在案）。
- 准入条件：live_readiness/admission_gate_design.md G1-G12 门清单+O-1..O-7 等 Owner 项+
  A-1/B-1..B-3/X-1 等产物项；07 号文 D 栏"实盘准入 live O-2~O-9（等模拟盘绿天数）"。

### 已知缺陷与断链
1. **G4 绿天数无机械计数器**：门判据"连续 N 日全 ok+零 error+验证环日更"（admission_gate_design
   §1 G4），仓内**未见计数器/checker 实装**（check_live_readiness.py 全文只有设计稿 §3，
   "本班不建"；sim 日刊 fresh/degraded 字段在但无跨日连绿判定件）——绿天数靠人翻台账。
2. **E4 重放 2 例数据面缺口**（68cc 基本面列缺失/93aa 成分股窗口缺失，交付报告 §1）——重放
   覆盖 46/48，缺口未修。
3. 09-22 断链事故链（四步无调度挂接+活写手回退）已治本（事件链挂接+classify_workspace_wip
   判 stale_rollback），但**说明 sim 链对"会话间暗手"零防护的历史前科**——卫兵面当前只防
   幽灵钱包/NaN，不防调度挂接被回退（待实查：无回归哨兵）。
4. **09-24 日报缺位（待实查）**：sim_launch/ 目录止于 delivery_report_20260923；09-24 日报应已由
   observe-chain 自动渲染，仓内未见——或未提交（禁 commit 纪律下在飞）或断链复发，待次日核。

### 全不全
- 有日刊/月偏离/归因——没有**准入门仪表**（G2b 纸面≥30 笔、G4 连绿 N 日、G5 演练次数三个
  计数器全部不存在，live_readiness 三项等产物没有生产者）。
- 有 strategy_screen 成绩——没有"sim 留校生"晋升面（sim_promotion_memo 件在，触发规则
  仓内未见；如实注）。

### 通不通
kline 落地→observe-chain→台账→日刊：通（09-23 实证）；plan→bridge→柜台→结算：通
（bridge_fill_check=1.0）；台账→准入门：**断（无计数器）**。

### 自动吗
全自动（09-23 起）；前置=Owner 晨间终端 ritual+密钥/终端等四类 Owner 事（B-3）。

**施工项**：TRD-A15（三计数器+check_live_readiness.py 落地）、TRD-A16（E4 两例数据缺口修复+
调度挂接回归哨兵）。

---

## 环节⑦ 日循环闭环（dloop/日刊/复盘）

### 现状组件+路径
- 总扳手：src/zephyr/plan_engine/daily_loop_master_switch.py（MOD-PLAN-033，testing）——
  数据就绪门(fail-closed)→regime 新鲜度→warroom→预案→次日概率→pf_alloc→盘中 L1→盘中
  归类→收盘验证→三表结算→日度拍板（MOD-BT-214，#305 安全态零下单）；dloop_post 16:45
  自动圈（总闸 data/runtime/daily_loop_master.disabled **实测不存在**=总闸开）。
- 事件链九棒：pipeline_events 挂 daily_kline SUCCESS 唤醒（E2E 实录 16:52 自动 9 棒）。
- decision_daily：拍板体落快照行（E2E §2b [DAILY-DECISION] target=09-22 state=expansion@1.00
  cap=60.00% no_trade=0 degraded=1(D2:L2)）。
- 收盘链：sector_close_final 15:10→eod_reconciliation 15:40（recon_runner.run_daily_reconciliation
  三账核对，schedule.yaml:202-213）→PostSettlement 15:30（run_post_settlement.py 尾挂 sim 日刊）。
- 判定台账三表结算：judgment_settler（E2E 实录 intraday scan=4 settled=4）。

### 已知缺陷与断链
1. **09 号文环节 9 两结论已被进展刷新（须在 09 文基础上勘读）**：①"日度编排器本体不存在"
   ——完整蓝图版（BT-P1-031 S1-S7）确实未建，但**等价功能体**（9 棒事件链+总扳手 16 段）
   09-21 起 E2E 双圈实证绿；②"warroom pipeline 仓库内零调用方"——现已挂 dloop premarket/
   postmarket 两段。本文按现状判：**盘后闭环通，蓝图版编排器与现役双轨的合并决策未做**
   （两套触发面并存：事件链自动+dloop 16:45 补漏，幂等靠底层闸，无冲实——但双轨无对账声明）。
2. 计划 vs 实际核对全史：postmarket_reconcile 仅签名占位（09 环节 9⑥ 引用）——**复盘的
   "核对"一环仍占位**，日刊（sim 平台日刊）≠决策复盘（decision_plan 验证）两本账未合流。
3. 六段↔五态映射未落（09 LK-16 引用）——盘中五态行与六段编排接口对不上的病根仍在。
4. decision_daily 历史=浅（v1 安全态刚建，09 引用）——门快照 L2 板块门恒 absent v1
  （live_admission_checklist M3：无持久化日度状态，依赖 L2 门的包当日禁用）。

### 全不全
- 有拍板快照——没有**快照的逐日审计报表**（谁在哪天为什么 no_trade/degraded，无消费端报表；
  decision_daily 行在库里躺着，Owner 面=warroom 组件 fail-open 人工看）。
- 有日循环——没有**周/月循环**（sim_deviation 月度件在但 deviation kind 曾"消而不产"
  pipeline_events.py:28-45 自述教训；决策链周复盘件仓内未见）。

### 通不通
数据→拍板：通（E2E 双圈）；拍板→次日预案：通（warroom 盘前段 target=次交易日）；拍板→执行：
通但**仅经 Owner 批准映射行**（环节④）；执行→结算→归因→（C3 退役/调权）：**半断**
（归因日账 attribution_daily 已挂 FIFO 末位，但 C3-02/C3-03 消费在 09 号文环节 6/9 判"未接线"
——引用不重复）。

### 自动吗
盘后全自动；盘中事件自动；复盘核对占位=人工。

**施工项**：TRD-A17（postmarket_reconcile 实装+双本账合流）、TRD-A18（六段↔五态映射，引用 09
LK-16）、TRD-A19（decision_daily 审计报表消费端）。

---

## 环节⑧ 实盘四禁与权限门

### 现状组件+路径
- **四禁正典**：QMT_REAL_*/enable_real/ZEPHYR_ENV=live/LiveSimulationSwitcher.switch_to_live
  全禁（docs/_working/automation/campaign/qmt_e2e_runbook.md:28-30，live_admission_checklist
  C1 沿用）；双终端辨识 TCP 配对法（config/qmt_environments.yaml disambiguation 节）。
- **锁三道**：①live 档 blocks_live_trading=true+代码断言（qmt_environments.yaml:62+
  pre_execution_checker.py:259-274 fail-closed 拒全部新单——S-1 已施工，live_readiness C2 红已闭）；
  ②switcher 一次性令牌 fail-closed（live_simulation_switcher.py:8,26-30）；③enable_real=False
  默认（qmt_file_bridge_integration.py:54,66）。live account=''未填（qmt_environments.yaml:54）。
- **权限门**：risk_tier_registry.yaml:55-92 high 域 9 个（含 D_TRADING/D_EX_CORE/D_RISK）+
  §5 四类 Owner 门位；B-007 五档阶梯 shadow→paper→pilot→daily_review→auto 换档唯一人工
  （system_charter.md:106）；promote_ready≠决定（promotion_combo_gate.py:15）。
- **零下单安全态**：GRADUATED_PACKAGES=frozenset()（daily_decision_orchestrator.py:122，
  裁定 #305；E2E 实证 enabled_packages=∅ 不产执行单）。

### 已知缺陷与断链（七红刷新——本文核心增量之一）
live_readiness 七红（09-22）→ 本班 09-25 实查刷新：
| 红项 | 09-22 判 | 09-25 实查 | 证据 |
|---|---|---|---|
| C2 blocks_live_trading 零消费 | 红 | **已闭（接线在）** | pre_execution_checker.py:61-94,259-274 |
| A1 交易级告警无专条 | 红 | **半闭**：登记册 4 条已入（v1.6.0），消费代码零（status=design 自注） | alert_threshold_registry.yaml:20-22 |
| R3 熔断态无持久化 | 红 | **半闭**：store+state 文件实测在，rebuild 零调用=休眠 | kill_switch_state_store.py+探针 |
| P1 仓位参数未 confirmed | 红 | 未闭（Owner 门位 O-2） | admission_gate_design §2 |
| P2 金字塔规则未接电 | 红 | 未闭（包导出无消费方，09-22 探针口径未见反证） | live_admission_checklist P2 |
| M4 交易心跳缺位 | 红 | **半闭**：deadman live_strategy_biz 通道+执行腿活性守卫在（paper/桥面）；常驻交易进程本无（D3），M4 语义随架构收窄 | deadman_switch.ps1:140-180 |
| K1 密钥轮换未办 | 红 | 未闭（**准入门第一依赖**，等 Owner） | tc10_owner_report.md:16 |
- **编号漂移**：07 号文 D 栏"live O-2~O-9"vs 准入档案 O-1..O-7——O-8/O-9 无档案定义。
  按"文档矛盾=事故"条款登记勘误（TRD-A22），禁按记忆猜测两编号所指。
- **待实查（保守声明）**：①ZephyrAlpha_PaperSession 从注册 DISABLED 转为实测就绪，启用动作
  无登记记录（Owner 窗口启用属合法，但无痕）；②大QMT 沙箱同等权限验证 9/18 期限已过无闭环
  记录；③PositionStatics.csv 红旗无复核。三项均不影响"当前无实盘连接"判断（live account 空+
  三道锁在），**但任何一项都足以否决挂实盘旗——本文不给出"实盘就绪度"结论，只给门位清单**。

### 全不全
- 有代码锁——没有**锁的定期测试**（三道锁无一在演练台账里有触发记录；G5 演练 0）。
- 有外部合规白项（C7/G12 程序化报备/券商条件/税负）——仓库内零载体，等 Owner 书面确认。

### 通不通
四禁→AI 操作面：通（runbook+宪法 §9.11 指令/数据边界双保险）；live 配置→逐单闸：通
（S-1 接线）；阶梯→签发记录：**断（无 pilot 签发载体，G11 空白属正常——前置未到）**。

### 自动吗
锁自动；升档/解锁/复位全人工（Owner）。

**施工项**：TRD-A20（K1 催办+核对，Owner）、TRD-A21（P1/P2 闭环，Owner+施工）、TRD-A22
（O 编号勘误+PaperSession 启用痕登记）。

---

## §9 施工项汇总表（TRD-A01 起）

| # | 施工项 | 环节 | 类型 | 前置/门位 |
|---|---|---|---|---|
| TRD-A01 | 槽位×触发面×守卫者对账表（决策链哨兵条目：连续 N 日无 decision_daily 行即告警） | ① | 登记+小施工 | 走注册表流程 |
| TRD-A02 | weekend_calibration/weekend_backfill day-of-week 实测核查与修正（APScheduler 0=mon 矛盾） | ① | 核查+一行修 | 待实查后动 |
| TRD-A03 | 收班巡检任务 f18d34c8 状态矛盾治理+NightlySentiment 双通道确认 | ① | 核查 | 低优 |
| TRD-A04 | MOD-PLAN-021 复用或退役裁定（与 dloop premarket 段双实现治理）+T 日晨间重评窗立项/显式豁免 | ② | 裁定+施工 | Owner 一句话 |
| TRD-A05 | warroom 第三任务（盘中实时走势分析）触发面（引用 09 环节 9 缺口） | ②③ | 施工 | 排 GPU 后 |
| TRD-A06 | THD-TRD-001..004 消费面落地（4 条告警接进交易运行时监控） | ③ | 施工 | G2b/G5 sim 接线点 |
| TRD-A07 | 盘中持仓风控环 runner 或显式降级人工+Owner 巡检排班 | ③ | 裁定+施工 | Owner |
| TRD-A08 | L4-14 执行成本反馈闭环（09 D34 施工化）+逐笔 TCA 台账（LK-12） | ④ | 施工 | 实盘前必修 |
| TRD-A09 | plan→订单映射提案批复接线（S1/S3/低迷/亢奋行+SIM-PLAN-001） | ④ | Owner 批+小施工 | Owner 逐行 |
| TRD-A10 | 桥客户端两缺陷治理（隔夜单拒单化+submit→cancel 竞态）+台账勾选滞后勘误 | ④ | 客户端侧施工 | 呈 Owner 已在办 |
| TRD-A11 | BT-P2-055 保持挂起，激活前置=窄考试立项（登记非施工） | ④ | 登记 | — |
| TRD-A12 | rebuild_from_disk 接入交易会话启动+首次 HALT 拒单演练入台账 | ⑤ | 小施工+演练 | G5 闭环 |
| TRD-A13 | 交易五级 vs TDM L0-L4 仲裁序立法（同日双触发谁说了算） | ⑤ | 裁定 | Owner |
| TRD-A14 | crisis θ 校准（O-5，月度演练回看误报率） | ⑤ | Owner 门位 | Owner |
| TRD-A15 | 准入三计数器（纸面笔数/连绿天数/演练次数）+check_live_readiness.py 实装 | ⑥ | 施工 | 设计稿在 |
| TRD-A16 | E4 重放两例数据缺口修复+sim 调度挂接回归哨兵 | ⑥ | 施工 | 数据面 |
| TRD-A17 | postmarket_reconcile 实装+决策复盘与平台日刊双账合流 | ⑦ | 施工 | 引用 09 环节 9 |
| TRD-A18 | 六段↔五态映射落地（09 LK-16 施工化） | ⑦ | 施工 | 引用 09 |
| TRD-A19 | decision_daily 审计报表消费端（Owner 晨报面） | ⑦ | 施工 | 低优 |
| TRD-A20 | K1 密钥轮换+叫核对（准入第一依赖） | ⑧ | Owner 门位 | **Owner** |
| TRD-A21 | P1 仓位参数 confirmed+P2 金字塔接电 | ⑧ | Owner+施工 | Owner |
| TRD-A22 | O-8/O-9 编号勘误+PaperSession 启用痕/沙箱权限验证/PositionStatics 三项待实查销号 | ⑧ | 登记+核查 | 快 |

## §10 优先级（按"影响真金白银安全"排序，前 5）

1. **TRD-A10**（桥客户端两缺陷）——唯一在实弹下单腿上复现的资金行为异常；隔夜单静默丢弃
   在实盘语境=自以为成交的裸奔。
2. **TRD-A12**（熔断重臂接线+首次演练）——重启失忆窗口使 DAILY_LOSS"当日不再恢复"语义失守；
   演练 0 意味着所有拒单闸未经过一次实弹证明。
3. **TRD-A02**（周末校准疑似错日）——同族事故已付过 daban 断供 5 日学费；数据断链是
   上游一切环节的地基。
4. **TRD-A20+TRD-A21**（密钥轮换+仓位参数 confirmed）——准入门两道 Owner 闸，非 Owner
   动作不能推进，但应持续催办挂账。
5. **TRD-A06+TRD-A15**（告警消费面+准入三计数器）——把"有尺没人量/有账没人数"的两处
   哑面接上声与数；这是 G4/G8 两门从黄转绿的机械前提。

## §11 挖掘执行日志

| 批 | 矿脉 | 证据源 | 判定 |
|---|---|---|---|
| C1 | 战役 09/07/08 号文全读+README 交付清单 | decision_map_campaign_20260924/ | signal（09 环节 7/8/9 结论引用不重复） |
| C2 | 排班真源+任务分布实测 | src/zephyr/data/config/schedule.yaml（24 槽全文）/tasks.yaml（271 任务计数） | signal |
| C3 | 调度/守护/死探代码 | scheduler.py、trading_calendar.py:151-163、register_guard_tasks.ps1、deadman_switch.ps1、register_process_reaper_task.ps1、start_trading.ps1 | signal（D3 禁用裁定在案） |
| C4 | 只读探针：schtasks 全量查询（2026-09-25 00:22）+data/runtime 三总闸与熔断 state 文件存在性 | 系统查询+文件实查 | signal（本文唯一非仓库证据源，已注时点） |
| C5 | sim 链台账族 | sim_launch/00_campaign_ledger.md、delivery_report_20260923.md、plan_order_mapping_proposal.md | signal（R1-R5 病灶+09-22 断链+09-23 闭环全录） |
| C6 | 实盘准入四件套+七红刷新 | live_readiness/ 四件逐面对照代码实查 | signal（3 红闭/2 红半闭/2 红未闭） |
| C7 | QMT 桥台账+执行件 | 2026-09-08-qmt-bridge-migration-ledger.md、trading_session.py、pre_execution_checker.py、trading_kill_switch.py、kill_switch_state_store.py、qmt_environments.yaml | signal |
| C8 | 日循环 E2E+决策件头注 | daily_loop_campaign/e2e_manual_run_report.md、daily_loop_master_switch.py、daily_warroom_pipeline.py、premarket_workflow.py、pipeline_events.py | signal |
| C9 | 告警/风控注册面 | alert_threshold_registry.yaml（THD-DRAWDOWN/THD-TRD）、crisis_gate.yaml、drawdown_state_machine 消费方 grep | signal |

**三扫收敛声明**：八环节×六项每格均有路径证据或"仓内未见"明示；与 09 号文重叠的缺口登记
（D34/D36/LK 系列/BT-P1-031）全部引用不重复，本文只做施工项化与运转状态判定。
**保守声明**：本文所有"通"的判定仅限 sim/纸面语境与数据链实测；**实盘语境下本文不断言任何
环节"安全"**——待实查三处（§环节⑧）销号前，准入门保持全红 baseline。
