---
ttl: task_bound
created: 2026-10-08
sid: st-mx07-W4
title: 离场族其余12节点prereg卡草稿（勘察收口版，宁缺毋假）
campaign: matrix-20261007
lane: W4
status: draft
---

# exit_family_12nodes_prereg_draft_v1 — 离场族其余 12 节点 prereg 卡草稿

- 车道: st-mx07-W4 | 2026-10-08 | 性质: **勘察后③路径产物（零跑数/零代码/判据候选只转录仓内权威）**
- 任务卡: W4 离场族 12 节点（E 道模板 prereg→双臂→重标定→进册；fire_grid 五门前置 fail-closed）
- 走③不走②的裁定留痕: 规格卡 12+1 张全在册且详实（勘察②过），但 ①schema 新维（X_tp/X_ladder 等）卡面原文"裁定前置"未裁定；②12 节点冻结 prereg 考卡不存在（t3b 通道已收官关闭，"新维度新判据须 Owner 批"=99_delivery §七在册原文）；③**T3b 终判 FAIL（2026-10-07 21:55，a46c937df1）晚于 backlog P2-1（2026-10-07 06:19，b2f22ae86e）**，E 道"有增益"与 T3b"死路钉死"构成未决证据冲突，12 节点考哪个窗/什么判据无人可自造；④fire_grid G1/G2（GPU 空闲/预算）不可承诺。缺一即不可跑数——宁缺毋假。

## 一、勘察结论（证据锚点）

1. **12 节点清单真源**: `docs/_working/matrix_campaign/mining/m2_exit_sector/00_exit_sector_index.md:17-35`
   （X 族 13 节点=S3/M7/L3）− M-1 核心 **X-S1-02**（已由 T3b 落地，见下）= **本车道 12 节点**。
   backlog 源= `master_backlog_v2.md:39`（P2-1"离场族其余 12 节点：复制 E 道通道"）。
2. **M-1 核心已落地核验**: `scripts/backtest/factory_grid_executor.py:822-880`（`_apply_exit_overlay`，
   X_stop=[off,atr3x,trail20] 序钉 J帽→stop→breaker）+ schema 维 phase>=3 门控（commit 5cdda376364，
   Owner T3b 批令兑现）+ T3b 已考毕终判 FAIL（`config/search_space_prereg_t3b.yaml` 冻结卡；
   判决书 t3b_verdict_20261007.md/.json）。**"落地即激活 X 族 13 节点"的前提半数已兑现**。
3. **E 道模板三件**: `scripts/backtest/fexam/exit_sim/prereg_frozen.yaml`（冻结参结构：frozen_at_utc
   先于一切仿真/装置/判据/重标定义务四段）+ `scripts/backtest/fexam/exit_sim/exit_simulator.py`
   （双臂同装置 on/off 配对）+ `docs/_working/fexam/exit_sim_report_v1.md`/.yaml（进册形态：
   判定/OOS 两臂指标/重标定实测/prereg 冻结时刻全录）。
4. **fire_grid 五门真源**: `scripts/backtest/fexam/grid_adapter/fire_grid.py:321-333`
   （G1_gpu_idle/G2_budget/G3_reaper_keep/G4_ignition_flags——G4 仅 `--fire --i-understand-ignition`
   双旗标后进 dict）+ `:303-316`（factor_surface≠v1 通道门=blocked_channel，禁静默降级）。
   **fail-closed=任一门 False 即 blocked（`:329-333`），禁放行**。dry-run 预演=
   `python scripts/backtest/fexam/grid_adapter/fire_grid.py`（逐行门检快照不占 GPU）；
   钉死断言=`tests/backtest/fexam/test_fire_grid_gates.py`。
5. **证据冲突原文**: E 道=`docs/_working/fexam/exit_sim_report_v1.md`（ATR 止损对照 **有增益**：
   OOS MaxDD 改善+16.5pp，判据=MaxDD 改善≥5pp 且 Sharpe 差≥-0.2，OOS 窗 2025-10-09..2026-09-30）
   vs T3b=`docs/_working/fullcirc_closeout_chief/99_delivery.md` §七（stop/breaker **FAIL**：CRISIS 窗
   2020-02/03 配对，0% 过 5pp 线，active 腿 cost-adj Sharpe 均值-0.14，"离场族死路钉死"）。
   两考卷装置/窗/判据均不同——**冲突=考点未定，非任一方造假**。

