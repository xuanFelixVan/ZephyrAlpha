---
ttl: permanent
doc_type: architecture_view
title: RegimeMetaAllocator 参数与双轨P&L基础设施
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.0.0"
date: 2026-08-10
topic: regime_meta_allocator
scope: 07_trading_decision_architecture
---

# RegimeMetaAllocator 参数与双轨P&L基础设施

> **性质**：由 [00_index_trading_decision](00_index_trading_decision.md) G15 主题组派生，将 RegimeMetaAllocator 的讨论要点落地为可施工的 spec + 伪代码。
> **施工图纪律**：本文档分两层——§3.1-§3.3（数据基础设施：backtest_store + clean P&L 双轨记录）status=active，**不依赖 C1 验证**，可立即施工；§3.4-§3.6（分配参数校准）status=draft，须等 [11_regime_backtest_validation_plan](11_regime_backtest_validation_plan.md) C1 验证通过（Shrinkage 有效性）+ 首批策略产出 PnL 后才能校准。
> **2026-08 研究整合**：regime-aware QP 优化器+自适应 gamma+EWMA 协方差（LORD-ZYTHOZ 2026-04）；滚动自适应元策略——横截面分散度/集中度/信号密度预测最优模式（Kou 2026-05 preprint arXiv:2605.0517）；HMM-RL 3 态组合分配（arXiv:2605.27848 2026-05）；MacroHFT 记忆增强上下文感知 RL 元策略（Zong 2026）。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G15 RegimeMetaAllocator 参数 |
| 所属 | 作战地图 08 + 30_multi_strategy_concurrency §2.2 |
| 依赖 | §3.1-§3.3：无前置（数据基础设施先行）；§3.4-§3.6：⚠️ 11_regime_backtest_validation_plan C1 验证结果（Shrinkage 有效性）+ G04（PerformanceScore 需策略 PnL） |
| 对标 | Morwane risk-throttle / RegimeScore 移除裁定（30_multi_strategy_concurrency §2.2）/ LORD-ZYTHOZ regime-aware allocator / Kou regime-adaptive meta-policy |
| 正交性 | ⚠️ 本身就是 regime 节流的消费者；数据基础设施层与 regime 正交 |
| 优先级 | §3.1-§3.3：P1（数据基础设施先行）；§3.4-§3.6：P3（第二阶段，等 regime 验证 + 策略 track record） |
| 状态 | ✅ §3.1-§3.3 active（双轨P&L+backtest_store 已定稿）；§3.4-§3.6 draft（参数待 C1 验证后校准，MOD-PA-007 已登记） |

## 2. 背景

### 2.1 项目处境

RegimeMetaAllocator 是 ZephyrAlpha 多策略并发架构（Model A：独立账本 + firm 聚合）的核心分配器，负责在各策略 sleeve 之间动态分配资金。其分配公式为：

```
allocation_i = normalize(Base_i × PerformanceScore_i × Shrinkage_i)
```

其中 Shrinkage 由 [10_regime_detector_spec](10_regime_detector_spec.md) 产出，PerformanceScore 依赖策略 PnL track record。**核心矛盾**：分配器需要"干净的策略 P&L"来校准 PerformanceScore，但策略 P&L 在实盘前只能来自回测，而回测 P&L 往往包含市场冲击成本、滑点偏差、前瞻偏差等"噪声"，直接用于校准会导致分配失真。

因此，**数据基础设施层（backtest_store + clean P&L 双轨记录）是分配器校准的前置件**，必须先行施工——这与 C1 验证（Shrinkage 有效性）正交，不互相阻塞。

### 2.2 核心问题

1. **回测 P&L ≠ 实盘 P&L**：回测中无市场冲击、无滑点分布、无信令成本、无拒单成本，直接用回测 P&L 校准 PerformanceScore 会高估策略容量和 Sharpe。
2. **P&L 需按 regime 分桶**：策略在不同 regime 下表现差异巨大（如打板策略在 CONSENSUS 退潮期 vs FERMENTING 发酵期），单一 Sharpe 无法反映 regime 依赖性。
3. **双轨记录**：raw P&L（账面收益，含一切成本）与 clean P&L（剥离市场冲击/滑点/信令成本后的 alpha 收益）需并行记录，前者用于实盘对账，后者用于分配器校准。
4. **分配参数校准时机**：Base_i 先验权重、PerformanceScore 映射、Shrinkage 四档映射、floor/cap 边界均需 C1 验证通过 + 足够 track record 后才能定标。

### 2.3 约束条件

- **C1 验证前置**：Shrinkage 有效性须经 [11_regime_backtest_validation_plan](11_regime_backtest_validation_plan.md) Phase 1 验证，否则分配参数无校准基准
- **双轨 P&L 不可后补**：backtest_store 必须从首个回测起就记录 clean P&L，否则历史数据无法回填
- **floor/cap 硬约束**：floor≥5%（防止策略饿死）、cap≤40%（防止单一策略独大）
- **稀有态差异化**：稀有 regime（如 CRISIS）样本少，Shrinkage 收缩需比常见态更激进

## 3. 决策

### 3.1 backtest_store 算法（数据基础设施·active）

