---
ttl: permanent
doc_type: architecture_view
title: 对账归因与TCA 2.0执行质量分析
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.2.0"
date: 2026-08-10
topic: reconciliation_attribution
scope: 07_trading_decision_architecture
---

# 对账归因与TCA 2.0执行质量分析

> **性质**：由 [00_index_trading_decision](00_index_trading_decision.md) G25 主题组派生，将对账归因的讨论要点落地为可施工的 spec + 伪代码。
> **施工图纪律**：本文档 status=active，对应模块允许施工。
> **2026-08 研究整合**：Brinson 3 因子归因（Allocation/Selection/Interaction）+ Carino 多期链接；T+1 结算适配（已实现/未实现选股效应分离）；TCA 2.0 滑点分布（Drovix 2026-05-27：median/p90/p99 + 信令成本 30min post-trade + 拒单成本 bps）；finantrix TCA 2.0（2026-08-08：pre-trade/intraday/post-trade 三阶段复用成本模型 + Algo Wheel 选择即优化问题 + 强化学习进入执行）；五分量执行成本拆解（spread/impact_temp/impact_perm/timing/opportunity/signalling/rejection）；Quod Financial 2026-06-09 三阶段 TCA 完整循环（square-root pre-trade 估计 + intraday 实时偏离监控）；OrderX 2026-07-09 reversion marks 诊断（T+5min/T+30min 区分 alpha vs impact）+ selection bias KS 检验；quant67 2026-05-01 IS 归因按 7 维度 group by 分解（策略/经纪商/算法/时段/品种/流动性/订单大小桶）。**v1.2.0 新增**：市场冲击模型族（Kissell-Glantz I-Star 临时/永久冲击闭式分离 + Bouchaud Propagator 时间衰减核 + Obizhaeva-Wang 价差恢复率分解）+ Algo Wheel TCA 驱动的算法路由（matched samples 防选择偏差 + RL 执行远期候选）。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G25 对账归因 |
| 所属 | 作战地图 11 |
| 依赖 | G22（执行，[40_execution_broker](40_execution_broker.md) 已定稿+代码已施工）+ G04（策略）+ G15（[34_regime_meta_allocator](34_regime_meta_allocator.md) clean P&L 双轨记录） |
| 对标 | 机构中后台对账 / Barra 归因 / Drovix TCA 2.0 / Brinson 归因 |
| 正交性 | ✅ 与 regime 正交 |
| 优先级 | P5 |
| 状态 | ✅ active — 每日对账+Brinson归因+TCA 2.0滑点分布+异常检测+报表生成已定稿 |

## 2. 背景

### 2.1 项目处境

对账归因是策略上线后的"后视镜"——通过每日对账确保成交/持仓/资金三方一致，通过 Brinson 归因分解超额收益来源，通过 TCA 2.0 分析执行质量。这三者是策略持续改进的反馈闭环：对账保证数据正确，归因指出 alpha 来源，TCA 指出执行损耗。

**TCA 1.0 → TCA 2.0 升级**（Drovix 2026-05 + finantrix 2026-08）：
- TCA 1.0：只报告平均滑点、IS 单一数字、parent order 完成即停止测量
- TCA 2.0：滑点分布（median/p90/p99）、五分量拆解、30min post-trade 信令成本、拒单成本转 bps、pre-trade/intraday/post-trade 三阶段复用

### 2.2 核心问题

1. **每日对账三方一致**：成交记录 vs 持仓变动 vs 资金变动必须一致，任何不一致都是异常。
2. **Brinson 归因 T+1 偏差**：A 股 T+1 结算使得当日买入的未实现收益被计入选股效应，高估 alpha——需分离已实现/未实现选股效应。
3. **滑点是分布而非均值**：平均滑点被尾部极值主导（NFP/FOMC/中央银行意外），需报告 median/p90/p99。
4. **IS 不能报告单一数字**：需拆解为 spread/impact/timing/opportunity/signalling 五分量（Drovix）。
5. **信令成本被漏测**：TCA 1.0 在 parent order 完成时停止测量，漏掉成交后 30 分钟的信息泄露成本。
6. **异常交易检测**：对账差异、滑点异常、换手率异常需自动检测告警。

### 2.3 约束条件

- **A 股 T+1**：当日买入不可卖，Brinson 归因需区分已实现/未实现
- **与 clean P&L 双轨记录联动**：[34_regime_meta_allocator] §3.2 的 clean P&L 是归因输入
- **每日盘后执行**：对账归因在每日收盘后批量执行
- **异常告警实时**：对账差异超阈值需实时告警

## 3. 决策

### 3.1 架构定义

对账归因由对账层、归因层、TCA 层、告警层四层构成：

```
对账层: 成交 vs 持仓 vs 资金 三方对账 → 差异检测 → 异常告警
                                                        ↓
归因层: Brinson 3因子(Allocation/Selection/Interaction) + Carino多期链接 + T+1适配
                                                        ↓
TCA 层: 滑点分布(median/p90/p99) + 五分量拆解 + 信令成本(30min) + 拒单成本(bps)
                                                        ↓
告警层: 异常交易检测 → 报表生成 → 反馈闭环
```

### 3.2 每日三方对账算法（对账层）

```python
from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Optional
import numpy as np


@dataclass
class TradeRecord:
    """成交记录。"""
    trade_id: str
    symbol: str
    strategy_id: str
    direction: str         # "buy" / "sell"
    quantity: float
    price: float
    amount: float          # quantity × price
    commission: float
    timestamp: str


@dataclass
class PositionSnapshot:
    """持仓快照。"""
    symbol: str
    quantity: float
    market_value: float
    cost_basis: float


@dataclass
class CapitalSnapshot:
    """资金快照。"""
    cash: float
    total_market_value: float
    total_equity: float    # cash + market_value


@dataclass
class ReconciliationResult:
    """对账结果。"""
    trade_vs_position_diff: dict[str, float]   # {symbol: 差异}
    trade_vs_capital_diff: float
    position_vs_capital_diff: float
    is_consistent: bool
    anomalies: list[str]


def daily_reconciliation(
    trades: list[TradeRecord],
    prev_positions: dict[str, PositionSnapshot],
    curr_positions: dict[str, PositionSnapshot],
    prev_capital: CapitalSnapshot,
    curr_capital: CapitalSnapshot,
    tolerance: float = 1.0,   # 容差（元）
) -> ReconciliationResult:
    """每日三方对账——成交 vs 持仓 vs 资金。

    对账逻辑：
    1. 成交→持仓：Σ(买入量) - Σ(卖出量) = 持仓变动量
    2. 成交→资金：Σ(卖出金额) - Σ(买入金额) - Σ(佣金) = 现金变动
    3. 持仓→资金：持仓市值变动 + 现金变动 = 总权益变动

    任何一方不一致（超容差）即为异常。
    """
    anomalies = []

    # 1. 成交 → 持仓对账
    trade_position_diff: dict[str, float] = {}
    all_symbols = set(prev_positions.keys()) | set(curr_positions.keys()) | {t.symbol for t in trades}

    for symbol in all_symbols:
        prev_qty = prev_positions.get(symbol, PositionSnapshot(symbol, 0, 0, 0)).quantity
        curr_qty = curr_positions.get(symbol, PositionSnapshot(symbol, 0, 0, 0)).quantity
        position_change = curr_qty - prev_qty

        trade_change = 0.0
        for t in trades:
            if t.symbol == symbol:
                if t.direction == "buy":
                    trade_change += t.quantity
                else:
                    trade_change -= t.quantity

        diff = position_change - trade_change
        if abs(diff) > tolerance:
            anomalies.append(f"position_trade_mismatch_{symbol}_diff_{diff:.2f}")
        trade_position_diff[symbol] = diff

    # 2. 成交 → 资金对账
    trade_capital_change = 0.0
    for t in trades:
        if t.direction == "sell":
            trade_capital_change += t.amount
        else:
            trade_capital_change -= t.amount
        trade_capital_change -= t.commission

    capital_change = curr_capital.cash - prev_capital.cash
    trade_capital_diff = capital_change - trade_capital_change
    if abs(trade_capital_diff) > tolerance:
        anomalies.append(f"capital_trade_mismatch_diff_{trade_capital_diff:.2f}")

    # 3. 持仓 → 资金对账
    prev_total_mv = sum(p.market_value for p in prev_positions.values())
    curr_total_mv = sum(p.market_value for p in curr_positions.values())
    mv_change = curr_total_mv - prev_total_mv
    expected_equity_change = mv_change + capital_change
    actual_equity_change = curr_capital.total_equity - prev_capital.total_equity
    position_capital_diff = actual_equity_change - expected_equity_change
    if abs(position_capital_diff) > tolerance:
        anomalies.append(f"position_capital_mismatch_diff_{position_capital_diff:.2f}")

    return ReconciliationResult(
        trade_vs_position_diff=trade_position_diff,
        trade_vs_capital_diff=trade_capital_diff,
        position_vs_capital_diff=position_capital_diff,
        is_consistent=len(anomalies) == 0,
        anomalies=anomalies,
    )
```

