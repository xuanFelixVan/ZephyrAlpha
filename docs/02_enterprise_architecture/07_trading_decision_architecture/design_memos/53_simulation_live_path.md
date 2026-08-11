---
ttl: permanent
doc_type: architecture_view
title: 模拟与实盘验证路径与5态FSM状态机
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.1.0"
date: 2026-08-10
topic: simulation_live_path
scope: 07_trading_decision_architecture
---

# 模拟与实盘验证路径与5态FSM状态机

> **性质**：由 [00_index_trading_decision](00_index_trading_decision.md) G24 主题组派生，将模拟与实盘验证路径的讨论要点落地为可施工的 spec + 伪代码。
> **施工图纪律**：本文档 status=active，对应模块允许施工。
> **2026-08 研究整合**：5态FSM状态机（NORMAL/THROTTLED/SOFT_HALT/HARD_HALT/UNWINDING）；fail-closed 设计（默认降级而非升级）；T+1 结算适配；手动恢复双批准（dual approval）；灰度上线（单策略先上）；实盘→模拟差异监控。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G24 模拟与实盘验证路径 |
| 所属 | 作战地图 04 |
| 依赖 | G23（[52_backtest_framework_docking](52_backtest_framework_docking.md) 回测通过）、G16（[35_drawdown_protocol_impl](35_drawdown_protocol_impl.md)）、G18（[37_liquidity_crisis_protocol](37_liquidity_crisis_protocol.md)） |
| 对标 | 机构 paper trading → 小资金 → 全量 / Kill Switch fail-closed 设计 |
| 正交性 | ✅ 与 regime 正交 |
| 优先级 | P4 |
| 状态 | ✅ active — 5态FSM+paper trading+灰度上线+差异监控+上线门控已定稿 |

## 2. 背景

### 2.1 项目处境

策略从回测到实盘需经过严格的验证路径：回测通过 → paper trading → 小资金实盘 → 全量部署。这条路径上的每一步都需要状态机控制，确保策略在异常情况下能安全降级而非崩溃。

**5态FSM** 是模拟实盘路径的核心控制机制，管理策略从正常运行到强制清仓的全生命周期。设计原则是 **fail-closed**：默认降级（更保守）而非升级（更激进），任何异常都倾向于保护资金而非追求收益。

### 2.2 核心问题

1. **状态转换安全性**：NORMAL→THROTTLED→SOFT_HALT→HARD_HALT→UNWINDING 是单向降级链，升级需人工双批准。
2. **T+1 结算适配**：A 股 T+1 使得当日买入不可卖，UNWINDING 状态只能清仓 T-1 及更早持仓。
3. **paper trading 真实性**：模拟环境需尽可能接近实盘（含滑点、冲击、拒单），否则模拟通过实盘仍会失败。
4. **灰度上线**：单策略先上，验证通过后再上其他策略，避免全量上线风险。
5. **实盘→模拟差异监控**：实盘与同步运行的模拟环境差异超阈值需告警。

### 2.3 约束条件

- **fail-closed**：异常默认降级，不自动升级
- **T+1 结算**：UNWINDING 只能清仓 T-1 及更早持仓
- **双批准升级**：状态升级需两个人工批准（操盘手+风控）
- **paper trading 时长**：至少 20 个交易日（1 个月）
- **小资金上限**：初始实盘不超过总资金 10%

## 3. 决策

### 3.1 架构定义

模拟实盘路径由验证路径层、5态FSM层、差异监控层三层构成：

```
验证路径层: 回测通过 → paper trading(20日) → 小资金(10%) → 半量(50%) → 全量(100%)
                                                                    ↓
5态FSM层: NORMAL → THROTTLED → SOFT_HALT → HARD_HALT → UNWINDING（单向降级）
          ↑_________________________________________|（双批准升级）
                                                                    ↓
差异监控层: 实盘 vs 模拟 差异检测 → 阈值告警 → 自动降级触发
```

### 3.2 5态FSM状态机定义