```python
from dataclasses import dataclass, field
from datetime import date
from enum import Enum
import numpy as np
from typing import Optional


class RegimeTag(Enum):
    """regime 标签——与 10_regime_detector_spec 12 态对齐。"""
    BULL_LOW_VOL = "bull_low_vol"
    BULL_HIGH_VOL = "bull_high_vol"
    RANGE_LOW_VOL = "range_low_vol"
    RANGE_HIGH_VOL = "range_high_vol"
    BEAR_LOW_VOL = "bear_low_vol"
    BEAR_HIGH_VOL = "bear_high_vol"
    CRISIS = "crisis"
    RECOVERY = "recovery"
    # ... 12 态完整枚举见 10_regime_detector_spec


@dataclass
class BacktestRecord:
    """单次回测记录——按 (strategy_id, regime_tag, trade_date) 唯一索引。"""
    # 标识
    backtest_id: str                    # 回测运行唯一 ID（含时间戳+参数哈希）
    strategy_id: str                    # 策略 ID（如 STR-DABAN-001）
    regime_tag: RegimeTag               # 当日 regime 标签
    trade_date: date                    # 交易日

    # Raw P&L（账面收益，含一切成本）
    raw_pnl: float                      # 当日账面盈亏（元）
    raw_return: float                   # 当日账面收益率
    raw_cumulative_pnl: float           # 累计账面盈亏

    # Clean P&L（剥离成本后的 alpha 收益，用于分配器校准）
    clean_pnl: float                    # 当日 alpha 盈亏（元）
    clean_return: float                 # 当日 alpha 收益率
    clean_cumulative_pnl: float         # 累计 alpha 盈亏

    # 成本拆解（raw - clean 的明细，TCA 2.0 五分量）
    cost_spread: float                  # 价差成本（bps）
    cost_market_impact: float           # 市场冲击成本（bps）
    cost_timing: float                  # 时机成本（bps）
    cost_opportunity: float             # 机会成本（bps，未成交部分）
    cost_signalling: float              # 信令成本（bps，30min post-trade 窗口反向漂移）
    cost_rejection: float               # 拒单成本（bps，拒单频率×价差）

    # 仓位与风险
    position_notional: float            # 当日持仓名义额
    turnover: float                     # 当日换手率
    max_drawdown: float                 # 截至当日最大回撤
    var_95: float                       # 当日 VaR 95%

    # 元数据
    backtest_params_hash: str           # 回测参数哈希（用于版本追溯）
    data_as_of: date                    # 数据截止日（PIT 铁律）


@dataclass
class BacktestStore:
    """回测结果存储——双轨 P&L + regime 分桶。

    设计原则：
    1. 不可变性：已写入记录不可修改（追加写入，append-only）
    2. PIT 铁律：每条记录带 data_as_of，防止前瞻偏差
    3. regime 分桶：P&L 按 regime_tag 分桶存储，支持 regime 条件 PerformanceScore
    4. 双轨并行：raw_pnl 与 clean_pnl 并行记录，前者对账后者校准
    5. 成本可追溯：clean_pnl 的每个扣减项都有明细（TCA 2.0 五分量）
    """
    records: dict[str, BacktestRecord] = field(default_factory=dict)  # {backtest_id: record}
    by_strategy_regime: dict[str, dict[str, list[str]]] = field(default_factory=dict)
    # by_strategy_regime[strategy_id][regime_tag] = [backtest_id, ...]

    def store(self, record: BacktestRecord) -> None:
        """追加写入回测记录——不可变。"""
        if record.backtest_id in self.records:
            raise ValueError(f"backtest_id {record.backtest_id} 已存在，backtest_store 不可变")
        self.records[record.backtest_id] = record

        # 建立 regime 分桶索引
        sid = record.strategy_id
        rtag = record.regime_tag.value
        if sid not in self.by_strategy_regime:
            self.by_strategy_regime[sid] = {}
        if rtag not in self.by_strategy_regime[sid]:
            self.by_strategy_regime[sid][rtag] = []
        self.by_strategy_regime[sid][rtag].append(record.backtest_id)

    def query_clean_pnl_series(
        self,
        strategy_id: str,
        regime_tag: Optional[RegimeTag] = None,   # None=全 regime
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> np.ndarray:
        """查询 clean P&L 序列——用于 PerformanceScore 校准。"""
        ids = []
        if regime_tag is not None:
            ids = self.by_strategy_regime.get(strategy_id, {}).get(regime_tag.value, [])
        else:
            for rtag_list in self.by_strategy_regime.get(strategy_id, {}).values():
                ids.extend(rtag_list)

        pnl_series = []
        for bid in ids:
            rec = self.records[bid]
            if start_date and rec.trade_date < start_date:
                continue
            if end_date and rec.trade_date > end_date:
                continue
            pnl_series.append(rec.clean_return)

        return np.array(pnl_series)

    def query_raw_pnl_series(
        self,
        strategy_id: str,
        regime_tag: Optional[RegimeTag] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> np.ndarray:
        """查询 raw P&L 序列——用于实盘对账。"""
        ids = []
        if regime_tag is not None:
            ids = self.by_strategy_regime.get(strategy_id, {}).get(regime_tag.value, [])
        else:
            for rtag_list in self.by_strategy_regime.get(strategy_id, {}).values():
                ids.extend(rtag_list)

        pnl_series = []
        for bid in ids:
            rec = self.records[bid]
            if start_date and rec.trade_date < start_date:
                continue
            if end_date and rec.trade_date > end_date:
                continue
            pnl_series.append(rec.raw_return)

        return np.array(pnl_series)
```

