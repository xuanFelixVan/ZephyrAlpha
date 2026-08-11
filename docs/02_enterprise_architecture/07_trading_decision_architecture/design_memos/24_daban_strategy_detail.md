---
ttl: permanent
doc_type: architecture_view
title: 打板策略细节
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.1.0"
date: 2026-08-10
topic: daban_strategy_detail
scope: 07_trading_decision_architecture
---

# 打板策略细节

> **性质**：由 [00_index_trading_decision](00_index_trading_decision.md) G08 主题组派生，将打板策略的讨论要点落地为可施工的 spec + 伪代码。
> **施工图纪律**：本文档 status=active，对应模块允许施工。
> **2026-08 研究整合**：2026-08 游资生态报告（炸板率 40%→68%、打板次日溢价 4.2%→1.7%）；黄一鸣 2026-04 量化连板接力四维标准；雪球 2026-04/07 情绪周期+龙头战法四模式；WyckoffTradingAgent 2026-07 板块状态分类（共识高潮/派发风险等）；2026-04 程序化交易新规（多账户联动实时监控）；**v1.1.0 新增**：疯牛 v2.0 四维评分体系（资金强度40+连板辨识度30+技术形态20+量波共振10，回测TOP20次日+4.94%/上涨率80%）；Smart Money Profiler 席位画像（quantskills 2026-06，机构/游资/北向身份标签+跨期行为画像）；连板强度公式+一进二连板率 BK_ZT2LBRatio（<10%停止打板）；龙虎榜净买率回测（>12%次日+3.10%/20日+5.11%）+合力型vs独食型+假机构陷阱识别。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G08 打板策略细节 |
| 所属 | 作战地图 05（BM-SEL-22~25）+ 30_multi_strategy_concurrency §4.3 |
| 依赖 | G04、G05、G06 |
| 对标 | 游资打板体系（龙虎榜/连板梯队/情绪周期）/ 量化社区连板策略 |
| 正交性 | ✅ 与 regime 正交 |
| 优先级 | P2 |
| 状态 | ✅ active — 连板梯队+情绪周期+龙头识别+四维接力+风控参数已定稿 |

## 2. 背景

### 2.1 项目处境

打板策略是 A 股独有的短线策略，核心逻辑：在个股涨停（触及涨跌停板上限）时买入，赌次日溢价或连板。2026 年打板生态发生剧变——量化成交占全市场 35%+，中小盘题材股超 50%，量化已用 ML 完整复刻游资盘口特征，传统打板套路失效。

### 2.2 核心问题

1. **炸板率飙升**：2023 年 40% → 2026 年 68%，打板次日溢价从 4.2% 降至 1.7%（高位科技涨停次日溢价中位数为负）。
2. **量化破解游资套路**：量化微秒级捕捉点火大单、封板挂单、分时脉冲；游资 T+1 受限，量化可融券 T+0 套利砸板。
3. **监管收紧**：2026-04 程序化交易新规落地，实时监控多账户联动、大额对倒、频繁撤单——暴力抱团高位龙头模式不复存在。
4. **连板高度下降**：2026 新特点——连板高度下降、趋势龙重要性上升、监管介入使"断板反包/趋势上行/容量中军"取代连续顶一字。
5. **容量极小**：打板单票几万~几十万，必须小账本独立运行。

### 2.3 约束条件

- **T+1 约束**：当日打板买入次日才能卖出，无法日内止损
- **涨跌停板**：涨停封板时买不进，需排队或开板瞬间抢入
- **容量极小**：单票几万~几十万，不适合大资金
- **2026-04 新规**：多账户联动实时监控，禁止暴力抱团
- **必须小账本**：打板策略独立运行，不与多因子/事件驱动混账

## 3. 决策

### 3.1 架构定义

打板策略由市场情绪层、标的筛选层、执行层三层构成：

```
市场情绪层: 涨停家数/连板晋级率/情绪周期定位 → 市场可交易性判定
                                        ↓
标的筛选层: 连板梯队识别 → 龙头识别 → 四维接力筛选 → 候选标的
                                        ↓
执行层: 封板排队/开板抢入/低吸 → T+1 卖出 → 打板专用风控
```

### 3.2 情绪周期定位算法