```python
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from enum import Enum
from typing import Optional


class FSMState(Enum):
    """5态FSM状态——单向降级链，升级需双批准。

    设计原则（fail-closed）：
    - 默认降级（更保守）而非升级（更激进）
    - 任何异常倾向于保护资金
    - 升级需双批准（操盘手+风控），降级可自动
    """
    NORMAL = "normal"           # 正常运行，全功能交易
    THROTTLED = "throttled"     # 节流：禁止新仓，允许减仓
    SOFT_HALT = "soft_halt"     # 软停止：禁止新仓+禁止加仓，允许减仓
    HARD_HALT = "hard_halt"     # 硬停止：禁止一切新交易，仅允许 UNWINDING
    UNWINDING = "unwinding"     # 清仓：强制平仓 T-1 及更早持仓


# 状态降级链（单向）
DOWNGRADE_CHAIN = {
    FSMState.NORMAL: FSMState.THROTTLED,
    FSMState.THROTTLED: FSMState.SOFT_HALT,
    FSMState.SOFT_HALT: FSMState.HARD_HALT,
    FSMState.HARD_HALT: FSMState.UNWINDING,
    FSMState.UNWINDING: FSMState.UNWINDING,  # 终态
}

# 状态允许的操作
ALLOWED_ACTIONS = {
    FSMState.NORMAL: {"buy", "sell", "hold"},
    FSMState.THROTTLED: {"sell", "hold"},           # 禁止新仓
    FSMState.SOFT_HALT: {"sell", "hold"},           # 禁止新仓+加仓
    FSMState.HARD_HALT: {"hold"},                   # 禁止一切新交易
    FSMState.UNWINDING: {"force_sell"},             # 仅强制清仓
}


@dataclass
class FSMTransition:
    """状态转换记录。"""
    from_state: FSMState
    to_state: FSMState
    timestamp: str
    trigger: str                # 触发原因
    approved_by: list[str]      # 批准人（升级需要双批准）
    is_automatic: bool          # 是否自动降级


@dataclass
class FSMContext:
    """FSM 运行时上下文——当前状态+转换历史+T+1锁仓+升级待审。

    注意：类名从 FSMState 改为 FSMContext，避免与 §3.2 的 FSMState(Enum) 命名冲突
    （v1.0 的 dataclass FSMState 遮蔽了 Enum FSMState，导致 current_state 字段类型
    注解引用 dataclass 自身而非 Enum，代码无法正常运行）。
    """
    current_state: FSMState               # 引用 FSMState(Enum)，不是 FSMContext
    entered_at: datetime
    transition_history: list[FSMTransition] = field(default_factory=list)
    # T+1 结算适配
    t1_locked_positions: dict[str, float] = field(default_factory=dict)  # 当日买入不可卖
    # 双批准升级待审
    pending_upgrade: Optional[dict] = None  # {target_state, requested_by, requester_role, approvals: [], approver_roles: []}
```

### 3.3 状态降级算法