### 3.3 Brinson 3 因子归因算法（归因层）

```python
@dataclass
class BrinsonResult:
    """Brinson 3 因子归因结果。"""
    allocation_effect: float       # 配置效应（行业权重选择）
    selection_effect: float        # 选股效应（行业内选股）
    interaction_effect: float      # 交互效应
    total_active_return: float     # 总主动回报
    # T+1 适配：分离已实现/未实现选股效应
    realized_selection: float      # 已实现选股效应（T-1及更早持仓）
    unrealized_selection: float    # 未实现选股效应（当日买入未卖）
    position_lock_warning: bool    # 持仓锁定告警（T+1未实现占比过高）


def calc_brinson_attribution(
    portfolio_weights: dict[str, float],       # {行业: 组合权重}
    benchmark_weights: dict[str, float],       # {行业: 基准权重}
    portfolio_returns: dict[str, float],       # {行业: 组合行业收益}
    benchmark_returns: dict[str, float],       # {行业: 基准行业收益}
) -> BrinsonResult:
    """Brinson 3 因子归因——分解超额收益来源。

    Brinson 模型（Brinson-Fachler 1985）：
    - Allocation Effect = Σ (wp_i - wb_i) × (rb_i - rb_total)
      配置效应：超配/低配行业带来的超额收益
    - Selection Effect = Σ wb_i × (rp_i - rb_i)
      选股效应：行业内选股带来的超额收益
    - Interaction Effect = Σ (wp_i - wb_i) × (rp_i - rb_i)
      交互效应：配置与选股的联合效应

    A 股 T+1 适配见 §3.4 calc_brinson_with_t1_settlement。
    """
    all_industries = set(portfolio_weights.keys()) | set(benchmark_weights.keys())

    allocation = 0.0
    selection = 0.0
    interaction = 0.0

    rb_total = sum(wb * rb for wb, rb in zip(benchmark_weights.values(), benchmark_returns.values()))

    for ind in all_industries:
        wp = portfolio_weights.get(ind, 0.0)
        wb = benchmark_weights.get(ind, 0.0)
        rp = portfolio_returns.get(ind, 0.0)
        rb = benchmark_returns.get(ind, 0.0)

        allocation += (wp - wb) * (rb - rb_total)
        selection += wb * (rp - rb)
        interaction += (wp - wb) * (rp - rb)

    total_active = allocation + selection + interaction

    return BrinsonResult(
        allocation_effect=allocation,
        selection_effect=selection,
        interaction_effect=interaction,
        total_active_return=total_active,
        realized_selection=selection,  # 默认全已实现，T+1 适配见 §3.4
        unrealized_selection=0.0,
        position_lock_warning=False,
    )


def calc_brinson_with_t1_settlement(
    portfolio_weights: dict[str, float],
    benchmark_weights: dict[str, float],
    portfolio_returns: dict[str, float],
    benchmark_returns: dict[str, float],
    # T+1 适配参数
    today_buy_weights: dict[str, float],       # {行业: 当日新买入权重}
    today_sell_weights: dict[str, float],      # {行业: 当日卖出权重}
) -> BrinsonResult:
    """Brinson 归因 T+1 结算适配——分离已实现/未实现选股效应。

    A 股 T+1 偏差问题：
    - 当日买入的持仓不可卖，其当日收益是"未实现"的
    - 标准 Brinson 将未实现收益计入选股效应，高估 alpha
    - 实际上 T+1 锁定的未实现收益更多反映市场 beta 而非选股 alpha

    适配逻辑：
    1. 计算标准 Brinson 选股效应
    2. 按 today_buy_weights 比例分离未实现部分
    3. 未实现部分标记为 unrealized_selection，不计入选股 alpha
    4. 若 unrealized_selection 占比 > 50%，触发 position_lock_warning

    这解决了 T+1 结算导致的选股效应高估问题。
    """
    # 标准 Brinson
    base_result = calc_brinson_attribution(
        portfolio_weights, benchmark_weights, portfolio_returns, benchmark_returns
    )

    # T+1 适配：分离未实现选股效应
    all_industries = set(portfolio_weights.keys()) | set(benchmark_weights.keys())
    rb_total = sum(wb * rb for wb, rb in zip(benchmark_weights.values(), benchmark_returns.values()))

    unrealized = 0.0
    for ind in all_industries:
        wb = benchmark_weights.get(ind, 0.0)
        rp = portfolio_returns.get(ind, 0.0)
        rb = benchmark_returns.get(ind, 0.0)
        today_buy = today_buy_weights.get(ind, 0.0)

        # 当日新买入部分的选股效应视为未实现
        if wb > 0:
            buy_ratio = today_buy / wb if wb > 0 else 0
            buy_ratio = min(buy_ratio, 1.0)
            unrealized += wb * (rp - rb) * buy_ratio

    realized = base_result.selection_effect - unrealized
    position_lock_warning = abs(unrealized) > abs(base_result.selection_effect) * 0.5

    return BrinsonResult(
        allocation_effect=base_result.allocation_effect,
        selection_effect=base_result.selection_effect,
        interaction_effect=base_result.interaction_effect,
        total_active_return=base_result.total_active_return,
        realized_selection=realized,
        unrealized_selection=unrealized,
        position_lock_warning=position_lock_warning,
    )
```

### 3.4 Carino 多期链接算法（归因层）

