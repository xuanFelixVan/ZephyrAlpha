---
ttl: permanent
doc_type: architecture_view
title: 买入流 spec
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.0.0"
date: 2026-08-10
topic: buy_flow
scope: 07_trading_decision_architecture
---

# 买入流 spec

> **性质**：由 [00_index_trading_decision](00_index_trading_decision.md) G19 主题组派生，将买入流的讨论要点落地为可施工的 spec + 伪代码。
> **施工图纪律**：本文档 status=active，对应模块允许施工。
> **2026-08 研究整合**：Almgren-Chriss 最优执行轨迹闭式解（2026 多源确认）；Implementation Shortfall（Perold 1988，IS framework）；TWAP/VWAP/POV/IS 选型边界（quant67.com 2026-05）；MAP-Elites 质量多样性执行（arXiv:2601.22113 2026-01）；Hawkes-LQ 自激励订单流（TechRxiv 2025-11，成本降 7.8-15.8%）。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G19 买入流 spec |
| 所属 | 作战地图 06 |
| 依赖 | G04-G06（选股+板块）、G12（仓位 [31_position_sizing](31_position_sizing.md)）、G16（风控 [35_drawdown_protocol_impl](35_drawdown_protocol_impl.md)） |
| 对标 | 机构分批建仓 / Wyckoff 吸筹时序 / Almgren-Chriss 最优执行 |
| 正交性 | ✅ 与 regime 正交 |
| 优先级 | P3 |
| 状态 | ✅ active — 分批建仓+突破失败降级+买入时序+价格锚定+资金分配算法已定稿 |

## 2. 背景

### 2.1 项目处境

买入流是策略信号到订单执行之间的桥梁。A 股 T+1 约束、涨跌停板、集合竞价制度使得买入时序和价格锚定尤为重要。不当的买入执行会导致显著滑点，侵蚀策略 alpha。

### 2.2 核心问题

1. **分批建仓 vs 一次性建仓**：大额订单一次性买入会冲击市场，需分批执行；但分批太多增加时间风险。
2. **板块回踩质量分级**：BM-BUY-04 买入优先级依赖板块回踩质量 A/B/C，不同等级对应不同建仓策略。
3. **突破失败降级**：买入信号基于突破，但突破可能失败，需设定降级规则（止损/观望/转空）。
4. **买入时序选择**：盘中/盘后/集合竞价各有优劣，需根据信号类型和流动性选择。
5. **资金分配到多标的**：多个标的同时触发买入信号时，如何分配有限资金。

### 2.3 约束条件

- **A 股 T+1**：当日买入次日才能卖出，买入前需充分确认信号
- **涨跌停板**：涨停封板时买不进，需排队或放弃
- **集合竞价**：9:15-9:25 可申报不可撤单（9:20 后），开盘价由集合竞价产生
- **价格笼子**：40_execution_broker v2.6.0+ 已实现 check_price_cage
- **资金预占**：40_execution_broker v2.6.0+ 已实现串行扣减+T+0 释放

## 3. 决策

### 3.1 架构定义

买入流由信号确认层、执行规划层、订单执行层三层构成：

```
信号确认: 策略信号 → 板块回踩质量分级(A/B/C) → 突破失败检查 → 买入确认
                                                                ↓
执行规划: 买入时序选择(盘中/盘后/竞价) → 分批建仓规划 → 资金分配 → 价格锚定
                                                                ↓
订单执行: 40_execution_broker → TWAP/VWAP/IS 算法 → 成交确认 → 滑点记录
```

### 3.2 板块回踩质量分级算法

