---
ttl: permanent
doc_type: architecture_view
title: 卖出流 spec
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.0.0"
date: 2026-08-10
topic: sell_flow
scope: 07_trading_decision_architecture
---

# 卖出流 spec

> **性质**：由 [00_index_trading_decision](00_index_trading_decision.md) G20 主题组派生，将卖出流的讨论要点落地为可施工的 spec + 伪代码。
> **施工图纪律**：本文档 status=active，对应模块允许施工。
> **2026-08 研究整合**：O'Neil 卖出法则；ATR 移动止损（trailing stop）；Implementation Shortfall 卖出滑点控制；tradingwyckoff 2026-01 Kill Switch 卖出路径；与回撤 Protocol（G16）和情绪周期（G21）联动。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G20 卖出流 spec |
| 所属 | 作战地图 07 |
| 依赖 | G19（[41_buy_flow](41_buy_flow.md)）、G16（[35_drawdown_protocol_impl](35_drawdown_protocol_impl.md)）、G21（[28_sentiment_cycle_trading](28_sentiment_cycle_trading.md)） |
| 对标 | 机构卖出纪律 / O'Neil 卖出法则 / Wyckoff 派发识别 |
| 正交性 | ⚠️ 情绪退潮卖出与 regime 协同（regime 给 Shrinkage，卖出逻辑在策略内） |
| 优先级 | P3 |
| 状态 | ✅ active — 止损/止盈/时间止损/情绪退潮/破位/分批卖出算法已定稿 |

## 2. 背景

### 2.1 项目处境

卖出比买入更难——买入是理性的选股决策，卖出涉及止损纪律、止盈贪婪、情绪控制。A 股 T+1 约束使得卖出决策必须在买入前就规划好（次日才能卖）。卖出流是策略盈利的最终兑现环节，卖出执行的优劣直接决定策略的实际收益。

### 2.2 核心问题

1. **止损方式选择**：固定百分比止损简单但忽略波动率；ATR 止损考虑波动率但参数敏感；移动止损能锁定利润但可能过早离场。
2. **止盈逻辑**：固定目标止盈简单但可能限制上行空间；移动止盈能跟踪趋势但回撤时才离场；分批止盈平衡两者。
3. **情绪退潮卖出**：情绪周期从"一致"转向"退潮"时，需主动减仓而非等止损触发——与 regime CRISIS/RECOVERY 协同。
4. **破位卖出**：技术破位（跌破均线/支撑/趋势线）是卖出信号，但需区分真破位和假破位。
5. **T+1 约束**：当日买入不可卖，卖出只能对 T-1 及更早持仓操作。

### 2.3 约束条件

- **A 股 T+1**：当日买入次日才能卖出
- **涨跌停板**：跌停时卖单可能无法成交，需挂单排队
- **与回撤 Protocol 联动**：回撤触发减仓/清仓时，卖出流需响应
- **与 Kill Switch 联动**：Kill Switch 触发时，卖出流执行强制平仓

## 3. 决策

### 3.1 架构定义

卖出流由触发层、规划层、执行层三层构成：

```
触发层: 止损检查 → 止盈检查 → 时间止损 → 情绪退潮 → 破位检查 → 回撤/Kill Switch 联动
                                                                        ↓
规划层: 卖出优先级排序 → 分批卖出规划 → 价格锚定 → 滑点控制
                                                                        ↓
执行层: 40_execution_broker → 限价/市价/排队 → 成交确认
```

### 3.2 止损触发算法