```python
from enum import Enum
from dataclasses import dataclass
import numpy as np

class SentimentPhase(Enum):
    """情绪周期五阶段（雪球 2026-04/07）。"""
    FREEZING = "冰点"     # 涨停<20，连板晋级率<30%
    STARTING = "启动"     # 涨停 20-40，连板晋级率 30-50%
    FERMENTING = "发酵"   # 涨停 40-60，连板晋级率 50-65%
    CONSENSUS = "一致"    # 涨停>60，连板晋级率>65%（高位风险）
    EBING = "退潮"        # 涨停骤降，炸板率飙升


@dataclass
class MarketSentiment:
    """市场情绪状态。"""
    phase: SentimentPhase
    limit_up_count: int          # 涨停家数
    limit_down_count: int        # 跌停家数
    consecutive_ladder: dict     # 连板梯队 {2板: N, 3板: N, ...}
    promotion_rate: float        # 连板晋级率 = 晋级家数 / 连板家数
    explosion_rate: float        # 炸板率 = 炸板数 / (炸板数 + 涨停数)
    is_tradable: bool            # 市场可交易性
    position_scale: float        # 仓位缩放系数


def evaluate_market_sentiment(
    limit_up_count: int,
    limit_down_count: int,
    consecutive_ladder: dict,     # {2: 10, 3: 5, 4: 2, 5: 1}
    yesterday_consecutive: dict,  # 昨日连板梯队
    explosion_count: int,         # 炸板数
) -> MarketSentiment:
    """情绪周期定位——五阶段判定市场可交易性。

    雪球 2026-04 投科投资《量化时代情绪龙头战法》：
    - 冰点 → 启动 → 发酵 → 一致 → 退潮
    - 2026 新特点：连板高度下降、趋势龙重要性上升

    黄一鸣 2026-04 四维筛选第一维：
    - 涨停家数 ≥ 30
    - 连板晋级率 ≥ 50%
    """
    # 连板晋级率 = 今日晋级家数 / 昨日连板家数
    yesterday_consecutive_total = sum(yesterday_consecutive.values()) if yesterday_consecutive else 0
    today_promoted = sum(consecutive_ladder.get(k + 1, 0) for k in yesterday_consecutive)
    promotion_rate = today_promoted / yesterday_consecutive_total if yesterday_consecutive_total > 0 else 0.0

    # 炸板率
    explosion_rate = explosion_count / (explosion_count + limit_up_count) if (explosion_count + limit_up_count) > 0 else 0.0

    # 五阶段判定
    if limit_up_count < 20 and promotion_rate < 0.30:
        phase = SentimentPhase.FREEZING
    elif limit_up_count < 40 and promotion_rate < 0.50:
        phase = SentimentPhase.STARTING
    elif limit_up_count < 60 and promotion_rate < 0.65:
        phase = SentimentPhase.FERMENTING
    elif limit_up_count >= 60 and promotion_rate >= 0.65:
        phase = SentimentPhase.CONSENSUS  # 高位风险
    else:
        phase = SentimentPhase.EBING

    # 可交易性判定（黄一鸣标准：涨停≥30 + 晋级率≥50%）
    if phase == SentimentPhase.FERMENTING:
        is_tradable = True
        position_scale = 1.0
    elif phase == SentimentPhase.STARTING:
        is_tradable = limit_up_count >= 30 and promotion_rate >= 0.50
        position_scale = 0.7  # 启动期仓位缩窄
    elif phase == SentimentPhase.CONSENSUS:
        is_tradable = True  # 可交易但高度警惕
        position_scale = 0.5  # 一致期仓位减半（退潮风险）
    elif phase == SentimentPhase.FREEZING:
        is_tradable = False
        position_scale = 0.0
    else:  # EBING
        is_tradable = False
        position_scale = 0.0

    return MarketSentiment(
        phase=phase,
        limit_up_count=limit_up_count,
        limit_down_count=limit_down_count,
        consecutive_ladder=consecutive_ladder,
        promotion_rate=promotion_rate,
        explosion_rate=explosion_rate,
        is_tradable=is_tradable,
        position_scale=position_scale,
    )
```

### 3.3 连板梯队识别算法

```python
@dataclass
class ConsecutiveLadder:
    """连板梯队状态。"""
    ladder: dict[int, list[str]]   # {连板数: [股票代码列表]}
    highest_consecutive: int       # 当前最高连板数
    is_complete: bool              # 梯队是否完整无断层
    leader_stocks: list[str]       # 龙头标的


def identify_consecutive_ladder(
    stocks_consecutive_count: dict[str, int],  # {股票代码: 连板数}
) -> ConsecutiveLadder:
    """连板梯队识别——检测梯队完整性和断层。

    黄一鸣 2026-04：
    - 当前市场最高连板/梯队前列（3 板+，或 2 板核心龙头）
    - 梯队完整无断层

    断层判定：如 5板→3板→1板（缺 4板和 2板）= 严重断层
    完整梯队：如 5板→4板→3板→2板→1板 = 健康
    """
    # 按连板数分组
    ladder = {}
    for stock, count in stocks_consecutive_count.items():
        if count not in ladder:
            ladder[count] = []
        ladder[count].append(stock)

    if not ladder:
        return ConsecutiveLadder(ladder={}, highest_consecutive=0, is_complete=False, leader_stocks=[])

    highest = max(ladder.keys())

    # 断层检测
    is_complete = True
    for n in range(highest, 0, -1):
        if n not in ladder or len(ladder[n]) == 0:
            is_complete = False
            break

    # 龙头识别：最高连板标的
    leader_stocks = ladder.get(highest, [])

    return ConsecutiveLadder(
        ladder=ladder,
        highest_consecutive=highest,
        is_complete=is_complete,
        leader_stocks=leader_stocks,
    )
```

### 3.4 四维量化接力筛选算法