### 3.2 clean P&L 双轨记录算法（数据基础设施·active）

```python
@dataclass
class CostDecomposition:
    """TCA 2.0 五分量成本拆解（Drovix 2026-05 + finantrix 2026-08）。

    核心原则（Drovix Research 2026-05-27）：
    - 滑点是分布而非均值，需报告 median/p90/p99
    - IS 不能报告单一数字，需拆解为 spread/impact/timing/opportunity/signalling
    - 信令成本：成交后 30 分钟反向漂移（被对手读盘的成本）
    - 拒单成本：拒单频率 × (拒单价 - 下一可执行价)，转 bps

    finantrix TCA 2.0（2026-08-08）：
    - pre-trade TCA 驱动路由决策，post-trade TCA 验证执行质量
    - 同一成本模型 before/during/after 三阶段复用
    """
    spread_bps: float            # 半价差成本
    impact_temp_bps: float       # 临时市场冲击（部分回弹）
    impact_perm_bps: float       # 永久市场冲击（信息泄露）
    timing_bps: float            # 时机成本（执行期间反向漂移）
    opportunity_bps: float       # 机会成本（未成交部分）
    signalling_bps: float        # 信令成本（成交后30min反向漂移）
    rejection_bps: float         # 拒单成本（拒单频率×价差损失）

    @property
    def total_bps(self) -> float:
        return (self.spread_bps + self.impact_temp_bps + self.impact_perm_bps
                + self.timing_bps + self.opportunity_bps
                + self.signalling_bps + self.rejection_bps)


def compute_clean_pnl(
    raw_pnl: float,                      # 账面盈亏（元）
    position_notional: float,            # 持仓名义额（元）
    cost: CostDecomposition,             # TCA 2.0 五分量成本拆解
) -> tuple[float, float]:
    """clean P&L 计算——从 raw P&L 剥离执行成本得到 alpha 收益。

    返回 (clean_pnl, clean_return)
    - clean_pnl = raw_pnl - 总执行成本（元）
    - clean_return = clean_pnl / position_notional

    双轨记录意义：
    - raw P&L 用于实盘对账（投资者看到的真实收益）
    - clean P&L 用于分配器校准（策略本身的 alpha 能力，剥离执行噪声）

    注意：clean P&L 是"理论 alpha"，实盘永远达不到（因为执行成本不可避免），
    但它反映了策略信号的纯预测力，是 PerformanceScore 的正确输入。
    """
    if position_notional <= 0:
        return 0.0, 0.0

    # 成本从 bps 转为元
    total_cost_bps = cost.total_bps
    total_cost_yuan = position_notional * total_cost_bps / 10000.0

    clean_pnl = raw_pnl - total_cost_yuan
    clean_return = clean_pnl / position_notional

    return clean_pnl, clean_return


def compute_signalling_cost(
    fill_prices: list[float],        # 各笔成交价
    fill_quantities: list[float],    # 各笔成交量
    mid_prices_30min_after: list[float],  # 各笔成交后30分钟中间价
    direction: int,                  # +1=买入, -1=卖出
) -> float:
    """信令成本计算——成交后 30 分钟反向漂移（Drovix 2026-05）。

    核心逻辑：
    - 买入后 30 分钟价格下跌 = 被对手读盘，信令成本为正
    - 卖出后 30 分钟价格上涨 = 被对手读盘，信令成本为正
    - 信令成本 = Σ(成交价 - 30min后中间价) × direction × 数量 / 名义额

    这是 TCA 2.0 相对 TCA 1.0 的关键升级：
    TCA 1.0 在 parent order 完成时停止测量，漏掉信令成本
    TCA 2.0 延长测量窗口至成交后 30 分钟，捕获信息泄露的长期成本
    """
    if not fill_prices or len(fill_prices) != len(fill_quantities):
        return 0.0

    total_notional = sum(p * q for p, q in zip(fill_prices, fill_quantities))
    if total_notional <= 0:
        return 0.0

    signalling_loss = 0.0
    for i, (fill_price, qty) in enumerate(zip(fill_prices, fill_quantities)):
        if i >= len(mid_prices_30min_after):
            break
        mid_after = mid_prices_30min_after[i]
        # 买入后价格下跌 → 损失；卖出后价格上涨 → 损失
        price_move = (fill_price - mid_after) * direction
        signalling_loss += price_move * qty

    # 转为 bps
    signalling_bps = -signalling_loss / total_notional * 10000  # 负损失=正成本
    return max(0.0, signalling_bps)


def compute_rejection_cost(
    rejection_rate: float,           # 拒单率（0-1）
    rejected_prices: list[float],    # 被拒单的报价
    next_executable_prices: list[float],  # 拒单后下一可执行价
    direction: int,                  # +1=买入, -1=卖出
) -> float:
    """拒单成本计算——拒单率转为 bps 成本（Drovix 2026-05）。

    核心逻辑：
    - 拒单不是二元事件，有三种可测量成本：
      1. 重新报价的时间延迟
      2. 延迟期间的价格漂移（adverse selection，结构性正向）
      3. 向拒单场所泄露的意图信息
    - 拒单成本 = Σ(下一可执行价 - 拒单价) × direction / 名义额

    决策级 TCA（Drovix）：
    - 2% 拒单率 + 不对称 adverse selection 可能比 5% 拒单率 + 对称行为更贵
    - 单看拒单率百分比没有意义，必须转为 bps 成本
    """
    if not rejected_prices or rejection_rate <= 0:
        return 0.0

    total_loss = 0.0
    for rej_price, next_price in zip(rejected_prices, next_executable_prices):
        # 买入被拒后下一可执行价更高 → 损失；卖出被拒后下一可执行价更低 → 损失
        adverse_move = (next_price - rej_price) * direction
        total_loss += adverse_move

    # 拒单成本 = 平均不利漂移 × 拒单率（bps）
    avg_adverse_bps = total_loss / len(rejected_prices) / rejected_prices[0] * 10000 if rejected_prices[0] > 0 else 0
    rejection_bps = avg_adverse_bps * rejection_rate
    return max(0.0, rejection_bps)
```

