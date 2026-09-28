---
ttl: task_bound
title: "F49 C2 组合聚合——净额轧平/约束栈/相关性聚类/budget 三级升级（L06 复飞卷）"
session: zc-l06-20260927
create_guard: creation_token 由落地车道随批补办（M2 车道先例）
---

# F49 · C2 组合聚合（TDM-F-C2-01..04）

> 上游=F-C1（sequence+feed）、全图 sleeve intent（M-12 数据轴承载）、F47 R1 broadcast；下游=F-C3 归因、E-L4/X-S2 净指令。
> 纯指令型声明（外审 M-59）：不触碰下单接口，一切下单经 E-L4/X-S2。

## 一、六向台账（实证锚点）

| 向 | 实证 |
|---|---|
| 上游输入 | C1 feed、R1 governance broadcast、各 sleeve intent；地图锚 yaml:3810（C2-01）|
| 下游消费 | C2-01→E-L4 净指令（state）+→X-S2-01；C2-04→C2-01；C2-02/03→C3 归因链 |
| 自动化触发 | 与 C1 同链——allocation_orchestrator 一次性装配（regime→RegimeMetaAllocator→**BudgetChangeHandler**→StrategyBook→AdjudicationCenter；**本日复证 import 锚 allocation_orchestrator.py:109/122**）；夜批 09-14..09-22 零缺勤（a54997e221 判据）|
| 真源与注册表 | 地图 yaml:3759-3947；32/33 号备忘录（firm_risk_aggregator/budget_change_handler 设计）在档；portfolio_model_refs PFM-HEU-002/PFM-RB-001/PFM-HEUR-009 |
| 门禁与质量尺 | 四节点全 auto；RLM-CONCENTRATION-002/003；C2-02 六层约束栈（D76 定稿）|
| 当前运行状态 | **黄偏绿**——四模块全 wired（本日消费方 grep 复证见 §三）；净指令下发 E-L4 的执行侧消费=模拟域 paper |

## 二、子模块三级枚举（本日实扫 wc -l）

- **position.core**（聚合与约束）：firm_risk_aggregator.py 804（MOD-POS-021，C2-01/02 共锚）｜correlation_regime_monitor.py 182（MOD-POS-012，ρ>0.70 减半/0.85 禁新仓）｜budget_change_handler.py 1020（MOD-POS-022，Tier1/2/3+防抖）｜covariance_estimator.py（MOD-POS-011 底座 Ledoit-Wolf）｜cross_strategy_position_merger.py（MOD-POS-005 底座）
- **pf_alloc**（装配消费方）：allocation_orchestrator.py 1382（BudgetChangeHandler 装配直调）｜batched_position_builder.py（firm_risk_aggregator 消费方）

## 三、接线四态独立复核

| 模块 | 消费方（本日 grep 实锚） | 四态 |
|---|---|---|
| firm_risk_aggregator | batched_position_builder/boundary_revision_engine/tomorrow_boundary_planner/single_name_cap_caliber/strategy_book/t1_sellable | wired |
| budget_change_handler | allocation_inputs/allocation_orchestrator/regime_meta_allocator | wired（装配直调）|
| correlation_regime_monitor | strategy_book/adaptive_risk_monitor（16 册口径，域内复证）| wired |

### 骨架勘误
无状态级勘误（总册 built/P1 与实测相符）。登记一处注记滞后：C3-03 地图 note 仍写"编排未接线（裁定#257②）"（yaml 本日实锚 note_confirmed 2026-09-18 仍带旧注）vs 实测 BudgetChangeHandler/RegimeMetaAllocator 已入 orchestrator 装配——该注记属 F50 卷回填项，此处交叉登记。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | BudgetChanged 事件链未接线（33 号复核自认） | 补事件发射或承认装配直调为正源回填 33 号（0.5-1 天）| P1 |
| 2 | C2-01 执行侧 netting 三空白（净差单真实撮合=模拟域） | 待实盘域开闸（S-1 锁着）随 G5 批 | P1 |
| 3 | C2-03 月度再聚类无调度登记 | 待 M5 补挖波核对计划任务面 | P1 |
| 4 | 验证欠账 BT-P3-039..042 plan=null | F52 卷统筹预注册 | P1 |

## 五、自审闸三态
**挖干可施工**（四模块消费面本日三源复证全 wired；缺口均在"执行侧/事件化/验证"三层，无码面缺口）。

## 六、复跑命令
```bash
grep -n "BudgetChangeHandler\|PositionAdjudicationCenter" src/zephyr/pf_alloc/allocation_orchestrator.py | head -3
grep -rln "firm_risk_aggregator\|FirmRiskAggregator" src/zephyr --include="*.py" | grep -v __pycache__ | grep -v "position/core/firm_risk"
sed -n '3810,3822p' config/trading_decision_map.yaml
awk '/node_id: TDM-F-C3-03/,0' config/trading_decision_map.yaml | grep -m2 "note_confirmed\|未接线"   # 注记滞后实证
```
