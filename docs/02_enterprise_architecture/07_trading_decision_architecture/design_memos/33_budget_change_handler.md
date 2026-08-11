---
ttl: permanent
doc_type: architecture_view
title: BudgetChangeHandler 三级升级协议
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.0.0"
date: 2026-08-10
topic: budget_change_handler
scope: 07_trading_decision_architecture
---

# BudgetChangeHandler 三级升级协议

> **性质**：由 [00_index_trading_decision](00_index_trading_decision.md) G14 主题组派生，将 BudgetChangeHandler 的讨论要点落地为可施工的 spec + 伪代码。
> **施工图纪律**：本文档 status=active，对应模块允许施工。
> **2026-08 研究整合**：机构级 budget rebalance 协议；convergence_window 按换手率差异化（30_multi_strategy_concurrency §6.4）；Perold Implementation Shortfall 框架（换仓成本 vs 不换仓成本权衡）；三级升级 fail-safe 设计。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G14 BudgetChangeHandler 三级升级 |
| 所属 | 作战地图 08 + 30_multi_strategy_concurrency §2.4 |
| 依赖 | G12（[31_position_sizing](31_position_sizing.md)）、G13（[32_firm_risk_aggregator](32_firm_risk_aggregator.md)）、G15（[34_regime_meta_allocator](34_regime_meta_allocator.md)） |
| 对标 | 机构级 budget rebalance 协议 / Perold Implementation Shortfall |
| 正交性 | ⚠️ budget 来源依赖 RegimeMetaAllocator（G15），但三级升级逻辑本身正交 |
| 优先级 | P2 |
| 状态 | ✅ active — Tier1封锁+Tier2自选砍仓+Tier3强裁+convergence_window+接口契约已定稿 |

## 2. 背景

### 2.1 项目处境

RegimeMetaAllocator（G15）根据 regime 切换和 PerformanceScore 动态调整各策略 sleeve 的资金预算（budget）。当某 sleeve 的 budget 被下调时，其当前持仓可能超出新 budget——需要一套协议安全地将持仓收敛到新 budget。BudgetChangeHandler 就是这套收敛协议，采用三级升级设计：先软后硬，给策略自选空间，但 firm 层有兜底强裁保证。

### 2.2 核心问题

1. **budget 下调触发**：regime 切换（如 BULL→BEAR）或 PerformanceScore 下降导致 sleeve budget 被下调。
2. **持仓超限**：当前持仓权重 > 新 budget，需卖出部分持仓收敛。
3. **策略自选 vs firm 强裁**：优先让策略自选卖出哪些持仓（策略最懂自己 alpha），但若策略不配合，firm 层必须强裁兜底。
4. **收敛窗口**：不同换手率策略收敛速度不同——打板 1-2 天、多因子 3-5 天、事件驱动 2-3 天。
5. **换仓成本权衡**：换仓有交易成本，不换仓有 drift 成本（Perold Implementation Shortfall）——需判断是否值得换仓。

### 2.3 约束条件

- **策略不能说"我不卖"**：rebalance_to_budget 接口是强制性的，策略必须返回卖出计划
- **T+1 约束**：当日卖出次日才能再买入，收敛需跨日
- **每级独立 log**：三级升级每级独立记录日志，便于复盘
- **与 [42_sell_flow](42_sell_flow.md) 联动**：Tier 2 自选砍仓复用卖出流的优先级排序

## 3. 决策

### 3.1 架构定义

BudgetChangeHandler 由触发检测层、三级升级层、收敛监控层三层构成：

```
触发检测层: budget 下调检测 → 超限计算 → convergence_window 判定
                                                        ↓
三级升级层: Tier1 封锁新仓(瞬时) → Tier2 自选砍仓(convergence_window内) → Tier3 强裁(超时兜底)
                                                        ↓
收敛监控层: 收敛进度追踪 → 升级触发 → 每级独立 log/复盘
```

### 3.2 budget 下调触发检测算法