```python
@dataclass
class DabanRelaySignal:
    """打板接力四维筛选信号。"""
    symbol: str
    market_sentiment_pass: bool     # 维度1：市场情绪
    ladder_pass: bool               # 维度2：连板梯队
    stock_quality_pass: bool        # 维度3：标的自身
    capital_flow_pass: bool         # 维度4：资金面
    all_pass: bool                  # 四维全部满足
    risk_flags: list[str]           # 风险标记
    suggested_position: float       # 建议仓位（成）


def evaluate_daban_relay(
    symbol: str,
    sentiment: MarketSentiment,         # 市场情绪
    ladder: ConsecutiveLadder,          # 连板梯队
    # 标的自身维度
    float_mkt_cap: float,               # 流通市值（亿）
    turnover_rate: float,               # 换手率
    volume_ratio_vs_avg: float,         # 量比（ vs 历史均量）
    consecutive_count: int,             # 当前连板数
    # 资金面维度
    seal_amount: float,                 # 封单金额（亿）
    main_net_inflow: float,             # 主力净流入（亿）
    northbound_net_inflow: float,       # 北向净流入（亿）
    dragon_tiger_inst_ratio: float,     # 龙虎榜游资+机构买入占比
    cancel_rate: float,                 # 撤单率
) -> DabanRelaySignal:
    """打板接力四维量化筛选——黄一鸣 2026-04。

    四维全部满足方可接力：
    1. 市场情绪：涨停≥30 + 晋级率≥50%
    2. 连板梯队：3板+或2板核心龙头，梯队完整无断层
    3. 标的自身：流通市值50-200亿 + 换手5%-15% + 价涨量增
    4. 资金面：封单≥1亿且占流通市值≥1% + 无大额撤单 + 主力+北向净流入 + 龙虎榜占比≥60%

    分阶段策略：
    - 2板接力（中性/强势市场）：仓位0.3-0.5成
    - 3板+接力（仅强势市场）：仓位0.2-0.3成
    """
    risk_flags = []

    # 维度 1：市场情绪
    market_pass = (
        sentiment.is_tradable and
        sentiment.limit_up_count >= 30 and
        sentiment.promotion_rate >= 0.50
    )
    if not market_pass:
        risk_flags.append(f"market_sentiment_fail(phase={sentiment.phase.value})")

    # 维度 2：连板梯队
    ladder_pass = (
        consecutive_count >= 2 and
        ladder.highest_consecutive >= 3 and
        ladder.is_complete
    )
    if not ladder_pass:
        risk_flags.append(f"ladder_fail(consecutive={consecutive_count}, highest={ladder.highest_consecutive})")

    # 维度 3：标的自身
    stock_pass = True
    if not (50 <= float_mkt_cap <= 200):
        stock_pass = False
        risk_flags.append(f"mkt_cap_out_of_range({float_mkt_cap:.0f}亿)")
    if not (0.05 <= turnover_rate <= 0.15):
        stock_pass = False
        if turnover_rate > 0.20:
            risk_flags.append(f"turnover_too_high({turnover_rate:.1%})_爆量排除")
        else:
            risk_flags.append(f"turnover_out_of_range({turnover_rate:.1%})")
    if volume_ratio_vs_avg < 1.0:
        stock_pass = False
        risk_flags.append(f"volume_ratio_low({volume_ratio_vs_avg:.1f})")

    # 维度 4：资金面
    capital_pass = True
    seal_ratio = seal_amount / float_mkt_cap if float_mkt_cap > 0 else 0.0
    if seal_amount < 1.0 or seal_ratio < 0.01:
        capital_pass = False
        risk_flags.append(f"seal_insufficient({seal_amount:.1f}亿, {seal_ratio:.2%})")
    if cancel_rate > 0.30:
        capital_pass = False
        risk_flags.append(f"cancel_rate_high({cancel_rate:.1%})")
    if main_net_inflow < 0 or northbound_net_inflow < 0:
        capital_pass = False
        risk_flags.append(f"capital_outflow(main={main_net_inflow:.1f}亿, north={northbound_net_inflow:.1f}亿)")
    if dragon_tiger_inst_ratio < 0.60:
        capital_pass = False
        risk_flags.append(f"dragon_tiger_low({dragon_tiger_inst_ratio:.1%})")

    all_pass = market_pass and ladder_pass and stock_pass and capital_pass

    # 建议仓位
    if not all_pass:
        suggested_position = 0.0
    elif consecutive_count == 2:
        suggested_position = 0.4  # 2板接力 0.3-0.5成
    elif consecutive_count >= 3:
        # 3板+仅强势市场（涨停≥40、晋级率≥60%）
        if sentiment.limit_up_count >= 40 and sentiment.promotion_rate >= 0.60:
            suggested_position = 0.25  # 3板+接力 0.2-0.3成
        else:
            suggested_position = 0.0
            risk_flags.append("3board_requires_strong_market")
    else:
        suggested_position = 0.0

    # 情绪仓位缩放
    suggested_position *= sentiment.position_scale

    return DabanRelaySignal(
        symbol=symbol,
        market_sentiment_pass=market_pass,
        ladder_pass=ladder_pass,
        stock_quality_pass=stock_pass,
        capital_flow_pass=capital_pass,
        all_pass=all_pass,
        risk_flags=risk_flags,
        suggested_position=suggested_position,
    )
```

### 3.5 龙头识别算法

```python
@dataclass
class LeaderPattern:
    """龙头战法模式（雪球 2026-04/07）。"""
    pattern: str           # "主线启动龙" / "弱转强龙" / "换手龙" / "分歧转一致"
    confidence: float      # [0, 1]
    entry_timing: str      # 入场时机描述


def identify_leader_pattern(
    consecutive_count: int,
    is_first_board: bool,          # 是否首板
    yesterday_turnover: float,     # 昨日换手率
    today_open_premium: float,     # 今日竞价溢价
    today_pullback_to_avg: bool,   # 今日回踩均价线
    volume_shrink_today: bool,     # 今日缩量
    divergence_today: bool,        # 今日是否分歧日
    consensus_from_divergence: bool,  # 分歧转一致
) -> LeaderPattern:
    """龙头识别——四种模式判定（雪球 2026-04/07 投科投资/溪江随笔）。

    2026 新特点：连板高度下降、趋势龙重要性上升、监管介入使
    "断板反包/趋势上行/容量中军"取代连续顶一字。

    四种龙头模式：
    1. 主线启动龙（首板/一进二）：首板质量+次日一进二确认
       买点：竞价有溢价但不过度一致、开盘换手分歧迅速回封
    2. 弱转强龙（二板/三板确认）：昨日充分换手板+今日竞价高开不虚高
       买点：开盘回踩不破均价线快速拉回封板
    3. 换手龙（市场总龙头）：分歧中不断换手淘汰持筹者
       买点：第一次大分歧日而非连续缩量加速日
    4. 分歧转一致（二波/反包）：分歧转一致时介入
       买点：非一致高潮尾端
    """
    # 模式 1：主线启动龙
    if is_first_board or consecutive_count == 1:
        if 0 < today_open_premium < 0.05 and today_pullback_to_avg:
            return LeaderPattern(
                pattern="主线启动龙",
                confidence=0.7,
                entry_timing="竞价有溢价但不一致+开盘分歧回封"
            )

    # 模式 2：弱转强龙
    if consecutive_count in (2, 3):
        if yesterday_turnover > 0.10 and 0 < today_open_premium < 0.03:
            if today_pullback_to_avg:
                return LeaderPattern(
                    pattern="弱转强龙",
                    confidence=0.8,
                    entry_timing="竞价高开不虚高+回踩均价线快速回封"
                )

    # 模式 3：换手龙
    if consecutive_count >= 3 and divergence_today:
        if not volume_shrink_today:  # 非缩量加速
            return LeaderPattern(
                pattern="换手龙",
                confidence=0.65,
                entry_timing="第一次大分歧日（非连续缩量加速日）"
            )

    # 模式 4：分歧转一致
    if consensus_from_divergence:
        return LeaderPattern(
            pattern="分歧转一致",
            confidence=0.6,
            entry_timing="分歧转一致时（非一致高潮尾端）"
        )

    return LeaderPattern(pattern="无龙头模式", confidence=0.0, entry_timing="")
```

