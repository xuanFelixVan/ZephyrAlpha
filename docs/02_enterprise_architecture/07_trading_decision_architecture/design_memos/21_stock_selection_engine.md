---
ttl: permanent
doc_type: architecture_view
title: 选股引擎架构
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.2.0"
date: 2026-08-11
topic: stock_selection_engine
scope: 07_trading_decision_architecture
---

# 选股引擎架构

> **性质**：由 [00_index_trading_decision](00_index_trading_decision.md) G05 主题组派生，将选股引擎的讨论要点落地为可施工的 spec + 伪代码。
> **施工图纪律**：本文档 status=active，对应模块允许施工。
> **2026-08 研究整合**：A 股 mask-first 设计（arXiv:2507.07107，可交易性掩码前置，避免 alpha 污染与回测失真）；WorldQuant Alpha 工厂分层（Region→Universe→Data→Expression→Operators→Decay→Neutralization→Tests）；首批 3 策略（[20_first_batch_strategies](20_first_batch_strategies.md)）差异化候选池；打板双引擎融合（[24_daban_strategy_detail](24_daban_strategy_detail.md) BM-SEL-22~25）内部化定位（对齐 [30_multi_strategy_concurrency §7.3](30_multi_strategy_concurrency.md)）。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G05 选股引擎架构 |
| 所属 | 作战地图 05 |
| 依赖 | G04（策略定义，[20_first_batch_strategies](20_first_batch_strategies.md) 已定稿 v1.2.4） |
| 对标 | WorldQuant Alpha 工厂分层 / qstobody 多引擎 |
| 正交性 | ✅ 与 regime 正交 |
| 优先级 | P1 |
| 状态 | ✅ active — L0→L1→L2-C 分层 pipeline + 标准接口 + 候选池生成 + mask-first 过滤 + 量化强度评级 + StrategyBook 对接契约已定稿 |

## 2. 背景

### 2.1 项目处境

[20_first_batch_strategies](20_first_batch_strategies.md) 已定稿首批 3 策略（打板+多因子+事件驱动），三策略在信号源/换手率/容量/选股池/持仓周期五维差异化。3 个策略各有独立 StrategyBook（[30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) Model A），选股引擎是 StrategyBook 的"选股维度"（what）的统一载体——charter §3 约束四明确"策略=选股信号×组合权重×执行方式，独立优化"，本讨论只定义选股信号维度，不越界到仓位/执行。

打板链已建 production（BM-SEL-22 短线评分卡7维 / BM-SEL-23 游资接力6因子+情绪周期4+1 / BM-SEL-24 量化强度6维 / BM-SEL-25 双引擎融合6类决策），因子工厂已建 production（BM-SEL-02 因子计算/注册表/IC-IR评估/多因子合成），事件处理已建 production（BM-SEL-27 盘中实时事件处理）。但三策略的选股 pipeline 缺乏统一接口与分层架构——各策略各自为政会产生接口碎片化，下游 StrategyBook/FirmRiskAggregator 无法统一消费。

作战地图 05 已有 4 层漏斗雏形（BM-SEL-16 分级指标过滤 → BM-SEL-17 初筛漏斗 → BM-SEL-18 精筛评分 → BM-SEL-19 事件驱动分布筛选，约 7000→1200→300→50→30），但该漏斗是设计态、未与多策略 Model A 的 StrategyBook 接口对齐。本讨论将漏斗重构为 L0→L1→L2-C 分层 pipeline，与 StrategyBook 对接契约对齐。

### 2.2 核心问题