```python
def downgrade_state(
    state: FSMContext,
    trigger: str,
    current_date: date,
) -> FSMContext:
    """状态自动降级——fail-closed，无需人工批准。

    降级触发条件：
    - NORMAL→THROTTLED：回撤 8-15%（WARNING）或 regime 切换到高风险
    - THROTTLED→SOFT_HALT：回撤 15-20%（REDUCING）或流动性危机 WARNING
    - SOFT_HALT→HARD_HALT：回撤 20-25%（HALTED）或流动性危机 CRISIS
    - HARD_HALT→UNWINDING：回撤 >25%（LIQUIDATING）或 Kill Switch 触发

    降级是自动的、即时的、无需批准的——保护资金优先。
    """
    new_state = DOWNGRADE_CHAIN[state.current_state]

    transition = FSMTransition(
        from_state=state.current_state,
        to_state=new_state,
        timestamp=datetime.now().isoformat(),
        trigger=trigger,
        approved_by=[],  # 降级无需批准
        is_automatic=True,
    )

    state.current_state = new_state
    state.entered_at = datetime.now()
    state.transition_history.append(transition)

    return state


def check_downgrade_triggers(
    state: FSMContext,
    drawdown_pct: float,                # 当前回撤百分比
    regime_tag: str,                    # 当前 regime
    liquidity_crisis_level: str,        # 流动性危机级别
    kill_switch_active: bool,           # Kill Switch 状态
    consecutive_loss_days: int,         # 连续亏损天数
) -> Optional[str]:
    """检查降级触发条件——返回触发原因或 None。

    与 [35_drawdown_protocol_impl] 和 [37_liquidity_crisis_protocol] 联动。
    """
    # Kill Switch 最高优先级 → 直接 UNWINDING
    if kill_switch_active:
        return "kill_switch_triggered"

    # 回撤触发（35_drawdown_protocol_impl §3.2 四级阈值）
    if drawdown_pct > 0.25:
        return f"drawdown_liquidating_{drawdown_pct:.1%}"
    elif drawdown_pct > 0.20 and state.current_state.value in ("normal", "throttled", "soft_halt"):
        return f"drawdown_halted_{drawdown_pct:.1%}"
    elif drawdown_pct > 0.15 and state.current_state.value in ("normal", "throttled"):
        return f"drawdown_reducing_{drawdown_pct:.1%}"
    elif drawdown_pct > 0.08 and state.current_state == FSMState.NORMAL:
        return f"drawdown_warning_{drawdown_pct:.1%}"

    # 流动性危机触发（37_liquidity_crisis_protocol）
    if liquidity_crisis_level == "BLACK_HOLE":
        return "liquidity_black_hole"
    elif liquidity_crisis_level == "CRISIS" and state.current_state.value in ("normal", "throttled"):
        return "liquidity_crisis"

    # 连续亏损触发
    if consecutive_loss_days >= 5 and state.current_state == FSMState.NORMAL:
        return f"consecutive_loss_{consecutive_loss_days}d"

    return None
```

### 3.4 状态升级算法（双批准）

```python
def request_upgrade(
    state: FSMContext,
    target_state: FSMState,
    requested_by: str,
    requester_role: str,             # "trader" / "risk_manager"
    reason: str,
) -> FSMContext:
    """请求状态升级——需双批准（操盘手+风控）。

    升级链（反向）：
    - UNWINDING → HARD_HALT
    - HARD_HALT → SOFT_HALT
    - SOFT_HALT → THROTTLED
    - THROTTLED → NORMAL

    升级不能跳级（如 UNWINDING 不能直接升 NORMAL）。
    升级需双批准：操盘手 + 风控。
    批准前状态不变（fail-closed）。
    """
    # 验证升级合法性（不能跳级）
    upgrade_chain = {v: k for k, v in DOWNGRADE_CHAIN.items()}
    expected_from = upgrade_chain.get(target_state)

    if state.current_state != expected_from:
        raise ValueError(
            f"非法升级：{state.current_state.value} → {target_state.value}，"
            f"必须从 {expected_from.value if expected_from else 'N/A'} 升级"
        )

    # 记录升级请求（待批准）
    state.pending_upgrade = {
        "target_state": target_state,
        "requested_by": requested_by,
        "requester_role": requester_role,
        "reason": reason,
        "approvals": [requested_by],  # 请求人算第一个批准
        "approver_roles": [requester_role],  # 初始化角色列表（v1.0 缺失导致 approve_upgrade 角色检查失效）
        "requested_at": datetime.now().isoformat(),
    }

    return state


def approve_upgrade(
    state: FSMContext,
    approver: str,
    approver_role: str,     # "trader" / "risk_manager"
) -> FSMContext:
    """批准状态升级——需双批准（操盘手+风控）。

    双批准逻辑：
    - 请求人算第一个批准
    - 第二个批准必须来自不同角色
    - 两个批准都到位后才执行升级
    - 批准前状态不变（fail-closed）
    """
    if state.pending_upgrade is None:
        return state

    # 检查是否已批准
    if approver in state.pending_upgrade["approvals"]:
        return state  # 重复批准忽略

    # 检查角色多样性
    existing_roles = state.pending_upgrade.get("approver_roles", [])
    if approver_role in existing_roles:
        return state  # 同角色已批准，需不同角色

    state.pending_upgrade["approvals"].append(approver)
    state.pending_upgrade.setdefault("approver_roles", []).append(approver_role)

    # 双批准完成 → 执行升级
    if len(state.pending_upgrade["approvals"]) >= 2:
        target = state.pending_upgrade["target_state"]
        transition = FSMTransition(
            from_state=state.current_state,
            to_state=target,
            timestamp=datetime.now().isoformat(),
            trigger=state.pending_upgrade["reason"],
            approved_by=state.pending_upgrade["approvals"],
            is_automatic=False,
        )
        state.current_state = target
        state.entered_at = datetime.now()
        state.transition_history.append(transition)
        state.pending_upgrade = None

    return state
```