```python
from dataclasses import dataclass
from enum import Enum
import numpy as np

class StopLossType(Enum):
    FIXED_PERCENT = "fixed_percent"     # 固定百分比止损
    ATR_BASED = "atr_based"             # ATR 波动率止损
    TRAILING = "trailing"               # 移动止损（追踪最高价）
    MOVING_AVERAGE = "moving_average"   # 均线止损


@dataclass
class StopLossSignal:
    """止损信号。"""
    symbol: str
    triggered: bool
    stop_type: StopLossType
    stop_price: float
    current_price: float
    reason: str


def check_stop_loss(
    symbol: str,
    entry_price: float,           # 买入价
    current_price: float,         # 当前价
    highest_since_entry: float,   # 买入后最高价
    atr: float,                   # 当前 ATR 值
    stop_config: dict,            # 止损配置
) -> StopLossSignal:
    """止损触发检查——多方式止损。

    止损方式（按优先级）：
    1. 固定百分比止损：current < entry × (1 - stop_pct) → 触发
    2. ATR 止损：current < entry - N × ATR → 触发（N 通常 1.5-2.0）
    3. 移动止损：current < highest × (1 - trail_pct) → 触发（锁定利润）
    4. 均线止损：current < MA(N) → 触发

    ATR 止损优势（FerroQuant 2026-04）：
    - 考虑个股波动率差异，高波动股止损更宽，低波动股止损更紧
    - PositionSize = (AccountRisk% × Equity) / (StopDistance × ATR_multiplier × PointValue)
    """
    triggered = False
    stop_type = None
    stop_price = 0.0
    reason = ""

    # 方式 1：固定百分比止损
    fixed_pct = stop_config.get("fixed_percent", 0.05)  # 默认 5%
    fixed_stop = entry_price * (1 - fixed_pct)
    if current_price <= fixed_stop:
        triggered = True
        stop_type = StopLossType.FIXED_PERCENT
        stop_price = fixed_stop
        reason = f"fixed_{fixed_pct:.0%}_stop"

    # 方式 2：ATR 止损（如果配置了且未触发）
    atr_multiplier = stop_config.get("atr_multiplier", 2.0)
    if not triggered and atr > 0:
        atr_stop = entry_price - atr_multiplier * atr
        if current_price <= atr_stop:
            triggered = True
            stop_type = StopLossType.ATR_BASED
            stop_price = atr_stop
            reason = f"atr_{atr_multiplier}x_stop"

    # 方式 3：移动止损（追踪最高价，锁定利润）
    trail_pct = stop_config.get("trail_percent", 0.08)  # 默认 8% 回撤
    if not triggered and highest_since_entry > entry_price:
        trail_stop = highest_since_entry * (1 - trail_pct)
        if current_price <= trail_stop:
            triggered = True
            stop_type = StopLossType.TRAILING
            stop_price = trail_stop
            reason = f"trailing_{trail_pct:.0%}_from_high_{highest_since_entry:.2f}"

    # 方式 4：均线止损（如果配置了 ma_value）
    ma_value = stop_config.get("ma_value")
    if not triggered and ma_value is not None and ma_value > 0:
        if current_price <= ma_value:
            triggered = True
            stop_type = StopLossType.MOVING_AVERAGE
            stop_price = ma_value
            reason = f"ma_stop_{ma_value:.2f}"

    return StopLossSignal(
        symbol=symbol,
        triggered=triggered,
        stop_type=stop_type or StopLossType.FIXED_PERCENT,
        stop_price=stop_price,
        current_price=current_price,
        reason=reason,
    )
```

### 3.3 止盈逻辑算法