### 3.3 PerformanceScore 计算（数据基础设施·active）

```python
@dataclass
class PerformanceScore:
    """策略 PerformanceScore——基于 clean P&L 的 regime 条件 Sharpe 映射。

    分配公式：allocation_i = normalize(Base_i × PerformanceScore_i × Shrinkage_i)
    PerformanceScore 范围 [0.5, 1.5]，映射 60 日 clean Sharpe。
    """
    strategy_id: str
    overall_score: float              # 全 regime 综合得分 [0.5, 1.5]
    regime_scores: dict[str, float]   # {regime_tag: score} regime 条件得分
    clean_sharpe_60d: float           # 60 日 clean Sharpe
    raw_sharpe_60d: float             # 60 日 raw Sharpe（对比用）
    sample_count: int                 # 60 日样本数
    confidence: str                   # "HIGH"(>40样本)/"MEDIUM"(20-40)/"LOW"(<20)


def compute_performance_score(
    strategy_id: str,
    backtest_store: BacktestStore,
    current_regime: RegimeTag,
    lookback_days: int = 60,
    risk_free_rate: float = 0.03,     # 年化无风险利率
) -> PerformanceScore:
    """PerformanceScore 计算——clean P&L regime 条件 Sharpe 映射 [0.5, 1.5]。

    映射规则（30_multi_strategy_concurrency §2.2）：
    - clean_sharpe ≥ 2.0 → 1.5（卓越）
    - clean_sharpe ≥ 1.0 → 1.2（优秀）
    - clean_sharpe ≥ 0.5 → 1.0（合格）
    - clean_sharpe ≥ 0.0 → 0.8（边际）
    - clean_sharpe < 0.0 → 0.5（差，但不归零，保留 floor）

    regime 条件得分：
    - 优先使用当前 regime 下的条件 Sharpe
    - 若当前 regime 样本不足（<20），降级用全 regime 综合 Sharpe
    - 样本不足时 confidence=LOW，Shrinkage 进一步收缩
    """
    from datetime import timedelta
    end_date = date.today()
    start_date = end_date - timedelta(days=lookback_days)

    # 全 regime clean P&L
    clean_returns = backtest_store.query_clean_pnl_series(
        strategy_id, regime_tag=None, start_date=start_date, end_date=end_date
    )
    raw_returns = backtest_store.query_raw_pnl_series(
        strategy_id, regime_tag=None, start_date=start_date, end_date=end_date
    )

    # 当前 regime 条件 clean P&L
    regime_clean_returns = backtest_store.query_clean_pnl_series(
        strategy_id, regime_tag=current_regime, start_date=start_date, end_date=end_date
    )

    sample_count = len(clean_returns)
    regime_sample_count = len(regime_clean_returns)

    # 综合 Sharpe（年化）
    if sample_count > 5:
        mean_clean = np.mean(clean_returns)
        std_clean = np.std(clean_returns)
        daily_rf = risk_free_rate / 252
        clean_sharpe = (mean_clean - daily_rf) / std_clean * np.sqrt(252) if std_clean > 0 else 0.0
    else:
        clean_sharpe = 0.0

    if len(raw_returns) > 5:
        mean_raw = np.mean(raw_returns)
        std_raw = np.std(raw_returns)
        daily_rf = risk_free_rate / 252
        raw_sharpe = (mean_raw - daily_rf) / std_raw * np.sqrt(252) if std_raw > 0 else 0.0
    else:
        raw_sharpe = 0.0

    # regime 条件 Sharpe
    if regime_sample_count >= 20:
        mean_regime = np.mean(regime_clean_returns)
        std_regime = np.std(regime_clean_returns)
        regime_sharpe = (mean_regime - daily_rf) / std_regime * np.sqrt(252) if std_regime > 0 else 0.0
        regime_confident = True
    else:
        regime_sharpe = clean_sharpe  # 降级
        regime_confident = False

    # Sharpe → Score 映射
    def sharpe_to_score(sharpe: float) -> float:
        if sharpe >= 2.0:
            return 1.5
        elif sharpe >= 1.0:
            return 1.2
        elif sharpe >= 0.5:
            return 1.0
        elif sharpe >= 0.0:
            return 0.8
        else:
            return 0.5

    overall_score = sharpe_to_score(clean_sharpe)

    # regime 条件得分
    regime_scores = {}
    for rtag in RegimeTag:
        rtag_returns = backtest_store.query_clean_pnl_series(
            strategy_id, regime_tag=rtag, start_date=start_date, end_date=end_date
        )
        if len(rtag_returns) >= 20:
            mean_r = np.mean(rtag_returns)
            std_r = np.std(rtag_returns)
            sharpe_r = (mean_r - daily_rf) / std_r * np.sqrt(252) if std_r > 0 else 0.0
            regime_scores[rtag.value] = sharpe_to_score(sharpe_r)
        else:
            regime_scores[rtag.value] = overall_score  # 样本不足降级

    # 置信度
    if sample_count >= 40:
        confidence = "HIGH"
    elif sample_count >= 20:
        confidence = "MEDIUM"
    else:
        confidence = "LOW"

    return PerformanceScore(
        strategy_id=strategy_id,
        overall_score=overall_score,
        regime_scores=regime_scores,
        clean_sharpe_60d=clean_sharpe,
        raw_sharpe_60d=raw_sharpe,
        sample_count=sample_count,
        confidence=confidence,
    )
```