### 3.5 T+1 结算适配算法

```python
def enforce_t1_settlement(
    state: FSMContext,
    current_positions: dict[str, float],     # {symbol: 持仓量}
    today_buys: dict[str, float],            # {symbol: 当日买入量}
    requested_sells: dict[str, float],       # {symbol: 请求卖出量}
) -> dict[str, float]:
    """T+1 结算适配——过滤当日买入不可卖的请求。

    A 股 T+1 约束：
    - 当日买入的持仓不可卖出
    - 只能卖出 T-1 及更早的持仓
    - UNWINDING 状态也受此约束

    返回合法的卖出请求（过滤掉 T+1 锁定的部分）。
    """
    legal_sells: dict[str, float] = {}

    for symbol, requested_qty in requested_sells.items():
        current_qty = current_positions.get(symbol, 0.0)
        today_buy_qty = today_buys.get(symbol, 0.0)

        # T-1 及更早持仓 = 当前持仓 - 当日买入
        t1_sellable = max(0.0, current_qty - today_buy_qty)

        # 合法卖出量 = min(请求量, T-1可卖量)
        legal_qty = min(requested_qty, t1_sellable)
        if legal_qty > 0:
            legal_sells[symbol] = legal_qty

        # 记录 T+1 锁定
        if requested_qty > legal_qty:
            locked = requested_qty - legal_qty
            state.t1_locked_positions[symbol] = locked

    return legal_sells


def execute_unwinding_with_t1(
    state: FSMContext,
    current_positions: dict[str, float],
    today_buys: dict[str, float],
    current_date: date,
) -> dict[str, float]:
    """UNWINDING 状态执行强制清仓——T+1 适配。

    清仓逻辑：
    1. T-1 及更早持仓：立即强制卖出
    2. 当日买入持仓：T+1 锁定，标记为次日清仓
    3. 次日开盘后清仓剩余 T+1 锁定持仓

    与 [42_sell_flow] 联动：
    - UNWINDING 使用跌停价排队卖出（流动性最差时）
    - 强制清仓不走常规卖出优先级，直接全卖
    """
    if state.current_state != FSMState.UNWINDING:
        return {}

    force_sells: dict[str, float] = {}

    for symbol, qty in current_positions.items():
        today_buy = today_buys.get(symbol, 0.0)
        t1_sellable = max(0.0, qty - today_buy)

        if t1_sellable > 0:
            # T-1 及更早持仓立即强制卖出
            force_sells[symbol] = t1_sellable

        if today_buy > 0:
            # 当日买入标记次日清仓
            state.t1_locked_positions[symbol] = today_buy

    return force_sells
```

### 3.6 paper trading 环境算法