```python
@dataclass
class TakeProfitSignal:
    """止盈信号。"""
    symbol: str
    triggered: bool
    partial: bool               # 是否部分止盈（分批）
    sell_ratio: float           # 卖出比例（1.0=全卖，0.5=半仓）
    reason: str


def check_take_profit(
    symbol: str,
    entry_price: float,
    current_price: float,
    holding_days: int,
    target_return: float = 0.15,        # 目标收益率 15%
    partial_thresholds: list = None,    # 分批止盈阈值
) -> TakeProfitSignal:
    """止盈逻辑——分批止盈 + 目标止盈 + 移动止盈。

    分批止盈策略：
    - 涨 10%：卖出 30%（锁定部分利润）
    - 涨 20%：卖出 30%
    - 涨 30%：卖出 40%（或由移动止损接管）

    O'Neil 卖出法则：
    - 涨 20-25% 后减仓（除非非常强势）
    - 连续放量滞涨 → 卖出信号
    """
    if partial_thresholds is None:
        partial_thresholds = [
            (0.10, 0.30),   # 涨 10% 卖 30%
            (0.20, 0.30),   # 涨 20% 卖 30%
            (0.30, 0.40),   # 涨 30% 卖 40%
        ]

    current_return = (current_price - entry_price) / entry_price

    # 检查分批止盈阈值
    for threshold, ratio in partial_thresholds:
        if current_return >= threshold:
            return TakeProfitSignal(
                symbol=symbol,
                triggered=True,
                partial=True,
                sell_ratio=ratio,
                reason=f"partial_tp_{threshold:.0%}_sell_{ratio:.0%}"
            )

    # 目标止盈
    if current_return >= target_return:
        return TakeProfitSignal(
            symbol=symbol,
            triggered=True,
            partial=False,
            sell_ratio=1.0,
            reason=f"target_tp_{target_return:.0%}"
        )

    return TakeProfitSignal(
        symbol=symbol, triggered=False, partial=False, sell_ratio=0.0, reason=""
    )
```

### 3.4 时间止损算法

```python
def check_time_stop(
    symbol: str,
    holding_days: int,
    max_holding_days: int,
    current_return: float,
    min_return_to_continue: float = -0.02,  # 最低收益要求
) -> dict:
    """时间止损——持有期满且收益不达标则卖出。

    时间止损逻辑：
    - 持有期超过 max_holding_days 且收益 < min_return_to_continue → 卖出
    - 持有期超过 max_holding_days × 1.5 → 强制卖出（无论收益）
    - 持有期内收益已达止盈目标 → 提前止盈（不触发时间止损）
    """
    if holding_days >= max_holding_days * 1.5:
        return {"triggered": True, "reason": f"time_force_exit_{holding_days}d", "sell_ratio": 1.0}

    if holding_days >= max_holding_days:
        if current_return < min_return_to_continue:
            return {"triggered": True, "reason": f"time_stop_{holding_days}d_return_{current_return:.1%}", "sell_ratio": 1.0}

    return {"triggered": False, "reason": "", "sell_ratio": 0.0}
```

### 3.5 情绪退潮卖出算法

```python
def check_sentiment_ebb_sell(
    symbol: str,
    sentiment_phase: str,        # 情绪周期阶段（冰点/启动/发酵/一致/退潮）
    position_return: float,      # 当前持仓收益率
    consecutive_limit_down: int, # 连续跌停天数
) -> dict:
    """情绪退潮卖出——与情绪周期（G21）和 regime（CRISIS/RECOVERY）协同。

    卖出逻辑：
    - 情绪"退潮"阶段 → 主动减仓 50%（不等止损）
    - 情绪"一致"阶段 + 持仓盈利 → 减仓 30%（高潮退潮风险）
    - 连续跌停 → 强制卖出排队（T+1 仅对 T-1 持仓）
    - regime CRISIS → 全部减仓（通过 Shrinkage 联动）
    """
    if consecutive_limit_down >= 1:
        return {
            "triggered": True,
            "sell_ratio": 1.0,
            "reason": f"limit_down_{consecutive_limit_down}d_force_sell",
            "order_type": "limit_down_queue",  # 跌停价排队
        }

    if sentiment_phase == "退潮":
        return {
            "triggered": True,
            "sell_ratio": 0.5,
            "reason": "sentiment_ebbing_reduce_50%",
            "order_type": "market",
        }

    if sentiment_phase == "一致" and position_return > 0.05:
        return {
            "triggered": True,
            "sell_ratio": 0.3,
            "reason": "sentiment_consensus_take_profit_30%",
            "order_type": "market",
        }

    return {"triggered": False, "sell_ratio": 0.0, "reason": "", "order_type": ""}
```

### 3.6 破位卖出算法

