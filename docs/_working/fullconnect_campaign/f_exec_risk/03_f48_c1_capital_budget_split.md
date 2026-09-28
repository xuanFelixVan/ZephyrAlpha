---
ttl: task_bound
title: "F48 C1 预算切分——六段灰度预算带/过渡带/尾部预备金/ANCHORED_CAP（L06 复飞卷）"
session: zc-l06-20260927
create_guard: creation_token 由落地车道随批补办（M2 车道先例）
---

# F48 · C1 预算切分（TDM-F-C1，组合流门户）

> 上游=F27 sleeve 组装/L1-AGG 六段 broadcast/C3-03 月度调权反馈；下游=F-C2 聚合+C2-04 budget 三级。
> B 半唯一全链自动运行段的上游门户（夜批运行证据在案）。

## 一、六向台账（实证锚点）

| 向 | 实证 |
|---|---|
| 上游输入 | L1-AGG daily broadcast（edge 实测；注：TDM-E-L1-AGG production 已翻转到 anchored_state_machine，commit a54997e221 本日实锚）、C3-03 feedback T-1、PP-001 配置（allocation_inputs.load_pp001_plan）|
| 下游消费 | F-C2 sequence+C2-04 feed；运行时真消费=daily_decision_orchestrator——**fail-closed 语义本日复证：daily_decision_orchestrator.py:619-620 `ctx.reasons.append("budget_run_missing")+ctx.degrade.append("D3_budget_run_missing")`** |
| 自动化触发 | 事件触发合规链：pipeline_events.maybe_emit_pf_alloc_daily（**pipeline_events.py:29/83 自注"pf_alloc 日分配的唯一自动产出者"**，daily_kline SUCCESS 唤醒）→ `python -m zephyr.pf_alloc.allocation_orchestrator` → alloc_budget_daily 落表；git log 本日实锚=a54997e221（夜批 09-14..09-22 七交易日零缺勤判据①）|
| 真源与注册表 | 地图 yaml:3726（TDM-F-C1）；六段灰度带 mounted 表 yaml:5620-5635 本日实锚（六状态全 proposed）；DAL-BUDGET-BAND（**design，code_ref=null**）；DAL-RISK-BUDGET（trial）|
| 门禁与质量尺 | node_type=gate；crisis_gate.py 456 行危机短路（裁定#392 D5）|
| 当前运行状态 | **绿（paper 域）**——ANCHORED_CAP 供件+组合层裁剪随 a54997e221 落位（cap=1−0.70×clamp((vol_pct−0.30)/0.70,0,1)，陈旧>7 日历日=applied False，一键切回 data/runtime/anchored_cap.disabled，回滚窗至 2026-10-23）|

## 二、子模块三级枚举（本日实扫 wc -l）

- **pf_alloc 根**（装配链）：allocation_orchestrator.py 1382（MOD-PA-030 分配链装配体 regime→RMA→BCH→StrategyBook→AdjudicationCenter，:109/:122 import 实锚）｜allocation_inputs.py 754（④锚定 cap 供件）｜allocation_persistence.py 160（落表）｜crisis_gate.py 456（危机闸）
- **pf_alloc.core**（节点字面锚+trial）：multi_strategy_capital_allocator.py 307（MOD-PA-003，消费=signal_weight_adjuster）｜risk_budget_allocator.py 96（DAL-RISK-BUDGET inverse_var/risk_parity/sharpe_weight，trial 休眠）

### 骨架勘误
总册 F48 行核心模块路径仅列 multi_strategy_capital_allocator.py——**运行载体实为 allocation_orchestrator.py 装配体**（15 号备忘录口径；multi_strategy_capital_allocator 只是节点字面锚，被 alloc 域内消费）。建议骨架补列 orchestrator 锚。

## 三、接线四态独立复核

| 面 | 四态 | 复核证据 |
|---|---|---|
| 日批产出链 | 已接线（事件触发） | maybe_emit_pf_alloc_daily :29/:83 自注唯一产出者 |
| 下游 fail-closed | 已接线 | orchestrator :619-620 D3 降级留痕 |
| ANCHORED_CAP | 已接线（a54997e221） | git log 实锚+tests/pf_alloc/test_anchored_cap.py 13 例（commit 自述）|
| 六段带数值承载 | **码缺** | DAL-BUDGET-BAND design+code_ref=null——带表只存在于地图注释（15 册判，本日无反证）|

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | DAL-BUDGET-BAND 无代码承载 | 带表落 config 或 allocation_inputs 常量+登记真源指针（0.5 天，本车道可修）| P1 |
| 2 | PP-001 权重演进计划未启动 | 等权→逆波动率→半 Kelly+HRP，挂排期 | P2 |
| 3 | UP-3 前瞻风险预算 trial 休眠 | 与 DAL-FWD-STOP/TAIL-HEDGE 同批待回测验证 | P2 |
| 4 | BT-P3-036 组合归因验证 plan=null | F52 卷统筹预注册 | P1 |

## 五、自审闸三态
**挖干可施工**（B 半唯一有夜批运行证据的环节；L1-AGG 翻转后 anchored 链已终批落地；带表代码化是唯一结构缺口）。

## 六、复跑命令
```bash
git log --oneline -1 -- src/zephyr/pf_alloc/allocation_orchestrator.py   # a54997e221
grep -n "maybe_emit_pf_alloc_daily" src/zephyr/strategy_pipeline/pipeline_events.py | head -2
sed -n '619,621p' src/zephyr/strategy_pipeline/daily_decision_orchestrator.py
grep -n "node_id: TDM-F-C1$" config/trading_decision_map.yaml   # :3726
sed -n '5620,5636p' config/trading_decision_map.yaml   # 六段带 mounted 表全 proposed
```