## 二、12 节点逐卡 prereg 草稿面

> 机制/计算式/数据列=转录自各规格卡（真源指针逐行给出，本草不复制全文只留锚）；
> "schema 维提案"全部标**裁定前置**；"判据候选"只引 E 道 verdict_gain 语义或 t3b exit_gain
> 语义两条在册门柱，**取哪条/改常数=Owner 批后才能冻结**。

### M 级 6 节点（模块补写；路径依赖行循环激活→T3b-T0 强制重标定 per_point_seconds，fail-closed）

| node_id | 机制（卡锚） | 数据列 | schema 维提案（裁定前置） | 判据候选（在册转录） |
|---|---|---|---|---|
| TDM-X-S1-03 止盈族 | spec_x_TDM-X-S1-03.md §1-2：移动止盈 Chandelier 2×ATR22 只升不降/峰值回撤 30% 兑现/目标位（"次日不板走"封板掩码）；与 X-S1-02 共享同一行循环 | close/high/low+stk_limit | `X_tp=[off, chandelier_trail, peak_giveback30, target_px, composite]`（卡 §4 原文） | E 道 verdict_gain 语义（同装置双臂 OOS MaxDD/Sharpe 配对） |
| TDM-X-S1-01 六桶分类 | spec_x_TDM-X-S1-01.md §1-2：8 源聚合去重按 TDM 六桶词表（risk/signal/target/trailing/time/volatility）出桶标签矩阵；纯布尔零行循环 | 依赖 S1-02/03/04 桶信号 | 不新增维（标签矩阵列随离场维出现） | t3b exit_gain 配对语义（桶开关 on/off） |
| TDM-X-S1-04 破位退潮 | spec_x_TDM-X-S1-04.md §1-2：突破失败（20 日新高跌回+量缩+连 3 次失败）M 级；退潮=J_regime_switch 代理（T6 ①已接线）；龙虎榜不可考=负结果#4 | close/amount | 桶信号并入六桶矩阵（本卡无独立维） | 同上 |
| TDM-X-S1-05 融合紧迫度 | spec_x_TDM-X-S1-05.md §1-2：权重表 0.9/0.7/0.5/0.5+共振 0.2（TDM 冻结口径禁改）→urgency 三档；close_confirm 去抖三参；唯一可独立单测的 X 族决策件 | close（周线 resample PIT shift） | 融合为桶信号的静态函数（无独立考维） | urgency 档作双臂开关配对 |
| TDM-X-S2-01 执行方式路由 | spec_x_TDM-X-S2-01.md §1：一次性 vs 分批（3 日×1/3）+参与率帽 10%（INV-UNIT-001）+市值/均额>1% 禁市价；5 分钟间隔等不可考=负结果#2 | volume/amount | 卖出路径切分维度（提案，卡未定名，裁定前置） | t3b 配对语义 |
| TDM-X-S2-05 分批止盈 | spec_x_TDM-X-S2-05.md §1-2：Exit Ladder +1R 减 50% 保本/+2R 减 25%/尾仓跟踪；1R=entry×0.07 固定档（卡内钉定）或随 X_stop ATR 档 | close+entry/stop 状态数组 | `X_ladder=[off, ladder_1r, all_at_once]`（卡 §4） | E 道 verdict_gain 语义 |

### S 级 3 节点（参数/导出接线，复用在册引擎旋钮）

| node_id | 现状与剩余动作（卡锚） | 前置 |
|---|---|---|
| TDM-X-FLOW 离场导出 | spec_x_TDM-X-FLOW.md §4：evaluate_recipe 返回处可选列 `exit_actions_json`（缺省不写=逐位零漂移，T6 同款纪律）；纯导出零算法，内容依赖 X-S1 族 M 级变换落地 | M 级先行 |
| TDM-X-R1-03 护盘白名单 | spec_x_TDM-X-R1-03.md §4：executor T6 ④已登记 `defensive_whitelist_assets()`（MOD-POS-026 真源）；**剩余=Owner 资金门位**（state_matrix euphoria/distribution 格内容禁 AI 自填）+t3 prereg defensive_leg=true 格点族 | Owner 门位 |
| TDM-X-S2-03 执行时段路由 | spec_x_TDM-X-S2-03.md §4：exec_caliber=close/next_open/vwap 已 T6 ②接线（`_c4_engine.py:603-639`）；剩余=考卷维进 t3 家族 prereg 抽样集+A/B=next_open vs close 净 Sharpe 差 | 新开考通道=Owner 批 |

