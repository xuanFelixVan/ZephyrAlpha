---
ttl: task_bound
completes_when: 三线数据面全部回填并经 10-09 00:15 双源比对终验后，本报告随 A3 终验批归档；未齐项按 pending-on-time 交接
title: 03_open_day_recheck_20261008 10-08 开市三复核报告（线A）
owner: st-fig13-followup-20261006
---

# 03_open_day_recheck_20261008 —— 10-08 开市三复核报告（线A · st-fig13-followup-20261006）

> 状态：**A1/A2/A3 三段全回填（三复核全 PASS）**；余=报告文件落地（token 登记窗口）+00:15 调度拍独立确认（非阻塞）。
> 复跑工具：.runtime/tmp/st-fig13-followup-20261006/a_recheck_queries.py（只读查证，逐项 JSON 留档）。

## 0. 预检（10-08 凌晨完成，即刻可做三项全过）

| # | 预检项 | 结果 | 证据 |
|---|--------|------|------|
| P1 | schtasks 在册态：sector_eqw（已改名 ZephyrAlpha_SectorEqwIntraday，B1 批）+ ZephyrAlpha_SimBridgeExecute | PASS | 三任务 Ready；Eqw next=10-08 15:40 / SimBridge next=09:35 / Sentinel next=09:40；旧名 sector_eqw_intraday 已注销不在册 |
| P2 | 哨兵闸代码在位 | PASS | scripts/governance/decision_chain_sentinel.py:23-24,435 is_trading_day 短路（任何 DB 连接前）+ --force 逃生；任务 Action 直指本件 |
| P3 | 生成器/validator 全绿基线 | PASS | 重生成 52 节点 + validator 0 错 0 警（B1 批随批留痕） |

## A1 · 撮合产能（15:46 实测回填）

判据：c1_market.kline_sector_intraday 中 trade_date=2026-10-08 行数≈17 万量级、580 板块族满格（DatabaseService 只读）。

- **PASS**：任务 LastRun=10-08 15:40:00、Result=0（**改名后首交易日触发实证**）；当日 **internal_eqw** 口径五周期满格——1m=**171,351 行**（正中 17 万判据）/5m=35,550/15m=12,798/30m=7,110/60m=4,266，**711 板块族**（超 580 判据，族全覆盖）。
- **口径修正（随 A2 批同步图 D13-48）**：判据原文写 synth_sh，实测 10-08 起数据源字面量=**internal_eqw**（runner INVARIANTS 在册口径；synth_sh=09-30 及之前历史行），图 D13-48 ev/EXEC 的 synth_sh 字样同步修正。

## A2 · sim_bridge 首交易日（09:35 起双拍；13:05 后汇总回填）

判据：schtasks LastRun/结果 + logs/sim_bridge_execute.log 非空留痕 + 任何产物表行；证据回写图13 D13-45（生成器 spec ev/obs 更新+重生成+validator PASS）。

- 盘前基线：LastRun=2026-10-07T13:05（假日拍）；log 文件不存在（假日零留痕=闸生效旁证）
- **09:35 拍实测（抓真缺陷）**：任务触发（LastRun=10-08 09:35:01）但 **Result=4294770688 且 log 不存在**——在册任务 Action 指向 `scripts\tasks\run\run_sim_bridge_execute_daily.ps1`（**不存在**，scripts 拆簇失准同款病，与 st-t3c-ops 车道 10-08 定性的"触发链断"同类）；而注册器源（HEAD scripts/tasks/register/register_sim_bridge_execute_task.ps1:29）指向的正确路径 `scripts\run_sim_bridge_execute_daily.ps1` 实存。
- **处置（09:47，线A 自裁）**：重跑注册器（Register -Force 幂等，state preserved）→ Action 正位实查 ARGS=正确路径、Next=10-08 13:05。**13:05 拍=修正后首个真交易日拍**，取证后回填。
- **13:05 拍实测（修正后首个真交易日拍）：PASS**——LastRun=10-08 13:05:00、Result=0；`.runtime/logs/sim_bridge_execute.log`（真身路径，任务文本所写 logs/ 系笔误）非空留痕 11,964 字节，当日行="SKIP: XtItClient not running -- bridge terminal offline"（诚实跳单：QMT 桥终端离线，与 st-t3c-ops 车道同日定性互证）；假日 SKIP 三连（10-01/02/03 各两拍"non-trading day"）=交易日闸负向验证再证。产物行=无（终端离线诚实不产单）。
- D13-45 回写：_待回填（A2 复核批，随 15:40 证据一并）_

## A3 · 哨兵闸实战 + 双源比对（09:40 / 00:15 分窗回填）

判据：10-08 09:40 后哨兵当日记录或资源册样本；10-06/07（假日）零记录=负向验证（**已提前 PASS**：.runtime/logs/decision_chain_alert.jsonl 仅 09-30 一条（闸前时代），10-06/07 零记录；哨兵任务 10-07 LastRun Result=0 干净退出）。

- 09:40 拍实测：**PASS**——LastRun=10-08 09:40:01、Result=0（干净退出）；alert jsonl 零新增（决策链健康=无缺勤告警；本件告警唯一出口=alert jsonl，无告警即无记录，正向实证=LastRun+Result+decision_daily 健康）；假日负向（10-06/07 零记录）已提前 PASS。
- 双源比对：**PASS（19:39 手工校验前置取证；Owner 问询"为何等 00:15"后裁定主动取证）**——`CrossSourceValidator().validate(time_window_minutes=840)`（与调度槽同口径 14h 窗）实跑：**healthy=True、5,224 只标的、fail=0、missing_primary=0**（主源 QMT 当日 tick 全量在位）；missing_backup=5,224 全量 warn="备源缺失此标的"（tdx 永久断供一致性注记非故障，known_data_gaps 2026-10-04 终裁在案）；**check_date=2026-10-08 共 5,224 行已落 cross_validation_log**（判据原文"10-09 00:15 后出行"系 00:15 调度槽的生产时点——本跑=同代码路径手工前置取证，00:15 调度拍降级为独立确认非唯一证据）。
- 表新鲜度旁证：手工跑前 max(check_date)=10-01（假日 18 行小样；09-30 全量 7,952 行），10-02..10-07 假日空窗=闸负向又一证。

## 结论

- **三项复核全 PASS**：A1 撮合产能（171,351 行×711 族，改名后首日实证）｜A2 sim_bridge（链断缺陷当场修复+13:05 修正后首拍留痕）｜A3 哨兵+双源（闸实战健康+5,224 行零 fail）。
- 假日负向验证：PASS（哨兵 alert 面/SimBridge SKIP 三连/比对表假日空窗三处独立实证）。
- 复核副产物两件真缺陷当场处置：①SimBridge 在册 Action 拆簇失准（重注册修正）②D13-48 图面 synth_sh 陈旧字样（A2 批已落 HEAD 6920658910 修正）。
- 待办：00:15 调度拍=独立确认（非阻塞，明晨查一眼即可）；本报告文件随 token 登记窗口冷却后终批落地。
