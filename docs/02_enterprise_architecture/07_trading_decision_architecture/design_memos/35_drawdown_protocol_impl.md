---
ttl: permanent
doc_type: architecture_view
title: 回撤 Protocol 落地 spec
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.2.0"
date: 2026-08-10
topic: drawdown_protocol_impl
scope: 07_trading_decision_architecture
---

# 回撤 Protocol 落地 spec

> **性质**：由 [00_index_trading_decision](00_index_trading_decision.md) G16 主题组派生，将 [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §2.5 的四级回撤框架落地为可施工的 spec + 伪代码。
> **施工图纪律**：本文档 status=active，对应模块允许施工；流程见 [01_design_memo_management_spec](01_design_memo_management_spec.md) §2.2。
> **2026-08 研究整合**：Hsieh (2023) drawdown modulation + restart 机制；FerroQuant (2026-04) 5% kill switch fail-closed 原则；TradeShield (2026-08) 多层 drawdown defense；tradingwyckoff (2026-01) Kill Switch Protocol。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G16 回撤 Protocol 落地 |
| 所属 | 作战地图 09 + 30_multi_strategy_concurrency §2.5 |
| 依赖 | G12（仓位，[31_position_sizing](31_position_sizing.md) 已定稿 v1.2.0+）—— 但框架已有，可并行 |
| 对标 | ARKA / LedgerMind / Sina 量化FOF / tradingwyckoff / FerroQuant / TradeShield |
| 正交性 | ✅ 与 regime 正交（drawdown 是账户级，regime 是市场级） |
| 优先级 | P2（与 G12 并行，风险优先原则） |
| 状态 | ✅ active — 四级阈值+Kill Switch+恢复+日度熔断算法已定稿 |

## 2. 背景

### 2.1 项目处境

ZephyrAlpha 是 A 股量化交易系统，首批策略（打板/多因子/事件驱动）即将进入回测验证阶段。回撤 Protocol 是账户级生存风控的最后一道防线——在策略层 alpha 失效时，确保账户不会因连续亏损触及不可恢复的深渊。

### 2.2 核心问题

1. **四级阈值如何落地到 StrategyBook 内部**：30_multi_strategy_concurrency §2.5.1 定义了 8%/15%/20%/25% 四级阈值，但未给出 StrategyBook 内部的数据结构、计算口径和执行路径。
2. **单策略 vs 组合层面分层如何实现**：§2.5.3 要求单策略回撤独立收缩、组合回撤全局收缩，需要明确两层回撤的独立计算和联动机制。
3. **恢复机制如何避免自动恢复陷阱**：§2.5.2 要求"Recovery requires explicit re-authorization"，需要设计人工授权接口和分阶段恢复算法。
4. **Kill Switch 如何保证不可覆盖**：§2.5.5 要求"触发即执行，不允许人工覆盖延迟"，需要在架构上保证 Kill Switch 的优先级高于一切策略信号。
5. **回撤基准净值如何计算**：A 股 T+1 结算、日内浮盈浮亏、分红除权等因素影响净值口径，需要明确计算规范。

### 2.3 约束条件

- **A 股 T+1 结算**：当日卖出资金 T+1 才可用，回撤触发减仓时需考虑资金可用性
- **日内 vs 收盘口径**：日内浮亏可能触发临时熔断，收盘口径用于四级阈值判定
- **Kill Switch 不可覆盖**：架构上必须 fail-closed，监控不可用时默认 halt
- **与 regime 的协同**：drawdown 是账户风险（管生存），regime 是市场风险（管仓位节流），两者正交但 Shrinkage 可叠加

## 3. 决策

### 3.1 架构定义

回撤 Protocol 作为 StrategyBook 内部的独立风控层，位于信号生成与订单执行之间：

```
策略信号 → [回撤 Protocol 门控] → 订单生成 → 执行层
                ↑
          净值监控 → 四级阈值评估 → Kill Switch 检查
```

**核心模块**：
- `DrawdownMonitor`：实时净值监控，计算当前回撤深度和持续时间
- `DrawdownLevelEvaluator`：四级阈值评估，输出当前回撤级别
- `KillSwitch`：紧急熔断，不可覆盖，fail-closed
- `RecoveryProtocol`：分阶段恢复，需人工授权
- `DailyCircuitBreaker`：日度熔断，防止单日极端亏损

### 3.2 四级回撤阈值落地算法

```python
from enum import IntEnum
from dataclasses import dataclass
from datetime import date
from typing import Optional

class DrawdownLevel(IntEnum):
    """四级回撤级别（30_multi_strategy_concurrency §2.5.1 行业基准）。"""
    NORMAL      = 0   # 回撤 < 8%
    WARNING     = 1   # 回撤 > 8%：降低新仓风险敞口至 75%
    REDUCING    = 2   # 回撤 > 15%：仓位缩减至 75%，停开新仓
    HALTED      = 3   # 回撤 > 20%：停所有新开仓，review
    LIQUIDATING = 4   # 回撤 > 25%：关闭所有仓位，强制休息

@dataclass
class DrawdownState:
    """回撤 Protocol 状态——每个 StrategyBook 独立维护一份，firm 层维护一份组合级。"""
    current_level: DrawdownLevel          # 当前回撤级别
    peak_nav: float                       # 历史峰值净值
    current_nav: float                    # 当前净值
    drawdown_pct: float                   # 当前回撤深度 (0.0 ~ 1.0)
    peak_drawdown: float                  # 历史最大回撤深度（用于恢复 50% 判定，如 0.20 = 曾回撤 20%）
    drawdown_duration_days: int           # 回撤持续天数（从 peak 到 now）
    peak_date: date                       # 峰值日期
    recovery_authorization: bool          # 是否有人工恢复授权
    forced_rest_until: Optional[date]     # 强制休息到期日（Level 4 触发后 5 交易日）
    daily_loss_pct: float                 # 当日已实现+浮亏百分比
    consecutive_loss_days: int            # 连续亏损天数


def compute_drawdown(nav_history: list[float]) -> tuple[float, float, date]:
    """计算回撤深度、峰值净值、峰值日期。

    口径（2026-08 定稿）：
    - 使用收盘净值（T+1 结算后的确认净值），不含日内浮盈浮亏
    - 分红除权日做前复权调整，避免虚假回撤
    - 峰值取历史最高收盘净值

    Returns: (drawdown_pct, peak_nav, peak_date)
    """
    if not nav_history:
        return 0.0, 0.0, date.today()

    peak_nav = nav_history[0]
    peak_idx = 0
    for i, nav in enumerate(nav_history):
        if nav > peak_nav:
            peak_nav = nav
            peak_idx = i

    current_nav = nav_history[-1]
    drawdown_pct = (peak_nav - current_nav) / peak_nav if peak_nav > 0 else 0.0
    return drawdown_pct, peak_nav, date.fromordinal(peak_idx + 1)  # 简化：实际从 trade_calendar 映射


def evaluate_drawdown_level(state: DrawdownState) -> DrawdownLevel:
    """四级阈值评估——根据当前回撤深度输出回撤级别。

    行业基准（30_multi_strategy_concurrency §2.5.1）：
    - Level 1 WARNING:  > 8%  → 降低新仓风险敞口至 75%
    - Level 2 REDUCING: > 15% → 仓位缩减至 75%，停开新仓
    - Level 3 HALTED:   > 20% → 停所有新开仓
    - Level 4 LIQUIDATING: > 25% → 清仓 + 强制休息 5 天

    强制休息期检查：Level 4 触发后 5 交易日内不允许任何交易，
    即使回撤已恢复也必须等强制休息到期。
    """
    # 强制休息期优先检查
    if state.forced_rest_until is not None:
        if date.today() < state.forced_rest_until:
            return DrawdownLevel.LIQUIDATING  # 强制休息期内仍标记为 LIQUIDATING

    # 更新历史最大回撤记录（用于 §3.4 恢复 50% 判定）
    if state.drawdown_pct > state.peak_drawdown:
        state.peak_drawdown = state.drawdown_pct

    dd = state.drawdown_pct

    if dd > 0.25:
        return DrawdownLevel.LIQUIDATING
    elif dd > 0.20:
        return DrawdownLevel.HALTED
    elif dd > 0.15:
        return DrawdownLevel.REDUCING
    elif dd > 0.08:
        return DrawdownLevel.WARNING
    else:
        return DrawdownLevel.NORMAL


def apply_drawdown_throttle(level: DrawdownLevel, base_risk_per_trade: float,
                            base_position_cap: float) -> tuple[float, float, bool]:
    """根据回撤级别输出风险节流参数。

    Returns: (adjusted_risk_per_trade, adjusted_position_cap, allow_new_positions)
    """
    if level == DrawdownLevel.NORMAL:
        return base_risk_per_trade, base_position_cap, True
    elif level == DrawdownLevel.WARNING:
        # Level 1: 单笔风险从 2% 降至 1.5%（75%）
        return base_risk_per_trade * 0.75, base_position_cap * 0.75, True
    elif level == DrawdownLevel.REDUCING:
        # Level 2: 仓位缩减至 75%，停开新仓（仅允许平仓和调仓）
        return base_risk_per_trade * 0.75, base_position_cap * 0.75, False
    elif level == DrawdownLevel.HALTED:
        # Level 3: 停所有新开仓
        return 0.0, base_position_cap * 0.5, False
    else:  # LIQUIDATING
        # Level 4: 清仓
        return 0.0, 0.0, False
```

### 3.3 Kill Switch 算法（不可覆盖，fail-closed）

```python
@dataclass
class KillSwitchTrigger:
    """Kill Switch 触发条件（30_multi_strategy_concurrency §2.5.5）。"""
    triggered: bool
    reason: str               # "daily_loss_6pct" / "drawdown_25pct" / "consecutive_5_loss" / "liquidity_crisis"
    action: str               # "flatten_all" / "halt_3d" / "reduce_50pct" / "stop_new_open"
    cooldown_days: int        # 触发后冷却天数


def kill_switch_check(state: DrawdownState, spread_multiple: float,
                      monitoring_alive: bool) -> KillSwitchTrigger:
    """Kill Switch 检查——每 tick 调用，fail-closed。

    原则（tradingwyckoff 2026-01 / FerroQuant 2026-04）：
    - 宁可错杀不可漏放
    - 触发即执行，不允许人工覆盖延迟
    - fail-closed：监控不可用时默认 halt

    2026-08 研究整合：
    - FerroQuant (2026-04): 5% portfolio drawdown = kill switch，信号引擎全部 halt
    - TradeShield (2026-08): 多层 drawdown defense，daily loss limit + trailing DD
    - FXMacroData (2026-05): kill switch stack = data brake + model brake + execution brake
      + portfolio brake + event brake；系统应 fail closed
    """
    # fail-closed：监控不可用 → 默认 halt
    if not monitoring_alive:
        return KillSwitchTrigger(
            triggered=True, reason="monitoring_down_fail_closed",
            action="halt_3d", cooldown_days=3
        )

    # 条件 1：单日亏损 > 6% → 立即平仓所有持仓，暂停交易 3 天
    if state.daily_loss_pct > 0.06:
        return KillSwitchTrigger(
            triggered=True, reason="daily_loss_6pct",
            action="flatten_all", cooldown_days=3
        )

    # 条件 2：回撤 > 25% → 清仓 + 强制休息 5 天 + 人工 review
    if state.drawdown_pct > 0.25:
        return KillSwitchTrigger(
            triggered=True, reason="drawdown_25pct",
            action="flatten_all", cooldown_days=5
        )

    # 条件 3：连续 5 天亏损 → 降仓至 50%，review 策略有效性
    if state.consecutive_loss_days >= 5:
        return KillSwitchTrigger(
            triggered=True, reason="consecutive_5_loss",
            action="reduce_50pct", cooldown_days=1
        )

    # 条件 4：流动性危机（买卖价差 > 正常 5x）→ 立即停止开仓，仅允许平仓
    if spread_multiple > 5.0:
        return KillSwitchTrigger(
            triggered=True, reason="liquidity_crisis",
            action="stop_new_open", cooldown_days=1
        )

    return KillSwitchTrigger(triggered=False, reason="", action="", cooldown_days=0)


def execute_kill_switch(trigger: KillSwitchTrigger, positions: dict[str, float],
                        allow_new_open: bool) -> dict:
    """Kill Switch 执行——不可覆盖，立即生效。

    架构保证：此函数的调用优先级高于一切策略信号。
    一旦触发，策略信号层被短路，直接进入执行层。
    """
    if not trigger.triggered:
        return {"action": "none", "positions": positions, "allow_new_open": allow_new_open}

    if trigger.action == "flatten_all":
        # 全部平仓——T+1 约束下只能挂卖单，不能立即成交
        return {
            "action": "flatten_all",
            "orders": {sym: -qty for sym, qty in positions.items() if qty > 0},
            "allow_new_open": False,
            "cooldown_until": trigger.cooldown_days,
        }
    elif trigger.action == "reduce_50pct":
        # 降仓至 50%
        return {
            "action": "reduce_50pct",
            "orders": {sym: -qty * 0.5 for sym, qty in positions.items() if qty > 0},
            "allow_new_open": False,
            "cooldown_until": trigger.cooldown_days,
        }
    elif trigger.action == "stop_new_open":
        # 停止开仓，仅允许平仓
        return {
            "action": "stop_new_open",
            "orders": {},
            "allow_new_open": False,
            "cooldown_until": trigger.cooldown_days,
        }
    else:  # halt_3d 或其他
        return {
            "action": "halt",
            "orders": {},
            "allow_new_open": False,
            "cooldown_until": trigger.cooldown_days,
        }
```

### 3.4 恢复协议算法（需人工授权）

```python
from datetime import timedelta

def check_recovery_conditions(state: DrawdownState,
                              trading_calendar: list[date]) -> tuple[bool, str]:
    """检查恢复条件是否满足（ARKA 2026: Recovery requires explicit re-authorization）。

    三阶段恢复（30_multi_strategy_concurrency §2.5.2）：
    - 回撤企稳：回撤从峰值恢复 50%（如从 -20% 回到 -10%）→ 解除停仓，风险敞口仍降 50%
    - 完全恢复：创新高（回撤归零）→ 恢复正常风险敞口
    - 强制休息期：Level 4 触发后 5 交易日不允许任何交易

    2026-08 研究整合：
    - Hsieh (2023, arXiv:2303.02613) drawdown modulation + restart 机制：
      当回撤接近预设限制时，policy 行为类似止损单；restart 机制在回撤恢复后
      重新启动交易，避免错过后续盈利机会。但 restart 须人工授权，不自动恢复。
    """
    # 强制休息期检查
    if state.forced_rest_until is not None:
        if date.today() < state.forced_rest_until:
            days_left = (state.forced_rest_until - date.today()).days
            return False, f"forced_rest_active_{days_left}d_left"

    # 创新高判定（完全恢复，恢复正常风险敞口）
    if state.current_nav >= state.peak_nav:
        return True, "full_recovery_new_high"

    # 回撤恢复 50% 判定——从峰值回撤恢复 50%（解除停仓，风险敞口仍降 50%）
    # 如峰值 100，回撤到 80（peak_drawdown=20%），恢复 50% 意味回到 90（当前 drawdown=10%）
    # 判定条件：当前回撤 < peak_drawdown * 0.5，且有人工授权
    if state.peak_drawdown > 0:
        recovery_threshold = state.peak_drawdown * 0.5
        if state.drawdown_pct < recovery_threshold and state.recovery_authorization:
            return True, (
                f"stabilized_50pct_recovery_dd_{state.drawdown_pct:.1%}"
                f"_vs_peak_{state.peak_drawdown:.1%}"
            )

    # 回撤企稳 fallback 判定（当前回撤 < 8% + 人工授权）
    if state.drawdown_pct < 0.08 and state.recovery_authorization:
        return True, "stabilized_with_authorization"

    return False, "conditions_not_met_or_no_authorization"


def recovery_protocol(state: DrawdownState, human_authorized: bool,
                      trading_calendar: list[date]) -> DrawdownState:
    """恢复协议——分阶段恢复，需人工授权。

    恢复不可跳级：LIQUIDATING → HALTED → REDUCING → WARNING → NORMAL
    每次升级一级，需要新的人工授权。
    """
    if not human_authorized:
        return state  # 无人工授权，不恢复

    can_recover, reason = check_recovery_conditions(state, trading_calendar)
    if not can_recover:
        return state  # 条件不满足，不恢复

    # 分阶段恢复：每次升级一级
    if state.current_level == DrawdownLevel.LIQUIDATING:
        state.current_level = DrawdownLevel.HALTED
        state.forced_rest_until = None  # 清除强制休息
    elif state.current_level == DrawdownLevel.HALTED:
        state.current_level = DrawdownLevel.REDUCING
    elif state.current_level == DrawdownLevel.REDUCING:
        state.current_level = DrawdownLevel.WARNING
    elif state.current_level == DrawdownLevel.WARNING:
        state.current_level = DrawdownLevel.NORMAL

    state.recovery_authorization = False  # 授权用完，下次恢复需重新授权
    return state
```

### 3.5 日度熔断算法

```python
def daily_circuit_breaker(portfolio_daily_loss_pct: float,
                          strategy_daily_loss_pct: dict[str, float],
                          max_portfolio_daily: float = 0.04,
                          max_strategy_daily: float = 0.05) -> dict:
    """日度熔断——防止单日极端亏损（30_multi_strategy_concurrency §2.5.1 补充）。

    - 组合单日亏损 > 4% → 暂停开仓 1 天
    - 单策略单日亏损 > 5% → 该策略暂停 1 天

    Returns: dict of {strategy_name: "paused"|"active"} + portfolio_paused: bool
    """
    result = {"portfolio_paused": False, "strategies": {}}

    # 组合熔断
    if portfolio_daily_loss_pct > max_portfolio_daily:
        result["portfolio_paused"] = True

    # 单策略熔断
    for strat, loss in strategy_daily_loss_pct.items():
        if loss > max_strategy_daily:
            result["strategies"][strat] = "paused"
        else:
            result["strategies"][strat] = "active"

    return result
```

### 3.6 单策略 vs 组合层面分层

```python
def layered_drawdown_control(
    strategy_states: dict[str, DrawdownState],   # 各策略独立回撤状态
    firm_state: DrawdownState,                    # firm 层组合回撤状态
    base_risk: float,
    base_cap: float,
) -> dict[str, tuple[float, float, bool]]:
    """分层回撤风控（30_multi_strategy_concurrency §2.5.3）。

    用户洞察："回撤深了是因为上一次交易没交易好，是策略的问题，不是市场的问题。"
    → 单策略回撤 = 策略问题 → 该策略独立收缩
    → 组合回撤 = 系统性问题 → 全局收缩（通过 Shrinkage 额外下调）

    两层独立计算，Shrinkage 叠加（取更严格者）。
    """
    # firm 层回撤节流
    firm_level = evaluate_drawdown_level(firm_state)
    firm_risk, firm_cap, firm_allow = apply_drawdown_throttle(firm_level, base_risk, base_cap)

    result = {}
    for strat_name, strat_state in strategy_states.items():
        # 单策略层回撤节流
        strat_level = evaluate_drawdown_level(strat_state)
        strat_risk, strat_cap, strat_allow = apply_drawdown_throttle(strat_level, base_risk, base_cap)

        # 叠加：取更严格者（min risk, min cap, AND allow_new）
        effective_risk = min(strat_risk, firm_risk)
        effective_cap = min(strat_cap, firm_cap)
        effective_allow = strat_allow and firm_allow

        result[strat_name] = (effective_risk, effective_cap, effective_allow)

    return result
```

### 3.7 回撤基准净值计算口径

| 因素 | 处理方式 | 理由 |
|---|---|---|
| **日内浮盈浮亏** | 不计入四级阈值判定，仅用于日度熔断 | T+1 结算前浮盈不可用，避免虚假回撤 |
| **收盘净值** | 四级阈值判定基准 | T+1 结算后的确认净值 |
| **分红除权** | 前复权调整 | 避免除权产生的虚假回撤 |
| **申赎资金流** | 调整后净值 = nav - 资金流入流出 | 避免资金流导致的虚假回撤 |
| **交易成本** | 已实现成本直接扣减净值 | 反映真实回撤 |

### 3.8 Decay-LORD FDR 自适应熔断（Phase 1.5+ 远期候选）

```python
def decay_lord_circuit_breaker(
    pnl_pvalues: list[float],       # 逐日 PnL 对应的 p-value 序列（越低越异常）
    alpha: float = 0.05,            # FDR 控制水平
    gamma: float = 0.95,            # 记忆衰减因子（越接近 1 记忆越长）
    delta: float = 0.01,            # 衰减下限（防止完全遗忘）
    lookback: int = 60,             # 回看窗口
) -> dict:
    """Decay-LORD FDR 自适应熔断——用记忆衰减 FDR 控制替代静态阈值。

    核心思想（quantbeckman.com 2025-04 / 2026-08 更新）：
    - 传统熔断用静态阈值（如 daily_loss > 6%），无法适应市场波动率变化
    - Decay-LORD 将 PnL 流转化为 p-value 序列，用 FDR 控制判断"异常"
    - 引入记忆衰减 γ^t：近期异常比远期异常更重要
    - FDR 控制的是"假阳性发现率"——避免在正常波动中误触发熔断

    公式：
    α_t = α · max(γ^t, 1-δ) + α · Σ_{j∈R_t} γ^{t-j}

    其中 R_t 是到时刻 t 为止的拒绝集（被判定为异常的时点）。

    与现有四级回撤的关系：
    - 四级回撤 = 已实现生存风险（事实驱动，MVP 必须保留）
    - Decay-LORD = 预测性异常检测（统计驱动，Phase 1.5+ 增强）
    - 两者正交：四级回撤管"已经亏了多少"，Decay-LORD 管"异常是否在加速"
    """
    n = len(pnl_pvalues)
    if n == 0:
        return {"trigger": False, "reason": "no_data"}

    # 步骤 1：计算衰减加权后的 FDR 阈值
    rejected_set = []  # R_t：被判定为异常的时点索引
    for t in range(n):
        # 衰减权重
        weight = max(gamma ** (n - 1 - t), 1 - delta)

        # 当前时刻的衰减累积 alpha 预算
        decayed_alpha = alpha * weight
        for j in rejected_set:
            decayed_alpha += alpha * (gamma ** (t - j))

        # BH-style 排序校正：p-value 排名 / 总数 × 衰减 alpha
        rank = sum(1 for p in pnl_pvalues[:t+1] if p <= pnl_pvalues[t])
        adjusted_threshold = decayed_alpha * rank / (t + 1)

        if pnl_pvalues[t] < adjusted_threshold:
            rejected_set.append(t)

    # 步骤 2：近 lookback 窗口内的异常密度 → 熔断判定
    recent_rejections = [t for t in rejected_set if t >= n - lookback]
    rejection_density = len(recent_rejections) / min(lookback, n)

    # 异常密度 > 30% → 触发自适应熔断
    trigger = rejection_density > 0.30

    return {
        "trigger": trigger,
        "rejection_density": rejection_density,
        "n_recent_rejections": len(recent_rejections),
        "lookback": lookback,
        "reason": f"decay_lord_density_{rejection_density:.1%}_in_{lookback}d"
                  if trigger else "normal",
        "phase": "Phase 1.5+",
        "note": "MVP 不启用——四级回撤+Kill Switch 已足够；Phase 1.5+ 积累 p-value 数据后评估",
    }


def pnl_to_pvalue(
    daily_pnl: float,
    pnl_history: list[float],
    window: int = 252,
) -> float:
    """将日 PnL 转化为 p-value——基于历史分布的经验 p-value。

    p-value = P(历史 PnL ≤ 当日 PnL)
    低 p-value = 当日 PnL 在历史分布左尾 = 异常亏损
    """
    if len(pnl_history) < window:
        return 0.5  # 数据不足时返回中性 p-value

    recent = pnl_history[-window:]
    rank = sum(1 for p in recent if p <= daily_pnl)
    return rank / len(recent)
```

### 3.9 现金底线（Cash Floor）三级防护（Phase 1.5+ 候选）

```python
# 三级现金底线阈值（r1000 框架对标，2026-08 整理）
CASH_FLOOR_LEVELS = {
    # 回撤阈值 → 最低现金占比（不可低于）
    0.08: 0.15,   # 回撤 > 8% → 现金 ≥ 15%
    0.15: 0.35,   # 回撤 > 15% → 现金 ≥ 35%
    0.25: 0.60,   # 回撤 > 25% → 现金 ≥ 60%
}


def enforce_cash_floor(
    drawdown_pct: float,
    current_cash_ratio: float,
    peak_nav: float,         # 用于权益驱动恢复判定
    current_nav: float,
) -> dict:
    """现金底线强制执行——回撤越深，强制持有的现金越多。

    与四级回撤的关系：
    - 四级回撤管"风险敞口节流"（降低单笔风险/仓位上限）
    - 现金底线管"最低现金缓冲"（确保有弹药应对追加保证金/赎回）
    - 两者互补：节流减少新风险，现金底线确保生存弹性

    权益驱动恢复（equity-based recovery hysteresis）：
    - 恢复判定基于权益（净值）而非时间
    - 净值恢复到 peak 的 95% 才解除现金底线
    - 避免在 V 型反弹中过早放松现金约束
    """
    # 确定当前应满足的现金底线
    required_cash_floor = 0.0
    for dd_threshold, cash_floor in sorted(CASH_FLOOR_LEVELS.items(), reverse=True):
        if drawdown_pct > dd_threshold:
            required_cash_floor = cash_floor
            break

    # 权益驱动恢复判定
    equity_ratio = current_nav / peak_nav if peak_nav > 0 else 1.0
    if equity_ratio >= 0.95 and required_cash_floor > 0:
        # 净值恢复到峰值的 95%，解除现金底线
        required_cash_floor = 0.0

    # 判定是否需要强制减仓以满足现金底线
    needs_rebalance = current_cash_ratio < required_cash_floor

    return {
        "required_cash_floor": required_cash_floor,
        "current_cash_ratio": current_cash_ratio,
        "needs_rebalance": needs_rebalance,
        "rebalance_amount": (required_cash_floor - current_cash_ratio) if needs_rebalance else 0.0,
        "equity_ratio": equity_ratio,
        "recovery_hysteresis": equity_ratio >= 0.95,
        "phase": "Phase 1.5+",
        "note": "MVP 不启用——四级回撤的 LIQUIDATING 级已含清仓；Phase 1.5+ 需精细现金管理时评估",
    }
```

## 4. 考虑过的替代方案

| 方案 | 描述 | 拒绝理由 |
|---|---|---|
| **自动恢复** | 回撤恢复到阈值以下自动恢复正常交易 | ARKA 2026 行业共识：Recovery requires explicit re-authorization；自动恢复可能导致在未充分企稳时激进建仓 |
| **单一全局回撤** | 只看 firm 层组合回撤，不看单策略 | 用户洞察：单策略回撤是策略问题，应独立收缩，不影响其他策略 |
| **VaR 替代回撤** | 用 VaR/ES 替代回撤作为主风控指标 | VaR/ES 是辅助监控（§2.5.4），回撤是生存底线，两者不可替代；VaR 有模型风险，回撤是已实现事实 |
| **连续回撤函数** | 用连续函数映射回撤深度到仓位，而非四级离散 | 四级离散阈值是行业基准（LedgerMind/ARKA/Sina），可解释性强，便于人工 review；连续函数过度工程 |
| **Hsieh restart 自动机制** | 完全采用 Hsieh (2023) 的 data-driven restart | Hsieh 的 restart 仍需人工授权（ARKA 共识），但其"回撤接近限制时 policy 行为类似止损单"的洞察已融入 Kill Switch 设计 |

## 5. 上限定义

| 上限 | 值 | 理由 |
|---|---|---|
| **最大可承受回撤** | 25%（Level 4 清仓线） | 行业基准：LedgerMind 2026-05；超过 25% 恢复需 33% 收益，心理和资金压力极大 |
| **单日最大亏损** | 6%（Kill Switch 线） | tradingwyckoff 2026-01；单日 6% 亏损意味着极端事件，需立即止损 |
| **连续亏损天数** | 5 天（降仓至 50%） | 防止策略在失效期持续亏损 |
| **强制休息期** | 5 交易日（Level 4 后） | ARKA 2026；强制冷静期，防止情绪化补仓 |
| **恢复路径** | 单向升级，每次一级，需授权 | 防止跳跃式恢复导致风险敞口骤增 |

**演进路径**：MVP 阶段使用静态四级阈值；Phase 1.5+ 在积累 6-12 个月实盘数据后，可考虑基于 Calmar ratio 的动态阈值调整（但四级框架不变，仅调整阈值数值）。

## 6. 待裁定

| 项 | 暂缓理由 | 重评条件 |
|---|---|---|
| **动态回撤阈值** | MVP 阶段使用行业静态基准 | 积累 6 个月实盘回撤数据后，基于 Calmar ratio 分布校准 |
| **Ulcer Index 监控** | Ulcer Index = √(Σ DD²/N)，衡量回撤"痛苦程度" | Phase 1.5+ 作为辅助指标加入监控面板 |
| **Hsieh modulation 系数** | Hsieh (2023) 的 drawdown modulation lemma 提供连续仓位调制 | 当前四级离散已足够；Phase 2+ 若需更平滑的仓位过渡可引入 |

## 7. 待定问题（讨论要点对齐）

- [x] ① 四级阈值（8/15/20/25%）落到 StrategyBook 内部的实现 spec → §3.2 `evaluate_drawdown_level` + `apply_drawdown_throttle`
- [x] ② 单策略 vs 组合层面分层（30_multi_strategy_concurrency §2.5.3）→ §3.6 `layered_drawdown_control`
- [x] ③ 恢复机制（企稳 50%/创新高/强制休息 5 天，§2.5.2）→ §3.4 `recovery_protocol`
- [x] ④ Kill Switch 触发条件与执行路径（§2.5.5）→ §3.3 `kill_switch_check` + `execute_kill_switch`
- [x] ⑤ 日度熔断（组合 -4%/单策略 -5%）→ §3.5 `daily_circuit_breaker`
- [x] ⑥ Kill Switch 不可覆盖原则 → §3.3 架构保证：Kill Switch 调用优先级高于一切策略信号
- [x] ⑦ 回撤基准净值计算口径 → §3.7 口径表
- [x] ⑧ 与 regime Shrinkage 的协同 → §3.6 两层独立计算，Shrinkage 叠加取更严格者

## 8. 引用

- [00_index_trading_decision](00_index_trading_decision.md) §3 G16
- [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §2.5（四级框架已定，必先读）
- [36_var_es_monitoring](36_var_es_monitoring.md)（G17，VaR/ES 辅助监控）
- [37_liquidity_crisis_protocol](37_liquidity_crisis_protocol.md)（G18，流动性危机 Kill Switch 联动）
- battle_map_09_risk_control（当前状态快照）
- **2026-08 研究引用**：
  - Hsieh (2023) "On Data-Driven Drawdown Control with Restart Mechanism in Trading" arXiv:2303.02613
  - FerroQuant (2026-04) "Risk Management in Automated Trading" — 5% kill switch fail-closed
  - TradeShield Protocol (2026-08) GitHub: PropGuard-Trailing-Equity-Armor — 多层 drawdown defense
  - FXMacroData (2026-05) "Kill Switch Framework For AI Bots" — kill switch stack, fail closed
  - tradingwyckoff (2026-01) "Drawdown in Trading: The Complete Guide" — Kill Switch Protocol
  - Villahermosa (2026-01) algostrategyanalyzer.com — Ulcer Index, Pain Table, recovery table
  - quantbeckman.com (2025-04/2026-08) "Risk Engine: Circuit Breaker" — Decay-LORD FDR 自适应熔断
  - r1000 框架 (2026-08 整理) — 三级现金底线 15%/35%/60% + 权益驱动恢复 hysteresis

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行：由 00_index G16 讨论要点占位 |
| 2026-08-10 | 1.0.0 | 落地 spec 定稿 | 四级回撤+Kill Switch+恢复协议+日度熔断+分层风控+净值口径全部算法化；整合 2026-08 研究（Hsieh restart/FerroQuant fail-closed/TradeShield 多层 defense） |
| 2026-08-10 | 1.1.0 | 恢复 50% 判定补全 | DrawdownState 新增 peak_drawdown 字段；evaluate_drawdown_level 更新历史最大回撤；check_recovery_conditions 实现"当前回撤 < peak_drawdown×0.5 + 人工授权"精确判定 |
| 2026-08-10 | 1.2.0 | 新增 Decay-LORD FDR 自适应熔断 + 现金底线三级防护 | §3.8 Decay-LORD FDR（quantbeckman.com 2025/2026）：记忆衰减 FDR 控制替代静态阈值，PnL→p-value→异常密度→熔断；§3.9 现金底线（r1000 框架对标）：三级现金底线 15%/35%/60% + 权益驱动恢复 hysteresis；两者均标注 Phase 1.5+ 候选 |