```python
def carino_linking(
    period_results: list[BrinsonResult],
    period_total_returns: list[float],    # 各期组合总回报
    benchmark_total_returns: list[float], # 各期基准总回报
) -> BrinsonResult:
    """Carino 多期链接——将多期 Brinson 归因链接为连续归因。

    Carino 链接（Carino 1999）：
    - 多期归因不能简单相加（复利效应）
    - Carino 链接用对数变换将各期归因链接为连续归因
    - 链接因子 k_t = (ln(1+R_t) - ln(1+B_t)) / (R_t - B_t)
    - 链接后归因 = Σ k_t × period_attribution_t

    用于月度/季度/年度归因报告。
    """
    if not period_results:
        return BrinsonResult(0, 0, 0, 0, 0, 0, False)

    # 计算链接因子
    linking_factors = []
    for rp, rb in zip(period_total_returns, benchmark_total_returns):
        if abs(rp - rb) > 1e-10:
            k = (np.log(1 + rp) - np.log(1 + rb)) / (rp - rb)
        else:
            k = 1.0 / (1 + rb) if abs(1 + rb) > 1e-10 else 1.0
        linking_factors.append(k)

    # 链接归因
    total_allocation = sum(k * r.allocation_effect for k, r in zip(linking_factors, period_results))
    total_selection = sum(k * r.selection_effect for k, r in zip(linking_factors, period_results))
    total_interaction = sum(k * r.interaction_effect for k, r in zip(linking_factors, period_results))
    total_active = total_allocation + total_selection + total_interaction

    total_realized = sum(k * r.realized_selection for k, r in zip(linking_factors, period_results))
    total_unrealized = sum(k * r.unrealized_selection for k, r in zip(linking_factors, period_results))

    return BrinsonResult(
        allocation_effect=total_allocation,
        selection_effect=total_selection,
        interaction_effect=total_interaction,
        total_active_return=total_active,
        realized_selection=total_realized,
        unrealized_selection=total_unrealized,
        position_lock_warning=any(r.position_lock_warning for r in period_results),
    )
```

### 3.5 TCA 2.0 滑点分布算法（TCA 层）

```python
@dataclass
class SlippageDistribution:
    """滑点分布——TCA 2.0 核心升级（Drovix 2026-05）。

    核心原则：滑点是分布而非均值，需报告 median/p90/p99。
    平均滑点被尾部极值主导（NFP/FOMC/中央银行意外），
    报告均值掩盖了"困难条件下 broker 表现如何"的关键问题。
    """
    median_bps: float           # 中位数（正常条件下的典型成本）
    p90_bps: float              # 90 分位（困难条件下的成本）
    p99_bps: float              # 99 分位（极端条件下的成本）
    mean_bps: float             # 均值（对比用，被尾部主导）
    std_bps: float              # 标准差
    sample_count: int
    stressed_sample_count: int  # 压力条件样本数（top decile 波动率）


def compute_slippage_distribution(
    slippages_bps: list[float],           # 各笔交易滑点（bps）
    is_stressed: list[bool],              # 各笔是否压力条件（top decile 波动率或 macro 事件窗口）
) -> SlippageDistribution:
    """计算滑点分布——TCA 2.0 核心算法。

    压力条件定义（Drovix 2026-05）：
    - top decile 已实现波动率
    - 或 15 分钟窗口覆盖一级 macro 事件（NFP/FOMC/中央银行意外）

    决策级洞察：
    - median 相同但 p99 差 4 倍的两个 broker 不是同一个 broker
    - 极端条件下才是真实成本所在
    """
    if not slippages_bps:
        return SlippageDistribution(0, 0, 0, 0, 0, 0, 0)

    arr = np.array(slippages_bps)
    stressed_count = sum(is_stressed)

    return SlippageDistribution(
        median_bps=float(np.median(arr)),
        p90_bps=float(np.percentile(arr, 90)),
        p99_bps=float(np.percentile(arr, 99)),
        mean_bps=float(np.mean(arr)),
        std_bps=float(np.std(arr)),
        sample_count=len(arr),
        stressed_sample_count=stressed_count,
    )
```

### 3.6 TCA 2.0 五分量执行成本拆解（TCA 层）

```python
@dataclass
class TCA2Result:
    """TCA 2.0 执行成本分析结果。"""
    # 五分量成本（bps）
    spread_bps: float
    impact_temp_bps: float       # 临时市场冲击（部分回弹）
    impact_perm_bps: float       # 永久市场冲击（信息泄露）
    timing_bps: float            # 时机成本
    opportunity_bps: float       # 机会成本（未成交）
    signalling_bps: float        # 信令成本（30min post-trade）
    rejection_bps: float         # 拒单成本

    # 滑点分布
    slippage_distribution: SlippageDistribution

    # 总执行成本
    total_cost_bps: float

    # 压力条件分析
    stressed_spread_bps: float
    stressed_impact_bps: float


def compute_tca2(
    # 成交数据
    fill_prices: list[float],
    fill_quantities: list[float],
    arrival_mids: list[float],           # 各笔到达中间价
    # 30min post-trade 数据（信令成本）
    mid_prices_30min_after: list[float],
    # 未成交数据（机会成本）
    unfilled_quantity: float,
    unfilled_target_price: float,
    # 拒单数据
    rejection_rate: float,
    rejected_prices: list[float],
    next_executable_prices: list[float],
    direction: int,                       # +1=买入, -1=卖出
    # 滑点历史（分布计算）
    historical_slippages: list[float],
    historical_is_stressed: list[bool],
) -> TCA2Result:
    """TCA 2.0 执行成本分析——五分量拆解 + 滑点分布。

    五分量（Drovix 2026-05-27 "Decomposing Execution Cost"）：
    1. Spread cost：半价差，最易测量但通常最小
    2. Market impact：自己的订单造成的价格变动，临时+永久
    3. Timing cost：执行期间反向漂移
    4. Opportunity cost：未成交部分的机会损失
    5. Signalling cost：成交后30min反向漂移（被对手读盘）

    额外分量：
    6. Rejection cost：拒单率转 bps 成本

    TCA 1.0 → 2.0 关键升级：
    - IS 不再报告单一数字，拆解为五分量
    - 滑点报告 median/p90/p99 而非均值
    - 测量窗口延长至成交后 30 分钟（信令成本）
    - 拒单率转为 bps 成本（决策级 TCA）
    """
    if not fill_prices:
        return TCA2Result(0, 0, 0, 0, 0, 0, 0, SlippageDistribution(0,0,0,0,0,0,0), 0, 0, 0)

    total_notional = sum(p * q for p, q in zip(fill_prices, fill_quantities))
    if total_notional <= 0:
        return TCA2Result(0, 0, 0, 0, 0, 0, 0, SlippageDistribution(0,0,0,0,0,0,0), 0, 0, 0)

    # 1. Spread cost（半价差）
    spread_loss = 0.0
    for i, (fill_price, qty, arrival_mid) in enumerate(zip(fill_prices, fill_quantities, arrival_mids)):
        spread_loss += abs(fill_price - arrival_mid) * qty
    spread_bps = spread_loss / total_notional * 10000

    # 2. Market impact（临时 + 永久）
    # 临时冲击：首笔成交价 vs 末笔成交价的部分回弹
    # 永久冲击：信息泄露导致的持久价格变动
    if len(fill_prices) > 1:
        vwap = sum(p * q for p, q in zip(fill_prices, fill_quantities)) / sum(fill_quantities)
        arrival = arrival_mids[0]
        impact_temp_bps = abs(vwap - arrival) * direction / total_notional * sum(fill_quantities) * 10000 * 0.7  # 70% 临时
        impact_perm_bps = abs(vwap - arrival) * direction / total_notional * sum(fill_quantities) * 10000 * 0.3  # 30% 永久
    else:
        impact_temp_bps = 0.0
        impact_perm_bps = 0.0

    # 3. Timing cost（执行期间反向漂移）
    if len(arrival_mids) > 1:
        end_mid = mid_prices_30min_after[-1] if mid_prices_30min_after else arrival_mids[-1]
        timing_loss = abs(end_mid - arrival_mids[0]) * direction * sum(fill_quantities)
        timing_bps = timing_loss / total_notional * 10000
    else:
        timing_bps = 0.0

    # 4. Opportunity cost（未成交部分）
    if unfilled_quantity > 0 and unfilled_target_price > 0:
        end_mid = mid_prices_30min_after[-1] if mid_prices_30min_after else arrival_mids[-1]
        opp_loss = abs(end_mid - unfilled_target_price) * direction * unfilled_quantity
        opportunity_bps = opp_loss / (total_notional + unfilled_quantity * unfilled_target_price) * 10000
    else:
        opportunity_bps = 0.0

    # 5. Signalling cost（30min post-trade 反向漂移）
    signalling_loss = 0.0
    for i, (fill_price, qty) in enumerate(zip(fill_prices, fill_quantities)):
        if i < len(mid_prices_30min_after):
            mid_after = mid_prices_30min_after[i]
            price_move = (fill_price - mid_after) * direction
            signalling_loss += price_move * qty
    signalling_bps = max(0.0, -signalling_loss / total_notional * 10000)

    # 6. Rejection cost（拒单转 bps）
    if rejection_rate > 0 and rejected_prices:
        total_rej_loss = 0.0
        for rej_price, next_price in zip(rejected_prices, next_executable_prices):
            adverse_move = (next_price - rej_price) * direction
            total_rej_loss += adverse_move
        avg_adverse_bps = total_rej_loss / len(rejected_prices) / rejected_prices[0] * 10000 if rejected_prices[0] > 0 else 0
        rejection_bps = max(0.0, avg_adverse_bps * rejection_rate)
    else:
        rejection_bps = 0.0

    # 滑点分布
    slippage_dist = compute_slippage_distribution(historical_slippages, historical_is_stressed)

    total_cost = (spread_bps + impact_temp_bps + impact_perm_bps + timing_bps
                  + opportunity_bps + signalling_bps + rejection_bps)

    # 压力条件分析（简化）
    stressed_spread = spread_bps * 1.5
    stressed_impact = (impact_temp_bps + impact_perm_bps) * 2.0

    return TCA2Result(
        spread_bps=spread_bps,
        impact_temp_bps=impact_temp_bps,
        impact_perm_bps=impact_perm_bps,
        timing_bps=timing_bps,
        opportunity_bps=opportunity_bps,
        signalling_bps=signalling_bps,
        rejection_bps=rejection_bps,
        slippage_distribution=slippage_dist,
        total_cost_bps=total_cost,
        stressed_spread_bps=stressed_spread,
        stressed_impact_bps=stressed_impact,
    )
```