```python
from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum
from typing import Optional


class StrategyTurnover(Enum):
    """策略换手率分类（30_multi_strategy_concurrency §6.4）。"""
    HIGH = "high"        # 打板：1-2 天 convergence
    MEDIUM = "medium"    # 事件驱动：2-3 天 convergence
    LOW = "low"          # 多因子：3-5 天 convergence


# convergence_window 映射（天）
CONVERGENCE_WINDOW = {
    StrategyTurnover.HIGH: 2,     # 打板 1-2 天
    StrategyTurnover.MEDIUM: 3,   # 事件驱动 2-3 天
    StrategyTurnover.LOW: 5,      # 多因子 3-5 天
}


@dataclass
class BudgetChangeRequest:
    """budget 变更请求。"""
    strategy_id: str
    old_budget: float              # 原 budget 比例
    new_budget: float              # 新 budget 比例
    current_weight: float          # 当前持仓权重
    turnover_class: StrategyTurnover
    trigger_reason: str            # 触发原因（regime切换/PerformanceScore下降/回撤缩减）
    trigger_date: date


@dataclass
class OverrunStatus:
    """持仓超限状态。"""
    strategy_id: str
    overrun_weight: float          # 超限权重 = current_weight - new_budget
    overrun_pct: float             # 超限比例 = overrun_weight / current_weight
    convergence_window_days: int   # 收敛窗口（天）
    deadline: date                 # 收敛截止日
    tier: int                      # 当前升级级别 (1/2/3)


def detect_budget_overrun(
    request: BudgetChangeRequest,
) -> Optional[OverrunStatus]:
    """检测 budget 下调是否导致持仓超限。

    超限判定：current_weight > new_budget
    收敛窗口：按策略换手率分类
    """
    overrun_weight = request.current_weight - request.new_budget

    if overrun_weight <= 0:
        return None  # 未超限，无需收敛

    overrun_pct = overrun_weight / request.current_weight if request.current_weight > 0 else 0.0
    window = CONVERGENCE_WINDOW[request.turnover_class]
    deadline = request.trigger_date + timedelta(days=window)

    return OverrunStatus(
        strategy_id=request.strategy_id,
        overrun_weight=overrun_weight,
        overrun_pct=overrun_pct,
        convergence_window_days=window,
        deadline=deadline,
        tier=1,  # 初始 Tier 1
    )
```

### 3.3 Tier 1 封锁新仓算法（瞬时）

```python
@dataclass
class Tier1Action:
    """Tier 1 动作——封锁新仓。"""
    strategy_id: str
    action: str = "block_new_positions"
    timestamp: str
    reason: str
    blocked_symbols: list[str]      # 被封锁的新仓标的


def execute_tier1_block(
    overrun: OverrunStatus,
    current_date: date,
    pending_buy_orders: list[str],  # 待执行的新仓买单标的
) -> Tier1Action:
    """Tier 1：封锁新仓（瞬时生效）。

    逻辑：
    - budget 下调瞬间触发，立即封锁该 sleeve 的所有新仓买入
    - 已有持仓不动（给策略 Tier 2 自选空间）
    - 封锁持续到持仓收敛到新 budget 内

    设计原则（fail-safe）：
    - 封锁是"止血"——防止超限进一步扩大
    - 不强制卖出——给策略 Tier 2 自选空间
    - 瞬时生效——不等 convergence_window
    """
    from datetime import datetime

    return Tier1Action(
        strategy_id=overrun.strategy_id,
        action="block_new_positions",
        timestamp=datetime.now().isoformat(),
        reason=f"budget_overrun_{overrun.overrun_pct:.1%}_block_new",
        blocked_symbols=pending_buy_orders,
    )
```

### 3.4 Tier 2 自选砍仓算法（convergence_window 内）