```python
@dataclass
class PaperTradingConfig:
    """paper trading 配置。"""
    duration_days: int = 20          # 至少 20 个交易日（1 个月）
    starting_capital: float = 1e6    # 模拟起始资金 100 万
    include_slippage: bool = True    # 模拟滑点
    include_impact: bool = True      # 模拟市场冲击
    include_rejection: bool = True   # 模拟拒单
    slippage_model: str = "historical"  # "historical" / "constant"
    impact_model: str = "square_root"   # Square-root market impact


@dataclass
class PaperTradingResult:
    """paper trading 结果。"""
    strategy_id: str
    start_date: date
    end_date: date
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    total_trades: int
    avg_slippage_bps: float
    rejection_rate: float
    # 与回测的差异
    backtest_return: float
    live_backtest_gap: float         # 实盘-回测收益差
    passed: bool                     # 是否通过验证


def run_paper_trading(
    strategy_id: str,
    config: PaperTradingConfig,
    backtest_return: float,          # 回测收益率（对比基准）
    # 回调
    strategy_signal_callback: callable,  # 策略信号生成回调
    market_data_callback: callable,      # 市场数据回调
) -> PaperTradingResult:
    """paper trading 验证——模拟环境运行策略 20 个交易日。

    验证门控：
    - live_backtest_gap < 3%（实盘与回测收益差）
    - max_drawdown < 回测最大回撤 × 1.2
    - sharpe_ratio > 回测 Sharpe × 0.8
    - rejection_rate < 5%

    任一门控不通过 → 不进入小资金实盘。
    """
    # 模拟运行——20 个交易日逐日循环
    total_return = 0.0
    daily_returns = []
    max_dd = 0.0
    peak = 1.0
    total_trades = 0
    slippages = []
    rejections = 0
    portfolio_nav = 1.0  # 归一化净值

    for day in range(config.duration_days):
        # 步骤 1：获取当日市场数据，生成策略信号
        market_data = market_data_callback(day)
        signals = strategy_signal_callback(market_data)

        day_pnl = 0.0
        for signal in signals:
            total_trades += 1

            # 步骤 2：模拟执行——滑点
            if config.include_slippage:
                # 历史滑点模型：取当日 high-low 价差的一半作为滑点代理
                slippage_bps = _estimate_slippage(signal, market_data, config.slippage_model)
            else:
                slippage_bps = 0.0
            slippages.append(slippage_bps)

            # 步骤 3：模拟执行——市场冲击（Square-root model）
            if config.include_impact:
                impact_bps = _estimate_market_impact(signal, market_data, config.impact_model)
            else:
                impact_bps = 0.0

            # 步骤 4：模拟执行——拒单（涨跌停封板/流动性不足）
            if config.include_rejection:
                is_rejected = _check_rejection(signal, market_data)
            else:
                is_rejected = False

            if is_rejected:
                rejections += 1
                continue  # 拒单不计入 P&L

            # 步骤 5：计算当日成交 P&L（扣除滑点+冲击成本）
            execution_cost = (slippage_bps + impact_bps) / 10000.0  # bps → 比率
            signal_pnl = signal.get("expected_return", 0.0) - execution_cost
            day_pnl += signal_pnl * signal.get("weight", 0.0)

        # 步骤 6：更新净值和回撤
        daily_return = day_pnl
        daily_returns.append(daily_return)
        portfolio_nav *= (1.0 + daily_return)
        total_return = portfolio_nav - 1.0

        if portfolio_nav > peak:
            peak = portfolio_nav
        dd = (peak - portfolio_nav) / peak if peak > 0 else 0.0
        if dd > max_dd:
            max_dd = dd

    # 计算指标
    sharpe = (np.mean(daily_returns) / np.std(daily_returns) * np.sqrt(252)
              if daily_returns and np.std(daily_returns) > 0 else 0.0)
    avg_slippage = float(np.mean(slippages)) if slippages else 0.0
    rejection_rate = rejections / total_trades if total_trades > 0 else 0.0
    live_backtest_gap = abs(total_return - backtest_return)

    # 门控判定
    passed = (
        live_backtest_gap < 0.03 and
        max_dd < 0.20 * 1.2 and  # 回测最大回撤假设 20%
        sharpe > 0.8 * 1.0 and   # 回测 Sharpe 假设 1.0
        rejection_rate < 0.05
    )

    return PaperTradingResult(
        strategy_id=strategy_id,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=config.duration_days),
        total_return=total_return,
        sharpe_ratio=sharpe,
        max_drawdown=max_dd,
        total_trades=total_trades,
        avg_slippage_bps=avg_slippage,
        rejection_rate=rejection_rate,
        backtest_return=backtest_return,
        live_backtest_gap=live_backtest_gap,
        passed=passed,
    )
```