```python
from enum import Enum
from dataclasses import dataclass

class PullbackQuality(Enum):
    """板块回踩质量分级（BM-BUY-04）。"""
    GRADE_A = "A"   # 优质回踩：缩量回踩均线、支撑明确、无破位
    GRADE_B = "B"   # 中等回踩：放量回踩但守住关键位
    GRADE_C = "C"   # 差质回踩：放量破位、支撑失效


@dataclass
class BuyExecutionPlan:
    """买入执行计划。"""
    symbol: str
    quality: PullbackQuality
    total_quantity: float
    batches: list[dict]      # [{quantity, timing, price_anchor, algorithm}]
    price_anchor: float      # 价格锚定
    max_slippage: float      # 最大允许滑点
    execution_window: str    # "intraday" / "closing_auction" / "after_close"


def evaluate_pullback_quality(
    sector_index,            # 板块指数 OHLCV
    ma_period: int = 20,     # 均线周期
    volume_shrink_threshold: float = 0.8,  # 缩量阈值（vs 5日均量）
) -> PullbackQuality:
    """板块回踩质量分级——BM-BUY-04 买入优先级依赖。

    A 级：缩量回踩均线、支撑明确、无破位 → 全仓建仓
    B 级：放量回踩但守住关键位 → 半仓建仓
    C 级：放量破位、支撑失效 → 观望/不建仓
    """
    close = sector_index['close'].values
    volume = sector_index['volume'].values
    ma = sector_index['close'].rolling(ma_period).mean().values

    current_price = close[-1]
    current_ma = ma[-1]
    prev_ma = ma[-2] if len(ma) > 1 else current_ma

    # 量比（vs 5 日均量）
    avg_vol_5d = np.mean(volume[-6:-1]) if len(volume) >= 6 else np.mean(volume)
    volume_ratio = volume[-1] / avg_vol_5d if avg_vol_5d > 0 else 1.0
    is_volume_shrink = volume_ratio < volume_shrink_threshold

    # 回踩均线判定
    near_ma = abs(current_price - current_ma) / current_ma < 0.02  # 距均线<2%

    # 均线方向（上升/走平/下降）
    ma_rising = current_ma > prev_ma

    # 破位判定
    is_breakdown = current_price < current_ma * 0.97  # 跌破均线3%以上

    if is_breakdown:
        return PullbackQuality.GRADE_C  # 破位→C级
    elif near_ma and is_volume_shrink and ma_rising:
        return PullbackQuality.GRADE_A  # 缩量回踩上升均线→A级
    elif near_ma and not is_volume_shrink and ma_rising:
        return PullbackQuality.GRADE_B  # 放量回踩但均线上升→B级
    else:
        return PullbackQuality.GRADE_C  # 其他→C级
```

### 3.3 分批建仓规划算法

```python
def plan_batch_buy(
    symbol: str,
    quality: PullbackQuality,
    total_quantity: float,
    current_price: float,
    available_budget: float,
    adv: float,                     # 日均成交额
    risk_per_trade: float = 0.02,   # 单笔风险
) -> BuyExecutionPlan:
    """分批建仓规划——根据回踩质量和流动性分批。

    分批策略（BM-BUY-04）：
    - A 级回踩：2 批（50% + 50%），间隔 1 日
    - B 级回踩：3 批（40% + 30% + 30%），间隔 1 日
    - C 级回踩：不建仓

    流动性约束：
    - 单批不超过 ADV 的 10%（避免冲击）
    - 若单批 > ADV 5%，使用 VWAP/TWAP 算法分批

    2026-08 研究整合：
    - Almgren-Chriss 最优执行轨迹闭式解：
      x(t) = X · sinh(κ·(T−t)) / sinh(κ·T)，κ = sqrt(λ·σ²/η)
      λ→0 退化为 TWAP（线性）；λ 大则前重后轻
    - quant67.com 2026-05 选型边界：
      TWAP: 流动性极差品种默认
      VWAP: 流动性充足、量曲线可预测
      IS: 大单、需平衡冲击与时序风险（显式风险厌恶参数）
    """
    if quality == PullbackQuality.GRADE_C:
        return BuyExecutionPlan(
            symbol=symbol, quality=quality, total_quantity=0,
            batches=[], price_anchor=current_price,
            max_slippage=0, execution_window="none"
        )

    # 分批比例
    if quality == PullbackQuality.GRADE_A:
        batch_ratios = [0.5, 0.5]
        execution_window = "intraday"
    else:  # GRADE_B
        batch_ratios = [0.4, 0.3, 0.3]
        execution_window = "intraday"

    # 流动性约束：单批不超过 ADV 的 10%
    max_batch_by_adv = adv * 0.10 / current_price  # 股数
    batches = []
    for i, ratio in enumerate(batch_ratios):
        batch_qty = total_quantity * ratio
        # 若单批超过 ADV 10%，需使用 VWAP/TWAP
        if batch_qty > max_batch_by_adv:
            algorithm = "VWAP"  # 大单用 VWAP 分批
        else:
            algorithm = "LIMIT"  # 小单用限价单

        batches.append({
            "batch_index": i,
            "quantity": batch_qty,
            "timing": f"day_{i}",  # 第 i 日执行
            "price_anchor": current_price,
            "algorithm": algorithm,
        })

    # 滑点控制：A 级 0.5%，B 级 1.0%
    max_slippage = 0.005 if quality == PullbackQuality.GRADE_A else 0.010

    return BuyExecutionPlan(
        symbol=symbol,
        quality=quality,
        total_quantity=total_quantity,
        batches=batches,
        price_anchor=current_price,
        max_slippage=max_slippage,
        execution_window=execution_window,
    )
```