### 3.4 RegimeMetaAllocator 分配算法（参数·draft，待 C1 验证）

> ⚠️ **本节 status=draft**：分配参数须等 [11_regime_backtest_validation_plan](11_regime_backtest_validation_plan.md) C1 验证通过（Shrinkage 有效性）+ 首批策略产出 PnL 后才能校准。以下伪代码为框架定型，参数值待校准。

```python
@dataclass
class AllocationResult:
    """分配结果。"""
    strategy_id: str
    allocation: float              # 归一化后分配比例 [0, 1]
    base: float                    # 先验权重
    performance_score: float       # [0.5, 1.5]
    shrinkage: float               # [0, 1] regime 节流系数
    raw_score: float               # base × perf × shrinkage（归一化前）
    floor_applied: bool            # 是否触底 floor
    cap_applied: bool              # 是否触顶 cap


def allocate_regime_meta(
    strategies: list[str],                # 策略 ID 列表
    base_weights: dict[str, float],       # {strategy_id: Base_i} 先验权重
    performance_scores: dict[str, PerformanceScore],
    shrinkage_map: dict[str, float],      # {strategy_id: Shrinkage_i} 来自 regime detector
    current_regime: RegimeTag,
    floor: float = 0.05,                  # 单策略下限 5%
    cap: float = 0.40,                    # 单策略上限 40%
    rare_regime_extra_shrink: float = 0.7,  # 稀有态额外收缩系数
) -> list[AllocationResult]:
    """RegimeMetaAllocator 分配算法。

    分配公式：allocation_i = normalize(Base_i × PerformanceScore_i × Shrinkage_i)

    参数说明（30_multi_strategy_concurrency §2.2）：
    - Base_i：先验权重，反映策略容量和战略重要性（如多因子 0.5 / 打板 0.2 / 事件驱动 0.3）
    - PerformanceScore_i：[0.5, 1.5]，60 日 clean Sharpe 映射（§3.3）
    - Shrinkage_i：[0, 1] regime 节流，四档映射（NORMAL=1.0/THROTTLED=0.7/HALTED=0.3/KILLED=0.0）
    - floor≥5%：防止策略饿死（保留最小跟踪能力）
    - cap≤40%：防止单一策略独大（集中度风险）

    稀有态差异化收缩（待 C1 验证后校准）：
    - CRISIS/RECOVERY 等稀有 regime 样本少，PerformanceScore 置信度低
    - 额外乘 rare_regime_extra_shrink（默认 0.7），进一步收缩
    - 避免稀有态的噪声 PerformanceScore 导致分配剧烈波动
    """
    raw_scores = {}
    results = []

    for sid in strategies:
        base = base_weights.get(sid, 1.0 / len(strategies))
        perf = performance_scores[sid]

        # 优先用 regime 条件得分
        perf_score = perf.regime_scores.get(current_regime.value, perf.overall_score)

        shrinkage = shrinkage_map.get(sid, 1.0)

        # 稀有态额外收缩
        if current_regime in (RegimeTag.CRISIS, RegimeTag.RECOVERY):
            shrinkage *= rare_regime_extra_shrink
            # 低置信度进一步收缩
            if perf.confidence == "LOW":
                shrinkage *= 0.5

        raw_score = base * perf_score * shrinkage
        raw_scores[sid] = raw_score

    # 归一化
    total_raw = sum(raw_scores.values())
    if total_raw <= 0:
        # 全部归零——均分 floor
        equal_alloc = 1.0 / len(strategies)
        for sid in strategies:
            results.append(AllocationResult(
                strategy_id=sid, allocation=equal_alloc,
                base=base_weights.get(sid, equal_alloc),
                performance_score=performance_scores[sid].overall_score,
                shrinkage=shrinkage_map.get(sid, 0.0),
                raw_score=0.0, floor_applied=True, cap_applied=False,
            ))
        return results

    for sid in strategies:
        allocation = raw_scores[sid] / total_raw

        floor_applied = False
        cap_applied = False

        # floor/cap 约束
        if allocation < floor:
            allocation = floor
            floor_applied = True
        elif allocation > cap:
            allocation = cap
            cap_applied = True

        results.append(AllocationResult(
            strategy_id=sid,
            allocation=allocation,
            base=base_weights.get(sid, 1.0 / len(strategies)),
            performance_score=performance_scores[sid].overall_score,
            shrinkage=shrinkage_map.get(sid, 1.0),
            raw_score=raw_scores[sid],
            floor_applied=floor_applied,
            cap_applied=cap_applied,
        ))

    # floor/cap 触发后需重新归一化（迭代收敛）
    return _renormalize_with_constraints(results, floor, cap)


def _renormalize_with_constraints(
    results: list[AllocationResult],
    floor: float,
    cap: float,
    max_iter: int = 10,
) -> list[AllocationResult]:
    """floor/cap 约束下的迭代重新归一化。

    触发 floor/cap 的策略固定在边界值，剩余策略在未约束空间内重新归一化。
    迭代直至收敛或达到 max_iter。
    """
    for _ in range(max_iter):
        fixed = [r for r in results if r.floor_applied or r.cap_applied]
        free = [r for r in results if not r.floor_applied and not r.cap_applied]

        if not fixed:
            break

        fixed_alloc = sum(r.allocation for r in fixed)
        remaining = 1.0 - fixed_alloc

        if remaining <= 0 or not free:
            break

        free_raw_sum = sum(r.raw_score for r in free)
        if free_raw_sum <= 0:
            equal = remaining / len(free)
            for r in free:
                r.allocation = equal
            break

        changed = False
        for r in free:
            new_alloc = r.raw_score / free_raw_sum * remaining
            if new_alloc < floor:
                r.allocation = floor
                r.floor_applied = True
                changed = True
            elif new_alloc > cap:
                r.allocation = cap
                r.cap_applied = True
                changed = True
            else:
                r.allocation = new_alloc

        if not changed:
            break

    return results
```