### 3.7 三阶段 TCA 循环算法（pre-trade / intraday / post-trade）

```python
@dataclass
class PreTradeTCAEstimate:
    """Pre-trade TCA 估计——下单前预估执行成本。

    输入（Quod Financial 2026-06-09）：
    - 订单规模 / ADV（5% ADV 与 25% ADV 行为截然不同）
    - 日内波动率（高波动增加 timing cost）
    - 买卖价差（任何 marketable order 的起始成本）
    - 日内流动性分布（决定 VWAP 调度行为）

    主要模型：square-root market impact（机构主流 pre-trade 估计框架）
    """
    estimated_total_cost_bps: float
    estimated_impact_bps: float          # 平方根冲击估计
    estimated_timing_bps: float
    recommended_algo: str                # 推荐算法（VWAP/POV/IS/adaptive）
    recommended_participation_rate: float
    recommended_urgency: str             # low/medium/high


@dataclass
class IntradayTCASnapshot:
    """Intraday TCA 快照——盘中实时监控执行质量。

    作用（Quod Financial 2026-06-09）：
    - 实时发现执行偏离预期（vs pre-trade estimate）
    - 触发算法切换或参数调整
    - 而非盘后才发现问题
    """
    timestamp: str
    executed_pct: float                  # 已执行比例
    realized_cost_bps: float             # 已实现成本
    pre_trade_estimate_bps: float        # pre-trade 估计
    deviation_bps: float                 # 偏离 = realized - estimate
    reversion_mark_5min_bps: float       # T+5min 中间价回撤（OrderX 诊断标记）
    reversion_mark_30min_bps: float      # T+30min 中间价回撤
    alpha_or_impact_tag: str             # "impact_temp" / "alpha" / "unclear"


def estimate_pre_trade_tca(
    order_size: float,
    adv: float,                          # 平均日成交额
    intraday_volatility: float,          # 日内波动率
    bid_ask_spread_bps: float,
    square_root_coefficient: float = 0.5,  # 平方根冲击系数（需历史校准）
) -> PreTradeTCAEstimate:
    """Pre-trade TCA 估计——square-root market impact 模型。

    平方根律（Bacry et al. 2024 实证）：
    - impact ∝ σ × sqrt(order_size / ADV)
    - 与线性模型相比，平方根律更贴近实证
    - 系数需用历史数据校准（A 股约 0.3-0.6）

    决策建议：
    - order_size/ADV < 5%：可激进，POV 20%
    - 5%-15%：中等，POV 10%
    - > 15%：保守，POV 5% 或拆分多日
    """
    participation = order_size / adv if adv > 0 else 1.0

    # 平方根冲击估计
    estimated_impact_bps = (
        square_root_coefficient * intraday_volatility * np.sqrt(participation) * 10000
    )
    estimated_timing_bps = intraday_volatility * np.sqrt(participation) * 10000 * 0.3
    estimated_total = estimated_impact_bps + estimated_timing_bps + bid_ask_spread_bps / 2

    # 算法推荐
    if participation < 0.05:
        recommended_algo = "POV"
        recommended_rate = 0.20
        recommended_urgency = "high"
    elif participation < 0.15:
        recommended_algo = "VWAP"
        recommended_rate = 0.10
        recommended_urgency = "medium"
    else:
        recommended_algo = "IS"          # Implementation Shortfall
        recommended_rate = 0.05
        recommended_urgency = "low"

    return PreTradeTCAEstimate(
        estimated_total_cost_bps=float(estimated_total),
        estimated_impact_bps=float(estimated_impact_bps),
        estimated_timing_bps=float(estimated_timing_bps),
        recommended_algo=recommended_algo,
        recommended_participation_rate=float(recommended_rate),
        recommended_urgency=recommended_urgency,
    )


def classify_alpha_vs_impact(
    fill_price: float,
    mid_5min_after: float,
    mid_30min_after: float,
    arrival_mid: float,
    direction: int,                      # +1=buy, -1=sell
) -> str:
    """区分 alpha vs impact——OrderX 2026-07 reversion marks 诊断。

    OrderX 2026-07-09 提出：reversion marks（mid at T+5min / T+30min / next open）
    不是目标，是诊断标记。核心逻辑：
    - 价格回撤到 pre-trade 水平 → 你付了 temporary impact（你的压力推价，停止后回弹）
    - 价格继续朝你方向走 → 订单携带真实 alpha（或永久信息），漂移是市场追上你
      持续 continuation 说明该交易更快（耐心在向市场捐 alpha）

    返回分类：
    - "impact_temp"：临时冲击（5min 回撤 > 50%）
    - "impact_perm"：永久冲击（30min 仍不回撤）
    - "alpha"：携带 alpha（价格继续朝方向走）
    - "unclear"：信号不明确
    """
    # 立即冲击幅度
    immediate_move = (fill_price - arrival_mid) * direction
    # 5min 后回撤幅度
    revert_5min = (fill_price - mid_5min_after) * direction
    # 30min 后回撤幅度
    revert_30min = (fill_price - mid_30min_after) * direction

    if immediate_move <= 0:
        return "unclear"

    # 5min 回撤 > 50% → 临时冲击
    if revert_5min / immediate_move > 0.5:
        return "impact_temp"

    # 30min 后价格继续朝原方向走 → alpha
    if revert_30min < 0:
        return "alpha"

    # 30min 仍未回撤 → 永久冲击（信息泄露）
    if revert_30min / immediate_move < 0.2:
        return "impact_perm"

    return "unclear"


def is_selection_bias_risk(
    orders_by_algo: dict[str, list[float]],   # {algo_name: [该 algo 处理的订单难度评分]}
) -> bool:
    """检测 TCA 选择偏差——OrderX 2026-07-09 警告。

    OrderX 2026-07 警告：
    - 比较各算法在被"挑选"的订单上的表现，会混淆策略与难度
    - 难订单送给谨慎算法，简单订单送给廉价算法，然后得出"廉价算法更好"的错误结论
    - 公平比较需要 matched samples 或 randomized routing 实验

    检测逻辑：
    - 各算法处理的订单难度分布是否有显著差异（KS 检验）
    - 若有显著差异 → 存在选择偏差风险 → TCA 结论不可信
    """
    from scipy import stats
    algos = list(orders_by_algo.keys())
    if len(algos) < 2:
        return False

    # 两两 KS 检验
    for i in range(len(algos)):
        for j in range(i + 1, len(algos)):
            sample_i = orders_by_algo[algos[i]]
            sample_j = orders_by_algo[algos[j]]
            if len(sample_i) < 10 or len(sample_j) < 10:
                continue
            _, p_value = stats.ks_2samp(sample_i, sample_j)
            if p_value < 0.05:
                return True  # 难度分布显著不同 → 选择偏差风险

    return False
```