```python
@dataclass
class RebalancePlan:
    """策略自选砍仓计划。"""
    strategy_id: str
    sell_orders: list[dict]         # [{symbol, weight_to_sell, priority, reason}]
    total_weight_to_sell: float
    expected_completion_days: int
    plan_timestamp: str


def request_tier2_rebalance(
    overrun: OverrunStatus,
    current_positions: dict[str, float],  # {symbol: weight}
    # 策略需提供的回调（接口契约）
    rebalance_callback: callable,         # 策略实现的 rebalance_to_budget 函数
) -> RebalancePlan:
    """Tier 2：请求策略自选砍仓（convergence_window 内）。

    接口契约（强制性）：
    - rebalance_callback(strategy_id, target_budget, current_positions) → RebalancePlan
    - 策略不能返回空计划（不能说"我不卖"）
    - 策略必须返回 total_weight_to_sell ≥ overrun_weight
    - 策略最懂自己 alpha，自选卖出 alpha 最弱的持仓

    与 [42_sell_flow] 联动：
    - 策略内部复用卖出流的优先级排序（止损>止盈>时间止损>情绪退潮）
    - 自选砍仓优先卖 alpha 衰减最快的持仓
    """
    plan = rebalance_callback(
        strategy_id=overrun.strategy_id,
        target_budget=overrun.overrun_weight,
        current_positions=current_positions,
    )

    # 契约校验——策略不能说"我不卖"
    if plan is None or plan.total_weight_to_sell < overrun.overrun_weight * 0.95:
        # 策略不配合 → 直接升级 Tier 3
        plan.tier_escalated = True
        plan.escalation_reason = "strategy_non_cooperative"

    return plan


def default_rebalance_to_budget(
    strategy_id: str,
    target_weight_to_sell: float,
    current_positions: dict[str, float],
    position_scores: dict[str, float],  # {symbol: alpha_score} 越低越优先卖
) -> RebalancePlan:
    """默认 rebalance_to_budget 实现——按 alpha_score 升序卖出。

    策略可覆盖此实现，但必须满足接口契约。
    默认逻辑：alpha_score 最低的持仓优先卖出。
    """
    from datetime import datetime

    # 按 alpha_score 升序排序（最低的先卖）
    sorted_symbols = sorted(
        current_positions.keys(),
        key=lambda s: position_scores.get(s, 0.0)
    )

    sell_orders = []
    remaining = target_weight_to_sell

    for symbol in sorted_symbols:
        if remaining <= 0:
            break
        weight = current_positions[symbol]
        sell_weight = min(weight, remaining)
        sell_orders.append({
            "symbol": symbol,
            "weight_to_sell": sell_weight,
            "priority": len(sell_orders) + 1,
            "reason": f"rebalance_alpha_score_{position_scores.get(symbol, 0.0):.3f}",
        })
        remaining -= sell_weight

    return RebalancePlan(
        strategy_id=strategy_id,
        sell_orders=sell_orders,
        total_weight_to_sell=target_weight_to_sell - remaining,
        expected_completion_days=1,
        plan_timestamp=datetime.now().isoformat(),
    )
```

### 3.5 Tier 3 按比例强裁算法（超时兜底）

```python
@dataclass
class Tier3Action:
    """Tier 3 动作——firm 层按比例强裁。"""
    strategy_id: str
    forced_sells: list[dict]        # [{symbol, weight_to_sell, force_reason}]
    total_forced_weight: float
    timestamp: str
    reason: str


def execute_tier3_force_reduce(
    overrun: OverrunStatus,
    current_positions: dict[str, float],
    current_date: date,
) -> Tier3Action:
    """Tier 3：firm 层按比例强裁（超时兜底）。

    触发条件：
    - convergence_window 超时（current_date > deadline）
    - 或 Tier 2 策略不配合（plan 为空或不足）

    强裁逻辑：
    - 所有持仓按等比例削减（公平，不偏袒任何标的）
    - 削减比例 = overrun_weight / current_total_weight
    - 立即生成卖出指令，不等策略

    设计原则（fail-safe 兜底）：
    - Tier 3 是最后防线，必须保证 budget 约束不被突破
    - 等比例削减最简单透明，可审计
    - 强裁日志独立记录，便于复盘策略不配合的原因
    """
    from datetime import datetime

    total_current = sum(current_positions.values())
    if total_current <= 0:
        return Tier3Action(
            strategy_id=overrun.strategy_id,
            forced_sells=[],
            total_forced_weight=0.0,
            timestamp=datetime.now().isoformat(),
            reason="no_positions_to_reduce",
        )

    # 等比例削减
    reduce_ratio = overrun.overrun_weight / total_current
    reduce_ratio = min(reduce_ratio, 1.0)  # 不超过 100%

    forced_sells = []
    for symbol, weight in current_positions.items():
        sell_weight = weight * reduce_ratio
        if sell_weight > 0:
            forced_sells.append({
                "symbol": symbol,
                "weight_to_sell": sell_weight,
                "force_reason": f"tier3_proportional_reduce_{reduce_ratio:.1%}",
            })

    return Tier3Action(
        strategy_id=overrun.strategy_id,
        forced_sells=forced_sells,
        total_forced_weight=sum(f["weight_to_sell"] for f in forced_sells),
        timestamp=datetime.now().isoformat(),
        reason=f"tier3_force_reduce_ratio_{reduce_ratio:.1%}",
    )
```