### 3.4 突破失败降级算法

```python
@dataclass
class BreakoutStatus:
    """突破状态检查结果。"""
    status: str          # "SUCCESS" / "FAILED" / "PENDING"
    action: str          # "proceed" / "abort" / "reduce_size" / "wait"
    failure_reason: str


def check_breakout_status(
    symbol: str,
    breakout_price: float,       # 突破价位
    current_price: float,        # 当前价格
    days_since_breakout: int,    # 突破后天数
    volume_ratio: float,         # 量比（vs 均量）
    breakout_level_type: str,    # "box" / "trendline" / "ma" / "previous_high"
) -> BreakoutStatus:
    """突破失败降级检查——买入信号基于突破时的安全阀。

    突破失败判定：
    - 突破后 3 日内回落至突破价以下 → FAILED
    - 突破后放量但次日缩量回落 → FAILED
    - 突破后横盘不涨不跌 → PENDING（观望）

    降级动作：
    - FAILED → abort（不买入/止损）
    - PENDING → wait（观望 1-2 日）
    - SUCCESS → proceed（正常买入）
    """
    # 突破失败：回落至突破价以下
    if current_price < breakout_price * 0.98:  # 跌破突破价 2%
        return BreakoutStatus(
            status="FAILED",
            action="abort",
            failure_reason=f"price_{current_price:.2f}_below_breakout_{breakout_price:.2f}_2%"
        )

    # 突破后放量但次日缩量 → 假突破
    if days_since_breakout == 1 and volume_ratio < 0.7:
        return BreakoutStatus(
            status="FAILED",
            action="abort",
            failure_reason=f"volume_shrink_day1_ratio_{volume_ratio:.2f}"
        )

    # 突破后横盘 → 观望
    if days_since_breakout >= 2 and abs(current_price - breakout_price) / breakout_price < 0.01:
        if days_since_breakout <= 3:
            return BreakoutStatus(
                status="PENDING",
                action="wait",
                failure_reason=f"sideways_{days_since_breakout}d"
            )
        else:
            return BreakoutStatus(
                status="FAILED",
                action="abort",
                failure_reason=f"sideways_too_long_{days_since_breakout}d"
            )

    return BreakoutStatus(status="SUCCESS", action="proceed", failure_reason="")
```

### 3.5 买入时序选择算法