### 3.5 滚动自适应元策略（参数·draft，待 C1 验证）

> **2026-05 研究**（Kou arXiv:2605.0517 "When to Route? Regime-Adaptive Meta-Policies"）：
> 模块化决策系统暴露多个操作点，下游效用随 regime 变化。路由在高分散/去相关时有帮助；低信号时直接优化更安全；集中信号丰富时 alpha 增强有帮助。横截面分散度、集中度、信号密度可预测哪种模式占优。基于近期表现的滚动自适应元策略无需预知最优模式即可获得竞争性或更优的风险收益。

```python
@dataclass
class RegimeMetaPolicy:
    """滚动自适应元策略——基于近期表现选择分配模式（Kou 2026-05）。

    三种分配模式：
    1. DIRECT：直接归一化分配（§3.4），低信号环境更安全
    2. ROUTED：路由共识分配，高分散/去相关环境有帮助
    3. ALPHA_AUGMENTED：alpha 增强分配，集中信号丰富环境有帮助

    模式选择基于近期表现（滚动窗口），无需预知最优模式。
    """
    mode: str                      # "DIRECT" / "ROUTED" / "ALPHA_AUGMENTED"
    dispersion: float              # 横截面分散度（策略收益横截面 std）
    concentration: float           # 信号集中度（top-1 策略 raw_score 占比）
    signal_density: float          # 信号密度（非零信号策略占比）
    recent_performance: dict       # {mode: recent_sharpe} 各模式近期表现


def select_meta_policy(
    strategies: list[str],
    raw_scores: dict[str, float],
    recent_returns_by_mode: dict[str, np.ndarray],  # {mode: 近期收益序列}
    dispersion_threshold: float = 0.02,   # 分散度阈值
    concentration_threshold: float = 0.50,  # 集中度阈值
    density_threshold: float = 0.60,       # 密度阈值
    lookback: int = 20,                    # 滚动窗口
) -> RegimeMetaPolicy:
    """滚动自适应元策略选择（Kou 2026-05 preprint）。

    核心洞察：
    - 不是找一个万能最优配置，而是刻画每种模式何时最有效
    - 横截面分散度高 → ROUTED 占优（策略间去相关，路由能挑选）
    - 信号集中度高 → ALPHA_AUGMENTED 占优（集中信号丰富）
    - 两者都低 → DIRECT 占优（低信号环境，直接优化更安全）

    滚动自适应：
    - 基于近 lookback 日各模式的实际 Sharpe 选择当前模式
    - 无需预知最优模式，竞争性或更优的风险收益
    """
    # 计算市场特征
    scores_array = np.array([raw_scores.get(s, 0) for s in strategies])
    dispersion = float(np.std(scores_array)) if len(scores_array) > 1 else 0.0
    total_score = np.sum(np.abs(scores_array))
    concentration = float(np.max(np.abs(scores_array)) / total_score) if total_score > 0 else 0.0
    non_zero = np.sum(np.abs(scores_array) > 1e-8)
    signal_density = float(non_zero / len(strategies)) if strategies else 0.0

    # 各模式近期表现
    recent_perf = {}
    for mode, returns in recent_returns_by_mode.items():
        if len(returns) >= 5:
            mean_r = np.mean(returns[-lookback:])
            std_r = np.std(returns[-lookback:])
            recent_perf[mode] = (mean_r / std_r * np.sqrt(252)) if std_r > 0 else 0.0
        else:
            recent_perf[mode] = 0.0

    # 模式选择：先用市场特征做先验，再用近期表现修正
    if dispersion > dispersion_threshold:
        prior_mode = "ROUTED"
    elif concentration > concentration_threshold and signal_density > density_threshold:
        prior_mode = "ALPHA_AUGMENTED"
    else:
        prior_mode = "DIRECT"

    # 近期表现修正：若某模式近期 Sharpe 显著优于先验模式，切换
    best_mode = max(recent_perf, key=recent_perf.get)
    if recent_perf.get(best_mode, 0) > recent_perf.get(prior_mode, 0) + 0.3:
        selected_mode = best_mode
    else:
        selected_mode = prior_mode

    return RegimeMetaPolicy(
        mode=selected_mode,
        dispersion=dispersion,
        concentration=concentration,
        signal_density=signal_density,
        recent_performance=recent_perf,
    )
```