### 3.8 IS 归因按维度分解算法（quant67 2026-05）

```python
@dataclass
class ISAttributionByDimension:
    """IS 归因按维度分解——quant67 2026-05-01。

    quant67 2026-05-01 提出：
    把 IS 拆出来后，下一步是把它归因到不同维度。
    归因的工程实现是「按维度 group by」。

    7 个核心维度（机构标准）：
    1. 策略（哪个策略的执行差）
    2. 经纪商（哪个 broker 的执行差）
    3. 算法（哪个执行算法的执行差）
    4. 时段（开盘/盘中/收盘的执行差）
    5. 品种（哪些标的的执行差）
    6. 流动性条件（高/低 ADV 的执行差）
    7. 订单大小桶（小/中/大单的执行差）
    """
    by_strategy: dict[str, float]        # {strategy_id: IS bps}
    by_broker: dict[str, float]
    by_algo: dict[str, float]
    by_session: dict[str, float]         # open/intraday/close
    by_symbol: dict[str, float]
    by_liquidity_bucket: dict[str, float]  # high/medium/low ADV
    by_order_size_bucket: dict[str, float]  # small/medium/large


def attribute_is_by_dimensions(
    orders: list[dict],                  # 每笔订单含 strategy/broker/algo/session/symbol/adv/order_size/is_bps
) -> ISAttributionByDimension:
    """IS 归因按 7 维度分解。

    工程实现（quant67 2026-05-01）：
    - 按维度 group by → 求加权平均 IS bps
    - 权重为订单金额（避免小订单噪声主导）
    - 输出每个维度的 IS bps 排名，定位执行损耗最严重的切片

    决策用途：
    - 找到 IS bps 最高的 broker → 考虑降权或退役
    - 找到 IS bps 最高的 session → 调整订单时段
    - 找到 IS bps 最高的 order_size_bucket → 调整拆单策略
    """
    def weighted_avg_by_key(orders: list[dict], key: str) -> dict[str, float]:
        buckets: dict[str, list[tuple[float, float]]] = {}
        for o in orders:
            k = o.get(key, "unknown")
            buckets.setdefault(k, []).append((o["is_bps"], o.get("notional", 1.0)))
        result = {}
        for k, vals in buckets.items():
            total_w = sum(w for _, w in vals)
            if total_w > 0:
                result[k] = sum(v * w for v, w in vals) / total_w
            else:
                result[k] = 0.0
        return result

    # 流动性分桶（基于 ADV）
    def liquidity_bucket(adv: float) -> str:
        if adv > 1e9: return "high"
        if adv > 1e8: return "medium"
        return "low"

    # 订单大小分桶（基于订单金额）
    def size_bucket(notional: float) -> str:
        if notional > 1e7: return "large"
        if notional > 1e6: return "medium"
        return "small"

    for o in orders:
        o["liquidity_bucket"] = liquidity_bucket(o.get("adv", 0))
        o["size_bucket"] = size_bucket(o.get("notional", 0))

    return ISAttributionByDimension(
        by_strategy=weighted_avg_by_key(orders, "strategy_id"),
        by_broker=weighted_avg_by_key(orders, "broker"),
        by_algo=weighted_avg_by_key(orders, "algo"),
        by_session=weighted_avg_by_key(orders, "session"),
        by_symbol=weighted_avg_by_key(orders, "symbol"),
        by_liquidity_bucket=weighted_avg_by_key(orders, "liquidity_bucket"),
        by_order_size_bucket=weighted_avg_by_key(orders, "size_bucket"),
    )
```

### 3.9 异常交易检测算法（告警层）

```python
@dataclass
class AnomalyAlert:
    """异常告警。"""
    alert_type: str              # "reconciliation_mismatch" / "slippage_outlier" / "turnover_anomaly"
    severity: str                # "WARNING" / "CRITICAL"
    message: str
    details: dict


def detect_anomalies(
    reconciliation: ReconciliationResult,
    tca_result: TCA2Result,
    daily_turnover: float,            # 当日换手率
    avg_turnover: float,              # 历史平均换手率
    turnover_threshold: float = 3.0,  # 换手率异常倍数
    slippage_p99_threshold: float = 50.0,  # p99 滑点阈值（bps）
) -> list[AnomalyAlert]:
    """异常交易检测——对账差异 + 滑点异常 + 换手率异常。"""
    alerts = []

    # 1. 对账差异
    if not reconciliation.is_consistent:
        for anomaly in reconciliation.anomalies:
            alerts.append(AnomalyAlert(
                alert_type="reconciliation_mismatch",
                severity="CRITICAL",
                message=f"对账不一致: {anomaly}",
                details={"anomaly": anomaly},
            ))

    # 2. 滑点异常
    if tca_result.slippage_distribution.p99_bps > slippage_p99_threshold:
        alerts.append(AnomalyAlert(
            alert_type="slippage_outlier",
            severity="WARNING",
            message=f"p99滑点异常: {tca_result.slippage_distribution.p99_bps:.1f}bps > {slippage_p99_threshold}bps",
            details={
                "p99_bps": tca_result.slippage_distribution.p99_bps,
                "median_bps": tca_result.slippage_distribution.median_bps,
            },
        ))

    # 3. 信令成本过高
    if tca_result.signalling_bps > 10.0:
        alerts.append(AnomalyAlert(
            alert_type="signalling_cost_high",
            severity="WARNING",
            message=f"信令成本过高: {tca_result.signalling_bps:.1f}bps（可能被对手读盘）",
            details={"signalling_bps": tca_result.signalling_bps},
        ))

    # 4. 换手率异常
    if avg_turnover > 0 and daily_turnover > avg_turnover * turnover_threshold:
        alerts.append(AnomalyAlert(
            alert_type="turnover_anomaly",
            severity="WARNING",
            message=f"换手率异常: {daily_turnover:.1%} > {avg_turnover:.1%} × {turnover_threshold}",
            details={"daily": daily_turnover, "avg": avg_turnover},
        ))

    return alerts
```

### 3.10 报表生成算法（告警层）