### 3.6 三级升级主循环算法

```python
@dataclass
class ConvergenceLog:
    """收敛日志——每级独立记录。"""
    strategy_id: str
    tier: int                       # 1/2/3
    action: str
    timestamp: str
    overrun_before: float
    overrun_after: float
    details: dict


def handle_budget_change(
    request: BudgetChangeRequest,
    current_positions: dict[str, float],
    position_scores: dict[str, float],
    pending_buy_orders: list[str],
    rebalance_callback: callable = None,
    current_date: date = None,
) -> tuple[OverrunStatus, list[ConvergenceLog]]:
    """BudgetChangeHandler 三级升级主循环。

    完整流程：
    1. 检测 budget 下调是否超限（§3.2）
    2. 若超限 → Tier 1 封锁新仓（§3.3，瞬时）
    3. 请求 Tier 2 自选砍仓（§3.4，convergence_window 内）
    4. 若 Tier 2 超时或不配合 → Tier 3 强裁（§3.5，兜底）
    5. 每级独立 log 记录
    """
    if current_date is None:
        current_date = date.today()

    logs: list[ConvergenceLog] = []
    from datetime import datetime

    # 步骤 1：检测超限
    overrun = detect_budget_overrun(request)
    if overrun is None:
        return None, logs  # 未超限，无需处理

    # 步骤 2：Tier 1 封锁新仓（瞬时）
    tier1 = execute_tier1_block(overrun, current_date, pending_buy_orders)
    logs.append(ConvergenceLog(
        strategy_id=overrun.strategy_id,
        tier=1,
        action="block_new_positions",
        timestamp=tier1.timestamp,
        overrun_before=overrun.overrun_weight,
        overrun_after=overrun.overrun_weight,  # Tier 1 不减仓，只封锁
        details={"blocked_symbols": tier1.blocked_symbols},
    ))
    overrun.tier = 1

    # 步骤 3：Tier 2 自选砍仓
    if rebalance_callback is None:
        rebalance_callback = lambda sid, tw, cp: default_rebalance_to_budget(
            sid, tw, cp, position_scores
        )

    plan = request_tier2_rebalance(overrun, current_positions, rebalance_callback)

    tier_escalated = getattr(plan, "tier_escalated", False)

    if not tier_escalated and plan.total_weight_to_sell >= overrun.overrun_weight * 0.95:
        # Tier 2 成功——策略自选砍仓
        overrun.tier = 2
        logs.append(ConvergenceLog(
            strategy_id=overrun.strategy_id,
            tier=2,
            action="strategy_self_reduce",
            timestamp=plan.plan_timestamp,
            overrun_before=overrun.overrun_weight,
            overrun_after=max(0, overrun.overrun_weight - plan.total_weight_to_sell),
            details={"sell_orders": plan.sell_orders},
        ))
    else:
        # 步骤 4：Tier 3 强裁（超时或不配合）
        overrun.tier = 3
        tier3 = execute_tier3_force_reduce(overrun, current_positions, current_date)
        logs.append(ConvergenceLog(
            strategy_id=overrun.strategy_id,
            tier=3,
            action="firm_force_reduce",
            timestamp=tier3.timestamp,
            overrun_before=overrun.overrun_weight,
            overrun_after=max(0, overrun.overrun_weight - tier3.total_forced_weight),
            details={
                "forced_sells": tier3.forced_sells,
                "escalation_reason": getattr(plan, "escalation_reason", "timeout"),
            },
        ))

    return overrun, logs
```

### 3.7 convergence_window 差异化设计