### 3.6 打板专用风控参数

```python
@dataclass
class DabanRiskParams:
    """打板专用风控参数——容量极小、T+1 约束、炸板率高。"""
    max_single_position: float       # 单票最大仓位（成），默认 0.5
    max_total_position: float        # 总仓位上限（成），默认 3.0
    stop_loss_next_day: float        # 次日止损线（低开≥3%且无大单抢筹无条件离场）
    stop_profit_3pct: bool           # 冲高3%-5%止盈
    stop_profit_5pct_volatility: bool  # 冲高≥5%且放量滞涨立即止盈
    forced_exit_30min: bool          # 打板30分钟内开板且无快速回封立即止损
    max_consecutive_loss: int        # 连续亏损上限（触发暂停）


def get_daban_risk_params(market_sentiment: MarketSentiment) -> DabanRiskParams:
    """根据市场情绪调整打板风控参数。"""
    base = DabanRiskParams(
        max_single_position=0.5,
        max_total_position=3.0,
        stop_loss_next_day=0.03,
        stop_profit_3pct=True,
        stop_profit_5pct_volatility=True,
        forced_exit_30min=True,
        max_consecutive_loss=3,
    )

    # 一致期（退潮风险高）收紧风控
    if market_sentiment.phase == SentimentPhase.CONSENSUS:
        base.max_single_position = 0.3
        base.max_total_position = 2.0
        base.stop_loss_next_day = 0.02  # 更紧止损

    # 启动期放宽
    if market_sentiment.phase == SentimentPhase.STARTING:
        base.max_total_position = 2.0  # 启动期仓位较保守

    return base
```

### 3.7 板块状态分类算法（WyckoffTradingAgent 2026-07）

```python
def classify_sector_state(
    sector_returns: dict[str, float],     # 当日各板块收益率
    sector_volumes: dict[str, float],     # 当日各板块成交量
    sector_prev_returns: dict[str, float],# 前日各板块收益率
) -> dict[str, str]:
    """板块状态分类——WyckoffTradingAgent 2026-07。

    A 股板块轮动实测（2025-10 至 2026-04, 申万一级 31 个行业）：
    - Top3 板块次日重合率 14.8%（85% 概率换热门）
    - Top3 完全不同的天数 63.2%
    - 板块领涨只持续 1 天 46.6%

    五种板块状态：
    | 状态 | 特征 | 系统反应 |
    | 共识高潮 | 多板块同时暴涨 | 重扣 -0.15（后3日下跌>2%概率29.8%）|
    | 分歧回调 | 涨跌分化，领涨回调 | 微加分 +0.01 |
    | 健康主线 | 一条明确主线持续领涨 | 加分 +0.03 |
    | 派发风险 | 领涨板块高位放量滞涨 | 重扣 -0.10（最危险）|
    | 中性混沌 | 涨跌互现无序 | 0 |

    板块强度公式（改进版）：
    score = 0.4×q20 + 0.3×q5 + 0.3×q3
    （q3=3日动量，快速感知方向变化；hot_bonus 从0.05降至0.02）
    """
    n_sectors = len(sector_returns)
    if n_sectors == 0:
        return {}

    # 统计涨跌分布
    up_count = sum(1 for r in sector_returns.values() if r > 0.02)
    down_count = sum(1 for r in sector_returns.values() if r < -0.02)
    flat_count = n_sectors - up_count - down_count

    # 排序找领涨/领跌
    sorted_sectors = sorted(sector_returns.items(), key=lambda x: x[1], reverse=True)
    top_sectors = sorted_sectors[:3]
    bottom_sectors = sorted_sectors[-3:]

    # 状态判定
    result = {}
    for sector, ret in sector_returns.items():
        prev_ret = sector_prev_returns.get(sector, 0)
        vol = sector_volumes.get(sector, 0)
        avg_vol = sum(sector_volumes.values()) / n_sectors

        # 共识高潮：多板块同时暴涨
        if up_count > n_sectors * 0.6 and ret > 0.03:
            result[sector] = "共识高潮"

        # 派发风险：领涨板块高位放量滞涨
        elif prev_ret > 0.03 and abs(ret) < 0.01 and vol > avg_vol * 1.5:
            result[sector] = "派发风险"

        # 分歧回调：前日领涨今日回调
        elif prev_ret > 0.03 and ret < -0.01:
            result[sector] = "分歧回调"

        # 健康主线：持续领涨
        elif ret > 0.03 and prev_ret > 0.02:
            result[sector] = "健康主线"

        # 中性混沌
        else:
            result[sector] = "中性混沌"

    return result
```