### 3.6 QP 优化器分配（参数·draft，远期增强）

> **2026-04 研究**（LORD-ZYTHOZ regime-aware-strategy-allocator）：
> 系统从 N 个独立策略引擎接收信号，根据实时市场状态评分效用，求解二次规划（QP）产生最优资金预算——每个周期，带完整风险门控。三个 regime 信号统治一切：波动率、相关性广度、趋势。regime 切换时自适应 gamma 自动重新校准风险厌恶。风险标志：OK → DE_RISK → KILL。

```python
def allocate_via_qp(
    strategies: list[str],
    expected_returns: np.ndarray,      # (N,) 各策略期望收益
    covariance_matrix: np.ndarray,     # (N, N) 策略收益协方差（EWMA）
    regime_gamma: float,               # 自适应风险厌恶系数
    floor: float = 0.05,
    cap: float = 0.40,
) -> np.ndarray:
    """QP 优化器分配——最大化效用 U = μᵀw - (γ/2)wᵀΣw（LORD-ZYTHOZ 2026-04）。

    约束：
    - Σw = 1（满仓）
    - floor ≤ w_i ≤ cap

    自适应 gamma（regime 切换时重新校准）：
    - BULL_LOW_VOL → γ=1.0（积极）
    - RANGE_HIGH_VOL → γ=2.0（中性）
    - CRISIS → γ=5.0（保守，风险厌恶激增）

    EWMA 协方差：
    - Σ_t = λ × Σ_{t-1} + (1-λ) × r_t r_tᵀ
    - λ=0.94（RiskMetrics 标准）
    - 相比等权协方差更 responsive

    注意：本算法为远期增强（Phase 1.5+），MVP 阶段使用 §3.4 的归一化分配。
    QP 需要 cvxpy 或 scipy.optimize，且需要足够 track record 估计协方差。
    """
    try:
        import cvxpy as cp
    except ImportError:
        # 降级到 §3.4 归一化分配
        return _fallback_normalize(expected_returns, floor, cap)

    n = len(strategies)
    w = cp.Variable(n)

    # 目标：最大化 μᵀw - (γ/2)wᵀΣw
    objective = cp.Maximize(
        expected_returns @ w - (regime_gamma / 2) * cp.quad_form(w, covariance_matrix)
    )

    # 约束
    constraints = [
        cp.sum(w) == 1,                    # 满仓
        w >= floor,                        # 下限
        w <= cap,                          # 上限
    ]

    prob = cp.Problem(objective, constraints)
    prob.solve()

    if prob.status != "optimal":
        return _fallback_normalize(expected_returns, floor, cap)

    return np.array(w.value)


def _fallback_normalize(
    expected_returns: np.ndarray,
    floor: float,
    cap: float,
) -> np.ndarray:
    """QP 降级——归一化期望收益。"""
    positive = np.maximum(expected_returns, 0)
    total = np.sum(positive)
    if total <= 0:
        return np.ones(len(expected_returns)) / len(expected_returns)
    weights = positive / total
    weights = np.clip(weights, floor, cap)
    weights = weights / np.sum(weights)  # 重新归一化
    return weights


def compute_adaptive_gamma(regime_tag: RegimeTag) -> float:
    """自适应风险厌恶系数——regime 切换时重新校准（LORD-ZYTHOZ 2026-04）。

    gamma 越高风险厌恶越强，分配越保守。
    """
    gamma_map = {
        RegimeTag.BULL_LOW_VOL: 1.0,      # 积极
        RegimeTag.BULL_HIGH_VOL: 1.5,     # 适度积极
        RegimeTag.RANGE_LOW_VOL: 1.5,     # 中性
        RegimeTag.RANGE_HIGH_VOL: 2.0,    # 适度保守
        RegimeTag.BEAR_LOW_VOL: 3.0,      # 保守
        RegimeTag.BEAR_HIGH_VOL: 4.0,     # 非常保守
        RegimeTag.CRISIS: 5.0,            # 极度保守
        RegimeTag.RECOVERY: 2.5,          # 谨慎乐观
    }
    return gamma_map.get(regime_tag, 2.0)
```

## 4. 考虑过的替代方案

| 方案 | 描述 | 拒绝理由 |
|---|---|---|
| **等权分配** | 所有策略等权 | 忽略策略绩效差异和 regime 节流；PerformanceScore + Shrinkage 更优 |
| **固定权重** | 按先验固定分配不调整 | 无法适应策略衰减和 regime 切换；动态分配更优 |
| **纯 RL 分配** | 强化学习端到端分配 | MVP 阶段过度工程，需大量数据；先归一化分配，Phase 2+ RL |
| **MacroHFT 元策略** | 记忆增强上下文感知 RL 元策略（Zong 2026） | 需 HFT 基础设施；Phase 2+ 远期评估 |
| **HMM-RL 3态分配** | 3态 HMM + RL 策略（arXiv:2605.27848） | regime detector 已有 12 态，3 态降级；RL 部分远期 |
| **纯 QP 优化器** | LORD-ZYTHOZ QP+自适应gamma | 需 cvxpy + 足够协方差数据；MVP 用归一化，Phase 1.5+ QP |
| **RegimeSense 4态重加权** | 4 regime 检测+策略池重加权（moh1tt 2026-03） | regime detector 已有 12 态更细；重加权逻辑可借鉴 |

