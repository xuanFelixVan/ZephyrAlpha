---
ttl: task_bound
title: F42 P1 持仓体检——全流通挖干案卷（矿道 L05）
session: zc-l05-20260927
creation_token: fc-f42-p1-checkup-20260927
---

# F42 P1 持仓体检——挖干案卷

> 一句话：持仓流首环——六子环节（对账快照/分级监控/逻辑存活/风险否决/组合级/结论汇总）盘前并行+盘中持续，输出每持仓当日动作清单；单票看对错，组合看结构。节点组=TDM-P-P1+01..06 共 7 节点（今日 yaml P 段机数：P1=7，零漂移）。总册 built｜P1｜T6；上游 F57 对账/QMT 桥/L1/F39，下游 F43/F44/X-S1。

## 一、六向台账（实证锚点）

| 向 | 内容（锚点） |
|---|---|
| ①上游输入 | F57 盘后四步对账产物；QMT 桥 Stock.csv；L1 六段（板块退潮判据）；F39 板块生命周期 |
| ②数据原料 | strategy_book 逐笔台账；ATR 距止损距离；四类 thesis 证据（打板梯队/因子暴露/事件衰减/做T 趋势） |
| ③状态输出 | 富台账快照+WATCH/MONITOR/HOLD 三档+ALIVE/WEAKENED/DEAD 三态+风险否决标记+每持仓一条当日动作（维持/可做T/可加仓/减仓/转离场） |
| ④下游消费 | F43 P2 资格门（被 P1-04 冻结）、F44 P3 资格门；X-S1 离场评估（**thesis_survival 节点注自认"[CONSUMERS] X 流离场评估（失效→转离场评估，待接线）"**，册引 f42 册 §一）；P2-04 减仓指令 |
| ⑤自动化触发 | **已证接线仅 P1-06 裁决中心**：pf_alloc/allocation_orchestrator.py 装配体（regime→RegimeMetaAllocator→BudgetChangeHandler→StrategyBook→AdjudicationCenter，:9-18/117-122/539/919 册引）走 dloop_post pf_alloc 分配棒，下游 sim_paper_ledger——但走分配语义非"盘前五路体检汇总"语义 |
| ⑥缺口债 | **体检五件（01-05）日循环编排入口零命中**（册引 2026-09-25 grep 实证；今日复核 daily_loop_master_switch/daily_warroom_pipeline 零命中）；P1 全族 7 件验证 untested |

## 二、子模块三级枚举（2026-09-27 实扫）

- 域 `src/zephyr/position/core/`：29 件 .py（今日 ls 实扫）。P1 挂点 6/6 在盘：position_state_machine.py（7 态 :91-100+灰度 4 阶段 :111-118）、sell_decision/core/position_triage.py（P1-02 跨域挂载，WATCH/MONITOR/HOLD :62-64）、plan_engine/thesis_survival.py（P1-03 跨域挂载，yaml:2720 今日实锚；ALIVE/WEAKENED/DEAD :46-59）、risk/core/ashare_stop_loss_engine.py（P1-04，触发 7 种 :86-95+严重 4 态 :98-105+亏损限额三级 :107-115）、position_drift_monitor.py（P1-05）、position_adjudication_center.py（P1-06，IntendedAction 四意图 :80-86）。
- position/core 其余件（P2/P3/C2 域共享，详见 F43/F44 卷）：pyramiding_rules、position_sizing_engine、position_limit_enforcer、rebalance_engine、t1_sellable、strategy_book、core_satellite_allocator、firm_risk_aggregator、correlation_regime_monitor 等。
- 域计数：position/ 38 件、sell_decision/ 28 件、plan_engine/ 37 件（今日实扫）。

## 三、接线四态独立复核（2026-09-27）

| 件 | 四态判定 | 独立证据 |
|---|---|---|
| P1-06 裁决中心 | **接线（分配语义）** | allocation_orchestrator 消费锚（册引四锚点）；今日未重跑逐行，锚点维持 |
| P1-01/02/03/04/05 体检五件 | **纯库挂机（编排悬空）** | 今日 grep position_triage|thesis_survival|position_drift_monitor|ashare_stop_loss 于 daily_loop_master_switch.py+daily_warroom_pipeline.py **零命中**（独立复核成立）；与 M5"order_daemon 建成未接线"同型 |
| X 流转离场评估消费 | **缺线（自认待接线）** | thesis_survival 节点注自认（册引）；F45 卷双源独立复核 sell_decision 包外零消费者今日 grep 成立 |
| 对账上游衔接 | **待核** | F57 盘后四步对账→P1 盘前对账的排程证据同样缺（册引） |

**骨架勘误（登记待 D 线）**：
1. **总册 F42 状态"built"与触发链实证矛盾**：六节点模块全在盘（built 的"实件"面成立），但体检五件无任何日循环编排入口——按全流通四要素判"自动化"向不绿，实际为"半建成半接线"态（f42 册 §八已自评"待挖（窄口）"）。建议总册 F42 行状态修正或加注（文档矛盾=事故，宪法 §4.3；本卷不代改总册）。
2. P1-02 挂载点在 sell_decision 域、P1-03 在 plan_engine 域——跨域挂载为地图既定口径（册引"跨域挂载正常"），非勘误，登记防误判。

## 四、缺口清单（处置+优先级）

| # | 缺口 | 处置 | 级 |
|---|---|---|---|
| G42-1 | 体检五件编排入口悬空（头号病灶） | a) 考古 sim_paper_ledger/AutoRuntime 事件链是否隐式驱动（0.5 天）→b) 无则立施工单"P1 体检棒"挂 dloop 链（1-2 天） | **P0** |
| G42-2 | X 流转离场评估待接线 | X 流 S1 输入接线（F45 卷 G45-1 同源，移交 F45 卷工单） | P1 |
| G42-3 | 判据-码面差异两处（P1-04 时间止损/事件禁区 vs 码面 7 触发类型；P1-06 五动作+人工确认 vs 四意图） | S4 场景对齐（改注或补枚举，各 0.5 天） | P1 |
| G42-4 | P1 全族 7 件验证 untested+止损引擎登记 P3 低优先与风险权重错配 | 提级申请（晨报列 Owner 清单）+sensor_monotonicity 批量冻结 | P1 |
| G42-5 | rpt_e05 已破止损判 WATCH 修正（2026-09-18）验证面覆盖 | 随 G42-4 批补配对测试 | P2 |

## 五、自审闸三态

**待挖（窄口）**（状态机血肉与验证欠账挖干；唯触发链向欠"谁调、何时调、跑没跑"最后一向实证——考古后补证即可翻挖干可施工；体检五件零编排今日独立复核成立）。

### 待裁
- G42-1 考古结论若为"隐式驱动"，须补排程证据登记；若为零驱动，体检棒施工批排期归 Owner。

## 六、复跑命令

```bash
sed -n '91,118p' src/zephyr/position/core/position_state_machine.py   # 7 态+灰度
sed -n '86,115p' src/zephyr/risk/core/ashare_stop_loss_engine.py      # 触发/严重级/限额
grep -n "AdjudicationCenter" src/zephyr/pf_alloc/allocation_orchestrator.py | head -4
grep -rn "position_triage\|thesis_survival\|position_drift_monitor\|ashare_stop_loss" src/zephyr/plan_engine/daily_loop_master_switch.py src/zephyr/plan_engine/daily_warroom_pipeline.py  # 预期空
grep -n "待接线" src/zephyr/plan_engine/thesis_survival.py
```