```python
@dataclass
class DailyReport:
    """日报表。"""
    report_date: date
    reconciliation: ReconciliationResult
    brinson: BrinsonResult
    tca2: TCA2Result
    anomalies: list[AnomalyAlert]
    # 归因维度
    strategy_attribution: dict[str, float]   # {strategy_id: PnL贡献}
    symbol_attribution: dict[str, float]     # {symbol: PnL贡献}
    period_attribution: dict[str, float]     # {时段: PnL贡献}


def generate_daily_report(
    report_date: date,
    reconciliation: ReconciliationResult,
    brinson: BrinsonResult,
    tca2: TCA2Result,
    anomalies: list[AnomalyAlert],
    strategy_pnl: dict[str, float],          # {strategy_id: 当日PnL}
    symbol_pnl: dict[str, float],            # {symbol: 当日PnL}
    period_pnl: dict[str, float],            # {时段: 当日PnL}
) -> DailyReport:
    """生成日报表——对账+归因+TCA+异常+多维归因。"""
    return DailyReport(
        report_date=report_date,
        reconciliation=reconciliation,
        brinson=brinson,
        tca2=tca2,
        anomalies=anomalies,
        strategy_attribution=strategy_pnl,
        symbol_attribution=symbol_pnl,
        period_attribution=period_pnl,
    )
```

### 3.11 市场冲击模型族——临时/永久冲击分离（TCA 层）

```python
@dataclass
class ImpactDecomposition:
    """市场冲击分解结果——临时/永久分量分离。

    三大机构模型对比（2026-08 研究整合）：
    | 模型 | 核心贡献 | 适用场景 | MVP 采用 |
    | Kissell-Glantz I-Star (2003) | 闭式分离临时(a1)/永久(a2)冲击 | pre-trade 估计 | ✅ 主用 |
    | Obizhaeva-Wang (2013) | 价差恢复率 ρ 分离冲击 | 单一往返交易分析 | ✅ 辅助 |
    | Bouchaud Propagator (2004) | 时间衰减核 G(t) 描述冲击传播 | 多笔交易累积冲击 | Phase 2 |

    I-Star 公式（Kissell "The Science of Algorithmic Trading" 2013）：
    - Temporary Impact = a1 × (size/ADV)^b1 × σ
    - Permanent Impact  = a2 × (size/ADV)^b2 × σ
    - σ = 日波动率，size/ADV = 参与率

    Obizhaeva-Wang 公式：
    - 临时冲击 ∝ (size/ADV) × (1 - ρ)，ρ = 价差恢复率
    - 永久冲击 ∝ (size/ADV) × ρ
    - 关键参数 ρ 需历史校准（A 股大盘股约 0.4-0.6）

    Bouchaud Propagator：
    - 价格冲击 = ∫ G(t-s) · ε(s) ds
    - G(t) = Γ/(t^γ)，γ ≈ 0.5（平方根律衰减）
    - 描述"今天的交易影响未来价格"的时间结构
    - 与无动态套利约束自洽（Gatheral 2010）
    """
    model: str                          # "I-Star" / "Obizhaeva-Wang" / "Propagator"
    temporary_impact_bps: float         # 临时冲击（部分回弹）
    permanent_impact_bps: float         # 永久冲击（信息泄露）
    total_impact_bps: float
    participation_rate: float
    # 模型特定参数
    params: dict                        # I-Star: {a1,a2,b1,b2}; OW: {rho}; Prop: {gamma, Gamma}


def estimate_istar_impact(
    order_size: float,
    adv: float,
    daily_volatility: float,
    a1: float = 0.5,                    # 临时冲击系数（需历史校准）
    a2: float = 0.3,                    # 永久冲击系数（需历史校准）
    b1: float = 1.0,                    # 临时冲击非线性指数
    b2: float = 1.0,                    # 永久冲击非线性指数
) -> ImpactDecomposition:
    """Kissell-Glantz I-Star 市场冲击模型——pre-trade 成本估计。

    闭式解优势：
    - 临时/永久冲击显式分离，可直接进 TCA 五分量（§3.6 impact_temp/impact_perm）
    - 参数 a1/a2/b1/b2 可从历史成交回填校准（MVP 用机构经验值，Phase 1.5+ 自校准）
    - 与 square-root 律兼容（b1=b2=0.5 时退化为平方根冲击）

    校准建议（机构经验，A 股大盘）：
    - a1 ≈ 0.4-0.7（临时冲击主导，约 60-70% 总冲击）
    - a2 ≈ 0.2-0.4（永久冲击，约 30-40%）
    - b1 = b2 = 0.5（平方根律，与 Gatheral 2010 无套利约束一致）
    """
    participation = order_size / adv if adv > 0 else 1.0
    temp_impact = a1 * (participation ** b1) * daily_volatility
    perm_impact = a2 * (participation ** b2) * daily_volatility
    return ImpactDecomposition(
        model="I-Star (Kissell-Glantz 2003)",
        temporary_impact_bps=temp_impact * 10000,
        permanent_impact_bps=perm_impact * 10000,
        total_impact_bps=(temp_impact + perm_impact) * 10000,
        participation_rate=participation,
        params={"a1": a1, "a2": a2, "b1": b1, "b2": b2},
    )


def estimate_obizhaeva_wang_impact(
    order_size: float,
    adv: float,
    recovery_rate: float = 0.5,         # 价差恢复率 ρ（需校准）
) -> ImpactDecomposition:
    """Obizhaeva-Wang 临时/永久冲击分离模型。

    核心贡献：将市场冲击显式分解为：
    - Temporary Impact: 交易时的瞬时价格偏移（随后部分恢复）
    - Permanent Impact: 交易后的新均衡价格偏移（不恢复）

    关键参数 recovery_rate ρ：
    - ρ = 0：纯临时冲击（完全回弹，无信息泄露）
    - ρ = 1：纯永久冲击（完全不回弹，纯信息）
    - ρ ∈ (0,1)：混合（A 股大盘股实证 ρ ≈ 0.4-0.6）

    适用场景：
    - 单一往返交易（开仓+平仓）的冲击分析
    - 与 I-Star 互补：I-Star 用于 pre-trade，OW 用于 post-trade 反推 ρ
    """
    participation = order_size / adv if adv > 0 else 1.0
    total_impact = participation  # 简化：总冲击 = 参与率
    temp_impact = total_impact * (1 - recovery_rate)
    perm_impact = total_impact * recovery_rate
    return ImpactDecomposition(
        model="Obizhaeva-Wang (2013)",
        temporary_impact_bps=temp_impact * 10000,
        permanent_impact_bps=perm_impact * 10000,
        total_impact_bps=total_impact * 10000,
        participation_rate=participation,
        params={"recovery_rate": recovery_rate},
    )


def calibrate_recovery_rate_from_tca(
    tca_result: "TCA2Result",
) -> float:
    """从 TCA 结果反推 Obizhaeva-Wang 恢复率 ρ——post-trade 校准。

    逻辑（OW 模型反推）：
    - ρ = permanent_impact / (temporary_impact + permanent_impact)
    - 直接用 §3.6 TCA 2.0 的 impact_temp / impact_perm 分量
    - 累积 N 笔后得到 ρ 分布，用于校准 pre-trade 估计

    校准频率：
    - MVP：月度批量校准（样本量小）
    - Phase 1.5+：按板块/流动性桶分组校准
    """
    total = tca_result.impact_temp_bps + tca_result.impact_perm_bps
    if total <= 0:
        return 0.5  # 默认值
    return tca_result.impact_perm_bps / total


def estimate_propagator_impact(
    order_sizes: list[float],           # 各笔交易规模
    adv: float,
    execution_times: list[float],       # 各笔执行时间戳
    observation_time: float,            # 观测时间
    gamma: float = 0.5,                 # 衰减指数（平方根律 γ≈0.5）
    Gamma: float = 0.3,                 # 核幅度（需校准）
) -> ImpactDecomposition:
    """Bouchaud Propagator 模型——时间衰减核描述冲击传播。

    核心思想（Bouchaud et al. 2004, "Fluctuations and Response in Financial Markets"）：
    - 单笔交易对价格的影响不是瞬时的，而是随时间衰减
    - 价格冲击 = ∫ G(t-s) · ε(s) ds，G(t) = Γ·t^(-γ)
    - ε(s) = 交易方向 × 规模的符号函数
    - γ ≈ 0.5 时退化为平方根律（与 Gatheral 2010 无套利约束一致）

    与 I-Star/OW 的区别：
    - I-Star/OW：单笔交易的瞬时冲击分解（pre-trade 估计）
    - Propagator：多笔交易的累积冲击时间结构（post-trade 分析）
    - Propagator 能解释"为什么前一笔交易影响后一笔的冲击成本"

    MVP 决策：
    - Propagator 需 tick 级数据基础设施，Phase 2+ 实施
    - MVP 用 I-Star pre-trade + OW post-trade 反推 ρ 已足够
    """
    if not order_sizes or adv <= 0:
        return ImpactDecomposition("Propagator", 0, 0, 0, 0, {})

    # 计算累积冲击（简化：忽略符号方向，用规模）
    cumulative_temp = 0.0
    cumulative_perm = 0.0
    for size, exec_time in zip(order_sizes, execution_times):
        if exec_time >= observation_time:
            continue
        dt = observation_time - exec_time
        if dt <= 0:
            continue
        participation = size / adv
        # 衰减核 G(t) = Gamma * t^(-gamma)
        # 已衰减部分 = 永久冲击；未衰减部分 = 临时冲击
        decay = Gamma * (dt ** (-gamma)) if dt > 0 else 0
        # 简化：衰减越久，临时冲击占比越小
        temp_share = max(0.0, min(1.0, decay))
        cumulative_temp += participation * temp_share
        cumulative_perm += participation * (1 - temp_share)

    return ImpactDecomposition(
        model="Bouchaud Propagator (2004)",
        temporary_impact_bps=cumulative_temp * 10000,
        permanent_impact_bps=cumulative_perm * 10000,
        total_impact_bps=(cumulative_temp + cumulative_perm) * 10000,
        participation_rate=sum(order_sizes) / adv,
        params={"gamma": gamma, "Gamma": Gamma},
    )
```