### 3.8 疯牛 v2.0 四维评分算法（2026-08 回测校准）

```python
@dataclass
class FengniuScore:
    """疯牛 v2.0 四维评分结果——基于回测重构的涨停捕捉模型。

    回测基础（2026-04-29→04-30，100 只涨停股）：
    - TOP20 平均次日涨幅 +4.94%
    - TOP20 上涨率 80.0%
    - 触发止损率(< -5%) 0%
    - 最强预测因子：资金强度（有信号连板率 32.7% vs 无信号 3.9%）

    四维评分体系（总分 100）：
    | 维度 | 权重 | 回测依据 |
    | 资金强度 | 40 | 最强预测因子，有信号连板率 32.7% vs 无 3.9% |
    | 连板辨识度 | 30 | 有连板记录连板率 26.4% vs 纯首板 8.5% |
    | 技术形态 | 20 | 均线/布林/60日线突破综合 |
    | 量波共振 | 10 | 量比/换手/封板时间综合 |
    """
    symbol: str
    capital_strength_score: float      # 维度1：资金强度（满分40）
    consecutive_identity_score: float  # 维度2：连板辨识度（满分30）
    technical_pattern_score: float     # 维度3：技术形态（满分20）
    volume_wave_score: float           # 维度4：量波共振（满分10）
    total_score: float                 # 总分（满分100）
    signal_level: str                  # "strong" / "medium" / "weak"
    sub_scores: dict[str, float]       # 各子项明细


def compute_fengniu_score(
    symbol: str,
    # 维度1：资金强度（40分）
    main_net_inflow: float,            # 主力净流入（万）
    capital_flow_ratio: float,         # 资金流占比（%）
    expma_breakthrough: float,         # EXPMA成本线突破幅度（%）
    # 维度2：连板辨识度（30分）
    consecutive_count: int,            # 连板数
    has_history_within_30d: bool,      # 30日内是否有涨停记录
    # 维度3：技术形态（20分）
    ma_aligned: bool,                  # 5>10>20 均线多头排列且收盘站上
    boll_breakthrough: float,          # 布林上轨突破幅度（1.06×上轨=满分）
    break_60d_line: float,             # 60日线（妖股线）突破幅度（%）
    # 维度4：量波共振（10分）
    volume_ratio: float,               # 量比
    turnover_rate: float,              # 换手率
    seal_time_minutes: float,          # 封板时间（开盘后分钟数）
) -> FengniuScore:
    """疯牛 v2.0 四维评分——基于回测数据重构的涨停捕捉模型。

    数据来源：疯牛 v2.0（2026-05-04 发布，2026-04-29→30 回测校准）
    核心改进 vs v1.0：移除"二次启动"（95%无效）+ 新增"连板辨识度"

    信号等级：
    - strong（≥80分）：重点关注，可介入
    - medium（60-79分）：一般关注，盘中确认
    - weak（<60分）：观望
    """
    # ===== 维度1：资金强度（40分）— 最强预测因子 =====
    # 主力净流入（20分）
    if main_net_inflow > 1000:
        s_main = 20.0
    elif main_net_inflow > 500:
        s_main = 15.0
    else:
        s_main = 5.0

    # 资金流占比（10分）
    if capital_flow_ratio > 15:
        s_flow = 10.0
    elif capital_flow_ratio > 10:
        s_flow = 7.0
    else:
        s_flow = 3.0

    # EXPMA成本线突破（10分）
    if expma_breakthrough > 5:
        s_expma = 10.0
    elif expma_breakthrough > 3:
        s_expma = 7.0
    else:
        s_expma = 3.0

    capital_score = s_main + s_flow + s_expma  # 满分40

    # ===== 维度2：连板辨识度（30分）=====
    # 连板数等级（25分）
    if consecutive_count >= 3:
        s_consec = 25.0
    elif consecutive_count == 2:
        s_consec = 20.0
    else:  # 首板
        s_consec = 8.0

    # 涨停历史（5分）：非首板（30日内有记录）12分，纯首板3分
    # 注意：回测显示有连板记录连板率 26.4% vs 纯首板 8.5%
    s_history = 5.0 if has_history_within_30d else 1.0

    consecutive_score = s_consec + s_history  # 满分30

    # ===== 维度3：技术形态（20分）=====
    # 均线多头排列（8分）
    s_ma = 8.0 if ma_aligned else 0.0

    # 突破布林上轨（6分）：突破 1.06×布林上轨得满分
    s_boll = 6.0 if boll_breakthrough >= 1.06 else (3.0 if boll_breakthrough >= 1.0 else 0.0)

    # 突破60日线/妖股线（6分）：突破3%以上
    s_60d = 6.0 if break_60d_line >= 3 else (3.0 if break_60d_line > 0 else 0.0)

    technical_score = s_ma + s_boll + s_60d  # 满分20

    # ===== 维度4：量波共振（10分）=====
    # 量比（4分）
    if volume_ratio > 3:
        s_vr = 4.0
    elif volume_ratio > 2:
        s_vr = 3.0
    else:
        s_vr = 1.0

    # 换手率（3分）：3%-8%为理想区间
    if 0.03 <= turnover_rate <= 0.08:
        s_turn = 3.0
    elif turnover_rate > 0.08:
        s_turn = 1.5  # 过高换手有分歧风险
    else:
        s_turn = 0.5

    # 封板时间（3分）：开盘即封板3分，10:30前2分
    if seal_time_minutes <= 0:
        s_seal = 3.0  # 开盘即封板
    elif seal_time_minutes <= 60:  # 10:30前
        s_seal = 2.0
    else:
        s_seal = 0.5  # 尾盘封板质量差

    volume_score = s_vr + s_turn + s_seal  # 满分10

    # ===== 总分与信号等级 =====
    total = capital_score + consecutive_score + technical_score + volume_score

    if total >= 80:
        level = "strong"
    elif total >= 60:
        level = "medium"
    else:
        level = "weak"

    return FengniuScore(
        symbol=symbol,
        capital_strength_score=capital_score,
        consecutive_identity_score=consecutive_score,
        technical_pattern_score=technical_score,
        volume_wave_score=volume_score,
        total_score=total,
        signal_level=level,
        sub_scores={
            "main_net_inflow": s_main,
            "capital_flow_ratio": s_flow,
            "expma_breakthrough": s_expma,
            "consecutive_count": s_consec,
            "history": s_history,
            "ma_aligned": s_ma,
            "boll_breakthrough": s_boll,
            "break_60d": s_60d,
            "volume_ratio": s_vr,
            "turnover": s_turn,
            "seal_time": s_seal,
        },
    )
```

