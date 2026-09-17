---
ttl: task_bound
completes_when: 九环节全部封矿+施工收口+循环检查连续两次 0 问题+红蓝通过+终局交付，或 Owner 叫停
title: 交易决策链总包战役——骨架挖矿总谱（环节全景封矿）/波次派发/状态回写
owner: ZephyrAlpha-Owner
session: st-tdchain-20260917
date: 2026-09-18
---

# 交易决策链总包战役 · 骨架挖矿总谱

> **总令**：Owner 通宵交接令 2026-09-18（做T v2+检测器重校准+WYF-3+G07 核查+准入判据+合并收口+E2E 模拟单）。**挖矿纪律**：先把环节挖清楚（本文档），每个环节一个子文件夹作业簿（六向台账：目标/证据/块/依赖/三态/下一步），挖干判据=六向台账填实+自审三态；"线内先挖后干、线间并行流水"，谁挖干谁先开工。
> **持久规则**：每完成一个有意义步骤即回写本文档 §6（防上下文压缩失忆）。

## 1. 三轴战役对账（防遗漏声明）

本仓库同一夜有三条战役轴并行，环节互不重叠：

| 战役轴 | 会话 | 环节轴 | 真源 |
|---|---|---|---|
| 自动化产线轴 | st-autolnk-20260917 | 8+1 工段（L1 上架/L2 转正/L3 胃/L4 体检/L5 标准库/L6 红线/车道G/事件轨） | docs/_working/automation/campaign/CAMPAIGN_LEDGER.md + mining/00_总环节谱.md |
| 残余挂账轴 | st-residual-20260917 | 6 施工环节+2 战役阶段（WO-1~WO-5 危机接线/归因/核对器/人群账本/演练/对冲/告警） | docs/_working/residual_construction/00_master_ledger.md |
| **交易决策链轴（本谱）** | st-tdchain-20260917 | **9 环节 E0-E8**（本文档 §2） | docs/_working/trading_vision/* + factory/t_v2/* + 本谱各作业簿 |

**交叉约束**：residual 战役 C1 裁定=pipeline_events.py / tasks.yaml / apply_market_tables_ddl.py 三共享文件归其总统筹独占——本轴 E1/E0 全程规避直改，涉及时登记挂单。

## 2. 环节清单（已封矿，共 9 环节）

| 环节 | 内容 | 作业簿 | 交接令任务映射 | 波次 | 状态 |
|---|---|---|---|---|---|
| E0 | 合并队列收口：regcal→p2b(拆函数)→orchp3→sowner001→sowner002 cherrypick×4→depgraph | e0_merge_closure/ | 任务 0 | W1 | 执行中 |
| E1 | 做T 数据面基建：ETF 分钟族时区修复+板块高周期合成+缺口登记 | e1_tdata_infra/ | 任务 1（数据半边） | W1 | 执行中 |
| E2 | 做T v2 复活口径封存：#304 砍现形态+窄考试 RED+复活条件 | e2_tv2_revival/ | 任务 1（考试半边） | W1 | 挖干 |
| E3 | regime r4/r10 重校准合并+复核（方向语义退役） | e3_regime_recal/ | 任务 2 | W1 | 挖干待合并 |
| E4 | WYF-3 封矿核实：#264→#271→#285 证伪加厚链 | e4_wyf3_closeout/ | 任务 3 | W1 | 挖干（前班已完成） |
| E5 | G07×state_label 关联核查（只读） | e5_g07_linkage/ | 任务 4 | W1 | 执行中 |
| E6 | 模拟盘准入判据：E6 双尺重考取证+STD-SIM-ACCESS-002 转正 | e6_sim_admission/ | 任务 5 | W2 | 执行中 |
| E7 | QMT 模拟盘 100 股端到端烟测+证据归档 | e7_qmt_e2e/ | 通宵令 E2E 明令 | W2 | 阻塞待终端 |
| E8 | 红蓝对抗+循环检查×2（连续两次 0 问题） | e8_redblue_loop/ | 通宵令第五条 | W3 | 待 W1/W2 |
| Q1 | 裁定批量原子登记+台账回写+临时文件清零+终局报告 | 本文档 §6 | 通宵令第六、七条 | 末 | 待 E8 |

**环节清单封矿声明**：交接令五任务+E2E+红蓝收尾，经对账（§1 三轴+裁定 #304-#326 新口径）归并为上述 9 环节，骨架拆分到"真源或口径变化"为止，不再新增环节；新发现一律记各作业簿"长尾"。

## 3. 接班时关键情报（防重挖，2026-09-18 03:0x-04:0x 侦察）

- **裁定已至 #326**：新裁定从 #327 起。owner_fast_sign 一页读全场：docs/_working/kimi_audit/owner_fast_sign_20260917.md。
- **做T v2 已被 #304 砍现形态**；窄考试已跑=RED（共振 +0.88bp vs 对照 +0.87bp，p=0.4997，净 -7.5bp）；复活=单假设预注册卡（毛边际>12bp+DSR>0.5）或真实 001 考试产物。
- **交接令过时点勘误**：①股票 15/30/60min 表已全量在库（2021-09-01→2026-09-16，5849 只，9798万/4886万/2449万行）——"15min 表不存在"已失效；②WYF-3 前班已终态（#285 维持置零）；③regime r4/r10 重校准已执行（session/st-regcal-20260917 分支待合并）；④组合门打分器已建成（promotion_combo_gate.py，40ca90eb88）。
- **数据面真实缺口**（CH 实测）：ETF 分钟族五表 trade_date<=2026-06-30 UTC 误标（kline_etf_15min 误标 23,168,185 行未修，修复脚本 scripts/data/repair_etf_minute_tz_split.py 在盘未入库）；kline_sector_intraday 09-11/14/15 仅 1m 合成行；kline_1min/15min 止于 09-16（09-17/18 缺，miniQMT 白班关停）；120min 全库空白（豁免：tasks.yaml:2027 先例"60min 两根聚合"，查询期聚合即可）；kline_index_intraday 不存在（intraday_l1_tracker.py:406 已登记 510300 代理）。
- **QMT E2E**：runbook=docs/_working/automation/campaign/qmt_e2e_runbook.md；协议=scripts/tests/smoke_test_qmt_broker.py（600000.SH 100 股跌停价限价买→撤单，零成交零风险）；09-15 有全通过先例；今夜尚无人下过单（防重复下单）；执行前置=XtMiniQmt.exe 进程在线（侦察时仅 XtItClient.exe 在线，Owner 白班会亲自开）。
- **在飞会话**：st-crisis-gate-20260918 / st-flashbiz-20260918 / st-altdatamap-20260918 / st-sopfix-20260918 等今晚活跃；主区有大量他会话未提交件与 staged 内容——本轴所有提交走队列正门（--enqueue）防连坐。

## 4. 波次计划（线间并行流水）

- **W1**：E0 合并链（主线串行 git 手术）+ E1/E5 代理执行 + E2/E4 封矿落档。
- **W2**：E6 转正+判据终稿 → E7 QMT 烟测（终端就绪即插队执行）→ E3 合并后复核。
- **W3**：E8 红蓝+循环检查×2 → Q1 裁定批量+台账回写+清理+终局报告。

## 5. 提交账本（回写用）

（待填）

## 6. 状态回写

| 环节 | 状态 | commit/证据 | 备注 |
|---|---|---|---|
| E0 | ⬜ | | |
| E1 | ⬜ | | |
| E2 | ⬜ | | |
| E3 | ⬜ | | |
| E4 | ⬜ | | |
| E5 | ⬜ | | |
| E6 | ⬜ | | |
| E7 | ⬜ | | |
| E8 | ⬜ | | |
| Q1 | ⬜ | | |