| 策略类型 | 换手率 | convergence_window | 理由 |
|---|---|---|---|
| 打板 | 高 | 1-2 天 | 持仓周期短，快速收敛 |
| 事件驱动 | 中 | 2-3 天 | 事件催化后逐步退出 |
| 多因子 | 低 | 3-5 天 | 因子 convergence 慢，避免冲击成本 |

**设计原理**（30_multi_strategy_concurrency §6.4）：
- 高换手率策略收敛快，短窗口减少 drift 成本
- 低换手率策略收敛慢，长窗口减少冲击成本
- 窗口过短 → 强制卖出冲击大；窗口过长 → drift 成本累积

## 4. 考虑过的替代方案

| 方案 | 描述 | 拒绝理由 |
|---|---|---|
| **直接强裁** | budget 下调立即强裁 | 无策略自选空间，冲击成本大；三级升级更平滑 |
| **无限等待** | 等策略自然收敛 | 无兜底，budget 约束可能长期被突破 |
| **单一 Tier** | 只有强裁无自选 | 策略最懂自己 alpha，自选更优 |
| **MVO 换仓** | 均值方差优化换仓 | 需协方差估计；O(N²)；聚合层不做优化 |
| **固定窗口** | 所有策略相同收敛窗口 | 忽略换手率差异；打板慢收敛浪费，多因子快收敛冲击大 |

## 5. 上限定义

| 上限 | 值 | 理由 |
|---|---|---|
| **Tier 1 响应** | 瞬时 | 封锁新仓必须立即生效 |
| **Tier 2 窗口** | 1-5 天 | 按换手率差异化 |
| **Tier 3 触发** | 超时或不配合 | fail-safe 兜底 |
| **强裁比例** | 等比例 | 公平透明可审计 |
| **log 独立** | 每级独立 | 便于复盘 |

**演进路径**：
- MVP：三级升级 + convergence_window + 接口契约
- Phase 1.5：Perold Implementation Shortfall 判断是否值得换仓（[22_sector_rotation_spec] 已实现 _is_rebalance_worthwhile）
- Phase 2：动态 convergence_window（regime 条件调整）

## 6. 待裁定

| 项 | 暂缓理由 | 重评条件 |
|---|---|---|
| **Perold IS 判断** | [22_sector_rotation_spec] 已实现 _is_rebalance_worthwhile | Phase 1.5+ 整合到 Tier 2 决策 |
| **动态窗口** | 需 regime 条件映射 | Phase 2+ regime 验证后 |
| **多 sleeve 协调** | MVP 单 sleeve 独立收敛 | 多 sleeve 同时超限时重评 |

## 7. 待定问题（讨论要点）

- [x] ① Tier 1 封锁新仓（瞬时）→ §3.3 定型
- [x] ② Tier 2 rebalance_to_budget 信号（策略自选砍仓）→ §3.4 定型
- [x] ③ Tier 3 按比例强裁（firm 层兜底）→ §3.5 定型
- [x] ④ convergence_window 按换手率差异化 → §3.7 定型
- [x] ⑤ rebalance_to_budget 接口契约（策略不能说"我不卖"）→ §3.4 定型
- [x] ⑥ 每级独立 log/复盘 → §3.6 定型

## 8. 引用

- [00_index_trading_decision](00_index_trading_decision.md) §3 G14
- [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §2.4 / §6.4
- [31_position_sizing](31_position_sizing.md)（G12 产出物）
- [32_firm_risk_aggregator](32_firm_risk_aggregator.md)（G13，依赖项）
- [34_regime_meta_allocator](34_regime_meta_allocator.md)（G15，budget 来源）
- [42_sell_flow](42_sell_flow.md)（G20，Tier 2 卖出优先级复用）
- [22_sector_rotation_spec](22_sector_rotation_spec.md)（_is_rebalance_worthwhile Perold IS）
- battle_map_08_position_management（当前状态快照）

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行：由 00_index G14 讨论要点占位，待讨论填空 |
| 2026-08-10 | 1.0.0 | 补齐 Tier1封锁+Tier2自选砍仓+Tier3强裁+convergence_window+接口契约+三级升级主循环 | 三级升级 fail-safe 设计，整合 30_multi_strategy_concurrency §2.4/§6.4 |