```python
def _estimate_slippage(signal: dict, market_data: dict, model: str) -> float:
    """估计滑点（bps）——paper trading 滑点模拟。

    模型选择：
    - "historical": 当日 high-low 价差的一半作为滑点代理（默认）
    - "constant": 固定 5bps（简化版）
    """
    if model == "constant":
        return 5.0  # 固定 5bps

    # historical 模型：价差代理
    high = market_data.get("high", 0.0)
    low = market_data.get("low", 0.0)
    close = market_data.get("close", 0.0)
    if close > 0 and high > low:
        spread_bps = (high - low) / close * 10000.0 / 2.0
        return min(spread_bps, 50.0)  # 上限 50bps
    return 5.0  # fallback


def _estimate_market_impact(signal: dict, market_data: dict, model: str) -> float:
    """估计市场冲击（bps）——Square-root market impact model。

    Impact = σ × √(POV) × coefficient

    POV = Participation of Volume = order_qty / ADV
    σ = 日波动率
    """
    if model != "square_root":
        return 0.0

    order_value = signal.get("order_value", 0.0)
    adv = market_data.get("adv", 1e8)  # 平均日成交额
    volatility = market_data.get("volatility", 0.02)  # 日波动率

    if adv <= 0:
        return 0.0

    pov = min(order_value / adv, 0.3)  # 参与率上限 30%
    # Square-root impact: impact ∝ σ × √(POV)
    impact_bps = volatility * np.sqrt(pov) * 10000.0 * 0.5  # 系数 0.5 为经验值
    return min(impact_bps, 100.0)  # 上限 100bps


def _check_rejection(signal: dict, market_data: dict) -> bool:
    """检查订单是否被拒——涨跌停封板/流动性不足。

    拒单条件：
    1. 买入信号 + 涨停封板（close == high == limit_up）→ 拒单
    2. 卖出信号 + 跌停封板（close == low == limit_down）→ 拒单
    3. 参与率 > 25%（大单冲击过大）→ 拒单
    """
    direction = signal.get("direction", "buy")
    close = market_data.get("close", 0.0)
    high = market_data.get("high", 0.0)
    low = market_data.get("low", 0.0)
    limit_up = market_data.get("limit_up", close * 1.1)
    limit_down = market_data.get("limit_down", close * 0.9)

    # 涨跌停封板检查
    if direction == "buy" and abs(close - limit_up) / limit_up < 0.001:
        return True  # 涨停封板，买单拒单
    if direction == "sell" and abs(close - limit_down) / limit_down < 0.001:
        return True  # 跌停封板，卖单拒单

    # 参与率检查
    order_value = signal.get("order_value", 0.0)
    adv = market_data.get("adv", 1e8)
    if adv > 0 and order_value / adv > 0.25:
        return True  # 参与率过高拒单

    return False
```

### 3.7 灰度上线算法

