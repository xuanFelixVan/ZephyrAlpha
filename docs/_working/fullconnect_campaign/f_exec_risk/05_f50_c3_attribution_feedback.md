---
ttl: task_bound
title: "F50 C3 绩效归因反馈——多维归因/升降级退役/调权/参数校准/信号健康（L06 复飞卷）"
session: zc-l06-20260927
create_guard: creation_token 由落地车道随批补办（M2 车道先例）
---

# F50 · C3 绩效归因反馈（TDM-F-C3-01..05）

> 上游=F49/F28 归因供料、P2-03 做T统计、S2-06 卖出闭环、E-L4-13/E-L3-08 feed；下游=回灌 F37/E-L1-AGG/E-L2（feedback T-1）、E-L0 当日 feed、F21 假说先验、C1 调权。
> 系统自我进化发动机：全部凭数据不凭感觉。

## 一、六向台账（实证锚点）

| 向 | 实证 |
|---|---|
| 上游输入 | C2 sequence、feed 边 6 条（edge 实测）、E-L9-E2 证伪回传；地图锚 yaml:3950（C3-01）|
| 下游消费 | C3-05→E-L1-AGG+E-L2（T-1）、C3-03→C1（feedback）、C3-01/04→E-L0、C3-02→F21 回灌 |
| 自动化触发 | C3-01/02 靠日链（daily_decision/attribution 阶段）；**C3-03 装配体夜批已运行**（orchestrator 内 RegimeMetaAllocator :109 import 实锚）——地图 C3-03 注"未接线（裁定#257②）"**本日复核仍滞后未回填**（yaml note_confirmed 2026-09-18 带旧注，接线随 MOD-PA-030 已落地）|
| 真源与注册表 | 地图 yaml:3950-4170；54/55 号备忘录；THD-RETIRE×3/BMK-INDEX-003/BMK-ABSOLUTE-001；crisis_gate.yaml θ 真源 |
| 门禁与质量尺 | 五节点全 auto；D84 正确性必改五件（T+1 切账/双轨基准/复权口径/孤儿成交/现金贡献行）；D86 双窗口+一票否决+滞回带 |
| 当前运行状态 | **黄（paper 域部分运行）**——C3-01 引擎 702 行在盘被 factor_exposure_manager/performance_attribution_degradation 消费（**本日 grep 复证 risk/core/ 两消费方+reporting/attribution_calculator**）；C3-03 夜批在跑；C3-04/C3-05 红节点 |

## 二、子模块三级枚举（本日实扫 wc -l）

- **pf_core.core**：performance_attribution_engine.py 702（MOD-PF-007，几何 Brinson+二分+IS 三分解；消费方=reporting/attribution_calculator、risk/core/factor_exposure_manager、risk/core/performance_attribution_degradation——本日 grep 实锚）
- **factor.governance**：lifecycle_state_machine.py 121（MOD-L02-013，C3-02 评审编排面，红节点承载）
- **pf_alloc.core**：regime_meta_allocator.py 804（MOD-PA-007，C3-03 调权，wired 夜批）
- **signal_quality**：signal_degradation_monitor.py 332（MOD-SIGQC-004，C3-05 传感器健康，红节点）
- **backtest.core**：walk_forward.py 332（MOD-BT-001，C3-04 四道 gate 容器）

## 三、接线四态独立复核

| 面 | 四态 | 复核证据 |
|---|---|---|
| C3-01 归因引擎 | 码 built+消费 wired | 三消费方 grep 实锚（本日独立复证超 16 册两方口径）|
| C3-03 调权 | 已接线（夜批） | orchestrator :109；地图注滞后=回填项 |
| C3-02 评审编排 | 红节点 | lifecycle_state_machine 在盘，月度/季度评审无调度体发起 |
| C3-04 校准闭环 | 红节点 | G04 工单在、无人串环（tracker #48）|
| C3-05 判准率加权 | 红节点 | D7-D13 判准率加权 src 零实现（16 册判，本日无反证）|

### 骨架勘误
总册 F50 行状态=**built**——实测 C3 五节点中 02/04/05 三红（paper 域部分运行），按四要素建议改 **partial**。wiring_gap_inventory §1.4 partial 30 清单未收编 F50，二次勘误登记。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | C3-04 校准闭环未转起来 | C3-01→C3-04→参数 registry 工单链立项（2-3 天，本车道可修）| P1 |
| 2 | C3-05 判准率加权零实现 | 与 E-L1-AGG 反馈边一起立项 | P1 |
| 3 | C3-02 评审编排无调度发起 | M5 登记月度任务 | P1 |
| 4 | 地图 C3-03 注记滞后 | S4 场景 D 裁定留痕刷新 note_confirmed | P2 |
| 5 | 验证欠账 BT-P3-043..047+portfolio_attribution 未跑 | 归因引擎自己没被验证——F52 卷统筹 | P1 |

## 五、自审闸三态
**挖干可施工**（红节点三处均有真源+修法；消费面较 16 册口径再增强一处证据 reporting/attribution_calculator；地图注回填项登记）。

## 六、复跑命令
```bash
grep -rln "performance_attribution_engine\|PerformanceAttributionEngine" src/zephyr --include="*.py" | grep -v __pycache__ | grep -v "pf_core/core"
grep -n "RegimeMetaAllocator" src/zephyr/pf_alloc/allocation_orchestrator.py | head -2
wc -l src/zephyr/pf_core/core/performance_attribution_engine.py src/zephyr/factor/governance/lifecycle_state_machine.py
awk '/node_id: TDM-F-C3-03/,0' config/trading_decision_map.yaml | head -8   # 注记滞后
```