```python
def check_breakdown_sell(
    symbol: str,
    current_price: float,
    ma_20: float,
    ma_60: float,
    support_level: float,        # 关键支撑位
    volume_ratio: float,         # 量比
    prev_close: float,
) -> dict:
    """破位卖出——技术破位识别和卖出信号。

    破位类型：
    1. 跌破 20 日均线 3% + 放量 → 破位卖出
    2. 跌破 60 日均线 → 中线破位卖出
    3. 跌破关键支撑位 + 放量 → 破位卖出
    4. 跳空低开 > 3% → 破位卖出

    假破位过滤：
    - 缩量跌破均线 → 可能假破位，观望 1 日
    - 放量跌破均线 → 真破位，立即卖出
    """
    # 跳空低开 > 3%
    gap_down = (prev_close - current_price) / prev_close
    if gap_down > 0.03:
        return {"triggered": True, "sell_ratio": 1.0,
                "reason": f"gap_down_{gap_down:.1%}"}

    # 跌破 60 日均线（中线破位）
    if current_price < ma_60 * 0.98:
        return {"triggered": True, "sell_ratio": 1.0,
                "reason": f"break_ma60_{ma_60:.2f}"}

    # 跌破 20 日均线 + 放量
    if current_price < ma_20 * 0.97 and volume_ratio > 1.2:
        return {"triggered": True, "sell_ratio": 0.5,
                "reason": f"break_ma20_vol_{volume_ratio:.1f}"}

    # 跌破关键支撑 + 放量
    if current_price < support_level * 0.98 and volume_ratio > 1.5:
        return {"triggered": True, "sell_ratio": 1.0,
                "reason": f"break_support_{support_level:.2f}_vol_{volume_ratio:.1f}"}

    # 缩量跌破 20 日均线 → 观望（假破位可能）
    if current_price < ma_20 * 0.97 and volume_ratio < 0.8:
        return {"triggered": False, "sell_ratio": 0.0,
                "reason": "low_vol_break_ma20_observe"}

    return {"triggered": False, "sell_ratio": 0.0, "reason": ""}
```

### 3.7 卖出优先级与分批卖出规划