```python
def select_buy_timing(
    signal_type: str,           # "breakout" / "pullback" / "event" / "limit_up"
    liquidity: float,           # 流动性指标（ADV）
    urgency: str,               # "high" / "medium" / "low"
) -> str:
    """买入时序选择——盘中/盘后/集合竞价。

    A 股交易时段：
    - 9:15-9:25 集合竞价（开盘价产生）
    - 9:30-11:30 / 13:00-14:57 连续竞价
    - 14:57-15:00 收盘集合竞价
    - 15:05-15:30 盘后固定价格交易（2026-07-06 新规扩容至全 A 股）

    选型规则：
    - 突破信号 + 高紧迫 → 开盘集合竞价（抢入）
    - 回踩信号 + 低紧迫 → 盘中限价（等回踩到位）
    - 事件信号 + 中紧迫 → 盘中 VWAP（分散冲击）
    - 涨停打板 → 封板排队或开板瞬间
    - 大额低流动性 → 盘后固定价格（按收盘价）
    """
    if signal_type == "limit_up":
        return "limit_up_queue"  # 涨停排队/开板抢入
    elif signal_type == "breakout" and urgency == "high":
        return "opening_auction"  # 开盘集合竞价抢入
    elif signal_type == "pullback" and urgency == "low":
        return "intraday_limit"  # 盘中限价等回踩
    elif signal_type == "event" and urgency == "medium":
        return "intraday_vwap"  # 盘中 VWAP 分散
    elif liquidity < 1e7:  # 低流动性（ADV < 1000 万）
        return "after_close"  # 盘后固定价格
    else:
        return "intraday_limit"  # 默认盘中限价
```

### 3.6 资金分配到多标的算法

```python
def allocate_budget_to_stocks(
    signals: list[dict],         # [{symbol, score, quality, adv, price}]
    total_budget: float,         # 可用资金
    max_single: float = 0.05,    # 单标的上限（5%）
    max_sector: float = 0.20,    # 单行业上限（20%）
    sector_map: dict = None,     # {symbol: sector}
) -> list[dict]:
    """资金分配到多标的——按信号得分和回踩质量分配。

    分配逻辑：
    1. 按综合得分排序
    2. A 级回踩优先分配（全额）
    3. B 级回踩减半分配
    4. C 级不分配
    5. 单标的 ≤ 5%，单行业 ≤ 20%
    6. 流动性约束：单标的 ≤ ADV 10%
    """
    # 过滤 C 级
    valid_signals = [s for s in signals if s.get("quality") != "C"]
    if not valid_signals:
        return []

    # 按得分排序
    valid_signals.sort(key=lambda x: x["score"], reverse=True)

    allocations = []
    remaining_budget = total_budget
    sector_allocations = {}

    for sig in valid_signals:
        if remaining_budget <= 0:
            break

        symbol = sig["symbol"]
        score = sig["score"]
        quality = sig.get("quality", "B")
        adv = sig["adv"]
        price = sig["price"]
        sector = sector_map.get(symbol, "unknown") if sector_map else "unknown"

        # 基础分配：按得分比例
        base_alloc = remaining_budget * score / sum(s["score"] for s in valid_signals)

        # 回踩质量调整
        if quality == "A":
            quality_mult = 1.0
        else:  # B
            quality_mult = 0.5

        alloc = base_alloc * quality_mult

        # 单标的上限
        alloc = min(alloc, total_budget * max_single)

        # 单行业上限
        sector_used = sector_allocations.get(sector, 0)
        alloc = min(alloc, total_budget * max_sector - sector_used)

        # 流动性约束：≤ ADV 10%
        max_by_adv = adv * 0.10
        alloc = min(alloc, max_by_adv)

        if alloc > 0:
            quantity = alloc / price
            allocations.append({
                "symbol": symbol,
                "budget": alloc,
                "quantity": quantity,
                "quality": quality,
                "score": score,
            })
            remaining_budget -= alloc
            sector_allocations[sector] = sector_used + alloc

    return allocations
```

### 3.7 与 budget 的协同

买入流必须与 BudgetChangeHandler（G14，[33_budget_change_handler](33_budget_change_handler.md)）协同：

- **Tier 1 封锁**：BudgetChangeHandler Tier 1 触发时，买入流被阻断（不允许新仓）
- **Tier 2 rebalance**：Tier 2 触发时，买入流仅允许调仓（卖出超配、买入低配），不允许净新开仓
- **Tier 3 强裁**：Tier 3 触发时，买入流完全冻结
- **资金预占**：40_execution_broker v2.6.0 已实现串行扣减，买入流挂单前检查可用资金

## 4. 考虑过的替代方案