1. **三策略选股池差异极大**：打板=连板梯队窄池（高换手、容量小）；多因子=全市场（低换手、大容量）；事件驱动=动态事件池（中换手）。如何用统一 pipeline 架构承载差异化候选池？
2. **A 股可交易性约束前置**：ST/*ST/退市风险警示/次新/停牌/涨跌停封板/流动性失效等约束在 alpha 生成前就应过滤——若 alpha 算完才发现标的不可交易，浪费算力且污染信号（arXiv:2507.07107 mask-first 设计的核心论点）。
3. **量化强度评级缺乏统一框架**：BM-SEL-22（打板7维）/ BM-SEL-24（量化6维）/ 多因子因子打分各自评分，缺乏跨策略可比较的强度评级——而 firm 层自然叠加需要各 sleeve 输出可比较的 target_portfolio。
4. **双引擎融合的层级归属**：BM-SEL-25 双引擎融合（游资60%+量化40%，情绪周期自适应权重）是跨策略层还是打板策略内部？[30_multi_strategy_concurrency §7.3](30_multi_strategy_concurrency.md) 已裁定为打板内部，本讨论需确认边界并落入 spec。
5. **与 StrategyBook 的对接契约**：选股引擎输出什么数据结构？StrategyBook 如何消费？仓位算法（[31_position_sizing](31_position_sizing.md)）如何从 target_portfolio 导出粗仓位？

### 2.3 约束条件

- **A 股不能做空** → 选股只做多，不做多空对冲式优化
- **T+1 结算** → 选股信号盘后生成，次日才能执行，不支持日内翻转
- **涨跌停板** → 涨停封板时买不进，需在候选池生成/过滤阶段就标记封板状态
- **ST/*ST/退市风险警示** → 不可交易，必须 mask 掉
- **次新股波动大** → 上市 <60 天的标的流动性不稳定，多因子 sleeve 排除（打板/事件驱动保留，因次新连板与事件触发次新是常见标的）
- **容量差异**：打板单票几万~几十万（[30_multi_strategy_concurrency §1.3](30_multi_strategy_concurrency.md)），多因子承载主资金——选股引擎输出不携带最终仓位，仓位由 StrategyBook 粗仓位+firm 层 Kelly 精裁决决定（[31_position_sizing](31_position_sizing.md) 分层裁定）
- **AI 开发** → 接口标准化是生存项，非优化项——三策略 pipeline 统一接口才能并行迭代

## 3. 决策

### 3.1 架构定义：L0→L1→L2-C 分层选股 pipeline

选股引擎采用 4 层分层 pipeline（对标 WorldQuant Alpha 工厂分层 Region→Universe→Data→Expression→Operators→Decay→Neutralization→Tests，以及作战地图 05 已有 BM-SEL-16~19 漏斗雏形）：

```
L0 候选池生成（Candidate Pool Generation）
   - 按策略类型生成差异化候选池
   - 打板: 连板梯队池 | 多因子: 全市场池 | 事件驱动: 事件触发池
   - 对标 WorldQuant Region + Universe
                    ↓
L1 量化过滤（Quantitative Filtering / Mask-First）
   - A 股可交易性掩码前置（arXiv:2507.07107）
   - ST/*ST/退市/次新/停牌/涨跌停封板/流动性失效 mask
   - 对标 WorldQuant Data + Universe refinement
                    ↓
L2 量化强度评级与排序（Scoring & Ranking）
   - 多维度打分: alpha信号强度 + 板块强度 + 情绪周期 + 资金面
   - A~E 五级评级（BM-SEL-24-B）
   - 对标 WorldQuant Expression + Operators + Decay + Neutralization
                    ↓
C 组合输出（Portfolio Composition）
   - target_portfolio dataclass 输出
   - 交给 StrategyBook 做粗仓位 → firm 层 Kelly 精裁决
   - 对标 WorldQuant Tests + output
```

**分层裁定原则**（对齐 [30_multi_strategy_concurrency §2.1](30_multi_strategy_concurrency.md) 分层哲学）：
- **L0 差异化**：候选池生成按策略类型分化，不强行统一——打板窄池/多因子宽池/事件动态池各有生成逻辑
- **L1 统一化**：量化过滤 mask 跨策略共享（A 股可交易性约束与策略无关），避免重复实现；策略特定 mask（次新/涨停封板）按策略差异化
- **L2 半统一**：评分框架统一（v1.2.0 升级为 6 维 BM-SEL-24），各维度内部按策略差异化（连板梯队/游资接力维度策略特定，情绪/板块/资金/技术维度可共享）
- **C 标准化**：target_portfolio 输出接口完全统一，下游 StrategyBook/FirmRiskAggregator 无需感知策略类型

### 3.2 选股 pipeline 标准接口

```python
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Any


class StrategyType(Enum):
    """策略类型——决定 L0 候选池生成逻辑与 L1/L2 差异化参数。"""
    DABAN = "daban"                 # 打板：连板梯队窄池
    MULTIFACTOR = "multifactor"     # 多因子：全市场宽池
    EVENT_DRIVEN = "event_driven"   # 事件驱动：动态事件池


class SentimentPhase(Enum):
    """情绪周期4+1阶段（BM-SEL-23-B，选股引擎只读不判）。"""
    FREEZING = "冰点"
    STARTING = "启动"
    FERMENTING = "发酵"
    CONSENSUS = "一致"
    EBING = "退潮"


class RatingGrade(Enum):
    """量化强度评级 A~E 五级（BM-SEL-24-B，v1.2.0 阈值对齐 SignalQuality）。"""
    A = "A"  # 最强（≥85分），直接追
    B = "B"  # 较强（≥70分），可介入
    C = "C"  # 中等（≥55分），观望
    D = "D"  # 较弱（≥40分），不介入
    E = "E"  # 最弱（<40分）或硬风险，剔除


class SignalQuality(Enum):
    """信号质量 A~E 五级（v1.2.0 从早期 A/B/C 三级升级）。

    与 RatingGrade 阈值对齐：
    - ≥85 → A（优秀，强信号）
    - ≥70 → B（良好，可执行）
    - ≥55 → C（中等，观望）
    - ≥40 → D（较弱，不介入）
    - <40 或硬风险（ST/停牌/封板/流动性失效）→ E（剔除）

    硬风险标的直接判 E，不参与评分——对齐 mask-first 设计（§3.3.1）。
    """
    A = "A"  # 优秀（≥85）
    B = "B"  # 良好（≥70）
    C = "C"  # 中等（≥55）
    D = "D"  # 较弱（≥40）
    E = "E"  # 最弱（<40）或硬风险


@dataclass
class SelectionContext:
    """选股上下文——pipeline 的统一输入。

    封装选股所需的所有外部信号：
    - 交易日期与策略标识
    - alpha 信号（策略特定的原始信号，如因子打分/连板结构/事件冲击）
    - 情绪周期阶段（来自 BM-SEL-23-B，选股引擎只读不判）
    - 板块强度（来自 G06 板块轮动）
    - 资金面数据（主力净流入/北向/龙虎榜）
    - budget 占比（来自 RegimeMetaAllocator，选股引擎只收数字不读 regime 输出）

    对齐 charter §3 约束三：选股不读 regime 输出，只收 budget 数字。
    """
    trading_date: date                          # 交易日期
    strategy_id: str                            # 策略标识（如 "daban_sleeve_1"）
    strategy_type: StrategyType                 # 策略类型
    alpha_signals: dict[str, dict[str, Any]]    # {symbol: {signal_name: value}} 策略特定 alpha 信号
    sentiment_phase: SentimentPhase             # 情绪周期阶段（BM-SEL-23-B 输出，市场级）
    sector_strength: dict[str, float]           # {sector: strength_score} 板块强度（G06 输出）
    capital_flow: dict[str, dict[str, float]]   # {symbol: {main_net_inflow, northbound, net_buy_ratio...}}
    budget_ratio: float                         # 当前 sleeve 的 budget 占比 [0,1]（来自 RegimeMetaAllocator）
    universe_snapshot: dict[str, dict]          # {symbol: {is_st, is_suspended, list_days, adv, limit_status...}}
    mask_policy: "TradabilityMaskPolicy" = None  # 可交易性掩码策略（§3.3.1，默认 MODERATE；None→MODERATE）


@dataclass
class CandidatePool:
    """L0 候选池输出。

    按策略类型生成的差异化候选池。
    候选池只含 symbol 列表 + 生成元数据，不做任何过滤（过滤在 L1）。
    """
    strategy_type: StrategyType
    symbols: list[str]                          # 候选标的列表
    pool_source: str                            # 候选池来源（"consecutive_ladder" / "full_market" / "event_triggered"）
    generated_at: datetime
    pool_meta: dict[str, Any] = field(default_factory=dict)  # 候选池元数据（如连板梯队结构/事件类型）


@dataclass
class FilteredUniverse:
    """L1 过滤后 universe。

    A 股 mask-first 设计（arXiv:2507.07107）：
    可交易性掩码在 alpha 生成/评分前应用，确保 alpha 模型只见可交易标的。
    """
    symbols: list[str]                          # 过滤后可交易标的
    rejected: dict[str, str]                    # {symbol: reject_reason} 被剔除的标的及原因
    mask_applied: list[str]                     # 应用的掩码列表（如 ["st", "suspended", "limit_up_sealed"]）
    filtered_at: datetime = field(default_factory=datetime.now)


@dataclass
class ScoredCandidate:
    """L2 单标的评分结果。"""
    symbol: str
    total_score: float                          # 总分 [0, 100]
    rating: RatingGrade                         # A~E 五级评级
    score_breakdown: dict[str, float]           # 各维度得分明细（alpha/sector/sentiment/capital）
    signal_source: str                          # alpha 信号来源描述
    confidence: float                           # 信号置信度 [0, 1]（=total_score/100）
    rank: int = 0                               # 排名（1=最强）


@dataclass
class TargetPosition:
    """目标持仓——target_portfolio 的单标的条目。

    注意：signal_weight 是选股引擎输出的"信号权重"（基于得分排序+评级分层），
    不是最终仓位。最终仓位由 StrategyBook 粗仓位算法 + firm 层 Kelly 精裁决决定
    （[31_position_sizing](31_position_sizing.md) 分层裁定）。
    """
    symbol: str
    signal_weight: float                        # 信号权重 [0, 1]，基于得分排序+评级分层+归一化
    score: float                                # 量化强度总分
    rating: RatingGrade                         # 评级
    score_breakdown: dict[str, float]           # 评分明细（供归因）
    signal_source: str                          # 信号来源
    confidence: float                           # 置信度


@dataclass
class TargetPortfolio:
    """C 组合输出——选股引擎的最终输出，StrategyBook 的输入。

    这是选股引擎与 StrategyBook 的对接契约（§3.8）。
    target_portfolio 只含"买什么"（what），不含"买多少"（how much）——
    后者由 StrategyBook 粗仓位 + firm 层 Kelly 决定。
    """
    strategy_id: str                            # 策略标识
    strategy_type: StrategyType                 # 策略类型
    trading_date: date                          # 交易日期
    positions: list[TargetPosition]             # 目标持仓列表（按 signal_weight 降序）
    cash_weight: float                          # 现金权重 [0, 1]（无信号时为 1.0）
    pipeline_meta: dict[str, Any]               # pipeline 元数据（各层统计、掩码、评分分布等）
    generated_at: datetime


@dataclass
class SelectionOutput:
    """选股 pipeline 完整输出——含各层中间结果供归因与调试。"""
    target_portfolio: TargetPortfolio           # 最终组合输出
    candidate_pool: CandidatePool               # L0 候选池
    filtered_universe: FilteredUniverse         # L1 过滤后 universe
    scored_candidates: list[ScoredCandidate]    # L2 评分结果（排序后）
```

### 3.3 L0 候选池生成算法

L0 按策略类型生成差异化候选池。三策略的候选池来源、生成逻辑、池大小完全不同。

```python
def generate_candidate_pool(ctx: SelectionContext) -> CandidatePool:
    """L0 候选池生成——按策略类型分派。

    三策略候选池差异化设计（对齐 [20_first_batch_strategies](20_first_batch_strategies.md) §2.5）：
    - 打板：连板梯队窄池（高换手、容量小、情绪驱动）
    - 多因子：全市场宽池（低换手、大容量、横截面选股）
    - 事件驱动：动态事件池（中换手、中容量、离散事件触发）

    候选池生成不做任何过滤（过滤在 L1 mask-first），
    只负责"哪些标的进入选股视野"。
    """
    if ctx.strategy_type == StrategyType.DABAN:
        return _generate_daban_pool(ctx)
    elif ctx.strategy_type == StrategyType.MULTIFACTOR:
        return _generate_multifactor_pool(ctx)
    elif ctx.strategy_type == StrategyType.EVENT_DRIVEN:
        return _generate_event_pool(ctx)
    else:
        raise ValueError(f"未知策略类型: {ctx.strategy_type}")


def _generate_daban_pool(ctx: SelectionContext) -> CandidatePool:
    """打板候选池生成——连板梯队窄池。

    来源：BM-SEL-22~25 打板链的连板梯队识别
    （[24_daban_strategy_detail](24_daban_strategy_detail.md) §3.3 `identify_consecutive_ladder`）。
    候选标的：当日涨停且连板数 ≥ 1 的标的（首板+连板梯队）。

    池特征：
    - 窄池：通常 10-50 只（涨停家数 20-60 范围）
    - 高换手：1-2 天 convergence（[30_multi_strategy_concurrency §6.4](30_multi_strategy_concurrency.md)）
    - 容量极小：单票几万~几十万

    注意：候选池生成不判断情绪周期可交易性（那在策略内部执行层），
    只负责收集连板梯队标的。情绪周期可交易性由 L2 评分的 sentiment 维度体现。
    """
    # 从 alpha_signals 中提取连板梯队（由 BM-SEL-23 上游填充）
    consecutive_ladder = ctx.alpha_signals.get("__consecutive_ladder__", {})
    # consecutive_ladder 示例: {1: ["000001"], 2: ["000002", "000003"], 3: ["600001"], ...}

    symbols = []
    for board_count, stock_list in consecutive_ladder.items():
        if board_count >= 1:  # 首板及以上
            symbols.extend(stock_list)

    return CandidatePool(
        strategy_type=StrategyType.DABAN,
        symbols=symbols,
        pool_source="consecutive_ladder",
        generated_at=datetime.now(),
        pool_meta={
            "ladder_structure": consecutive_ladder,
            "highest_board": max(consecutive_ladder.keys()) if consecutive_ladder else 0,
            "pool_size": len(symbols),
        },
    )


def _generate_multifactor_pool(ctx: SelectionContext) -> CandidatePool:
    """多因子候选池生成——全市场宽池。

    来源：BM-SEL-02 因子工厂（全市场因子计算，[battle_map_05](../battle_map/battle_map_05_stock_selection.md) BM-SEL-02-A~L）。
    候选标的：沪深全 A 股（上证+深证+创业板+科创板）。

    池特征：
    - 宽池：约 5000 只（沪深 A 股全市场）
    - 低换手：3-5 天 convergence（[30_multi_strategy_concurrency §6.4](30_multi_strategy_concurrency.md)）
    - 大容量：承载主资金

    注意：全市场池在 L1 会被 mask-first 过滤大幅缩减
    （ST/次新/停牌/流动性不足等约占 20-30%）。
    """
    # 全市场 = universe_snapshot 中的所有标的
    symbols = list(ctx.universe_snapshot.keys())

    return CandidatePool(
        strategy_type=StrategyType.MULTIFACTOR,
        symbols=symbols,
        pool_source="full_market",
        generated_at=datetime.now(),
        pool_meta={
            "exchange_scope": "SH+SZ+CYB+KCB",
            "pool_size": len(symbols),
        },
    )


def _generate_event_pool(ctx: SelectionContext) -> CandidatePool:
    """事件驱动候选池生成——动态事件触发池。

    来源：BM-SEL-27 盘中实时事件处理（公告/新闻/龙虎榜/异动）。
    候选标的：当日有事件触发的标的（非固定池，即生即灭）。

    池特征：
    - 动态池：通常 5-30 只（视当日事件密度）
    - 中换手：2-3 天 convergence（[30_multi_strategy_concurrency §6.4](30_multi_strategy_concurrency.md)）
    - 中容量

    事件类型（[20_first_batch_strategies](20_first_batch_strategies.md) §2.4）：
    - 业绩公告 / 并购重组 / 政策利好 / 突发事件 / 龙虎榜异动
    """
    # 从 alpha_signals 中提取事件触发标的（由 BM-SEL-27 上游填充）
    event_triggers = ctx.alpha_signals.get("__event_triggers__", {})
    # event_triggers 示例: {"000001": {"event_type": "业绩预增", "impact": 0.8}, ...}

    symbols = list(event_triggers.keys())

    return CandidatePool(
        strategy_type=StrategyType.EVENT_DRIVEN,
        symbols=symbols,
        pool_source="event_triggered",
        generated_at=datetime.now(),
        pool_meta={
            "event_types": {sid: evt.get("event_type") for sid, evt in event_triggers.items()},
            "pool_size": len(symbols),
        },
    )
```

### 3.3.1 mask-first 可交易性掩码（TradabilityMaskPolicy）

mask-first 设计（arXiv:2507.07107v2）的核心论点：A 股结构性不可交易标的（ST/停牌/涨跌停封板/流动性失效）必须在 alpha 生成/评分前 mask，否则会从两个方向污染 pipeline——

1. **upstream contamination（上游污染）**：涨跌停封板标的的盘口/成交数据异常（封板期间无成交或成交价=涨跌停价），若进入 alpha 计算会污染因子横截面排名与 IC 评估，且污染会向下游传播（contamination upstream）。
2. **row_filter 虚增 IC**：在 alpha 算完后用 `row_filter` 过滤不可交易标的，会人为剔除"低分且不可交易"的样本，导致 IC 虚增约 +18%、样本外 Sharpe 虚高 -0.44（即回测 Sharpe 比真实高 0.44，是回测失真的主要来源）。

**mask-first 是单一最大贡献者**：在 ablation 研究中，从 row_filter 切换到 mask-first 单独贡献 +0.44 Sharpe（样本外），超过因子正交化（+0.18）与 IC-IR 加权（+0.12）等其他改进。因此 mask 贯穿 L0→L1→L2-C 全 pipeline：L0 候选池生成后立即应用 mask，L1 评分只在 mask 通过的标的上进行，L2-C 组合输出继承 mask 状态。

```python
class TradabilityMaskPolicy(Enum):
    """可交易性掩码策略——控制 mask 严格程度（§3.3.1）。

    三档策略对应不同 sleeve 的风险偏好与池特征：
    - STRICT：所有掩码全开（含次新/涨停封板），最保守，适合多因子宽池
    - MODERATE：共享掩码 + 策略特定掩码（默认，§3.4 表格），平衡
    - PERMISSIVE：仅 ST + 停牌 + 流动性，最宽松，适合打板窄池
    """
    STRICT = "strict"            # 全掩码（次新/涨停封板对所有策略剔除）
    MODERATE = "moderate"        # 默认：共享 + 策略特定（§3.4 _evaluate_reject）
    PERMISSIVE = "permissive"    # 仅硬约束（ST + 停牌 + 流动性）
```

`mask_policy` 字段已加入 `SelectionContext`（§3.2），pipeline 在 L1 调用 `apply_mask_first_filter(pool, ctx, mask_policy=ctx.mask_policy or TradabilityMaskPolicy.MODERATE)` 时读取策略。`apply_mask_first_filter` 的 policy-aware 实现见 §3.4（已升级为接受 `mask_policy` 参数）；`TradabilityMask` dataclass（含 `is_tradable` + `mask_reason` 汇总字段）亦见 §3.4。

**policy → 掩码集映射**：

| Policy | ST | 停牌 | 次新 | 涨停封板 | 流动性 | 适用 |
|---|---|---|---|---|---|---|
| STRICT | ✓剔除 | ✓剔除 | ✓剔除 | ✓剔除 | ✓剔除 | 多因子宽池（最保守） |
| MODERATE | ✓剔除 | ✓剔除 | 策略特定 | 策略特定 | ✓剔除 | 默认（三策略差异化，§3.4 表格） |
| PERMISSIVE | ✓剔除 | ✓剔除 | ✗保留 | ✗保留 | ✓剔除 | 打板窄池（最宽松） |

### 3.4 L1 量化过滤算法（A 股 mask-first 设计）

L1 采用 A 股 mask-first 设计（arXiv:2507.07107）：可交易性掩码在 alpha 生成/评分前应用，确保 alpha 模型只见可交易标的。

```python
@dataclass
class TradabilityMask:
    """A 股可交易性掩码——mask-first 设计核心。

    arXiv:2507.07107 核心思想：
    A 股有大量结构性不可交易标的（ST/停牌/涨跌停封板/流动性失效），
    若在 alpha 生成后才过滤，会导致：
    1. alpha 模型浪费算力在不可交易标的
    2. 不可交易标的的异常数据（如停牌期间的前收盘价）污染 alpha 信号
    3. 回测失真（回测假设可交易但实际不可交易，导致收益虚高）

    mask-first 方案：在 pipeline 最前端构建可交易性掩码，
    后续所有 alpha 计算/评分只在 mask 通过的标的上进行。

    跨策略共享：ST/停牌/流动性等约束与策略无关，mask 可复用。
    策略特定：次新/涨停封板按策略差异化处理。
    """
    is_st: bool                 # ST/*ST/退市风险警示
    is_suspended: bool          # 停牌
    is_new_stock: bool          # 次新股（上市 <60 天）
    is_limit_up_sealed: bool    # 涨停封板（买不进）
    is_limit_down_sealed: bool  # 跌停封板（卖不出，T+1 不涉及但标记）
    is_illiquid: bool           # 流动性不足（ADV < 阈值）
    reject_reason: str = ""     # 首要剔除原因（策略特定，由 _evaluate_reject 填充）
    is_tradable: bool = True    # 汇总：是否可交易（硬约束级，True=可进入 alpha 评分）
    mask_reason: str = ""       # 汇总：首要不可交易原因（is_tradable=False 时非空，对齐 §3.3.1）


def build_tradability_mask(
    symbol: str,
    snapshot: dict,             # universe_snapshot[symbol]
    strategy_type: StrategyType,
    adv_threshold: float = 5e6, # 流动性阈值（默认 500 万日均成交额）
    new_stock_days: int = 60,   # 次新定义（上市 <60 天）
) -> TradabilityMask:
    """构建单标的可交易性掩码——mask-first。

    策略差异化过滤（对齐 [20_first_batch_strategies](20_first_batch_strategies.md) §2.2-2.4 选股池范围）：
    - 打板：不排除次新（次新连板是常见标的），但排除 ST/停牌；涨停封板是目标不 mask
    - 多因子：排除次新（上市<60天因子不稳定）+ ST + 停牌 + 流动性不足 + 涨停封板（买不进）
    - 事件驱动：不排除次新（事件可能触发次新），排除 ST + 停牌 + 涨停封板（买不进）

    涨停封板特殊处理：
    - 打板策略：涨停封板是目标状态（要打板），不 mask，但标记（执行层排队/抢入）
    - 多因子/事件驱动：涨停封板买不进，mask 掉
    """
    is_st = snapshot.get("is_st", False) or snapshot.get("is_delisting_warning", False)
    is_suspended = snapshot.get("is_suspended", False)
    list_days = snapshot.get("list_days", 999)
    is_new_stock = list_days < new_stock_days
    adv = snapshot.get("adv", 0)
    is_illiquid = adv < adv_threshold

    # 涨跌停封板状态
    limit_status = snapshot.get("limit_status", "normal")
    is_limit_up_sealed = limit_status == "limit_up_sealed"
    is_limit_down_sealed = limit_status == "limit_down_sealed"

    # 汇总字段（硬约束级；策略特定原因由 _evaluate_reject 层叠加到 reject_reason）
    is_tradable = not (is_st or is_suspended or is_illiquid)
    mask_reason = ""
    if is_st:
        mask_reason = "st_or_delisting"
    elif is_suspended:
        mask_reason = "suspended"
    elif is_illiquid:
        mask_reason = "illiquid"

    return TradabilityMask(
        is_st=is_st,
        is_suspended=is_suspended,
        is_new_stock=is_new_stock,
        is_limit_up_sealed=is_limit_up_sealed,
        is_limit_down_sealed=is_limit_down_sealed,
        is_illiquid=is_illiquid,
        is_tradable=is_tradable,
        mask_reason=mask_reason,
    )


def apply_mask_first_filter(
    pool: CandidatePool,
    ctx: SelectionContext,
    mask_policy: TradabilityMaskPolicy = TradabilityMaskPolicy.MODERATE,
) -> FilteredUniverse:
    """L1 量化过滤——应用 mask-first 可交易性掩码（policy-aware，§3.3.1）。

    mask_policy 控制掩码严格程度（§3.3.1）：
    - STRICT：次新/涨停封板对所有策略剔除（最保守）
    - MODERATE：共享掩码 + 策略特定掩码（默认，下表）
    - PERMISSIVE：仅 ST + 停牌 + 流动性（最宽松）

    MODERATE 过滤规则（按策略类型差异化）：
    | 掩码 | 打板 | 多因子 | 事件驱动 |
    |---|---|---|---|
    | ST/*ST | ✗ 剔除 | ✗ 剔除 | ✗ 剔除 |
    | 停牌 | ✗ 剔除 | ✗ 剔除 | ✗ 剔除 |
    | 次新(<60天) | ✓ 保留 | ✗ 剔除 | ✓ 保留 |
    | 涨停封板 | ✓ 保留(目标) | ✗ 剔除 | ✗ 剔除 |
    | 流动性不足 | ✗ 剔除 | ✗ 剔除 | ✗ 剔除 |

    共享掩码（跨策略）：ST + 停牌 + 流动性——所有策略剔除
    策略特定掩码：次新/涨停封板——按策略差异化
    """
    rejected = {}
    passed = []

    for symbol in pool.symbols:
        snapshot = ctx.universe_snapshot.get(symbol, {})
        mask = build_tradability_mask(symbol, snapshot, pool.strategy_type)

        reject_reason = _evaluate_reject(mask, pool.strategy_type, mask_policy)
        if reject_reason:
            rejected[symbol] = reject_reason
        else:
            passed.append(symbol)

    mask_applied = ["st", "suspended", "new_stock", "limit_up_sealed", "illiquid"]

    return FilteredUniverse(
        symbols=passed,
        rejected=rejected,
        mask_applied=mask_applied,
    )


def _evaluate_reject(
    mask: TradabilityMask,
    strategy_type: StrategyType,
    mask_policy: TradabilityMaskPolicy = TradabilityMaskPolicy.MODERATE,
) -> str:
    """评估掩码是否触发剔除——按策略 + policy 差异化。

    返回空字符串=通过，非空=剔除原因。

    policy 调制（§3.3.1）：
    - STRICT：次新 + 涨停封板对所有策略剔除（最保守）
    - MODERATE：共享 + 策略特定（默认）
    - PERMISSIVE：仅 ST + 停牌 + 流动性（跳过次新/涨停封板）
    """
    # ===== 共享硬约束：ST + 停牌 + 流动性（所有 policy 剔除）=====
    if mask.is_st:
        return "st_or_delisting"
    if mask.is_suspended:
        return "suspended"

    # PERMISSIVE：仅硬约束，跳过次新/涨停封板
    if mask_policy == TradabilityMaskPolicy.PERMISSIVE:
        if mask.is_illiquid:
            return "illiquid"
        return ""

    # STRICT：次新 + 涨停封板对所有策略剔除
    if mask_policy == TradabilityMaskPolicy.STRICT:
        if mask.is_new_stock:
            return "new_stock_strict"
        if mask.is_limit_up_sealed:
            return "limit_up_sealed_strict"
        if mask.is_illiquid:
            return "illiquid"
        return ""

    # ===== MODERATE：策略特定掩码 =====
    if strategy_type == StrategyType.MULTIFACTOR:
        # 多因子：排除次新（因子不稳定）+ 涨停封板（买不进）+ 流动性不足
        if mask.is_new_stock:
            return "new_stock_multifactor"
        if mask.is_limit_up_sealed:
            return "limit_up_sealed_unbuyable"
        if mask.is_illiquid:
            return "illiquid"

    elif strategy_type == StrategyType.DABAN:
        # 打板：保留次新（次新连板常见）+ 保留涨停封板（目标状态）
        # 仅剔除流动性极度不足
        if mask.is_illiquid:
            return "illiquid_daban"

    elif strategy_type == StrategyType.EVENT_DRIVEN:
        # 事件驱动：保留次新（事件可能触发次新）+ 剔除涨停封板（买不进）+ 流动性不足
        if mask.is_limit_up_sealed:
            return "limit_up_sealed_unbuyable"
        if mask.is_illiquid:
            return "illiquid_event"

    return ""


def _loewin_orthogonalize(factor_matrix):
    """Löwdin 对称正交化——消除因子共线性，保留因子方向。

    公式：F_orth = F (F^T F)^{-1/2}

    对比 Gram-Schmidt（非对称，顺序敏感）：
    - Löwdin 对称正交化对所有因子平等对待，不依赖因子顺序
    - 正交化后各因子两两不相关，IC 评估更纯净
    - 保留因子的原始方向（旋转最小化），信息损失最小

    用于 L1 多因子 sleeve 的因子预处理（BM-SEL-02-G 因子正交化）。
    ablation 贡献：+0.18 Sharpe（仅次于 mask-first +0.44）。
    """
    import numpy as np
    F = np.asarray(factor_matrix, dtype=float)
    # 中心化（去均值）
    F = F - F.mean(axis=0, keepdims=True)
    # (F^T F)^{-1/2} via 对称特征分解：A = V Λ V^T → A^{-1/2} = V Λ^{-1/2} V^T
    FtF = F.T @ F
    eigvals, eigvecs = np.linalg.eigh(FtF)
    eigvals = np.clip(eigvals, 1e-10, None)  # 防奇异
    inv_sqrt = (eigvecs * (eigvals ** -0.5)) @ eigvecs.T
    F_orth = F @ inv_sqrt
    return F_orth


def _compute_ic_ir_weights(
    ic_history: dict[str, list[float]],  # {factor: [ic_t-Window..t-1]}
    min_window: int = 20,
) -> dict[str, float]:
    """滚动 IC-IR 动态权重——按各因子的信息系数信息比分配权重。

    IC-IR = mean(IC) / std(IC)（滚动窗口内）
    权重 ∝ max(IC-IR, 0)，归一化到 [0, 1]。

    对比等权（忽略因子质量差异）与 IC 加权（忽略 IC 稳定性）：
    - IC-IR 同时考虑 IC 的水平与稳定性，高且稳的因子获更高权重
    - 负 IC-IR 因子权重归零（剔除反向且不稳定的因子）
    - 滚动窗口适应因子衰减（IC 随时间漂移）

    ablation 贡献：+0.12 Sharpe。
    """
    positive_ir: dict[str, float] = {}
    for factor, ics in ic_history.items():
        if len(ics) < min_window:
            continue
        recent = ics[-min_window:]
        mean_ic = sum(recent) / len(recent)
        var_ic = sum((x - mean_ic) ** 2 for x in recent) / len(recent)
        std_ic = (var_ic ** 0.5) or 1e-8
        ir = mean_ic / std_ic
        if ir > 0:
            positive_ir[factor] = ir
    total_ir = sum(positive_ir.values()) or 1.0
    return {f: ir / total_ir for f, ir in positive_ir.items()}


def score_l1_multifactor(
    factor_values: dict[str, dict[str, float]],  # {symbol: {factor: value}}
    ic_history: dict[str, list[float]],          # {factor: [ic...]}
) -> dict[str, float]:
    """L1 多因子合成评分——Löwdin 正交化 + IC-IR 加权。

    pipeline：
    1. 因子矩阵组装 → Löwdin 对称正交化（消除共线性）
    2. IC-IR 动态权重计算（滚动窗口）
    3. 正交化后因子 × IC-IR 权重 → 综合得分
    4. 横截面排名归一化到 [0, 100]

    对齐 BM-SEL-02-H 多因子合成（[battle_map_05](../battle_map/battle_map_05_stock_selection.md)）。
    """
    import numpy as np
    symbols = list(factor_values.keys())
    factors = list(ic_history.keys())
    if not symbols or not factors:
        return {s: 0.0 for s in symbols}

    # 1. 组装因子矩阵 (N, K)
    F = np.array([[factor_values[s].get(f, 0.0) for f in factors] for s in symbols])

    # 2. Löwdin 正交化
    F_orth = _loewin_orthogonalize(F)

    # 3. IC-IR 权重
    weights = _compute_ic_ir_weights(ic_history)
    w_vec = np.array([weights.get(f, 0.0) for f in factors])

    # 4. 加权合成 + 横截面归一化到 [0, 100]
    composite = F_orth @ w_vec  # (N,)
    lo, hi = composite.min(), composite.max()
    if hi - lo > 1e-10:
        composite = (composite - lo) / (hi - lo) * 100.0
    else:
        composite = np.full_like(composite, 50.0)
    return {s: float(composite[i]) for i, s in enumerate(symbols)}
```

### 3.5 L2 量化强度评级算法

L2 对过滤后的 universe 做多维度打分，输出 A~E 五级评级与排序。评分框架跨策略统一——v1.2.0 从 4 维升级为 **6 维 BM-SEL-24**（连板梯队/游资接力/情绪周期/板块强度/资金流向/技术形态），各维度内部按策略差异化。下方先给出 v1.0 4维简化版（`compute_strength_score`，保留兼容旧调用方），再给出 v1.2.0 6维生产路径（`compute_six_dim_strength`）。

```python
@dataclass
class StrengthScore:
    """量化强度评分——4 维度统一框架。

    4 维度设计（跨策略统一框架，各维度内部策略差异化）：
    1. alpha 信号强度（策略特定）：打板=游资接力6因子+连板潜力7维双引擎融合
       / 多因子=因子综合得分 / 事件=事件冲击强度
    2. 板块强度（跨策略共享）：来自 G06 板块轮动
    3. 情绪周期（跨策略共享）：来自 BM-SEL-23-B 情绪周期4+1阶段
    4. 资金面（跨策略共享）：主力净流入/北向/龙虎榜净买率

    权重按策略类型差异化（对齐 [20_first_batch_strategies](20_first_batch_strategies.md) §2.5 差异化矩阵）：
    - 打板：alpha 40% + 板块 15% + 情绪 25% + 资金 20%（情绪驱动型）
    - 多因子：alpha 60% + 板块 15% + 情绪 5% + 资金 20%（alpha 主导型）
    - 事件驱动：alpha 50% + 板块 10% + 情绪 15% + 资金 25%（事件+资金驱动型）
    """
    alpha_strength: float       # 维度1：alpha 信号强度 [0, 100]
    sector_strength: float      # 维度2：板块强度 [0, 100]
    sentiment_strength: float   # 维度3：情绪周期强度 [0, 100]
    capital_strength: float     # 维度4：资金面强度 [0, 100]
    total_score: float          # 加权总分 [0, 100]
    weights: dict[str, float]   # 各维度权重


def score_alpha_strength(
    symbol: str,
    ctx: SelectionContext,
    strategy_type: StrategyType,
) -> float:
    """维度1：alpha 信号强度评分——策略特定。

    打板（BM-SEL-23-A 游资接力6因子 + BM-SEL-22-C 连板潜力7维）：
    - 复用打板链已建的评分卡，归一化到 [0, 100]
    - 双引擎融合：游资60% + 量化40%（BM-SEL-25，打板内部融合，§3.7）
    - 6因子：连板高度25 + 封单质量20 + 涨停时间15 + 开板次数15 + 竞价强度10 + 助攻梯队15

    多因子（BM-SEL-02-H 多因子合成）：
    - 因子综合得分（IC 加权/正交化后），横截面排名归一化到 [0, 100]
    - 因子组合方式在 G09 多因子细节讨论

    事件驱动（BM-SEL-27 事件冲击）：
    - 事件冲击强度（事件类型×历史冲击幅度×衰减阶段），归一化到 [0, 100]
    - 事件冲击衰减曲线在 G10 事件驱动细节讨论
    """
    signals = ctx.alpha_signals.get(symbol, {})

    if strategy_type == StrategyType.DABAN:
        # 打板：游资接力6因子评分（BM-SEL-23-A）
        relay_score = signals.get("relay_6factor_score", 0)  # 已是 [0, 100]
        # 连板潜力7维评分（BM-SEL-22-C）
        potential_score = signals.get("limit_up_potential_score", 0)  # [0, 100]
        # 双引擎融合：游资60% + 量化40%（BM-SEL-25，打板内部融合，§3.7）
        # 注意：此处 alpha_strength 已是打板内部双引擎融合后的综合 alpha
        # 情绪周期自适应权重（BM-SEL-25-B）在打板 sleeve 内部进一步调整，此处用基准权重
        alpha_score = 0.6 * relay_score + 0.4 * potential_score
        return alpha_score

    elif strategy_type == StrategyType.MULTIFACTOR:
        # 多因子：因子综合得分（BM-SEL-02-H 多因子合成）
        composite_score = signals.get("factor_composite_score", 0)  # [0, 100]
        return composite_score

    elif strategy_type == StrategyType.EVENT_DRIVEN:
        # 事件驱动：事件冲击强度（BM-SEL-27）
        impact_score = signals.get("event_impact_score", 0)  # [0, 100]
        return impact_score

    return 0.0


def score_sector_strength(
    symbol: str,
    ctx: SelectionContext,
) -> float:
    """维度2：板块强度评分——跨策略共享。

    来自 G06 板块轮动（[22_sector_rotation_spec](22_sector_rotation_spec.md)）。
    板块强度公式（WyckoffTradingAgent 2026-07，[24_daban_strategy_detail](24_daban_strategy_detail.md) §3.7）：
    score = 0.4×q20 + 0.3×q5 + 0.3×q3
    （q3=3日动量，q5=5日动量，q20=20日动量）

    标的板块强度 = 所属板块的板块强度评分，归一化到 [0, 100]。
    板块状态分类（共识高潮/分歧回调/健康主线/派发风险/中性混沌）由 G06 输出。
    """
    sector = ctx.universe_snapshot.get(symbol, {}).get("sector", "unknown")
    sector_score = ctx.sector_strength.get(sector, 50.0)  # 默认中性 50
    return sector_score


def score_sentiment_strength(ctx: SelectionContext) -> float:
    """维度3：情绪周期强度评分——跨策略共享。

    来自 BM-SEL-23-B 情绪周期4+1阶段（[24_daban_strategy_detail](24_daban_strategy_detail.md) §3.2）。
    选股引擎只读情绪周期阶段，不参与判定（判定在 BM-SEL-23-B 上游）。

    情绪周期→强度映射（市场级，非标的级）：
    - 发酵期：情绪最健康，强度 100
    - 启动期：情绪上升，强度 70
    - 一致期：情绪过热，强度 50（警惕退潮）
    - 退潮期：情绪退潮，强度 30
    - 冰点期：情绪冰点，强度 20

    注意：情绪周期是市场级信号，同一天所有标的共享同一情绪强度。
    差异化在 alpha 信号维度体现（如打板内部的情绪周期自适应权重 BM-SEL-25-B）。
    """
    phase_mapping = {
        SentimentPhase.FERMENTING: 100.0,   # 发酵期最强
        SentimentPhase.STARTING: 70.0,      # 启动期较强
        SentimentPhase.CONSENSUS: 50.0,     # 一致期中等（退潮风险）
        SentimentPhase.EBING: 30.0,         # 退潮期较弱
        SentimentPhase.FREEZING: 20.0,      # 冰点期最弱
    }
    return phase_mapping.get(ctx.sentiment_phase, 50.0)


def score_capital_strength(
    symbol: str,
    ctx: SelectionContext,
) -> float:
    """维度4：资金面强度评分——跨策略共享。

    资金面数据：主力净流入 + 北向净流入 + 龙虎榜净买率。
    归一化到 [0, 100]。

    龙虎榜净买率回测（东方财富 2026-08，[24_daban_strategy_detail](24_daban_strategy_detail.md) §3.9）：
    - 净买率 >12% → 次日 +3.10%，20日 +5.11%
    - 净买率 <0% → 资金流出，弱势

    Smart Money 信号（quantskills 2026-06，[24_daban_strategy_detail](24_daban_strategy_detail.md) §3.9）：
    - strong: 净买率>12% + 合力型
    - medium: 净买率>3% + 买方≥卖方1.2倍
    - weak: 其他
    """
    flow = ctx.capital_flow.get(symbol, {})

    main_net = flow.get("main_net_inflow", 0)       # 主力净流入（万）
    northbound = flow.get("northbound_net", 0)       # 北向净流入（万）
    net_buy_ratio = flow.get("net_buy_ratio", 0)     # 龙虎榜净买率

    # 主力净流入评分（0-40分）
    if main_net > 5000:
        s_main = 40.0
    elif main_net > 1000:
        s_main = 30.0
    elif main_net > 0:
        s_main = 20.0
    else:
        s_main = 5.0  # 净流出

    # 北向净流入评分（0-30分）
    if northbound > 2000:
        s_north = 30.0
    elif northbound > 0:
        s_north = 20.0
    else:
        s_north = 10.0

    # 龙虎榜净买率评分（0-30分）
    if net_buy_ratio > 0.12:
        s_dt = 30.0  # 净买率>12% → 次日显著正收益
    elif net_buy_ratio > 0.03:
        s_dt = 20.0
    elif net_buy_ratio > 0:
        s_dt = 10.0
    else:
        s_dt = 5.0

    return s_main + s_north + s_dt


def compute_strength_score(
    symbol: str,
    ctx: SelectionContext,
    strategy_type: StrategyType,
) -> StrengthScore:
    """L2 量化强度评级——4 维度加权总分（v1.0 简化版，保留兼容旧调用方）。

    v1.2.0 生产路径改用 compute_six_dim_strength（6维 BM-SEL-24，见本节末尾）。
    本函数保留以兼容尚未迁移到 6维的旧调用方，逻辑不变。

    权重按策略类型差异化（对齐 [20_first_batch_strategies](20_first_batch_strategies.md) §2.5 差异化矩阵）。
    """
    # 各维度评分
    alpha_s = score_alpha_strength(symbol, ctx, strategy_type)
    sector_s = score_sector_strength(symbol, ctx)
    sentiment_s = score_sentiment_strength(ctx)
    capital_s = score_capital_strength(symbol, ctx)

    # 权重配置（策略差异化）
    if strategy_type == StrategyType.DABAN:
        # 打板：情绪驱动型，alpha+情绪占 65%
        weights = {"alpha": 0.40, "sector": 0.15, "sentiment": 0.25, "capital": 0.20}
    elif strategy_type == StrategyType.MULTIFACTOR:
        # 多因子：alpha 主导型，alpha 占 60%
        weights = {"alpha": 0.60, "sector": 0.15, "sentiment": 0.05, "capital": 0.20}
    else:  # EVENT_DRIVEN
        # 事件驱动：事件+资金驱动型，alpha+资金占 75%
        weights = {"alpha": 0.50, "sector": 0.10, "sentiment": 0.15, "capital": 0.25}

    total = (
        weights["alpha"] * alpha_s
        + weights["sector"] * sector_s
        + weights["sentiment"] * sentiment_s
        + weights["capital"] * capital_s
    )

    return StrengthScore(
        alpha_strength=alpha_s,
        sector_strength=sector_s,
        sentiment_strength=sentiment_s,
        capital_strength=capital_s,
        total_score=total,
        weights=weights,
    )


def rating_from_score(total_score: float, hard_risk: bool = False) -> RatingGrade:
    """总分→A~E 五级评级（v1.2.0 阈值对齐 SignalQuality）。

    阈值：≥85→A / ≥70→B / ≥55→C / ≥40→D / <40→E。
    硬风险（ST/停牌/封板/流动性失效）直接判 E，不参与评分
    ——对齐 mask-first 设计（§3.3.1，硬风险标的在 L1 已被 mask）。
    """
    if hard_risk:
        return RatingGrade.E
    if total_score >= 85:
        return RatingGrade.A
    elif total_score >= 70:
        return RatingGrade.B
    elif total_score >= 55:
        return RatingGrade.C
    elif total_score >= 40:
        return RatingGrade.D
    else:
        return RatingGrade.E


def rank_and_filter_candidates(
    filtered: FilteredUniverse,
    ctx: SelectionContext,
    strategy_type: StrategyType,
    min_rating: RatingGrade = RatingGrade.C,  # 最低评级阈值
    max_positions: int = 20,                   # 最大持仓数
    crowding_days: dict[str, int] | None = None,  # v1.2.0 各维度因子拥挤天数（供 apply_factor_crowding_decay）
) -> list[ScoredCandidate]:
    """L2 排序与筛选——按评级阈值+最大持仓数截断。

    v1.2.0：评分改用 6维 BM-SEL-24（compute_six_dim_strength + map_signals_to_six_dims
    + apply_factor_crowding_decay）。旧 4维 compute_strength_score 保留兼容。

    max_positions 按策略类型差异化（§3.8 `_get_max_positions`）：
    - 打板：≤5 只（容量极小）
    - 多因子：≤20 只（承载主资金，分散化）
    - 事件驱动：≤10 只（中容量）
    """
    scored = []
    for symbol in filtered.symbols:
        # v1.2.0: 6维 BM-SEL-24 强度评级（取分→衰减→加权→分级）
        strength = compute_six_dim_strength(symbol, ctx, strategy_type, crowding_days)
        rating = strength.grade
        confidence = strength.total_score / 100.0

        scored.append(ScoredCandidate(
            symbol=symbol,
            total_score=strength.total_score,
            rating=rating,
            score_breakdown={
                "consecutive_ladder": strength.consecutive_ladder,
                "hot_money_relay": strength.hot_money_relay,
                "sentiment_cycle": strength.sentiment_cycle,
                "sector_strength": strength.sector_strength,
                "capital_flow": strength.capital_flow,
                "technical_pattern": strength.technical_pattern,
                "total_raw": strength.total_raw,
            },
            signal_source=f"{strategy_type.value}_pipeline_v1.2",
            confidence=confidence,
        ))

    # 按总分降序排序
    scored.sort(key=lambda x: x.total_score, reverse=True)

    # 评级过滤
    rating_order = [RatingGrade.A, RatingGrade.B, RatingGrade.C, RatingGrade.D, RatingGrade.E]
    min_idx = rating_order.index(min_rating)
    valid_ratings = set(rating_order[:min_idx + 1])
    scored = [s for s in scored if s.rating in valid_ratings]

    # 最大持仓数截断
    scored = scored[:max_positions]

    # 填充排名
    for i, s in enumerate(scored, 1):
        s.rank = i

    return scored
```

#### 3.5.1 6维 BM-SEL-24 强度评级（v1.2.0 生产路径）

v1.2.0 将 L2 强度评级从 4 维升级为 6 维 BM-SEL-24：将 alpha 信号拆解为更细粒度的策略特定维度（连板梯队/游资接力），并新增技术形态维度。评分流程：**取分 → apply_factor_crowding_decay 双曲衰减 → DIMENSION_WEIGHTS 加权 → 分级**。

```python
# 6维 BM-SEL-24 维度标识
SIX_DIMENSIONS = (
    "consecutive_ladder",   # 连板梯队
    "hot_money_relay",      # 游资接力
    "sentiment_cycle",      # 情绪周期
    "sector_strength",      # 板块强度
    "capital_flow",         # 资金流向
    "technical_pattern",    # 技术形态
)

# 各策略 6维权重（对齐 [20_first_batch_strategies](20_first_batch_strategies.md) §2.5 差异化矩阵）
# - 打板：连板0.25 + 游资0.25（情绪驱动型，连板+游资占 50%）
# - 多因子：资金0.25 + 技术0.30（alpha 主导型，资金+技术占 55%）
# - 事件驱动：情绪0.20 + 资金0.20（事件+资金驱动型）
DIMENSION_WEIGHTS: dict[StrategyType, dict[str, float]] = {
    StrategyType.DABAN: {
        "consecutive_ladder": 0.25,
        "hot_money_relay": 0.25,
        "sentiment_cycle": 0.15,
        "sector_strength": 0.10,
        "capital_flow": 0.15,
        "technical_pattern": 0.10,
    },
    StrategyType.MULTIFACTOR: {
        "consecutive_ladder": 0.05,
        "hot_money_relay": 0.10,
        "sentiment_cycle": 0.10,
        "sector_strength": 0.20,
        "capital_flow": 0.25,
        "technical_pattern": 0.30,
    },
    StrategyType.EVENT_DRIVEN: {
        "consecutive_ladder": 0.10,
        "hot_money_relay": 0.15,
        "sentiment_cycle": 0.20,
        "sector_strength": 0.15,
        "capital_flow": 0.20,
        "technical_pattern": 0.20,
    },
}

# 维度类型：机械型衰减，判断型不衰减（arXiv:2512.11913v1）
MECHANICAL_DIMENSIONS = frozenset({
    "consecutive_ladder", "hot_money_relay", "capital_flow", "technical_pattern",
})
JUDGMENT_DIMENSIONS = frozenset({
    "sentiment_cycle", "sector_strength",
})


@dataclass
class QuantitativeStrength:
    """6维 BM-SEL-24 量化强度评级（v1.2.0 升级）。

    从 v1.0 的 4 维（alpha/sector/sentiment/capital）升级为 6 维：
    将 alpha 拆解为连板梯队 + 游资接力（策略特定），并新增技术形态维度。

    6 维度：
    1. consecutive_ladder（连板梯队）：连板高度/梯队位置/封单质量
    2. hot_money_relay（游资接力）：游资席位合力/接力意愿
    3. sentiment_cycle（情绪周期）：市场情绪阶段（BM-SEL-23-B）
    4. sector_strength（板块强度）：所属板块动量（G06）
    5. capital_flow（资金流向）：主力/北向/龙虎榜净买率
    6. technical_pattern（技术形态）：量价/突破/形态

    评分流程：取分 → apply_factor_crowding_decay 衰减 → DIMENSION_WEIGHTS 加权 → 分级。
    """
    consecutive_ladder: float              # 连板梯队 [0, 100]
    hot_money_relay: float                # 游资接力 [0, 100]
    sentiment_cycle: float                # 情绪周期 [0, 100]
    sector_strength: float                # 板块强度 [0, 100]
    capital_flow: float                   # 资金流向 [0, 100]
    technical_pattern: float              # 技术形态 [0, 100]
    total_raw: float                      # 衰减前总分（均值，供归因）
    total_score: float                    # 衰减后加权总分 [0, 100]
    grade: RatingGrade                    # A~E 等级（对齐 SignalQuality）
    weights: dict[str, float]             # 各维度权重
    decayed_dims: dict[str, float]        # 衰减后各维度得分（供归因）


def apply_factor_crowding_decay(
    dim_scores: dict[str, float],          # {dimension: raw_score}
    crowding_days: dict[str, int],         # {dimension: days_since_crowded}
    lambda_decay: float = 0.05,            # 双曲衰减系数
) -> dict[str, float]:
    """因子拥挤双曲衰减（arXiv:2512.11913v1）。

    机械型维度（规则驱动，易被拥挤套利）按双曲衰减：
        α(t) = K / (1 + λ·t)
    其中 t = 拥挤天数，K = 原始得分，λ = 衰减系数。

    判断型维度（情绪周期/板块强度，主观+宏观驱动）不衰减——
    这类维度的"拥挤"难以量化且衰减模式不同，保持原值。

    维度分类：
    - 机械型（衰减）：consecutive_ladder / hot_money_relay / capital_flow / technical_pattern
    - 判断型（不衰减）：sentiment_cycle / sector_strength

    arXiv:2512.11913 实证：机械型因子拥挤后 IC 在 20-40 天衰减 30-50%，
    双曲衰减（λ≈0.05）比线性衰减更贴合实测衰减曲线。
    """
    decayed: dict[str, float] = {}
    for dim, score in dim_scores.items():
        if dim in MECHANICAL_DIMENSIONS:
            t = crowding_days.get(dim, 0)
            decayed[dim] = score / (1.0 + lambda_decay * t)
        else:
            # 判断型维度不衰减
            decayed[dim] = score
    return decayed


def map_signals_to_six_dims(
    symbol: str,
    ctx: SelectionContext,
    strategy_type: StrategyType,
) -> dict[str, float]:
    """各策略 L1 信号差异化映射到 6 维。

    不同策略的 alpha 信号来源不同，映射到 6 维的方式差异化：
    - 打板：连板梯队 + 游资接力是主维度（来自 BM-SEL-22~23）
    - 多因子：技术形态 + 资金流向是主维度（来自 BM-SEL-02 因子工厂）
    - 事件驱动：情绪周期 + 资金流向是主维度（来自 BM-SEL-27 事件冲击）

    跨策略共享维度（sentiment_cycle/sector_strength/capital_flow）复用本节上方
    score_sentiment_strength/score_sector_strength/score_capital_strength。
    """
    signals = ctx.alpha_signals.get(symbol, {})
    # 跨策略共享维度（复用 v1.0 共享评分函数）
    sentiment_s = score_sentiment_strength(ctx)
    sector_s = score_sector_strength(symbol, ctx)
    capital_s = score_capital_strength(symbol, ctx)

    if strategy_type == StrategyType.DABAN:
        # 打板：连板梯队 + 游资接力为主（BM-SEL-22-C / BM-SEL-23-A）
        return {
            "consecutive_ladder": signals.get("limit_up_potential_score", 0.0),
            "hot_money_relay": signals.get("relay_6factor_score", 0.0),
            "sentiment_cycle": sentiment_s,
            "sector_strength": sector_s,
            "capital_flow": capital_s,
            "technical_pattern": signals.get("technical_pattern_score", 50.0),
        }
    elif strategy_type == StrategyType.MULTIFACTOR:
        # 多因子：技术形态 + 资金流向为主（BM-SEL-02-H 因子合成）
        return {
            "consecutive_ladder": signals.get("momentum_score", 50.0),
            "hot_money_relay": signals.get("smart_money_score", 50.0),
            "sentiment_cycle": sentiment_s,
            "sector_strength": sector_s,
            "capital_flow": capital_s,
            "technical_pattern": signals.get("factor_composite_score", 0.0),
        }
    else:  # EVENT_DRIVEN
        # 事件驱动：情绪周期 + 资金流向为主（BM-SEL-27 事件冲击）
        return {
            "consecutive_ladder": signals.get("momentum_score", 50.0),
            "hot_money_relay": signals.get("smart_money_score", 50.0),
            "sentiment_cycle": sentiment_s,
            "sector_strength": sector_s,
            "capital_flow": capital_s,
            "technical_pattern": signals.get("event_impact_score", 0.0),
        }


def compute_six_dim_strength(
    symbol: str,
    ctx: SelectionContext,
    strategy_type: StrategyType,
    crowding_days: dict[str, int] | None = None,
) -> QuantitativeStrength:
    """6维 BM-SEL-24 量化强度评分主函数（v1.2.0 生产路径）。

    流程：取分（map_signals_to_six_dims）→ apply_factor_crowding_decay 双曲衰减
    → DIMENSION_WEIGHTS 加权 → rating_from_score 分级。

    对齐 BM-SEL-24 量化强度6维（[battle_map_05](../battle_map/battle_map_05_stock_selection.md)）。
    """
    # 1. 取分——各策略 L1 信号差异化映射到 6 维
    raw_dims = map_signals_to_six_dims(symbol, ctx, strategy_type)

    # 2. 因子拥挤双曲衰减（机械型衰减，判断型不衰减）
    crowding = crowding_days or {}
    decayed = apply_factor_crowding_decay(raw_dims, crowding)

    # 3. 加权
    weights = DIMENSION_WEIGHTS[strategy_type]
    total_raw = sum(raw_dims[d] for d in SIX_DIMENSIONS) / len(SIX_DIMENSIONS)
    total = sum(weights[d] * decayed[d] for d in SIX_DIMENSIONS)

    # 4. 分级（对齐 SignalQuality 阈值，硬风险在 L1 已被 mask）
    grade = rating_from_score(total)

    return QuantitativeStrength(
        consecutive_ladder=raw_dims["consecutive_ladder"],
        hot_money_relay=raw_dims["hot_money_relay"],
        sentiment_cycle=raw_dims["sentiment_cycle"],
        sector_strength=raw_dims["sector_strength"],
        capital_flow=raw_dims["capital_flow"],
        technical_pattern=raw_dims["technical_pattern"],
        total_raw=total_raw,
        total_score=total,
        grade=grade,
        weights=weights,
        decayed_dims=decayed,
    )
```

### 3.6 C 组合输出算法

```python
def compose_target_portfolio(
    scored: list[ScoredCandidate],
    ctx: SelectionContext,
    strategy_type: StrategyType,
    candidate_pool: CandidatePool,
    filtered: FilteredUniverse,
) -> SelectionOutput:
    """C 组合输出——将评分结果转为 target_portfolio。

    signal_weight 计算策略：评级分层+得分加权混合
    - A 级：权重乘数 ×1.5
    - B 级：权重乘数 ×1.0
    - C 级：权重乘数 ×0.5
    然后按得分在同级内加权，最后归一化。

    注意：signal_weight 不是最终仓位！
    最终仓位 = StrategyBook 粗仓位（risk parity/等权）× firm 层 Kelly 精裁决
    （[31_position_sizing](31_position_sizing.md) 分层裁定）。
    """
    if not scored:
        # 无信号→全现金
        target = TargetPortfolio(
            strategy_id=ctx.strategy_id,
            strategy_type=strategy_type,
            trading_date=ctx.trading_date,
            positions=[],
            cash_weight=1.0,
            pipeline_meta={"reason": "no_valid_candidates"},
            generated_at=datetime.now(),
        )
    else:
        # 评级分层乘数
        rating_multipliers = {
            RatingGrade.A: 1.5,
            RatingGrade.B: 1.0,
            RatingGrade.C: 0.5,
        }

        # 计算原始权重 = 评级乘数 × 得分
        raw_weights = []
        for s in scored:
            mult = rating_multipliers.get(s.rating, 0.5)
            raw_weights.append(mult * s.total_score)

        # 归一化到 [0, 1]，总和 = 1 - cash_buffer
        cash_buffer = 0.05  # 预留 5% 现金缓冲
        total_raw = sum(raw_weights)
        if total_raw > 0:
            signal_weights = [w / total_raw * (1 - cash_buffer) for w in raw_weights]
        else:
            signal_weights = [0] * len(scored)

        positions = []
        for s, w in zip(scored, signal_weights):
            positions.append(TargetPosition(
                symbol=s.symbol,
                signal_weight=w,
                score=s.total_score,
                rating=s.rating,
                score_breakdown=s.score_breakdown,
                signal_source=s.signal_source,
                confidence=s.confidence,
            ))

        target = TargetPortfolio(
            strategy_id=ctx.strategy_id,
            strategy_type=strategy_type,
            trading_date=ctx.trading_date,
            positions=positions,
            cash_weight=cash_buffer,
            pipeline_meta={
                "n_candidates": len(candidate_pool.symbols),
                "n_passed_mask": len(filtered.symbols),
                "n_scored": len(scored),
                "rating_distribution": _count_ratings(scored),
                "mask_rejection_summary": _summarize_rejections(filtered.rejected),
            },
            generated_at=datetime.now(),
        )

    return SelectionOutput(
        target_portfolio=target,
        candidate_pool=candidate_pool,
        filtered_universe=filtered,
        scored_candidates=scored,
    )


def _count_ratings(scored: list[ScoredCandidate]) -> dict[str, int]:
    """统计评级分布。"""
    dist = {}
    for s in scored:
        dist[s.rating.value] = dist.get(s.rating.value, 0) + 1
    return dist


def _summarize_rejections(rejected: dict[str, str]) -> dict[str, int]:
    """汇总掩码剔除原因分布。"""
    summary = {}
    for reason in rejected.values():
        summary[reason] = summary.get(reason, 0) + 1
    return summary
```

### 3.7 双引擎融合定位说明（BM-SEL-25 内部融合）

**核心裁定**：BM-SEL-25 双引擎融合（游资情绪引擎 60% + 量化强度引擎 40%，情绪周期自适应权重）是**打板策略内部融合**，**非跨策略层**。

**裁定依据**（对齐 [30_multi_strategy_concurrency §7.3](30_multi_strategy_concurrency.md)）：
- BM-SEL-25 双引擎融合 → 保留，定位为"打板策略内部"融合，非跨策略层
- BM-SEL-02-K 多策略投票加权 → 降级为策略内部机制（非跨策略层）

**层级边界澄清**：

| 层级 | 范围 | 机制 | 状态 |
|---|---|---|---|
| **跨策略层（firm 层）** | 多 sleeve 之间 | FirmRiskAggregator 自然叠加（求和+裁剪，O(N) 加法） | [32_firm_risk_aggregator](32_firm_risk_aggregator.md) |
| **策略内部层（sleeve 内）** | 单策略内多引擎融合 | 打板双引擎融合（BM-SEL-25，游资60%+量化40%） | [24_daban_strategy_detail](24_daban_strategy_detail.md) §3.4 |
| **选股引擎层（本讨论）** | 跨策略统一 pipeline | L0→L1→L2-C 分层 | 本文档 |

**双引擎融合在 pipeline 中的位置**：
- BM-SEL-25 双引擎融合发生在**打板策略的 L2 评分阶段**（§3.5 `score_alpha_strength` 打板分支）
- 具体而言：打板的 alpha 信号强度 = 0.6 × 游资接力6因子（BM-SEL-23-A）+ 0.4 × 连板潜力7维（BM-SEL-22-C）
- 情绪周期自适应权重（BM-SEL-25-B：冰点量化70%/主升游资70%/退潮量化60%）在打板 sleeve 内部进一步调整 alpha 强度，**不**影响多因子/事件驱动 sleeve
- 6类决策输出（BM-SEL-25-C：主升龙头/二进三/跟风/复苏/伪强/地天反包）是打板 sleeve 内部的决策分类，不跨策略

**为何不是跨策略层**：
1. **charter 约束二（统一框架派）**：跨策略层用 firm 层自然叠加（O(N) 加法），不用投票/融合（O(N²) 复杂度，[30_multi_strategy_concurrency §3.2](30_multi_strategy_concurrency.md) 拒绝 Model D）
2. **归因清晰度**：双引擎融合是打板 alpha 的内部构成，归因到打板 sleeve；若提到跨策略层，会模糊"打板 alpha vs 多因子 alpha"的归因边界
3. **差异化保护**：打板是情绪驱动型（游资60%），多因子是 alpha 主导型（因子60%），事件是事件驱动型——三者的引擎融合逻辑不同，强行统一跨策略融合会破坏差异化（违反 charter 约束五）
4. **主升龙头并入打板**（[20_first_batch_strategies](20_first_batch_strategies.md) §2.1 裁定）：BM-SEL-25-C-1 主升龙头决策类是打板双引擎融合的最强输出，作为独立策略会产生 alpha 重叠，已并入打板 sleeve

**双引擎融合的可施工 spec**（v1.2.0 补齐，打板 sleeve 内部）：

```python
class FusionStrategy(Enum):
    """双引擎融合策略（BM-SEL-25，打板策略内部）。"""
    WEIGHTED = "weighted"            # 加权融合（游资60%+量化40%，情绪周期自适应微调）
    CONDITIONAL = "conditional"      # 条件融合（情绪周期门控：冰点/退潮期量化权重提升）
    DECISION_TREE = "decision_tree"  # 6类决策树（BM-SEL-25-C）


@dataclass
class EngineScore:
    """单引擎评分——游资情绪引擎或量化强度引擎的输出。"""
    engine_name: str             # "hot_money"（游资情绪）/ "quantitative"（量化强度）
    score: float                 # 引擎评分 [0, 100]
    confidence: float            # 置信度 [0, 1]
    breakdown: dict[str, float]  # 引擎内部维度得分（供归因）


@dataclass
class FusedSignal:
    """双引擎融合后信号——打板 alpha 的最终形态。"""
    fused_score: float                 # 融合后综合分 [0, 100]
    hot_money_component: float         # 游资引擎贡献（融合前原始分）
    quantitative_component: float      # 量化引擎贡献（融合前原始分）
    fusion_strategy: FusionStrategy    # 实际使用的融合策略
    decision_class: str = ""           # 6类决策分类（BM-SEL-25-C，DECISION_TREE 时填充）
    sentiment_adjusted: bool = False   # 是否经情绪周期自适应权重调整


def fuse_dual_engine(
    hot_money: EngineScore,
    quantitative: EngineScore,
    sentiment_phase: SentimentPhase,
    strategy: FusionStrategy = FusionStrategy.WEIGHTED,
) -> FusedSignal:
    """打板双引擎融合（BM-SEL-25，打板策略内部融合，非跨策略层）。

    融合方式：
    - WEIGHTED：基准权重 游资60% + 量化40%，情绪周期自适应微调
      （BM-SEL-25-B：冰点量化70% / 主升游资70% / 退潮量化60%）
    - CONDITIONAL：情绪周期门控——冰点/退潮期以量化引擎为主（游资信号失效）
    - DECISION_TREE：6类决策分类（主升龙头/二进三/跟风/复苏/伪强/地天反包）

    定位：打板 sleeve 内部（本节§3.7），非跨策略层。
    对齐 [24_daban_strategy_detail](24_daban_strategy_detail.md) §3.4 BM-SEL-25。
    """
    # 情绪周期自适应权重 (w_hot, w_quant)（BM-SEL-25-B）
    phase_weights = {
        SentimentPhase.FREEZING: (0.30, 0.70),    # 冰点：量化70%（游资信号失效）
        SentimentPhase.STARTING: (0.50, 0.50),
        SentimentPhase.FERMENTING: (0.60, 0.40),  # 发酵：基准 游资60%+量化40%
        SentimentPhase.CONSENSUS: (0.65, 0.35),
        SentimentPhase.EBING: (0.40, 0.60),       # 退潮：量化60%
    }
    w_hot, w_quant = phase_weights.get(sentiment_phase, (0.60, 0.40))

    if strategy == FusionStrategy.WEIGHTED:
        fused = w_hot * hot_money.score + w_quant * quantitative.score
        return FusedSignal(
            fused_score=fused,
            hot_money_component=hot_money.score,
            quantitative_component=quantitative.score,
            fusion_strategy=strategy,
            sentiment_adjusted=True,
        )
    elif strategy == FusionStrategy.CONDITIONAL:
        # 情绪周期门控：冰点/退潮期以量化引擎为主
        if sentiment_phase in (SentimentPhase.FREEZING, SentimentPhase.EBING):
            fused = 0.30 * hot_money.score + 0.70 * quantitative.score
        else:
            fused = 0.60 * hot_money.score + 0.40 * quantitative.score
        return FusedSignal(
            fused_score=fused,
            hot_money_component=hot_money.score,
            quantitative_component=quantitative.score,
            fusion_strategy=strategy,
            sentiment_adjusted=True,
        )
    else:  # DECISION_TREE
        fused = w_hot * hot_money.score + w_quant * quantitative.score
        decision_class = _classify_daban_decision(fused, hot_money, quantitative, sentiment_phase)
        return FusedSignal(
            fused_score=fused,
            hot_money_component=hot_money.score,
            quantitative_component=quantitative.score,
            fusion_strategy=strategy,
            decision_class=decision_class,
            sentiment_adjusted=True,
        )


def _classify_daban_decision(
    fused: float,
    hot_money: EngineScore,
    quantitative: EngineScore,
    sentiment_phase: SentimentPhase,
) -> str:
    """6类决策分类（BM-SEL-25-C）：主升龙头/二进三/跟风/复苏/伪强/地天反包。

    分类逻辑（简化，完整规则见 [24_daban_strategy_detail](24_daban_strategy_detail.md) §3.4）：
    - 主升龙头：fused≥85 + 游资≥80 + 发酵/一致期
    - 二进三：连板高度≥2 + 游资接力强（fused≥70）
    - 跟风：fused 60-75 + 板块强度高
    - 复苏：冰点/退潮期 + 量化引擎转正（≥55）
    - 伪强：游资高但量化<40（情绪虚高）
    - 地天反包：跌停后反转（特殊形态，兜底）
    """
    if fused >= 85 and hot_money.score >= 80 and sentiment_phase in (
        SentimentPhase.FERMENTING, SentimentPhase.CONSENSUS
    ):
        return "主升龙头"
    if hot_money.score >= 70 and quantitative.score < 40:
        return "伪强"
    if sentiment_phase in (SentimentPhase.FREEZING, SentimentPhase.EBING) and quantitative.score >= 55:
        return "复苏"
    if 60 <= fused < 75:
        return "跟风"
    if fused >= 70:
        return "二进三"
    return "地天反包"
```

### 3.8 与 StrategyBook 的对接契约

选股引擎的输出 `TargetPortfolio` 是 StrategyBook 的输入契约。

```python
def run_selection_pipeline(ctx: SelectionContext) -> SelectionOutput:
    """选股 pipeline 主入口——L0→L1→L2-C 完整流程。

    这是选股引擎对 StrategyBook 暴露的统一接口。
    StrategyBook 调用此函数获取 target_portfolio，再做粗仓位。
    """
    # L0 候选池生成
    pool = generate_candidate_pool(ctx)

    # L1 mask-first 量化过滤
    filtered = apply_mask_first_filter(pool, ctx)

    # L2 量化强度评级与排序
    scored = rank_and_filter_candidates(
        filtered, ctx, ctx.strategy_type,
        min_rating=RatingGrade.C,
        max_positions=_get_max_positions(ctx.strategy_type),
    )

    # C 组合输出
    output = compose_target_portfolio(scored, ctx, ctx.strategy_type, pool, filtered)

    return output


def _get_max_positions(strategy_type: StrategyType) -> int:
    """各策略最大持仓数——按容量与换手率差异化。

    - 打板：≤5 只（容量极小，单票几万~几十万，[30_multi_strategy_concurrency §1.3](30_multi_strategy_concurrency.md)）
    - 多因子：≤20 只（承载主资金，分散化需求）
    - 事件驱动：≤10 只（中容量）
    """
    if strategy_type == StrategyType.DABAN:
        return 5
    elif strategy_type == StrategyType.MULTIFACTOR:
        return 20
    else:  # EVENT_DRIVEN
        return 10


def _compute_vol_20d(returns: list[float]) -> float:
    """计算 20 日收益波动率 σ_20d（供 inverse-vol risk parity）。"""
    if len(returns) < 2:
        return 1e-6  # 数据不足，给极小波动率（退化为等权时由调用方处理）
    mean = sum(returns) / len(returns)
    var = sum((r - mean) ** 2 for r in returns) / len(returns)
    return max(var ** 0.5, 1e-6)


def selection_to_target_portfolio(
    output: SelectionOutput,
    budget: float = 1.0,
    market_data: dict[str, dict] | None = None,
) -> TargetPortfolio:
    """将选股输出转为 risk-parity 加权的 target_portfolio（v1.2.0 补齐实现）。

    v1.2.0：补齐 inverse-vol risk parity 实现（原 v1.0 仅占位"实现见 31_position_sizing"）。

    inverse-vol risk parity：
        final_weight_i ∝ signal_weight_i × (1 / σ_i,20d)
    其中 σ_i,20d 为标的 i 的 20 日收益波动率，归一化到 budget。
    signal_weight 来自 §3.6 compose_target_portfolio 的评级分层+得分加权。

    market_data=None 时退化为等权（无波动率数据）。

    对齐 [31_position_sizing](31_position_sizing.md) 分层裁定：
    - 此处是 StrategyBook 粗仓位层（risk parity，不用 Kelly）
    - firm 层 Kelly 精裁决在 [32_firm_risk_aggregator](32_firm_risk_aggregator.md)
    """
    target = output.target_portfolio
    positions = target.positions
    if not positions:
        return target

    # 无 market_data → 退化为等权
    if market_data is None:
        n = len(positions)
        eq = budget / n
        for p in positions:
            p.signal_weight = eq
        return target

    # inverse-vol: final_weight_i ∝ signal_weight_i × (1/σ_i)
    raw: dict[str, float] = {}
    for p in positions:
        rets = market_data.get(p.symbol, {}).get("returns_20d", [])
        sigma = _compute_vol_20d(rets)
        raw[p.symbol] = p.signal_weight * (1.0 / sigma)

    total_raw = sum(raw.values())
    if total_raw <= 0:
        # 全部 signal_weight=0 或数据异常 → 退化为等权
        n = len(positions)
        for p in positions:
            p.signal_weight = budget / n
    else:
        for p in positions:
            p.signal_weight = raw[p.symbol] / total_raw * budget

    return target
```

**对接契约要点**：

| 维度 | 选股引擎职责 | StrategyBook 职责 |
|---|---|---|
| **买什么（what）** | ✅ 输出 target_portfolio（symbol + signal_weight + rating） | 消费 target_portfolio |
| **买多少（how much）** | ❌ 不输出最终仓位 | ✅ 粗仓位（risk parity/等权）× signal_weight |
| **怎么买（how）** | ❌ 不参与执行 | 交给 G19 买入流（[41_buy_flow](41_buy_flow.md)） |
| **budget 适配** | ❌ 不读 regime 输出 | ✅ 收 budget 数字，rebalance_to_budget（[33_budget_change_handler](33_budget_change_handler.md)） |
| **PnL 归因** | 提供 score_breakdown（各维度得分） | ✅ 独立 PnL 归因 |

**signal_weight → 最终仓位的转换**（StrategyBook 内部）：
```
final_position_i = signal_weight_i × strategy_budget × risk_parity_factor_i
```
其中：
- `signal_weight_i`：选股引擎输出（本讨论 §3.6）
- `strategy_budget`：RegimeMetaAllocator 分配的 sleeve 资金占比（[34_regime_meta_allocator](34_regime_meta_allocator.md)）
- `risk_parity_factor_i`：StrategyBook 粗仓位算法（inverse-vol risk parity，[31_position_sizing](31_position_sizing.md)）

**分层裁定对齐**（[30_multi_strategy_concurrency §2.1](30_multi_strategy_concurrency.md)）：
- 选股引擎只管"选什么"——不越界到仓位/执行
- 仓位决策分两层：StrategyBook 粗仓位（等权/risk parity，不用 Kelly）+ firm 层 Kelly 精裁决（MOD-POS-001）
- 选股引擎的 signal_weight 是"信号强度排序"，不是"仓位建议"

## 4. 考虑过的替代方案

### 4.1 统一候选池（不分策略类型）—— 拒绝

- **方案描述**：三策略共用一个全市场候选池，在 L2 评分阶段用不同权重区分
- **拒绝理由**：三策略选股池差异极大（打板窄池10-50只 vs 多因子宽池5000只），强行统一会导致：
  1. 打板策略在全市场池中评分，连板梯队信号被稀释——打板 alpha 来自连板结构，全市场池中非连板标的无该信号
  2. 多因子策略在连板窄池中评分，因子横截面排名失效——多因子需大样本横截面排序，窄池样本不足
  3. 事件驱动策略的动态事件池无法用固定池承载——事件即生即灭，非固定池
- **处置**：L0 差异化候选池（§3.3），L1/L2 半统一

### 4.2 跨策略双引擎融合（BM-SEL-25 提到 firm 层）—— 拒绝

- **方案描述**：将打板双引擎融合（游资60%+量化40%）扩展为跨策略融合，在 firm 层融合打板+多因子+事件驱动
- **拒绝理由**：
  1. **charter 约束二**：跨策略层用自然叠加（O(N) 加法），不用融合/投票（[30_multi_strategy_concurrency §3.2](30_multi_strategy_concurrency.md) 拒绝 Model D 加权投票）
  2. **归因纠缠**：跨策略融合会模糊"打板 alpha vs 多因子 alpha"的归因边界，违反 AI-dev 归因清晰度生存项（[30_multi_strategy_concurrency §1.3](30_multi_strategy_concurrency.md)）
  3. **差异化破坏**：三策略的引擎融合逻辑不同（打板情绪驱动/多因子alpha主导/事件事件驱动），强行统一跨策略融合破坏差异化（违反 charter 约束五）
- **处置**：BM-SEL-25 双引擎融合保留在打板策略内部（§3.7，对齐 [30_multi_strategy_concurrency §7.3](30_multi_strategy_concurrency.md)）

### 4.3 不做 mask-first（alpha 算完再过滤）—— 拒绝

- **方案描述**：先对全市场算 alpha，最后再过滤 ST/停牌/涨跌停封板
- **拒绝理由**：
  1. **算力浪费**：A 股约 20-30% 标的不可交易（ST/停牌/封板），alpha 计算浪费 20-30% 算力
  2. **信号污染**：不可交易标的的异常数据（如停牌期间的前收盘价、ST股异常波动）污染 alpha 信号
  3. **回测失真**：回测假设可交易但实际不可交易，导致回测收益虚高（arXiv:2507.07107 mask-first 核心论点）
- **处置**：L1 mask-first 前置过滤（§3.4），在 alpha 评分前应用可交易性掩码

### 4.4 选股引擎直接输出最终仓位 —— 拒绝

- **方案描述**：选股引擎输出 final_position（含 Kelly 仓位），StrategyBook 直接执行
- **拒绝理由**：
  1. **违反分层裁定**（[30_multi_strategy_concurrency §2.1](30_multi_strategy_concurrency.md)）：仓位决策分两层——StrategyBook 粗仓位 + firm 层 Kelly 精裁决。选股引擎越界做仓位会破坏分层
  2. **Kelly 需密度预测**：Kelly 仓位需估计预期收益/方差，这是组合层职责，不应在选股层重复（分层裁定第一性原理：Kelly 需密度预测不宜每策略重复）
  3. **归因纠缠**：选股+仓位混在一起，亏钱时无法区分"选股错"还是"仓位错"
- **处置**：选股引擎只输出 signal_weight（§3.8），仓位交给 StrategyBook + firm 层

## 5. 上限定义

| 上限 | 值 | 理由 |
|---|---|---|
| **策略类型数** | 3（打板+多因子+事件驱动） | 对齐 [20_first_batch_strategies](20_first_batch_strategies.md) 首批3策略；第4/5策略在 G11 第二批次 |
| **打板最大持仓** | ≤5 只 | 容量极小（单票几万~几十万，[30_multi_strategy_concurrency §1.3](30_multi_strategy_concurrency.md)） |
| **多因子最大持仓** | ≤20 只 | 承载主资金，分散化需求 |
| **事件驱动最大持仓** | ≤10 只 | 中容量，介于打板与多因子之间 |
| **最低评级阈值** | C 级（≥55分，v1.2.0 对齐 SignalQuality） | D/E 级标的剔除，保证最低信号质量 |
| **L1 共享掩码** | ST + 停牌 + 流动性 | 跨策略共享，所有策略剔除 |
| **L1 策略特定掩码** | 次新/涨停封板 | 按策略差异化（§3.4） |
| **cash_buffer** | 5% | 预留现金缓冲，防极端情况 |

### 演进路径

- **第一阶段（立即施工）**：3 策略 L0→L1→L2-C pipeline 落地，signal_weight 评级分层+得分加权输出，StrategyBook 粗仓位用等权
- **第二阶段（各 sleeve 有 3-6 个月实盘 PnL 后）**：L2 评分权重校准（基于各维度 IC 衰减实测），StrategyBook 粗仓位转 inverse-vol risk parity
- **第三阶段（首批 track record 后）**：上加第 4/5 策略（价值反转/动量趋势，G11），pipeline 扩展 StrategyType 枚举 + L0 候选池生成

### 为何这是上限而非妥协

- 3 策略已覆盖高/低/中换手率 + 小/大/中容量 + 情绪/横截面/事件三类 alpha 来源（[20_first_batch_strategies](20_first_batch_strategies.md) §2.5）
- pipeline 架构可扩展（新增策略只需扩展 StrategyType 枚举 + L0 候选池生成 + L2 权重配置），上限不在架构而在策略数
- 多于 3 策略会稀释研究带宽（charter §3 约束五：单人+AI+资金小，少而精是唯一可行路径）

## 6. 待裁定

| 暂缓项 | 暂缓理由 | 重评条件 | 责任方 |
|---|---|---|---|
| L2 评分权重精确校准 | 当前权重（打板0.4/0.15/0.25/0.20 等）基于先验，未经 IC 衰减实测 | 首批策略实盘 3 月后，用各维度 IC 衰减数据校准 | G05 后续 |
| 多因子因子组合方式 | IC 加权/正交化/打分待定 | G09 多因子细节讨论 | G09 |
| 事件冲击衰减曲线 | 事件类型×冲击幅度×衰减阶段待定 | G10 事件驱动细节讨论 | G10 |
| max_positions 精确值 | 打板5/多因子20/事件10为先验 | 各策略容量精确测算后校准 | G08/G09/G10 |
| mask-first 次新阈值 | 当前 60 天，未实测最优 | 多因子 sleeve 实盘后校准 | G09 |
| BM-SEL-16~19 漏斗与 L0→L1→L2-C 对齐 | 作战地图已有4层漏斗雏形（BM-SEL-16分级过滤→17初筛→18精筛→19事件筛选），与本 pipeline 关系待澄清 | G05 施工时与作战地图 owner 对齐 | G05 + battle_map owner |

## 7. 待定问题（讨论要点对齐）

- [x] ① 双引擎融合（BM-SEL-25，30_multi_strategy_concurrency 定位为"打板策略内部融合"，非跨策略层）→ §3.7 双引擎融合定位说明
- [x] ② L0→L1→L2-C 分层 → §3.1 架构定义 + §3.3-§3.6 各层算法
- [x] ③ 量化强度评级 → §3.5 L2 量化强度评级算法（6维 BM-SEL-24 + apply_factor_crowding_decay 双曲衰减 + map_signals_to_six_dims 差异化映射 + A~E 五级）
- [x] ④ 选股 pipeline 标准接口（输入信号→输出 target_portfolio）→ §3.2 dataclass 定义（SelectionContext→TargetPortfolio）
- [x] ⑤ 候选池生成→过滤→排序→输出 → §3.3 L0 候选池生成 + §3.4 L1 mask-first 过滤 + §3.5 L2 评级排序 + §3.6 C 组合输出
- [x] ⑥ 与 StrategyBook 的对接契约 → §3.8 对接契约（target_portfolio 接口规范 + signal_weight→最终仓位转换 + 分层裁定对齐）

## 8. 引用

### 8.1 相关设计备忘
- [00_index_trading_decision](00_index_trading_decision.md) §3 G05
- [20_first_batch_strategies](20_first_batch_strategies.md)（G04 产出物，首批3策略定义，必先读）
- [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §2.1（分层裁定）/ §3.2（拒绝 Model D 投票）/ §7.3（BM-SEL-25 内部融合定位）
- [24_daban_strategy_detail](24_daban_strategy_detail.md)（G08 打板细节，BM-SEL-22~25 打板链）
- [31_position_sizing](31_position_sizing.md)（G12 仓位算法，signal_weight→最终仓位转换）
- [32_firm_risk_aggregator](32_firm_risk_aggregator.md)（G13 FirmRiskAggregator，跨策略自然叠加）
- [33_budget_change_handler](33_budget_change_handler.md)（G14 BudgetChangeHandler，budget 适配）
- [34_regime_meta_allocator](34_regime_meta_allocator.md)（G15 RegimeMetaAllocator，budget 来源）
- [22_sector_rotation_spec](22_sector_rotation_spec.md)（G06 板块轮动，板块强度输入）
- [41_buy_flow](41_buy_flow.md)（G19 买入流，target_portfolio 下游消费者）

### 8.2 相关作战地图
- [battle_map_05_stock_selection.md](../battle_map/battle_map_05_stock_selection.md)（选股阶段）
  - BM-SEL-02：因子计算与信号生成（多因子 sleeve 依赖，BM-SEL-02-A~L 全链）
  - BM-SEL-16~19：4层漏斗雏形（分级指标过滤→初筛漏斗→精筛评分→事件驱动分布筛选，与本 pipeline 对齐待裁定）
  - BM-SEL-22~25：打板链（短线评分卡7维 / 游资接力6因子+情绪周期4+1 / 量化强度6维 / 双引擎融合6类决策）
  - BM-SEL-27：盘中实时事件处理（事件驱动 sleeve 依赖）

### 8.3 depgraph 模块（引用稳定 path / blueprint_id）
| 模块 | blueprint_id | path | 本讨论关系 |
|---|---|---|---|
| StrategyBook | MOD-POS-020 | `src/zephyr/position/core/strategy_book.py` | target_portfolio 的消费者 |
| FirmRiskAggregator | MOD-POS-021 | `src/zephyr/position/core/firm_risk_aggregator.py` | 跨策略自然叠加（求和+裁剪） |
| RegimeMetaAllocator | MOD-PA-007 | `src/zephyr/pf_alloc/core/regime_meta_allocator.py` | budget 来源（第二阶段） |
| BudgetChangeHandler | MOD-POS-022 | `src/zephyr/position/core/budget_change_handler.py` | budget 适配三级升级 |

### 8.4 开源实证参考
- arXiv:2507.07107 — A 股 mask-first 设计：可交易性掩码前置，避免 alpha 污染与回测失真。本讨论 §3.3.1/§3.4 L1 mask-first 过滤的直接依据（row_filter 虚增 IC +18%/Sharpe -0.44，mask-first 单一最大贡献者 +0.44 Sharpe）
- arXiv:2512.11913 — 因子拥挤双曲衰减：机械型因子 α(t)=K/(1+λt) 衰减，判断型不衰减。本讨论 §3.5 apply_factor_crowding_decay 的依据
- WorldQuant Alpha 工厂分层 — Region→Universe→Data→Expression→Operators→Decay→Neutralization→Tests 八层架构。本讨论 L0→L1→L2-C 分层 pipeline 的对标范式
- quantskills (2026-06) Smart Money Profiler — 席位画像+合力型/独食型识别。§3.5 资金面评分依据（[24_daban_strategy_detail](24_daban_strategy_detail.md) §3.9 已整合）
- 东方财富 (2026-08) 龙虎榜净买率回测 — 净买率>12% 次日+3.10%/20日+5.11%。§3.5 资金面评分阈值依据

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行：由 00_index G05 讨论要点占位，待讨论填空 |
| 2026-08-10 | 1.0.0 | 落地 spec 定稿 | L0→L1→L2-C 分层 pipeline + 标准接口（SelectionContext→TargetPortfolio dataclass）+ 候选池生成（打板连板梯队/多因子全市场/事件驱动动态池三策略差异化）+ mask-first 过滤（arXiv:2507.07107，ST/次新/停牌/涨跌停封板/流动性按策略差异化）+ 量化强度评级（4维度 alpha+板块+情绪+资金，A~E五级，策略差异化权重）+ 双引擎融合内部化定位（对齐 30_multi_strategy_concurrency §7.3，BM-SEL-25 是打板内部融合非跨策略层）+ StrategyBook 对接契约（target_portfolio 接口规范 + signal_weight→最终仓位转换 + 分层裁定对齐）；整合 2026-08 研究（A 股 mask-first / WorldQuant Alpha 工厂分层 / 龙虎榜净买率回测）；4 个替代方案拒绝（统一候选池/跨策略融合/不做mask-first/选股直接输出仓位） |
| 2026-08-10 | 1.1.0 | 补齐 mask-first 设计（arXiv:2507.07107v2） | §3.3.1 新增 TradabilityMaskPolicy 枚举（STRICT/MODERATE/PERMISSIVE）+ policy→掩码集映射表；apply_mask_first_filter 升级为 policy-aware（接受 mask_policy 参数）；_evaluate_reject 增补 STRICT/PERMISSIVE 分支；TradabilityMask 增补 is_tradable/mask_reason 汇总字段；SelectionContext 增 mask_policy 字段；实证：row_filter 虚增 IC +18%/Sharpe -0.44，mask-first 单一最大贡献者 +0.44 Sharpe；涨跌停板 upstream contamination 防护；mask 贯穿 L0→L1→L2-C pipeline |
| 2026-08-11 | 1.2.0 | 6维 BM-SEL-24 + 因子拥挤衰减 + risk_parity 补齐 | §3.5/§3.6 从 4维升级为 6维 BM-SEL-24（连板梯队/游资接力/情绪周期/板块强度/资金流向/技术形态）：新增 QuantitativeStrength dataclass + DIMENSION_WEIGHTS（三策略各自权重，打板连板0.25+游资0.25 / 多因子资金0.25+技术0.30 / 事件驱动情绪0.20+资金0.20）+ apply_factor_crowding_decay 因子拥挤双曲衰减（arXiv:2512.11913v1，机械型 α(t)=K/(1+λt) 衰减/判断型不衰减）+ map_signals_to_six_dims 各策略差异化映射 + compute_six_dim_strength 6维评分主函数（取分→衰减→加权→分级）；§3.4 增补 Löwdin 对称正交化 _loewin_orthogonalize + IC-IR 加权 _compute_ic_ir_weights + score_l1_multifactor；SignalQuality 升级为 A~E 五级（≥85/≥70/≥55/≥40/<40，硬风险→E）+ rating_from_score 阈值对齐；§3.7 增补 EngineScore/FusedSignal/FusionStrategy/fuse_dual_engine 双引擎融合可施工 spec（WEIGHTED/CONDITIONAL/DECISION_TREE + 6类决策分类）；§3.8 risk_parity inverse-vol 实现补齐 + selection_to_target_portfolio(market_data=None)；§7 讨论要点③更新；§8 引用增补 arXiv:2512.11913 |