### 3.9 Smart Money 席位画像算法（quantskills 2026-06）

```python
from dataclasses import dataclass, field
from enum import Enum


class SeatType(Enum):
    """龙虎榜席位身份标签（quantskills 2026-06 Smart Money Profiler）。"""
    INSTITUTIONAL = "机构专用"      # 公募/社保/保险/券商自营，中长线
    NORTHBOUND = "沪深股通"          # 北向资金，近年游资化但仍偏好龙头
    HOT_MONEY_RETAIL = "游资营业部"  # 知名游资/散户集中营
    QUANT = "量化席位"              # 如华鑫上海分公司
    UNKNOWN = "未识别"


@dataclass
class SeatProfile:
    """席位画像——跨期行为档案。

    quantskills Smart Money Profiler（2026-06-29）核心能力：
    把交易行为还原成"有名有姓的资金主体"，每个席位累积可持久化画像。

    画像字段（基于龙虎榜历史数据累积）：
    - 上榜频次：该席位历史出现次数
    - 累计净买卖：历史净买入/净卖出总额
    - 上榜后5/10/20日胜率：该席位买入后标的5/10/20日正收益比例
    - 平均持有/退出周期：估计的持仓天数
    - 偏好板块：该席位最常操作的行业
    - 风格标签：合力型/独食型/一日游/假机构
    """
    seat_name: str                       # 席位名称
    seat_type: SeatType                  # 身份标签
    appearance_count: int                # 上榜频次
    cumulative_net_buy: float            # 累计净买入（万）
    win_rate_5d: float                   # 上榜后5日胜率
    win_rate_10d: float                  # 上榜后10日胜率
    win_rate_20d: float                  # 上榜后20日胜率
    avg_hold_days: int                   # 平均持有天数
    preferred_sectors: list[str]         # 偏好板块
    style_tags: list[str]                # 风格标签


@dataclass
class DragonTigerAnalysis:
    """龙虎榜分析结果——资金结构与席位画像综合。"""
    symbol: str
    # 资金结构
    total_buy: float                     # 买方前五总额
    total_sell: float                    # 卖方前五总额
    net_buy: float                       # 净买入额
    net_buy_ratio: float                 # 净买率 = 净买入 / 当日成交额
    buy_sell_ratio: float                # 买方总额 / 卖方总额
    # 席位分析
    buyer_profiles: list[SeatProfile]    # 买方席位画像
    seller_profiles: list[SeatProfile]   # 卖方席位画像
    # 结构判定
    structure_type: str                  # "合力型" / "独食型" / "分歧型"
    is_fake_institutional: bool          # 是否假机构陷阱
    smart_money_signal: str              # "strong" / "medium" / "weak" / "avoid"
    risk_flags: list[str]                # 风险标记


def analyze_dragon_tiger(
    symbol: str,
    total_turnover: float,               # 当日成交额
    buyer_seats: list[dict],             # [{seat_name, seat_type, buy_amount, sell_amount, profile}]
    seller_seats: list[dict],            # [{seat_name, seat_type, buy_amount, sell_amount, profile}]
) -> DragonTigerAnalysis:
    """龙虎榜资金结构分析——席位画像+合力型/独食型/假机构识别。

    2026-08 研究整合：
    - 净买率回测（东方财富 2026-08）：净买率>12% → 次日+3.10%，20日+5.11%
    - 合力型 vs 独食型：买一至买五金额分布均匀（合力型）优于买一占比>50%（独食型）
      独食型次日易因单一资金砸盘而低开
    - 假机构陷阱特征：买入金额整齐（如888万）、尾盘突击买入、次日快速出货
    - Smart Money Profiler（quantskills 2026-06）：席位身份标签+跨期行为画像

    强势信号标准（综合）：
    - 买方前五总额 ≥ 卖方 1.5倍
    - 净买入额占当日成交额 > 3%
    - 净买率 > 12% → 次日显著正收益

    危险信号：
    - 卖榜为空（可能主力拆单出货）
    - 同一席位同时出现在买卖榜（对倒嫌疑）
    - 量化席位扎堆（走势反人性）
    - 假机构陷阱（整齐买入金额+尾盘突击）
    """
    total_buy = sum(s.get("buy_amount", 0) for s in buyer_seats)
    total_sell = sum(s.get("sell_amount", 0) for s in seller_seats)
    net_buy = total_buy - total_sell
    net_buy_ratio = net_buy / total_turnover if total_turnover > 0 else 0.0
    buy_sell_ratio = total_buy / total_sell if total_sell > 0 else float("inf")

    risk_flags = []

    # ===== 结构判定：合力型 / 独食型 / 分歧型 =====
    buy_amounts = [s.get("buy_amount", 0) for s in buyer_seats]
    top1_buy = max(buy_amounts) if buy_amounts else 0
    top1_ratio = top1_buy / total_buy if total_buy > 0 else 0

    if top1_ratio > 0.50:
        structure_type = "独食型"
        risk_flags.append(f"solo_buyer_dominant(top1={top1_ratio:.1%})_次日易低开")
    elif buy_sell_ratio >= 1.5:
        structure_type = "合力型"  # 买方分布均匀且总额显著大于卖方
    else:
        structure_type = "分歧型"
        risk_flags.append(f"buy_sell_ratio_low({buy_sell_ratio:.2f})")

    # ===== 假机构陷阱识别 =====
    is_fake_inst = False
    for seat in buyer_seats:
        if seat.get("seat_type") == SeatType.INSTITUTIONAL:
            buy_amt = seat.get("buy_amount", 0)
            # 假机构特征：买入金额整齐（如888万、666万等吉利数字）
            if buy_amt > 0:
                # 检查是否为"整齐"金额（万元级别取整到吉利数字）
                amt_wan = buy_amt / 10000
                is_tidy = any(
                    abs(amt_wan - nice) < 1.0
                    for nice in [888, 666, 999, 520, 1314, 168]
                )
                # 尾盘突击：需配合时间数据，此处简化用画像标签
                is_late_rush = "尾盘突击" in seat.get("profile", SeatProfile).style_tags if isinstance(seat.get("profile"), SeatProfile) else False
                if is_tidy or is_late_rush:
                    is_fake_inst = True
                    risk_flags.append(f"fake_institutional({seat['seat_name']}, amt={amt_wan:.0f}万)")
                    break

    # ===== 危险信号检测 =====
    # 卖榜为空（可能主力拆单出货）
    if total_sell == 0:
        risk_flags.append("empty_sell_list_可能拆单出货")

    # 同一席位同时出现在买卖榜（对倒嫌疑）
    buyer_names = {s["seat_name"] for s in buyer_seats}
    seller_names = {s["seat_name"] for s in seller_seats}
    overlap = buyer_names & seller_names
    if overlap:
        risk_flags.append(f"wash_trade_suspect(overlap={overlap})")

    # 量化席位扎堆
    quant_count = sum(1 for s in buyer_seats if s.get("seat_type") == SeatType.QUANT)
    if quant_count >= 2:
        risk_flags.append(f"quant_cluster({quant_count}席)_走势反人性")

    # ===== Smart Money 信号综合判定 =====
    if net_buy_ratio > 0.12 and buy_sell_ratio >= 1.5 and structure_type == "合力型":
        signal = "strong"  # 净买率>12% + 合力型 → 次日显著正收益
    elif net_buy_ratio > 0.03 and buy_sell_ratio >= 1.2:
        signal = "medium"
    elif is_fake_inst or "wash_trade_suspect" in str(risk_flags):
        signal = "avoid"
    else:
        signal = "weak"

    return DragonTigerAnalysis(
        symbol=symbol,
        total_buy=total_buy,
        total_sell=total_sell,
        net_buy=net_buy,
        net_buy_ratio=net_buy_ratio,
        buy_sell_ratio=buy_sell_ratio,
        buyer_profiles=[s.get("profile") for s in buyer_seats if s.get("profile")],
        seller_profiles=[s.get("profile") for s in seller_seats if s.get("profile")],
        structure_type=structure_type,
        is_fake_institutional=is_fake_inst,
        smart_money_signal=signal,
        risk_flags=risk_flags,
    )
```