### 3.12 Algo Wheel——TCA 驱动的算法路由（TCA 层）

```python
@dataclass
class AlgoWheelDecision:
    """Algo Wheel 算法路由决策——基于历史 TCA 的智能算法选择。

    finantrix 2026-08-08 "Execution Algorithms and SOR — TCA 2.0"：
    - Algo Wheel 把"选哪个执行算法"建模为优化问题
    - 输入：订单特征（规模/urgency/品种/流动性 regime）
    - 输出：在当前条件下历史 TCA 表现最优的算法
    - 关键陷阱：选择偏差（OrderX 2026-07 警告）——难订单送谨慎算法，
      简单订单送廉价算法，会得出"廉价算法更好"的错误结论

    MVP 路由规则（参与率驱动）：
    | 参与率 | 推荐算法 | 理由 |
    | <0.1% | direct_limit | 冲击可忽略，拆了反增最低佣金成本 |
    | 0.1%-1% | twap | 均匀切片，被动挂单 |
    | 1%-5% | vwap_with_cap | 契合日内量能分布，参与率≤5% |
    | >5% | is_multi_day | IS 风险厌恶轨迹 + 多日分拆 |

    Phase 1.5+ 升级路径：
    - matched_samples：历史 TCA 按订单特征匹配，消除选择偏差
    - RL 执行：finantrix 2026-08 指出 RL 已进入执行领域，
      但需大量历史数据 + 仿真环境，Phase 2+ 候选
    """
    recommended_algo: str
    reasoning: str
    expected_cost_bps: float            # 基于历史 TCA 的预期成本
    confidence: str                     # "high" / "medium" / "low"（样本量驱动）
    alternative_algo: str               # 备选算法
    selection_bias_risk: bool           # 是否存在选择偏差风险


def algo_wheel_route(
    order: dict,                        # {symbol, size, side, urgency, ...}
    market_conditions: dict,            # {adv, volatility, spread, depth, ...}
    historical_tca: list[dict],         # 历史 TCA 记录（按算法分组）
) -> AlgoWheelDecision:
    """Algo Wheel 算法路由——基于历史 TCA 的智能算法选择。

    决策流程：
    1. 按参与率分桶确定候选算法集
    2. 从历史 TCA 检索同桶同流动性 regime 的记录
    3. 计算各候选算法的加权平均 IS bps（权重=订单金额）
    4. 检测选择偏差（§3.7 is_selection_bias_risk）
    5. 输出最优算法 + 备选 + 置信度

    A 股适配：
    - 个人账户小资金多数订单 <0.1% ADV → direct_limit
    - 涨跌停板 → 唯一可成交价位挂单（涨停价/跌停价）
    - miniQMT 不支持券商端算法 → 系统自实现 TWAP/VWAP/IS
    """
    size = order.get("size", 0)
    adv = market_conditions.get("adv", 0)
    urgency = order.get("urgency", "normal")
    participation = size / adv if adv > 0 else 1.0

    # Step 1: 按参与率分桶确定候选算法集
    if urgency == "urgent":
        primary, alt = "market_order", "direct_limit"
        reasoning = "urgency=urgent, accept slippage"
    elif participation < 0.001:
        primary, alt = "direct_limit", "twap"
        reasoning = f"tiny order ({participation:.3%} ADV), no split needed"
    elif participation < 0.01:
        primary, alt = "twap", "vwap_with_cap"
        reasoning = f"small order ({participation:.2%} ADV), uniform slicing"
    elif participation < 0.05:
        primary, alt = "vwap_with_cap", "is"
        reasoning = f"medium order ({participation:.2%} ADV), volume-weighted"
    else:
        primary, alt = "is_multi_day", "vwap_with_cap"
        reasoning = f"large order ({participation:.2%} ADV), IS + multi-day split"

    # Step 2-3: 从历史 TCA 检索同桶记录计算预期成本
    expected_cost = 0.0
    sample_count = 0
    bucket_costs: dict[str, list[float]] = {}
    for tca in historical_tca:
        algo = tca.get("algo", "unknown")
        is_bps = tca.get("is_bps", 0)
        bucket_costs.setdefault(algo, []).append(is_bps)

    if primary in bucket_costs and bucket_costs[primary]:
        expected_cost = sum(bucket_costs[primary]) / len(bucket_costs[primary])
        sample_count = len(bucket_costs[primary])

    # Step 4: 检测选择偏差
    orders_by_algo = {
        algo: [t.get("difficulty_score", 0.5) for t in historical_tca if t.get("algo") == algo]
        for algo in bucket_costs
    }
    bias_risk = is_selection_bias_risk(orders_by_algo)

    # Step 5: 置信度（样本量驱动）
    if sample_count >= 30:
        confidence = "high"
    elif sample_count >= 10:
        confidence = "medium"
    else:
        confidence = "low"

    return AlgoWheelDecision(
        recommended_algo=primary,
        reasoning=reasoning,
        expected_cost_bps=expected_cost,
        confidence=confidence,
        alternative_algo=alt,
        selection_bias_risk=bias_risk,
    )


def compute_algo_scorecard(
    historical_tca: list[dict],         # 历史 TCA 记录
    lookback_days: int = 30,
) -> dict[str, dict]:
    """算法记分卡——按算法汇总 TCA 表现。

    finantrix 2026-08-08 指出：
    - Algo Wheel 的输入是"算法记分卡"——按算法分组的历史 TCA 统计
    - 关键指标：中位 IS bps / p90 IS bps / 样本量 / 选择偏差标志
    - 记分卡每日更新，驱动次日算法路由

    输出示例：
    {
        "twap": {"median_bps": 8.2, "p90_bps": 15.3, "sample": 45, "bias_risk": False},
        "vwap_with_cap": {"median_bps": 7.1, "p90_bps": 12.8, "sample": 32, "bias_risk": True},
        ...
    }
    """
    by_algo: dict[str, list[float]] = {}
    for tca in historical_tca:
        algo = tca.get("algo", "unknown")
        by_algo.setdefault(algo, []).append(tca.get("is_bps", 0))

    scorecard = {}
    for algo, costs in by_algo.items():
        if not costs:
            continue
        arr = np.array(costs)
        scorecard[algo] = {
            "median_bps": float(np.median(arr)),
            "p90_bps": float(np.percentile(arr, 90)),
            "p99_bps": float(np.percentile(arr, 99)),
            "mean_bps": float(np.mean(arr)),
            "sample": len(arr),
            "bias_risk": len(costs) < 10,  # 样本不足视为偏差风险
        }
    return scorecard
```

