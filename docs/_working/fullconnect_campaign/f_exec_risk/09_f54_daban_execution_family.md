---
ttl: task_bound
title: "F54 打板执行族——daban 八件（信号/负载/PIT 闭环，执行半边挂 G22）（L06 复飞卷）"
session: zc-l06-20260927
create_guard: creation_token 由落地车道随批补办（M2 车道先例）
---

# F54 · 打板执行族（ex_core/daban_*.py 八件）

> 上游=F41 L4-05 打板专项（判据面）；下游=F53 订单生命周期（执行面）；真源=24 号文 daban_strategy_detail 缺失#1-#12 编号体系。

## 一、六向台账（实证锚点）

| 向 | 实证 |
|---|---|
| 上游输入 | daban_load_producer 四引擎负载日频批产→c1_market.daban_engine_load；daban_sleeve_strategy PIT 真读（pf_core/strategies/daban_sleeve_strategy.py:4 消费实证）|
| 下游消费 | signal/load/pit 三件闭环（回测+权重面）；**execution/exit/instant_breaker/monitors 四件零实盘消费者**（M7-04 B3，本日 grep daban_execution 域外零命中复证）——sleeve 现在产的是权重，走 trading_session delta 普通下单，打板专用三段分笔/瞬时熔断/持续监控全未挂 |
| 自动化触发 | daban_load_producer.run_daily_batch 日频批（T3⑧）；daban_pit_safety 主循环=回测面唯一装配打板决策链处 |
| 真源与注册表 | 蓝图=docs/03_modules/_domain_execution_core/（八件 [ALGO_FLOW] 机生 yaml 在盘）；设计真源=docs/_working/archive/2026-09/design_memos/24_daban_strategy_detail.md |
| 门禁与质量尺 | daban_pit_safety INV-004（龙虎榜 T-1 PIT 铁律+未来函数双保险）；signal pre_validate（≥70 放行/50-70 降仓/<50 否决）+classify_decision_v192 七类（PHASE_THRESHOLDS 冰点20/反核40/主升40/疯狂65/退潮85 事实禁板）|
| 当前运行状态 | **黄（回测半绿/执行半红）**——回测+权重半边闭环（load_producer 已闭环）；执行半边等 G22 执行层落线 |

## 二、子模块三级枚举（本日实扫 wc -l，八件 1919 行）

- **信号/门控**：daban_signal_decision.py 113（pre_validate 七类决策）｜daban_named_functions.py 248（8 具名函数：梯队健康四档/连板死亡池/竞价三维/纸老虎否决/封单结构/次日溢价/反核板/量化席位降权）
- **执行族（零消费者四件）**：daban_execution.py 196（60/30/opportunistic 三段+SaR>2% 削 30%+Hawkes 封单核+TimingDecision+CapacityCalculator）｜daban_exit_decision.py 128（NextDayExitDecision 硬退三件+高开两档+reflush）｜daban_instant_circuit_breaker.py 74（sleeve 级瞬时熔断，与账户级 KillSwitch 并列优先级更高）｜daban_monitors.py 144（#9 渐进降仓+#6 信号失效 OK→REDUCE→STOP）
- **安全/负载**：daban_pit_safety.py 197（INV-004+PIT 回测框架主循环）｜daban_load_producer.py 819（四引擎负载真源，已闭环）

## 三、接线四态独立复核

| 面 | 四态 | 复核证据 |
|---|---|---|
| 负载→sleeve 权重 | 已闭环 | daban_load_producer 消费方=pf_core/strategies/daban_sleeve_strategy（本日 grep 实锚）|
| 信号决策 | 回测面 wired | pit_safety 主循环唯一装配处 |
| 执行四件 | **码成闸空** | 域外零消费（本日复证，与 M7-04 B3 同判）|
| execution_route_policy 打板专用路径 | testing | ex_sor/core/execution_route_policy.py（90 号 Phase1 交付）——与 daban_execution 同一条腿两半，G22 应一批装配（M7-05 提速项）|

### 骨架勘误
总册 F54 行状态=**built**——按运行态应记 **partial（回测半闭环/执行半零消费）**；且总册行写"daban 六件套"，实测**八件**（daban_named_functions/daban_load_producer 两件未计入）。双重勘误登记。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | 执行四件零实盘消费者 | G22 装配批：daban_execution 经 sleeve→session 注入或专项执行腿+execution_route_policy 打板路径同批（1-2 天；挂 G22=M7 施工+Owner 排期）| P1 |
| 2 | 瞬时熔断未挂实盘接线 | 随缺口 1 同批（保命面，G22 前保持回测域）| P1 |
| 3 | trade_log 无排板标记/order_type 全 market（BT-P2-045 caliber_note） | 回测流水 schema 增字段（M1/BT 组交界）| P1 |
| 4 | 微结构族 7 件 design-frozen 头注未统一（M7-04 B2） | 头注改 design-frozen+冻结依据指针（0.5 天可施工）| P2 |

## 五、自审闸三态
**挖干可施工**（八件全勘+回测/执行两半边界清晰；缺口 1 挂 G22 有归属有量级；文档↔代码映射经 algo_flow 机生天然成册，净零纪律不新增注册表）。

## 六、复跑命令
```bash
wc -l src/zephyr/ex_core/daban_*.py | tail -1   # 1919 行/8 件
grep -rln "daban_execution\|DabanExecution" src/zephyr scripts --include="*.py" | grep -v __pycache__ | grep -v ex_core   # 零命中=执行半边缺口复证
grep -rln "daban_load_producer" src/zephyr/pf_core/strategies/   # 回测半边闭环实证
grep -n "INV-004\|PHASE_THRESHOLDS" src/zephyr/ex_core/daban_pit_safety.py src/zephyr/ex_core/daban_signal_decision.py | head -4
```