### 3.10 连板强度与一进二连板率算法

```python
def calc_consecutive_strength(
    close_price: float,
    close_price_n_days_ago: float,    # N日前收盘价
    volume: float,                     # 当日成交量
    sentiment_factor: float,           # 情绪因子（涨停家数/连板晋级率综合）
    n: int = 5,                        # N日回看窗口
) -> float:
    """连板强度指标——量化辅助决策。

    公式（2026-04 连板算法）：
    连板强度 = (当日收盘价 - N日前收盘价) × 成交量 × 情绪因子

    用途：
    - 衡量连板标的的动量强度
    - 横截面排序选择最强连板标的
    - 与疯牛评分互补：疯牛评分是离散分类，连板强度是连续排序

    情绪因子计算：
    sentiment_factor = 涨停家数 / 50 × 连板晋级率
    （涨停50家为中性基准，晋级率反映接力意愿）
    """
    price_change = close_price - close_price_n_days_ago
    strength = price_change * volume * sentiment_factor
    return strength


def calc_zt2lb_ratio(
    today_2board_count: int,           # 今日二板家数（一进二成功）
    yesterday_1board_count: int,       # 昨日首板家数
) -> float:
    """一进二连板率（BK_ZT2LBRatio）——市场短线情绪温度计。

    定义：BK_ZT2LBRatio = 今日二板家数 / 昨日首板家数

    2026-04 连板算法实证：
    - 该比率骤降（如低于10%）说明市场短线情绪极差
    - 低于10%时应停止任何打板操作

    与情绪周期五阶段的关系：
    - 冰点期：BK_ZT2LBRatio < 10%，停止打板
    - 启动期：10%-30%
    - 发酵期：30%-50%
    - 一致期：>50%（但需警惕退潮）
    """
    if yesterday_1board_count == 0:
        return 0.0
    return today_2board_count / yesterday_1board_count


def should_halt_daban(zh2lb_ratio: float, explosion_rate: float) -> tuple[bool, str]:
    """打板熔断判定——综合一进二连板率与炸板率。

    返回 (是否停止打板, 原因)

    熔断条件：
    1. BK_ZT2LBRatio < 10%：市场短线情绪极差，停止打板
    2. 炸板率 > 70%：炸板率过高，打板胜率崩塌
    3. 两者同时触发：强制停止并复盘
    """
    if zh2lb_ratio < 0.10 and explosion_rate > 0.70:
        return True, f"dual_halt(zh2lb={zh2lb_ratio:.1%}, explosion={explosion_rate:.1%})"
    if zh2lb_ratio < 0.10:
        return True, f"zh2lb_too_low({zh2lb_ratio:.1%}<10%)"
    if explosion_rate > 0.70:
        return True, f"explosion_too_high({explosion_rate:.1%}>70%)"
    return False, ""
```