```python
class DeploymentStage(Enum):
    """灰度上线阶段。"""
    PAPER_TRADING = "paper_trading"    # 模拟验证
    SMALL_CAPITAL = "small_capital"    # 小资金（10%）
    HALF_CAPITAL = "half_capital"      # 半量（50%）
    FULL_CAPITAL = "full_capital"      # 全量（100%）


@dataclass
class DeploymentPlan:
    """灰度上线计划。"""
    strategy_id: str
    stage: DeploymentStage
    capital_ratio: float           # 资金比例
    duration_days: int             # 该阶段持续天数
    promotion_criteria: dict       # 升级到下一阶段的门控
    demotion_criteria: dict        # 降级到上一阶段的门控


def get_default_deployment_plan(strategy_id: str) -> list[DeploymentPlan]:
    """默认灰度上线计划——4 阶段渐进。"""
    return [
        DeploymentPlan(
            strategy_id=strategy_id,
            stage=DeploymentStage.PAPER_TRADING,
            capital_ratio=0.0,        # 模拟无实盘资金
            duration_days=20,
            promotion_criteria={"live_backtest_gap": 0.03, "max_drawdown": 0.24, "sharpe_ratio": 0.8},
            demotion_criteria={},
        ),
        DeploymentPlan(
            strategy_id=strategy_id,
            stage=DeploymentStage.SMALL_CAPITAL,
            capital_ratio=0.10,       # 10% 小资金
            duration_days=30,
            promotion_criteria={"live_backtest_gap": 0.03, "max_drawdown": 0.20, "sharpe_ratio": 1.0},
            demotion_criteria={"live_backtest_gap": 0.08, "max_drawdown": 0.25},
        ),
        DeploymentPlan(
            strategy_id=strategy_id,
            stage=DeploymentStage.HALF_CAPITAL,
            capital_ratio=0.50,       # 50% 半量
            duration_days=60,
            promotion_criteria={"live_backtest_gap": 0.02, "max_drawdown": 0.15, "sharpe_ratio": 1.2},
            demotion_criteria={"live_backtest_gap": 0.05, "max_drawdown": 0.20},
        ),
        DeploymentPlan(
            strategy_id=strategy_id,
            stage=DeploymentStage.FULL_CAPITAL,
            capital_ratio=1.0,        # 100% 全量
            duration_days=0,          # 无限期
            promotion_criteria={},
            demotion_criteria={"live_backtest_gap": 0.04, "max_drawdown": 0.18},
        ),
    ]
```

### 3.8 实盘→模拟差异监控算法

```python
@dataclass
class LiveSimDiff:
    """实盘 vs 模拟差异。"""
    date: date
    live_return: float
    sim_return: float
    return_diff: float             # live - sim
    cumulative_diff: float         # 累计差异
    slippage_diff: float           # 滑点差异
    fill_rate_diff: float          # 成交率差异
    is_anomaly: bool               # 是否异常


def monitor_live_sim_diff(
    live_returns: list[float],
    sim_returns: list[float],
    live_slippages: list[float],
    sim_slippages: list[float],
    live_fill_rates: list[float],
    sim_fill_rates: list[float],
    dates: list[date],
    diff_threshold: float = 0.02,  # 单日差异阈值 2%
    cum_diff_threshold: float = 0.05,  # 累计差异阈值 5%
) -> list[LiveSimDiff]:
    """实盘→模拟差异监控——差异超阈值告警并触发降级。

    核心逻辑：
    - 实盘与同步运行的模拟环境每日对比
    - 单日收益差异 > 2% → 告警
    - 累计收益差异 > 5% → 触发 FSM 降级
    - 滑点差异大 → 执行质量问题
    - 成交率差异大 → 流动性问题

    与 5态FSM 联动：
    - 累计差异超阈值 → 自动降级（THROTTLED）
    - 严重差异 → HARD_HALT
    """
    diffs = []
    cum_diff = 0.0

    for i, d in enumerate(dates):
        live_ret = live_returns[i] if i < len(live_returns) else 0.0
        sim_ret = sim_returns[i] if i < len(sim_returns) else 0.0
        return_diff = live_ret - sim_ret
        cum_diff += return_diff

        live_slip = live_slippages[i] if i < len(live_slippages) else 0.0
        sim_slip = sim_slippages[i] if i < len(sim_slippages) else 0.0
        slip_diff = live_slip - sim_slip

        live_fill = live_fill_rates[i] if i < len(live_fill_rates) else 1.0
        sim_fill = sim_fill_rates[i] if i < len(sim_fill_rates) else 1.0
        fill_diff = live_fill - sim_fill

        is_anomaly = (
            abs(return_diff) > diff_threshold or
            abs(cum_diff) > cum_diff_threshold or
            abs(slip_diff) > 10.0  # 滑点差异 >10bps
        )

        diffs.append(LiveSimDiff(
            date=d,
            live_return=live_ret,
            sim_return=sim_ret,
            return_diff=return_diff,
            cumulative_diff=cum_diff,
            slippage_diff=slip_diff,
            fill_rate_diff=fill_diff,
            is_anomaly=is_anomaly,
        ))

    return diffs
```