### L 级 3 节点（只登记，禁夜战——沿用 00_exit_sector_index.md 分级）

- TDM-X-S1（组骨架）/TDM-X-S2（组骨架）：组节点无独立机制，随子节点聚合。
- TDM-X-S2-04 本地条件单：tick 级语义不可考（99_negative_results #3），维持只登记。

## 三、流转面（照 E 道 template，四步硬序）

1. **prereg 冻结**：Owner 批考点/判据后，按 `exit_sim/prereg_frozen.yaml` 四段结构（frozen_at_utc
   先于一切仿真/device/judge_frozen/recalibration_duty）落卡；先冻卷后开考。
2. **双臂**：同装置同信号同成本 on/off 配对（E 道纪律：判据只看配对对照，官方引擎跑仅 sanity）。
3. **重标定**：M 级路径依赖格点 warm 1 次实测 3 次取均值→per_run_seconds→grid_unit 外推；
   **禁沿用 0.53s/格旧口径**（E 道已废止；T3b 实测 5.08s/点、E 道 0.428s/次为新参考值域）。
4. **进册**：verdict 三态（有增益/无增益/负增益）如实落 report md+yaml（形态照 exit_sim_report_v1）；
   负结果同样入册。

## 四、fire_grid 五门前置 fail-closed 检查单（开考机械前置，任一不过即 blocked）

| 门 | 判据（file:line） | 当前状态 |
|---|---|---|
| G1_gpu_idle | fire_grid.py:318,322（gpu_probe） | 未验（开考前必查） |
| G2_budget | fire_grid.py:224-246,323（campaign 帽+wall clock） | 12 节点批预算未立项 |
| G3_reaper_keep | fire_grid.py:248-258,324（白名单登记） | 长批须先登 process_reaper_keep.txt |
| G4_ignition_flags | fire_grid.py:326-327（--fire+--i-understand-ignition 双旗标） | 未点火（正确态） |
| 通道门 | fire_grid.py:303-316（factor_surface≠v1=blocked_channel） | v1 面不受影响 |

## 五、缺失面清单（→dispatch_blockers.md 同步登记）

1. **B1 schema 新维裁定**: X_tp/X_ladder/卖出路径切分维——各卡"裁定前置"原文在册，未经 Owner 批不得实现进考。
2. **B2 冻结 prereg 考卡**: t3b 通道已收官关闭（99_delivery §七）；12 节点新考卡（窗/判据/预算）须 Owner 批后冻结（先冻卷后开考）。
3. **B3 考点/判据冲突裁定**: E 道有增益 vs T3b FAIL——12 节点考哪个窗（OOS 2025-10.. vs CRISIS 2020-02/03）、用哪条门柱（MaxDD≥5pp+Sharpe≥-0.2 vs exit_gain 5pp 配对），本草无权代裁。
4. **B4 GPU 预算+T0 重标定窗**: M 级 6 节点行循环口径须实测重标定后才能定 T1/T2 点数（fail-closed）；预算随 B2 卡一并批。
5. **B5 X-R1-03 Owner 资金门位**: 防御格内容+defensive_leg 启用=Owner 专属（禁 AI 自填，卡 §4 原文）。
6. **B6 注册表热冲突（施工面披露）**: 本草 creation_token（matrix-w4-exit-family-12nodes-prereg-draft-20261008）已入工作区在册（CREATE-GUARD 磁盘读取口径，先例=L5 a7f7c2b6f43 "token 落册随其批"）；capability 册 gateway claim 在 st-mx07-W2 手中且该册夜战多班竞写（死快照回卷险情 chief 已登记），**token 落 git 随 W2 批或后续 token 袋，本车道不抢写**。

## 六、诚实位

- 本草零跑数/零代码/零新判据；全部判据候选转录自 exit_sim_report_v1.md、99_delivery §七、各规格卡并逐处给锚。
- 12 节点的 E 道式逐节点双臂开考，在 B1-B5 关闭前**机械不可达**（fire_grid fail-closed+判据冻结纪律），本草不预支任何 verdict。
- X-S1-02 不在本草范围（M-1 已落地+已考毕 FAIL 入册）；本车道未改其实现。