## 4. 考虑过的替代方案

| 方案 | 描述 | 拒绝理由 |
|---|---|---|
| **传统打板** | 不筛选情绪周期，逢板就打 | 2026 炸板率 68%，传统打板胜率崩塌 |
| **高频打板** | 微秒级 ML 捕捉盘口特征 | 2026-04 新规监控多账户联动；需 co-location+Level-2，MVP 不可行 |
| **融券 T+0 砸板** | 量化融券 T+0 套利 | 2024-2025 限融政策约束；A 股融券标的有限 |
| **大资金打板** | 打板策略承载主资金 | 容量极小（单票几万~几十万），必须小账本独立运行 |
| **连续顶一字** | 连续涨停板排队 | 2026 连板高度下降，监管介入使"断板反包/趋势上行"取代连续顶一字 |

## 5. 上限定义

| 上限 | 值 | 理由 |
|---|---|---|
| **单票仓位** | ≤ 0.5 成 | 容量极小 + 炸板率高 |
| **总仓位** | ≤ 3 成 | 打板是小账本策略，不超过总资金的 30% |
| **次日止损** | 低开≥3% 且无大单抢筹 → 离场 | 黄一鸣 2026-04 通用规则 |
| **30 分钟开板止损** | 打板 30 分钟内开板且无快速回封 → 立即止损 | 黄一鸣 2026-04 |
| **连续亏损暂停** | 3 次连续亏损 → 暂停打板 1 天 | 防止情绪化连续打板 |

## 6. 待裁定

| 项 | 暂缓理由 | 重评条件 |
|---|---|---|
| **量化 ML 盘口特征** | 2026-04 新规监控多账户联动 | Phase 2+ 合规框架就绪后 |
| **趋势龙模式** | 2026 新特点但模式未定型 | 积累 3 月实盘数据后评估 |
| **板块强度 0.4q20+0.3q5+0.3q3** | WyckoffTradingAgent 实测有效 | MVP 阶段先用，实盘后校准权重 |

## 7. 待定问题（讨论要点对齐）

- [x] ① 连板梯队识别 → §3.3 `identify_consecutive_ladder`
- [x] ② 情绪周期定位器（BM-SEL-23-B）→ §3.2 `evaluate_market_sentiment` 五阶段
- [x] ③ 主升龙头识别 → §3.5 `identify_leader_pattern` 四种模式
- [x] ④ 打板容量极小（单票几万~几十万）→ §5 上限 + 必须小账本
- [x] ⑤ 双引擎融合在此策略内部（BM-SEL-25）→ §3.4 四维筛选+§3.7 板块状态分类
- [x] ⑥ 打板专用风控参数 → §3.6 `get_daban_risk_params`
- [x] ⑦ T+1 约束下的打板时序 → §3.4 分阶段策略（2板/3板+）+ 次日止盈止损

## 8. 引用

- [00_index_trading_decision](00_index_trading_decision.md) §3 G08
- [20_first_batch_strategies](20_first_batch_strategies.md)（G04 产出物，必先读）
- [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §4.3 / §6.3
- [28_sentiment_cycle_trading](28_sentiment_cycle_trading.md)（G21 情绪周期）
- battle_map_05_stock_selection（BM-SEL-22~25 当前状态快照）
- **2026-08 研究引用**：
  - 东方财富 (2026-08-03) "8 月游资彻底换打法" — 炸板率 68%、次日溢价 1.7%
  - 黄一鸣 (2026-04-20) "龙头战法｜量化连板接力规则" — 四维筛选标准
  - 投科投资 (2026-04-22) 雪球 "量化时代情绪龙头战法完整指南" — 五阶段+四模式
  - 溪江随笔 (2026-07-08) 雪球 "龙头股投资的细节把握"
  - YoungCan-Wang/WyckoffTradingAgent Wiki (2026-07-23) — 板块状态分类+板块强度公式
  - 2026-04 程序化交易新规 — 多账户联动实时监控

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行 |
| 2026-08-10 | 1.0.0 | 落地 spec 定稿 | 情绪周期五阶段+连板梯队+龙头四模式+四维接力筛选+板块状态分类+专用风控算法化；整合 2026-08 研究（炸板率68%/黄一鸣四维/情绪周期/WyckoffTradingAgent 板块分类） |
| 2026-08-10 | 1.1.0 | 新增 §3.8-§3.10 | 疯牛v2.0四维评分（资金强度40+连板辨识度30+技术形态20+量波共振10，回测TOP20次日+4.94%）；Smart Money席位画像（quantskills 2026-06，合力型/独食型/假机构识别）；连板强度公式+一进二连板率BK_ZT2LBRatio（<10%停止打板）；龙虎榜净买率回测（>12%次日+3.10%） |