```python
def prioritize_and_plan_sells(
    positions: list[dict],       # 持仓列表 [{symbol, entry_price, current_price, holding_days, ...}]
    market_data: dict,           # 市场数据 {symbol: {ma_20, ma_60, atr, volume_ratio, ...}}
    sentiment_phase: str,
    drawdown_level: int,         # 回撤级别 0-4
    kill_switch_active: bool,
) -> list[dict]:
    """卖出优先级排序与分批规划——多触发源综合排序。

    优先级（从高到低）：
    1. Kill Switch 触发 → 强制全卖（不可覆盖）
    2. 回撤 Level 4 清仓 → 强制全卖
    3. 回撤 Level 3 停仓 → 卖出超配部分
    4. 连续跌停 → 排队卖出
    5. 固定百分比止损 → 全卖
    6. ATR 止损 → 全卖
    7. 情绪退潮 → 减仓 50%
    8. 破位卖出 → 全卖/半卖
    9. 分批止盈 → 部分卖出
    10. 时间止损 → 全卖
    """
    sell_orders = []

    for pos in positions:
        symbol = pos["symbol"]
        entry = pos["entry_price"]
        current = pos["current_price"]
        holding = pos["holding_days"]
        highest = pos.get("highest_since_entry", entry)
        md = market_data.get(symbol, {})

        sell_signal = {"symbol": symbol, "orders": [], "priority": 0}

        # 优先级 1-2：Kill Switch / 回撤 Level 4 → 强制全卖，跳过个股检查（全仓已含个股）
        # 注意：v1.0.0 使用 elif 结构导致 Level 3 时跳过所有个股止损/破位检查，
        #       v1.1.0 修复：Level 3 超配削减 + 个股止损/破位可同时触发（止损优先级 5 高于削减 3，
        #       执行层取 max ratio → 止损 100% 覆盖削减 50%，符合"风险优先"原则）
        if kill_switch_active or drawdown_level >= 4:
            sell_signal["orders"].append({"type": "force_flatten", "ratio": 1.0,
                                          "priority": 1, "reason": "kill_switch_or_dd_level4"})
            sell_signal["priority"] = 1

        else:
            # 优先级 3：回撤 Level 3 超配削减（组合层动作，不跳过个股检查）
            if drawdown_level == 3:
                sell_signal["orders"].append({"type": "reduce_overweight", "ratio": 0.5,
                                              "priority": 3, "reason": "dd_level3_reduce"})
                sell_signal["priority"] = 3

            # 优先级 4-10：个股信号逐项检查（Level 3 和 Normal 均执行）
            atr = md.get("atr", 0)
            stop_config = pos.get("stop_config", {"fixed_percent": 0.05, "atr_multiplier": 2.0, "trail_percent": 0.08})

            # 止损（优先级 5）——Level 3 时止损 100% 覆盖削减 50%，执行层取 max ratio
            sl = check_stop_loss(symbol, entry, current, highest, atr, stop_config)
            if sl.triggered:
                sell_signal["orders"].append({"type": "stop_loss", "ratio": 1.0,
                                              "priority": 5, "reason": sl.reason})
                sell_signal["priority"] = max(sell_signal["priority"], 5)

            # 止盈
            tp = check_take_profit(symbol, entry, current, holding)
            if tp.triggered and sell_signal["priority"] < 9:
                sell_signal["orders"].append({"type": "take_profit", "ratio": tp.sell_ratio,
                                              "priority": 9, "reason": tp.reason})
                sell_signal["priority"] = max(sell_signal["priority"], 9)

            # 时间止损
            ts = check_time_stop(symbol, holding, pos.get("max_holding", 30),
                                 (current - entry) / entry)
            if ts["triggered"] and sell_signal["priority"] < 10:
                sell_signal["orders"].append({"type": "time_stop", "ratio": ts["sell_ratio"],
                                              "priority": 10, "reason": ts["reason"]})
                sell_signal["priority"] = max(sell_signal["priority"], 10)

            # 情绪退潮
            se = check_sentiment_ebb_sell(symbol, sentiment_phase,
                                          (current - entry) / entry,
                                          pos.get("consecutive_limit_down", 0))
            if se["triggered"] and sell_signal["priority"] < 7:
                sell_signal["orders"].append({"type": "sentiment_ebb", "ratio": se["sell_ratio"],
                                              "priority": 7, "reason": se["reason"],
                                              "order_type": se.get("order_type", "market")})
                sell_signal["priority"] = max(sell_signal["priority"], 7)

            # 破位
            bd = check_breakdown_sell(symbol, current, md.get("ma_20", current),
                                      md.get("ma_60", current), md.get("support", current),
                                      md.get("volume_ratio", 1.0), md.get("prev_close", current))
            if bd["triggered"] and sell_signal["priority"] < 8:
                sell_signal["orders"].append({"type": "breakdown", "ratio": bd["sell_ratio"],
                                              "priority": 8, "reason": bd["reason"]})
                sell_signal["priority"] = max(sell_signal["priority"], 8)

        # 同一标的多订单合并：执行层取最高优先级 + 最大卖出比例
        if sell_signal["orders"]:
            sell_orders.append(sell_signal)

    # 按优先级排序（数字越小优先级越高）
    sell_orders.sort(key=lambda x: x["priority"])
    return sell_orders
```

### 3.8 T+1 卖出约束处理

T+1 结算约束下的卖出规则：

| 持仓类型 | 可卖出 | 处理 |
|---|---|---|
| **T-1 及更早持仓** | ✅ 可卖 | 正常执行卖出信号 |
| **T 日新买入** | ❌ 不可卖 | 卖出信号记录，次日执行 |
| **跌停封板** | ⚠️ 排队 | 挂跌停价排队，可能无法成交 |
| **Kill Switch 触发** | T-1 持仓强制卖 | T 日新仓不可卖，次日强制 |

## 4. 考虑过的替代方案