## 4. 考虑过的替代方案

| 方案 | 描述 | 拒绝理由 |
|---|---|---|
| **TCA 1.0 均值滑点** | 报告平均滑点 | 被尾部极值主导，掩盖困难条件下的真实成本 |
| **单一 IS 数字** | Implementation Shortfall 单一数字 | 捆绑 4 种不同成本，无法定位问题 |
| **无信令成本** | TCA 1.0 在 parent order 完成时停止测量 | 漏掉成交后 30min 信息泄露成本 |
| **拒单率百分比** | 只报告拒单率百分比 | 无经济含义，需转 bps 成本 |
| **标准 Brinson 无 T+1 适配** | 不区分已实现/未实现 | T+1 未实现收益高估选股 alpha |
| **简单相加多期归因** | 多期归因直接相加 | 忽略复利效应，Carino 链接更准确 |
| **仅用 square-root 冲击** | 不区分临时/永久冲击 | 无法进 TCA 五分量拆解（§3.6 需 temp/perm 分量）；I-Star 闭式分离更精确 |
| **Propagator MVP 实施** | MVP 即上 Bouchaud Propagator | 需 tick 级数据基础设施，MVP 用 I-Star+OW 已足够；Phase 2+ |
| **RL 执行 MVP 实施** | MVP 即用 RL 驱动 Algo Wheel | finantrix 2026-08 指出需大量历史数据+仿真环境；Phase 2+ 候选 |

## 5. 上限定义

| 上限 | 值 | 理由 |
|---|---|---|
| **对账容差** | 1.0 元 | A 股最小价格变动单位的合理容差 |
| **p99 滑点阈值** | 50 bps | 超过即告警 |
| **信令成本阈值** | 10 bps | 超过即可能被读盘 |
| **换手率异常倍数** | 3× | 超过历史均值 3 倍即告警 |
| **T+1 未实现占比** | 50% | 超过即持仓锁定告警 |

**演进路径**：
- MVP：每日对账 + Brinson T+1 适配 + TCA 2.0 五分量 + 异常检测
- Phase 1.5：Carino 多期链接 + 因子归因（Barra 风格）
- Phase 2：pre-trade TCA 驱动路由决策（finantrix TCA 2.0 三阶段复用）

## 6. 待裁定

| 项 | 暂缓理由 | 重评条件 |
|---|---|---|
| **Barra 因子归因** | 需因子风险模型 | Phase 1.5+ 因子库成熟后 |
| **pre-trade TCA 路由** | 需历史成本模型 | Phase 2+ 执行数据积累后 |
| **RL 执行优化** | 需 RL 基础设施 | Phase 2+（finantrix 2026-08 指出 RL 已进入执行领域） |
| **Bouchaud Propagator 实施** | 需 tick 级数据基础设施 | Phase 2+ Level-2 数据就绪 |
| **I-Star 参数自校准** | 需历史成交回填 | Phase 1.5+ 执行数据 ≥1000 笔后 |
| **matched_samples Algo Wheel** | 需大量历史 TCA 数据 | Phase 1.5+ 数据积累后消除选择偏差 |

## 7. 待定问题（讨论要点）

- [x] ① PnL 归因（策略贡献分解）→ §3.8 报表生成 strategy_attribution
- [x] ② 每日对账（成交 vs 持仓 vs 资金）→ §3.2 定型
- [x] ③ 归因维度（策略/标的/因子/时段）→ §3.8 定型（因子归因 Phase 1.5+）
- [x] ④ 与 StrategyBook 独立 PnL 归因的对接 → §3.8 strategy_attribution
- [x] ⑤ 异常交易检测 → §3.7 定型
- [x] ⑥ 报表生成 → §3.8 定型

## 8. 引用

- [00_index_trading_decision](00_index_trading_decision.md) §3 G25
- [40_execution_broker](40_execution_broker.md)（G22 产出物，成交数据来源）
- [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §2.2（StrategyBook PnL）
- [34_regime_meta_allocator](34_regime_meta_allocator.md)（G15，clean P&L 双轨记录）
- battle_map_11_reconciliation（当前状态快照）

**外部研究引用**：
- Drovix Research "TCA That Actually Drives Decisions"（2026-05-27）：TCA 2.0 滑点分布+信令成本+拒单成本
- Drovix Research "Decomposing Execution Cost: Five Components"（2026-05-18）：五分量拆解
- finantrix "Execution Algorithms and SOR — TCA 2.0"（2026-08-08）：pre-trade/intraday/post-trade 三阶段 + Algo Wheel + RL 执行
- OrderX "Introduction to Algorithmic Execution Part 12: Benchmarks & TCA"（2026-07-09）：reversion marks + selection bias
- Quod Financial "Three-Stage TCA"（2026-06-09）：pre-trade/intraday/post-trade 完整循环
- quant67 "IS Attribution by Dimension"（2026-05-01）：7 维度 group by 分解
- Brinson & Fachler (1985)：3 因子归因模型
- Carino (1999)：多期链接算法
- Perold (1988)：Implementation Shortfall 框架
- Kissell & Glantz "Optimal Trading Strategies"（2003）/ Kissell "The Science of Algorithmic Trading"（2013）：I-Star 临时/永久冲击闭式分离
- Obizhaeva & Wang (2013) "Optimal Trading Strategy and Supply/Demand Dynamics"：价差恢复率分解
- Bouchaud, Farmer, Lillo (2004/2009) "Fluctuations and Response in Financial Markets"：Propagator 时间衰减核
- Gatheral (2010) "No-Dynamic-Arbitrage and Market Impact"：无动态套利约束 → 平方根律唯一自洽

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行：由 00_index G25 讨论要点占位，待讨论填空 |
| 2026-08-10 | 1.0.0 | 补齐每日对账+Brinson T+1适配+Carino多期链接+TCA 2.0滑点分布+五分量拆解+异常检测+报表生成 | 整合 Drovix 2026-05 TCA 2.0 + finantrix 2026-08 + Brinson T+1 适配 |
| 2026-08-10 | 1.1.0 | 新增 §3.7 三阶段 TCA 循环+§3.8 IS 归因按 7 维度分解 | 整合 Quod Financial 2026-06-09 三阶段 TCA + OrderX 2026-07 reversion marks/selection bias + quant67 2026-05 IS 维度归因 |
| 2026-08-10 | 1.2.0 | 新增 §3.11 市场冲击模型族（I-Star/OW/Propagator 临时永久分离）+§3.12 Algo Wheel TCA 驱动算法路由 | 整合 Kissell-Glantz I-Star 2003 + Obizhaeva-Wang 2013 + Bouchaud Propagator 2004 + finantrix 2026-08 Algo Wheel + Gatheral 2010 无套利约束 |
