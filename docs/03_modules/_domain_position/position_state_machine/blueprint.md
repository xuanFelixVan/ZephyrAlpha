---
module_id: MOD-POS-002
title: "仓位状态机蓝图 — 仓位生命周期状态转换"
doc_type: blueprint
status: Active
version: "0.1.0"
ttl: permanent
layer: L03_position
layer_name: position
functional_domain: position
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-02"
last_updated: "2026-08-02"
priority: P0
blueprint_level: module
responsibility_domain: 
---

# MOD-POS-002 Position State Machine — 仓位状态机 蓝图

> **module_id**: MOD-POS-002 | **域**: D_POSITION | **层**: L03 仓位管理
> **优先级**: P0 | **成熟度**: L1 🔵 骨架 → production | **建设标记**: ✅可建
> **SSoT**: depgraph MOD-POS-002 | **设计真源**: D:\临时工作区\依赖图\07-D-POSITION-仓位管理域.md §1.1 POS-02, §4 E-POS-05

## 1. 定位

仓位裁决中心的状态根——管理单标的仓位生命周期状态转换。复用共享 `StateMachine[S]` 基类
(MOD-INF-038) 管转换合法性，业务规则(观察期/冷却期/灰度)在业务层包装，不污染共享基类。

状态机:
```
NONE → BUILDING → ACTIVE → OBSERVING → REDUCING → EXITING → CLOSED
                                ↑                        ↓
                                └──── (冷却期后可重建) ───┘
```

属 A 类基础设施(状态转换矩阵+观察期/冷却期/灰度逻辑明确)，时间参数为 C 类可调默认值。
依据: 07-D-POSITION §1.1 POS-02, §4 E-POS-05

## 2. 不变量 (INVARIANTS)

- **状态转换必须合法**: 仅允许定义的 Transition，非法转换抛 InvalidTransitionError
- **OBSERVING 期间禁止新买入**: can_buy() 返回 False (软止损/异常开盘/暴跌触发)
- **CLOSED 冷却期禁止重建**: cooldown_until 未到时 can_rebuild() 返回 False
- **灰度阶段单调推进**: 5%→20%→50%→100% 不可回退，回退抛 GraduationRegressionError
- **满仓阶段自动转 ACTIVE**: STAGE_4_100PCT 完成即 BUILDING→ACTIVE
- **时间通过 now 参数注入**: 状态机不耦合具体日历/数据源

## 3. 错误契约 (ERROR_CONTRACT)

| 错误类 | error_code | 触发条件 |
|--------|-----------|---------|
| ObservingPeriodViolationError | ZA-POS-0001 | 观察期内尝试新买入 |
| CooldownPeriodError | ZA-POS-0002 | 冷却期内尝试重新建仓 |
| GraduationRegressionError | ZA-POS-0003 | 灰度阶段回退或未满最短验证天数 |
| InvalidTransitionError | (共享基类) | 非法状态转换 |

## 4. 依赖关系

| 方向 | 模块 | 契约/事件 | 说明 |
|------|------|---------|------|
| 消费 | MOD-INF-038 StateMachine[S] | 共享基类 | 转换合法性矩阵 |
| 产出 | MOD-POS-003 漂移监控 | E-POS-05 StateChanged | 状态变化通知 |
| 产出 | MOD-POS-009 审计 | E-POS-05 StateChanged | 审计追溯 |
| 产出 | MOD-POS-016 卖仓联动 | E-POS-05 StateChanged | 卖仓双向联动 |
| 产出 | D-SELL-DECISION | PositionStateFeedback | 仓位状态反向影响卖出阈值 |

## 5. 关键状态与事件

- **PositionState**: NONE / BUILDING / ACTIVE / OBSERVING / REDUCING / EXITING / CLOSED
- **ObservingReason**: SOFT_STOP / ABNORMAL_OPEN / PLUNGE
- **GraduationStage**: STAGE_1_5PCT / STAGE_2_20PCT / STAGE_3_50PCT / STAGE_4_100PCT
- **E-POS-05 StateChangedEvent**: symbol / from_state / to_state / timestamp / reason / context_snapshot

## 6. 接口

```python
fsm = PositionStateMachine("000001.SZ")
fsm.start_building(now=t0)                          # NONE → BUILDING (灰度1)
fsm.advance_graduation(now=t0+6d)                   # 灰度 1→2 (校验最短天数)
fsm.activate(now=t0+21d)                            # BUILDING → ACTIVE
fsm.enter_observing(ObservingReason.SOFT_STOP, now) # → OBSERVING
fsm.exit_observing(confirm=True, now)               # → REDUCING
fsm.start_exiting(now)                              # → EXITING
fsm.close(cooldown_until=t2+5d, now=t2)             # → CLOSED (冷却期)
```

可调参数 (PositionStateMachineConfig):
- observing_confirm_minutes=15 (观察期确认窗口)
- cooldown_trading_days=5 (CLOSED 后最小重仓间隔)
- graduation_stage_days=5 (灰度每阶段最短验证天数)

## 7. 设计决策

| 决策 | 理由 |
|------|------|
| 复用共享 StateMachine[S] 基类 | 避免重复状态机逻辑，转换合法性集中管理 |
| 业务规则在业务层包装 | 观察期/冷却期/灰度是仓位域专属，不污染共享基类 |
| 时间通过 now 注入 | 状态机不耦合日历，便于测试 |
| 满仓自动转 ACTIVE | 灰度4阶段完成=建仓完成，无需额外显式调用 |

## 8. 测试计划

- 全状态转换路径合法 (NONE→...→CLOSED→BUILDING 循环)
- 非法转换抛 InvalidTransitionError
- OBSERVING 期间 can_buy()=False
- CLOSED 冷却期 can_rebuild()=False，到期 True
- 灰度单调推进 + 回退抛错
- 灰度满仓自动转 ACTIVE
- 事件发布 (E-POS-05) + 订阅者异常隔离