| 方案 | 描述 | 拒绝理由 |
|---|---|---|
| **一次性全仓买入** | 信号触发即全仓买入 | 大额订单冲击市场，滑点显著 |
| **固定 3 批均分** | 不考虑回踩质量均分 3 批 | A 级回踩应更快建仓，C 级不应建仓 |
| **仅用 TWAP** | 所有买入都用 TWAP | TWAP 隐含风险厌恶为零，不适合需要平衡冲击与时序风险的大单 |
| **仅用 IS** | 所有买入都用 Almgren-Chriss IS | IS 需估计波动率和冲击系数，小单过度工程 |
| **盘后固定价格全用** | 所有买入都用盘后固定价格 | 盘后流动性弱于盘中，仅适合低流动性品种 |

## 5. 上限定义

| 上限 | 值 | 理由 |
|---|---|---|
| **单批量** | ≤ ADV 10% | 避免市场冲击 |
| **单标的** | ≤ 5% 总资金 | 分散风险 |
| **单行业** | ≤ 20% 总资金 | 行业集中度控制 |
| **最大滑点** | A 级 0.5%，B 级 1.0% | 滑点超限取消订单 |

## 6. 待裁定

| 项 | 暂缓理由 | 重评条件 |
|---|---|---|
| **Almgren-Chriss IS 全实现** | 需估计 σ/η/γ 参数 | Phase 1.5+ 积累冲击成本数据后 |
| **MAP-Elites 质量多样性执行** | arXiv:2601.22113 前沿研究 | Phase 2+ RL 执行框架就绪 |
| **Hawkes-LQ 自激励订单流** | 需高频订单流数据 | Phase 2+ Level-2 数据就绪 |

## 7. 待定问题（讨论要点对齐）

- [x] ① 分批建仓（BM-BUY-04 买入优先级依赖板块回踩质量 A/B/C）→ §3.2 `evaluate_pullback_quality` + §3.3 `plan_batch_buy`
- [x] ② 突破失败降级 → §3.4 `check_breakout_status`
- [x] ③ 买入时序（盘中/盘后/集合竞价）→ §3.5 `select_buy_timing`
- [x] ④ 买入价格锚定 → §3.3 `price_anchor`（当前价格作为锚定基准）
- [x] ⑤ 资金分配到多标的 → §3.6 `allocate_budget_to_stocks`
- [x] ⑥ 与 budget 的协同 → §3.7 BudgetChangeHandler Tier 联动
- [x] ⑦ T+1 约束 → §2.3 约束条件 + 买入后次日才能卖出

## 8. 引用

- [00_index_trading_decision](00_index_trading_decision.md) §3 G19
- [22_sector_rotation_spec](22_sector_rotation_spec.md)（G06 板块回踩质量，输入依赖）
- [31_position_sizing](31_position_sizing.md)（G12 仓位，输入依赖）
- [33_budget_change_handler](33_budget_change_handler.md)（G14 budget 协同）
- [40_execution_broker](40_execution_broker.md)（G22 执行层，资金预占+价格笼子）
- [35_drawdown_protocol_impl](35_drawdown_protocol_impl.md)（G16 风控门控）
- battle_map_06_buy_flow（BM-BUY-04 当前状态快照）
- **2026-08 研究引用**：
  - Almgren-Chriss 闭式解（2026 多源确认：hftradingbook.com / youngju.dev / quant67.com）
  - quant67.com (2026-05) TWAP/VWAP/POV/IS 选型边界
  - arXiv:2601.22113 (2026-01) MAP-Elites 质量多样性执行 — 样本外 2.13 bps vs VWAP 5.23 bps
  - TechRxiv (2025-11) Hawkes-LQ 自激励订单流 — 成本降 7.8-15.8%
  - Perold (1988) Implementation Shortfall 框架

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行 |
| 2026-08-10 | 1.0.0 | 落地 spec 定稿 | 板块回踩质量分级+分批建仓+突破失败降级+买入时序+资金分配+budget协同算法化；整合 2026-08 研究（Almgren-Chriss/IS/MAP-Elites/Hawkes-LQ） |