## 5. 上限定义

| 上限 | 值 | 理由 |
|---|---|---|
| **单策略 floor** | ≥ 5% | 防止策略饿死，保留最小跟踪能力 |
| **单策略 cap** | ≤ 40% | 防止单一策略独大，集中度风险 |
| **PerformanceScore 范围** | [0.5, 1.5] | 差策略不归零（保留 floor），好策略不无限放大 |
| **Shrinkage 范围** | [0, 1] | KILLED=0 完全停止，NORMAL=1 不节流 |
| **稀有态额外收缩** | ×0.7 | 稀有 regime 样本少，PerformanceScore 置信度低 |
| **低置信度额外收缩** | ×0.5 | 样本不足时进一步保守 |
| **QP gamma 范围** | [1.0, 5.0] | BULL_LOW_VOL=1.0 积极，CRISIS=5.0 极度保守 |

**演进路径**：
- MVP（§3.1-§3.3 active）：双轨 P&L + backtest_store + PerformanceScore 计算
- Phase 1（§3.4 draft→active）：归一化分配 + Shrinkage 四档（C1 验证通过后）
- Phase 1.5（§3.5）：滚动自适应元策略（DIRECT/ROUTED/ALPHA_AUGMENTED）
- Phase 2（§3.6）：QP 优化器 + 自适应 gamma + EWMA 协方差

## 6. 待裁定

| 项 | 暂缓理由 | 重评条件 |
|---|---|---|
| **分配参数校准** | 须 C1 验证 Shrinkage 有效性 | [11_regime_backtest_validation_plan](11_regime_backtest_validation_plan.md) Phase 1 通过 |
| **Base_i 先验权重** | 需首批策略 track record | 首批 3 策略回测 P&L 产出后 |
| **Shrinkage 四档映射** | 须 C1 验证四档有效性 | C1 验证 + regime detector 产出稳定 Shrinkage |
| **QP 优化器** | 需 cvxpy + 协方差数据 | Phase 1.5+ 积累 6 月 P&L 数据后 |
| **滚动自适应元策略** | 需多模式 track record | Phase 1.5+ 各模式有足够样本后 |
| **MacroHFT RL 元策略** | 需 HFT 基础设施 | Phase 2+ LLM/RL 平台就绪后 |

## 7. 待定问题（讨论要点）

> 以下来自 00_index §3 G15 讨论要点，讨论时逐项对齐后落入 §3 决策。

- [x] ① 分配公式 `allocation_i = normalize(Base_i × PerformanceScore_i × Shrinkage_i)` → §3.4 定型
- [ ] ② Base_i 先验权重 → 待首批策略 track record 后校准
- [x] ③ PerformanceScore 60 日 Sharpe 映射 [0.5,1.5] → §3.3 定型
- [ ] ④ Shrinkage 置信度→风险节流映射（30_multi_strategy_concurrency §2.2 四档）→ 待 C1 验证
- [x] ⑤ floor≥5% / cap≤40% → §3.4 定型
- [x] ⑥ 稀有态差异化收缩 → §3.4 定型（×0.7 额外收缩）
- [ ] ⑦ 第二阶段上线时机 → 待 C1 验证 + 首批策略 P&L

## 8. 引用

- [00_index_trading_decision](00_index_trading_decision.md) §3 G15
- [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §2.2
- [11_regime_backtest_validation_plan](11_regime_backtest_validation_plan.md)（C1 验证，前置门槛）
- [10_regime_detector_spec](10_regime_detector_spec.md)（Shrinkage 产出方）
- [36_var_es_monitoring](36_var_es_monitoring.md)（VaR 风险监控）
- [54_reconciliation_attribution](54_reconciliation_attribution.md)（对账归因，raw P&L 消费方）
- battle_map_08_position_management（当前状态快照）

**外部研究引用**：
- LORD-ZYTHOZ regime-aware-strategy-allocator（2026-04）：QP 优化器+自适应 gamma+EWMA 协方差
- Kou et al. "When to Route? Regime-Adaptive Meta-Policies"（arXiv:2605.0517, 2026-05）：滚动自适应元策略
- "Regime-Based Portfolio Allocation Using HMM and RL"（arXiv:2605.27848, 2026-05）：3态 HMM+RL 组合分配
- Zong et al. "MacroHFT: Memory Augmented Context-aware RL"（2026）：记忆增强元策略
- Drovix Research "TCA That Actually Drives Decisions"（2026-05-27）：TCA 2.0 滑点分布+信令成本
- finantrix "Execution Algorithms and SOR — TCA 2.0"（2026-08-08）：pre-trade TCA 驱动路由

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行：由 00_index G15 讨论要点占位，参数等 C1 验证后校准 |
| 2026-08-10 | 1.0.0 | 补齐 backtest_store + clean P&L 双轨记录 + PerformanceScore + 分配算法框架 + 滚动自适应元策略 + QP 优化器 | 数据基础设施层（§3.1-§3.3）不依赖 C1 验证可立即施工；整合 2026-08 regime 分配最新研究（LORD-ZYTHOZ QP/Kou 滚动自适应/Drovix TCA 2.0） |