| 方案 | 描述 | 拒绝理由 |
|---|---|---|
| **仅固定百分比止损** | 所有标的统一 5% 止损 | 忽略波动率差异，高波动股过早止损、低波动股过晚止损 |
| **仅移动止损** | 只用 trailing stop | 趋势初期过早离场，错失大趋势 |
| **自动止损无人工干预** | 纯算法止损 | Kill Switch 不可覆盖，但普通止损可人工延迟一日（极端情况） |
| **一次性全卖** | 止损/止盈全仓卖出 | 大额订单冲击市场，分批卖出更优 |

## 5. 上限定义

| 上限 | 值 | 理由 |
|---|---|---|
| **固定止损** | 5% | 默认止损线 |
| **ATR 止损** | 2×ATR | 考虑波动率 |
| **移动止损** | 最高价回撤 8% | 锁定利润 |
| **时间止损** | 30 天 | 默认最大持有期 |
| **分批止盈** | 10%/20%/30% 三档 | 平衡锁定利润与上行空间 |

## 6. 待裁定

| 项 | 暂缓理由 | 重评条件 |
|---|---|---|
| **动态止损参数** | MVP 使用静态参数 | 积累 6 月实盘数据后校准 |
| **ML 卖出信号** | 机器学习卖出时机 | Phase 2+ 平台就绪 |
| **盘后固定价格卖出** | 2026-07-06 新规扩容 | 盘后流动性特征待观察 |

## 7. 待定问题（讨论要点对齐）

- [x] ① 卖出时序（止损/止盈/时间止损）→ §3.2-3.4 + §3.7 `prioritize_and_plan_sells` 优先级排序
- [x] ② 止损触发（固定%/移动/ATR）→ §3.2 `check_stop_loss` 四方式
- [x] ③ 止盈逻辑 → §3.3 `check_take_profit` 分批+目标
- [x] ④ 情绪退潮卖出（与 regime CRISIS/RECOVERY 协同）→ §3.5 `check_sentiment_ebb_sell`
- [x] ⑤ 破位卖出 → §3.6 `check_breakdown_sell` 四类破位+假破位过滤
- [x] ⑥ 分批卖出 → §3.3 分批止盈 + §3.7 优先级规划
- [x] ⑦ T+1 卖出约束 → §3.8 约束表
- [x] ⑧ 与回撤 Protocol 的联动 → §3.7 优先级 1-3（Kill Switch/Level 4/Level 3）

## 8. 引用

- [00_index_trading_decision](00_index_trading_decision.md) §3 G20
- [41_buy_flow](41_buy_flow.md)（G19，依赖项）
- [35_drawdown_protocol_impl](35_drawdown_protocol_impl.md)（G16 回撤 Protocol 联动）
- [28_sentiment_cycle_trading](28_sentiment_cycle_trading.md)（G21 情绪周期，退潮卖出输入）
- [40_execution_broker](40_execution_broker.md)（G22 执行层）
- battle_map_07_sell_flow（当前状态快照）
- **2026-08 研究引用**：
  - FerroQuant (2026-04) ATR 波动率定标止损
  - tradingwyckoff (2026-01) Kill Switch 卖出路径
  - O'Neil 卖出法则（涨 20-25% 减仓、放量滞涨卖出）
  - Perold (1988) Implementation Shortfall 卖出滑点控制

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行 |
| 2026-08-10 | 1.0.0 | 落地 spec 定稿 | 四方式止损(固定/ATR/移动/均线)+分批止盈+时间止损+情绪退潮+破位卖出+优先级排序+T+1约束算法化；整合 2026-08 研究（FerroQuant ATR/O'Neil/Kill Switch 联动） |
| 2026-08-10 | 1.1.0 | 修复 Level 3 elif 逻辑缺陷 | `prioritize_and_plan_sells` 中 `elif drawdown_level == 3` 跳过所有个股止损/破位检查；改为 `if` 结构使 Level 3 超配削减与个股止损可同时触发（止损 100% 覆盖削减 50%，符合风险优先原则） |