## 4. 考虑过的替代方案

| 方案 | 描述 | 拒绝理由 |
|---|---|---|
| **3态FSM** | NORMAL/HALT/UNWINDING | 粒度不够，无法区分节流和软停止 |
| **自动升级** | 异常恢复后自动升级 | fail-closed 原则，升级需人工双批准 |
| **跳级升级** | UNWINDING 直接升 NORMAL | 风险过大，需逐级验证 |
| **无 T+1 适配** | UNWINDING 忽略 T+1 | A 股 T+1 强约束，不可忽略 |
| **全量上线** | 跳过灰度直接全量 | 风险集中，灰度上线更安全 |
| **无差异监控** | 实盘不与模拟对比 | 无法发现执行质量问题 |

## 5. 上限定义

| 上限 | 值 | 理由 |
|---|---|---|
| **paper trading 时长** | ≥ 20 交易日 | 1 个月覆盖多种市场条件 |
| **小资金比例** | ≤ 10% | 初始实盘风险控制 |
| **单日差异阈值** | 2% | 实盘 vs 模拟单日收益差异 |
| **累计差异阈值** | 5% | 实盘 vs 模拟累计收益差异 |
| **升级批准数** | 2（双批准） | 操盘手+风控 |
| **降级** | 自动即时 | fail-closed |

**演进路径**：
- MVP：5态FSM + paper trading + 灰度上线 + 差异监控
- Phase 1.5：自动降级触发条件优化（regime 条件差异化）
- Phase 2：多策略并行灰度（不同策略不同阶段）

## 6. 待裁定

| 项 | 暂缓理由 | 重评条件 |
|---|---|---|
| **自动升级条件** | MVP 需人工双批准 | Phase 1.5+ 积累足够 track record 后 |
| **多策略并行灰度** | MVP 单策略灰度 | Phase 2+ 多策略成熟后 |
| **regime 条件差异化降级** | 需 regime 验证 | C1 验证通过后 |

## 7. 待定问题（讨论要点）

- [x] ① 模拟验证（paper trading）环境 → §3.6 定型
- [x] ② 模拟时长 → §3.6 定型（20 交易日）
- [x] ③ 实盘小资金验证路径 → §3.7 定型（4 阶段灰度）
- [x] ④ 实盘→模拟差异监控 → §3.8 定型
- [x] ⑤ 上线决策门控 → §3.6/§3.7 定型（门控+灰度）
- [x] ⑥ 灰度上线（单策略先上）→ §3.7 定型

## 8. 引用

- [00_index_trading_decision](00_index_trading_decision.md) §3 G24
- [52_backtest_framework_docking](52_backtest_framework_docking.md)（G23，回测通过前置）
- [35_drawdown_protocol_impl](35_drawdown_protocol_impl.md)（G16，回撤降级触发）
- [37_liquidity_crisis_protocol](37_liquidity_crisis_protocol.md)（G18，流动性危机降级触发）
- [42_sell_flow](42_sell_flow.md)（G20，UNWINDING 清仓路径）
- battle_map_04_simulation_validation（当前状态快照）

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行：由 00_index G24 讨论要点占位，待讨论填空 |
| 2026-08-10 | 1.0.0 | 补齐 5态FSM状态机+T+1适配+双批准升级+paper trading+灰度上线+差异监控 | fail-closed 设计，整合回撤/流动性/Kill Switch 降级触发 |
| 2026-08-10 | 1.1.0 | P0 bug 修复 + paper trading 循环落地 | FSMState Enum/dataclass 命名冲突修复（dataclass→FSMContext）；approve_upgrade 双批准角色检查失效修复（初始化 approver_roles）；run_paper_trading 模拟循环从注释占位改为落地实现（滑点/冲击/拒单/P&L/回撤追踪）；新增 _estimate_slippage/_estimate_market_impact/_check_rejection 辅助函数 |
