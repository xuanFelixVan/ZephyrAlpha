---
ttl: permanent
doc_type: architecture_view
title: 情绪周期×交易决策
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.0.0"
date: 2026-08-10
topic: sentiment_cycle_trading
scope: 07_trading_decision_architecture
---

# 情绪周期×交易决策

> **性质**：由 [00_index_trading_decision](00_index_trading_decision.md) G21 主题组派生，将情绪周期的讨论要点落地为可施工的 spec + 伪代码。
> **施工图纪律**：本文档 status=active，对应模块允许施工。
> **2026-08 研究整合**：A股情绪周期五阶段实操体系（eastmoney 2026-03 实操版、xueqiu 2026-06 五阶段标准模型、55188 2026-07 启动/发酵/高潮/分歧/退潮循环口诀）；炸板率与跌停数量情绪温度评分模型（yueniuzq 2026-06，亏钱效应先行指标）；龙虎榜情绪温度与席位画像（eastmoney 2026-06 因子挖掘/盘大牛 2026-06 游资血槽/sina 2026-02 龙虎榜顶部判断）；打板盈亏比作为情绪反馈（24_daban_strategy_detail 2026-08 炸板率 68%/次日溢价 1.7%）。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G21 情绪周期×交易决策 |
| 所属 | 跨作战地图 05/06/07/09 |
| 依赖 | G04、G08（打板最依赖情绪周期）、G02/G03（regime 12 态，分工边界） |
| 对标 | 游资情绪周期体系（启动/发酵/高潮/分歧/退潮）/ 龙虎榜情绪温度 / 涨跌停情绪温度计 |
| 正交性 | ✅ 与 regime 12 态正交：情绪周期=sleeve 内 alpha 择时（决定买卖什么），regime=市场级风险节流（决定多谨慎），两者时间尺度不同（情绪短 1-2 周，regime 中 1-3 月） |
| 优先级 | P2（打板策略前置） |
| 状态 | ✅ active — 五阶段定义+定位器算法+各阶段买卖纪律+regime 映射+策略部署+隐形驱动验证方法已定稿 |

## 2. 背景

### 2.1 项目处境

- A 股是散户主导的情绪市场（散户成交占比长期超 60%），短期走势由情绪驱动，中期看情绪与基本面共振，长期才回归价值（xueqiu 2026-06）。情绪波动领先基本面，是短线策略的核心"势"
- 多策略并发架构已定稿为 Model A（[30_multi_strategy_concurrency](30_multi_strategy_concurrency.md)）：独立账本 + firm 风险聚合 + regime 风险节流。首批 3 策略（打板/多因子/事件驱动）已定义（[20_first_batch_strategies](20_first_batch_strategies.md)）
- 情绪周期探测器 BM-SEL-23-B 已 🟦 production，下游被 BM-SEL-25 双引擎融合消费；regime 检测器由另一 AI 负责（[10_regime_detector_spec](10_regime_detector_spec.md) C-prime 方案：BM-SEL-03-B 升级为 12 态本体，BM-SEL-23-B 降级为情绪轴软输入）
- 2026 打板生态剧变：炸板率从 2023 年 40% 飙升到 68%，打板次日溢价从 4.2% 降至 1.7%；连板高度下降、趋势龙重要性上升；2026-04 程序化交易新规监控多账户联动（[24_daban_strategy_detail](24_daban_strategy_detail.md) §2.2）

### 2.2 核心问题

1. **情绪周期五阶段如何精确定义**：游资圈有多种命名（启动/发酵/高潮/分歧/退潮 vs 冰点/反核/主升/疯狂/退潮），需统一为本系统的标准五阶段及各阶段可观测的市场特征指标，避免"模糊感觉"驱动决策
2. **情绪周期定位器如何算法化**：BM-SEL-23-B 当前是 production 资产但准确率待评估（[30_multi_strategy_concurrency §6.3](30_multi_strategy_concurrency.md)），错判代价大（主升判成冰点→该进攻时防守），需有"置信度<60%→默认保守"的兜底
3. **情绪周期与 regime 12 态如何分工**：两者都沾"情绪"（regime 12 态含情绪维度，BM-SEL-23-B 也含情绪），[20_first_batch_strategies §5 待裁定-4](20_first_batch_strategies.md) 明确"需 G21 澄清边界"——本讨论裁定
4. **各策略在不同情绪阶段如何部署**：打板在主升/疯狂重仓，多因子在冰点/反核布局，事件驱动跨阶段——需算法化各阶段的 position_scale/throttle_factor/allow_new_open/策略亲和性
5. **情绪周期作为"隐形驱动"如何验证**：[30_multi_strategy_concurrency §1.3](30_multi_strategy_concurrency.md) 明确"情绪周期是所有短周期策略的共同隐形驱动→策略间相关性可能高于直觉"，需定义验证方法（分层后相关性是否显著下降）

### 2.3 约束条件

- **A 股 T+1**：当日买入次日才能卖出，情绪周期定位必须盘前/盘中可观测，不能依赖事后数据
- **涨跌停板**：涨停封板时买不进，情绪极端期（疯狂/退潮）流动性失效
- **打板容量极小**：单票几万~几十万，情绪周期驱动的打板 sleeve 必须小账本独立运行
- **情绪周期是隐形驱动**：所有短周期策略（打板/事件驱动尤其）共享同一情绪 beta，[20_first_batch_strategies §2.5](20_first_batch_strategies.md) 已预警"打板与事件驱动相关性可能高于直觉"——这是 G07 施工前必测项
- **与 regime 正交**：[20_first_batch_strategies §1.4](20_first_batch_strategies.md) 对齐 charter §3 约束三"策略选股不读 regime 输出"——情绪周期是 sleeve 内 alpha 择时信号，不破坏 regime 风险节流的正交
- **production 资产不可动**：BM-SEL-23-B 已 production 且有下游依赖（BM-SEL-25 双引擎融合），输出契约变更须谨慎

## 3. 决策

### 3.1 架构定义

情绪周期×交易决策由三层构成，作为 sleeve 内 alpha 择时的完整闭环：

```
情绪周期定位层: 多维指标(涨停数/跌停数/连板高度/炸板率/打板盈亏比/换手率)
                → BM-SEL-23-B 定位器 → 5 维灰度概率分布 P(5阶段)
                                                              ↓
买卖纪律层:    各阶段 position_scale / throttle_factor / allow_new_open
              / 策略亲和性 → sleeve 内 alpha 择时（决定买卖什么）
                                                              ↓
regime 协同层: 情绪周期软影响 12 态概率（映射表）→ regime 做 Shrinkage 风险节流
              （决定多谨慎，不决定买卖什么）
```

**核心定位（与 regime 分工裁定）**：
- **情绪周期 = sleeve 内 alpha 择时信号**：回答"现在该买卖什么"——打板在主升/疯狂期重仓连板梯队，多因子在冰点/反核期布局低位横截面
- **regime 12 态 = 市场级风险节流**：回答"现在该多谨慎"——通过 Shrinkage 收缩总暴露，不参与选股
- **两者正交**：情绪周期管"方向/标的"，regime 管"力度/谨慎度"；时间尺度不同（情绪短 1-2 周，regime 中 1-3 月）；不破坏 [20_first_batch_strategies §1.4](20_first_batch_strategies.md) charter §3 约束三"策略选股不读 regime 输出"

### 3.2 五阶段情绪周期定义

```python
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional


class SentimentPhase(Enum):
    """情绪周期五阶段——A 股短周期炒作的微观视角。

    统一命名（对齐 10_regime_detector_spec §3.3 与 24_daban_strategy_detail §3.2）：
        FREEZING   = 冰点   （绝望期，空头力量衰竭，底部拐点前夜）
        STARTING    = 反核   （希望期，首批试探性入场，情绪拐点确认）
        FERMENTING  = 主升   （乐观期，主线明确，赚钱效应扩散）
        CONSENSUS   = 疯狂   （一致看多期，加速赶顶，波动放大）
        EBING       = 退潮   （亏钱效应期，主线断裂，流动性枯竭）

    游资圈命名对照（55188 2026-07 / xueqiu 2026-06 / eastmoney 2026-03）：
        启动/发酵/高潮/分歧/退潮 ≈ 反核/主升/疯狂/退潮前兆/退潮
    本系统采用"冰点/反核/主升/疯狂/退潮"五段命名，与 regime 映射表对齐。
    """
    FREEZING = "冰点"      # 绝望期：地量大跌、恐慌一致看空、利好麻木
    STARTING = "反核"      # 希望期：止跌缩量反弹、局部赚钱效应、利好敏感
    FERMENTING = "主升"    # 乐观期：放量上涨、主线清晰、赚钱效应扩散
    CONSENSUS = "疯狂"    # 一致期：加速赶顶、连板高位、波动放大
    EBING = "退潮"        # 退潮期：涨停骤降、炸板率飙升、核按钮批量


@dataclass
class PhaseCharacteristics:
    """各阶段市场特征指标——eastmoney 2026-03 实操版 + xueqiu 2026-06 标准模型。

    所有阈值均来自游资圈实战共识，可作为定位器的先验判据与人工复盘对照表。
    """
    phase: SentimentPhase
    # 涨跌停维度（情绪热度核心）
    limit_up_range: tuple[int, int]       # 涨停家数区间
    limit_down_range: tuple[int, int]     # 跌停家数区间
    consecutive_height: tuple[int, int]   # 连板高度区间（最高板）
    # 炸板率维度（资金信心指标）
    explosion_rate_range: tuple[float, float]   # 炸板率区间（炸板数/(炸板数+涨停数)）
    # 赚钱效应维度（最真实的情绪反馈）
    next_day_premium_range: tuple[float, float]  # 打板次日溢价区间
    # 量能维度
    turnover_desc: str                    # 换手率/成交额特征描述
    # 资金行为
    fund_behavior: str                    # 资金行为特征
    # 本质
    essence: str                          # 阶段本质


# 五阶段特征表（先验判据，定位器 §3.3 的参考阈值）
PHASE_CHARACTERISTICS: dict[SentimentPhase, PhaseCharacteristics] = {
    SentimentPhase.FREEZING: PhaseCharacteristics(
        phase=SentimentPhase.FREEZING,
        limit_up_range=(0, 20),
        limit_down_range=(10, 999),     # ≥10 家
        consecutive_height=(0, 2),
        explosion_rate_range=(0.40, 1.00),
        next_day_premium_range=(-0.05, -0.02),   # 打板必亏
        turnover_desc="地量，成交额较均值萎缩 50%+，换手率个股<1%",
        fund_behavior="散户恐慌割肉，机构观望，北向逆势小单流入",
        essence="空头力量衰竭，多头孕育，底部拐点前夜",
    ),
    SentimentPhase.STARTING: PhaseCharacteristics(
        phase=SentimentPhase.STARTING,
        limit_up_range=(20, 40),
        limit_down_range=(0, 10),
        consecutive_height=(2, 3),
        explosion_rate_range=(0.30, 0.40),
        next_day_premium_range=(-0.02, 0.01),   # 试错期，溢价差
        turnover_desc="温和放量，较冰点提升 30%+，新题材冒头试盘",
        fund_behavior="先知先觉资金布局，散户犹豫，游资试错龙头",
        essence="情绪拐点确认，赚钱效应萌芽，主线酝酿期",
    ),
    SentimentPhase.FERMENTING: PhaseCharacteristics(
        phase=SentimentPhase.FERMENTING,
        limit_up_range=(40, 80),
        limit_down_range=(0, 5),
        consecutive_height=(4, 6),
        explosion_rate_range=(0.20, 0.30),
        next_day_premium_range=(0.02, 0.04),    # 打板有正溢价
        turnover_desc="放量上涨，较均值提升 20%+，板块形成梯队",
        fund_behavior="资金共识强，风险偏好拉满，打板/追高/低吸均赚钱",
        essence="趋势确立，主线明确，赚钱效应扩散",
    ),
    SentimentPhase.CONSENSUS: PhaseCharacteristics(
        phase=SentimentPhase.CONSENSUS,
        limit_up_range=(80, 999),   # >80 家
        limit_down_range=(0, 3),
        consecutive_height=(7, 999),  # 7 板+
        explosion_rate_range=(0.00, 0.20),
        next_day_premium_range=(0.04, 0.08),   # 溢价极高
        turnover_desc="天量，板块全面爆发，后排跟风也涨停",
        fund_behavior="资金盲目乐观，物极必反，机构开始减持",
        essence="加速赶顶，波动放大，退潮风险积累",
    ),
    SentimentPhase.EBING: PhaseCharacteristics(
        phase=SentimentPhase.EBING,
        limit_up_range=(0, 30),
        limit_down_range=(15, 999),   # 跌停一片
        consecutive_height=(0, 3),
        explosion_rate_range=(0.50, 1.00),   # >50%
        next_day_premium_range=(-0.08, -0.03),  # 空间板被核
        turnover_desc="流动性枯竭，核按钮批量出现，全线杀跌无抵抗",
        fund_behavior="空间板闷杀→跌停家数堆积→偶尔反抽→继续埋",
        essence="主线断裂，亏钱效应扩散，空仓为最优选择",
    ),
}
```

### 3.3 情绪周期定位器算法（BM-SEL-23-B 升级版）

```python
@dataclass
class SentimentLocatorInput:
    """情绪周期定位器输入——多维可观测指标。

    所有指标均为盘后可获取（T 日收盘后定位 T+1 信号），部分支持盘中实时更新。
    对齐 24_daban_strategy_detail §3.2 与 10_regime_detector_spec §2.5.4 灰度输出要求。
    """
    # 涨跌停维度
    limit_up_count: int                 # 涨停家数
    limit_down_count: int               # 跌停家数
    explosion_count: int                # 炸板家数
    # 连板梯队维度
    consecutive_ladder: dict[int, int]  # {连板数: 家数}，如 {2: 10, 3: 5, 4: 2, 5: 1}
    yesterday_consecutive: dict[int, int]  # 昨日连板梯队，用于计算晋级率
    # 赚钱效应维度（情绪反馈最真实）
    daban_next_day_premium: float       # 打板次日平均溢价（当日打板标的次日开盘均值）
    # 量能维度
    avg_turnover_rate: float            # 市场平均换手率
    market_amount_ratio_vs_ma20: float  # 成交额 / 20 日均量
    # 资金行为维度（龙虎榜情绪温度，eastmoney 2026-06）
    dragon_tiger_net_buy_ratio: float  # 龙虎榜净买率 = 净买入 / 当日成交额（>12% 为强信号）
    northbound_net_inflow: float        # 北向净流入（亿）
    # 历史状态（用于贝叶斯更新平滑）
    yesterday_phase_prob: Optional[dict[SentimentPhase, float]] = None  # 昨日 5 维概率


@dataclass
class SentimentLocatorOutput:
    """情绪周期定位器输出——5 维灰度概率分布。

    对齐 10_regime_detector_spec §2.5.4 用户裁定：
    "输出的内容还是一个属于灰度，1%到100%来组成。比如说冰点，今天可能是45%的冰点，
     明天是80%，后天上午10点的时候出现了100%的冰点。"

    灰度输出的好处：映射表可用概率加权（P(冰点)=80% 时加的力度 > P(冰点)=45% 时），
    天然实现"软影响"。
    """
    phase_prob: dict[SentimentPhase, float]   # 5 维概率分布，Σ=1
    dominant_phase: SentimentPhase            # 主导阶段（argmax）
    confidence: float                         # 置信度 = max(P)
    is_tradable: bool                         # 市场可交易性（综合判定）
    position_scale: float                     # 仓位缩放系数（0.0-1.0，供 sleeve 直接用）
    evidence_scores: dict[str, float]         # 各维度证据得分（归因用）
    fallback_triggered: bool                  # 是否触发兜底（置信度<60%→默认保守）


def locate_sentiment_phase(
    inp: SentimentLocatorInput,
    confidence_threshold: float = 0.60,
) -> SentimentLocatorOutput:
    """情绪周期定位器（BM-SEL-23-B 升级版）——5 维灰度概率分布定位。

    算法分四步：
    1. 多维指标评分：对每个阶段，按 PHASE_CHARACTERISTICS 阈值计算证据得分
    2. 先验+贝叶斯更新：用昨日概率作先验，今日证据作似然，归一化得后验
    3. 兜底机制：置信度<60% → 默认保守（回退 FREEZING/EBING 强收缩）
    4. 可交易性+仓位缩放：综合置信度与主导阶段输出 sleeve 可直接消费的 position_scale

    错判代价大（主升判成冰点→该进攻时防守），故采用"宁保守不激进"原则：
    - 兜底优先回退到收缩态（FREEZING/EBING），不回退到扩张态（FERMENTING/CONSENSUS）
    - 置信度<60% 时 position_scale 强制 ≤0.3，无论主导阶段是什么

    2026-08 研究整合：
    - eastmoney 2026-03 五大核心指标（涨停数/跌停数/炸板率/赚钱效应/板块联动）
    - yueniuzq 2026-06 炸板率与跌停数量评分模型（亏钱效应先行指标）
    - xueqiu 2026-06 五阶段标准模型量化信号
    """
    # ===== 步骤 1：多维指标评分（每个阶段的证据得分）=====
    # 计算连板晋级率 = 今日晋级家数 / 昨日连板家数
    yesterday_consec_total = sum(inp.yesterday_consecutive.values()) if inp.yesterday_consecutive else 0
    today_promoted = sum(
        inp.consecutive_ladder.get(k + 1, 0) for k in inp.yesterday_consecutive
    )
    promotion_rate = today_promoted / yesterday_consec_total if yesterday_consec_total > 0 else 0.0

    # 炸板率 = 炸板数 / (炸板数 + 涨停数)
    total_attempt = inp.explosion_count + inp.limit_up_count
    explosion_rate = inp.explosion_count / total_attempt if total_attempt > 0 else 0.0

    # 最高连板高度
    highest_consec = max(inp.consecutive_ladder.keys()) if inp.consecutive_ladder else 0

    # 板块联动近似（用连板梯队宽度，梯队越宽共识越强）
    ladder_breadth = len(inp.consecutive_ladder)

    # 对每个阶段计算证据得分（0-1，越大越支持该阶段）
    evidence: dict[SentimentPhase, float] = {}

    # FREEZING 冰点：涨停少 + 跌停多 + 炸板率高 + 次日溢价负 + 缩量
    evidence[SentimentPhase.FREEZING] = _score_phase(
        target=SentimentPhase.FREEZING,
        limit_up=inp.limit_up_count,
        limit_down=inp.limit_down_count,
        explosion_rate=explosion_rate,
        next_day_premium=inp.daban_next_day_premium,
        highest_consec=highest_consec,
        amount_ratio=inp.market_amount_ratio_vs_ma20,
    )

    # STARTING 反核：涨停回升 + 跌停减少 + 炸板率中等 + 缩量反弹
    evidence[SentimentPhase.STARTING] = _score_phase(
        target=SentimentPhase.STARTING,
        limit_up=inp.limit_up_count,
        limit_down=inp.limit_down_count,
        explosion_rate=explosion_rate,
        next_day_premium=inp.daban_next_day_premium,
        highest_consec=highest_consec,
        amount_ratio=inp.market_amount_ratio_vs_ma20,
    )

    # FERMENTING 主升：涨停多 + 连板高 + 炸板率低 + 正溢价 + 放量
    evidence[SentimentPhase.FERMENTING] = _score_phase(
        target=SentimentPhase.FERMENTING,
        limit_up=inp.limit_up_count,
        limit_down=inp.limit_down_count,
        explosion_rate=explosion_rate,
        next_day_premium=inp.daban_next_day_premium,
        highest_consec=highest_consec,
        amount_ratio=inp.market_amount_ratio_vs_ma20,
    )

    # CONSENSUS 疯狂：涨停极多 + 连板极高 + 炸板率极低 + 高溢价 + 天量
    evidence[SentimentPhase.CONSENSUS] = _score_phase(
        target=SentimentPhase.CONSENSUS,
        limit_up=inp.limit_up_count,
        limit_down=inp.limit_down_count,
        explosion_rate=explosion_rate,
        next_day_premium=inp.daban_next_day_premium,
        highest_consec=highest_consec,
        amount_ratio=inp.market_amount_ratio_vs_ma20,
    )

    # EBING 退潮：涨停骤降 + 跌停一片 + 炸板率飙升 + 负溢价 + 核按钮
    evidence[SentimentPhase.EBING] = _score_phase(
        target=SentimentPhase.EBING,
        limit_up=inp.limit_up_count,
        limit_down=inp.limit_down_count,
        explosion_rate=explosion_rate,
        next_day_premium=inp.daban_next_day_premium,
        highest_consec=highest_consec,
        amount_ratio=inp.market_amount_ratio_vs_ma20,
    )

    # ===== 步骤 2：先验+贝叶斯更新 =====
    # 先验：昨日概率（若有），否则均匀先验 1/5
    if inp.yesterday_phase_prob is not None:
        prior = inp.yesterday_phase_prob
    else:
        prior = {p: 0.2 for p in SentimentPhase}

    # 情绪周期有惯性（不会一日内从冰点跳到疯狂），加转移平滑
    # 转移核：对角线加权（同阶段保持），邻阶段次之（冰点↔反核↔主升↔疯狂↔退潮）
    transition_order = [
        SentimentPhase.FREEZING, SentimentPhase.STARTING,
        SentimentPhase.FERMENTING, SentimentPhase.CONSENSUS, SentimentPhase.EBING,
    ]
    smoothed_prior = _apply_transition_smoothing(prior, transition_order, diag_weight=0.6)

    # 后验 ∝ 先验 × 似然（证据得分）
    posterior = {
        p: max(smoothed_prior[p] * evidence[p], 1e-9)
        for p in SentimentPhase
    }
    total = sum(posterior.values())
    phase_prob = {p: v / total for p, v in posterior.items()}

    # ===== 步骤 3：兜底机制 =====
    dominant = max(phase_prob, key=phase_prob.get)
    confidence = phase_prob[dominant]
    fallback_triggered = False

    if confidence < confidence_threshold:
        # 置信度不足 → 默认保守，回退到收缩态
        # 优先回退 FREEZING（若 EBING 证据也强则回退 EBING），不回退扩张态
        fallback_triggered = True
        if evidence[SentimentPhase.EBING] > evidence[SentimentPhase.FREEZING]:
            # 退潮特征更明显 → 回退 EBING
            dominant = SentimentPhase.EBING
            phase_prob = {p: (1.0 if p == SentimentPhase.EBING else 0.0) for p in SentimentPhase}
            phase_prob[SentimentPhase.FREEZING] = 0.0
        else:
            # 默认回退 FREEZING（最保守）
            dominant = SentimentPhase.FREEZING
            phase_prob = {p: (1.0 if p == SentimentPhase.FREEZING else 0.0) for p in SentimentPhase}
        confidence = 1.0  # 兜底后置为确定（但 position_scale 仍强收缩）

    # ===== 步骤 4：可交易性 + 仓位缩放 =====
    is_tradable, position_scale = _compute_tradability(
        dominant, confidence, fallback_triggered, promotion_rate, explosion_rate,
    )

    return SentimentLocatorOutput(
        phase_prob=phase_prob,
        dominant_phase=dominant,
        confidence=confidence,
        is_tradable=is_tradable,
        position_scale=position_scale,
        evidence_scores=evidence,
        fallback_triggered=fallback_triggered,
    )


def _score_phase(
    target: SentimentPhase,
    limit_up: int,
    limit_down: int,
    explosion_rate: float,
    next_day_premium: float,
    highest_consec: int,
    amount_ratio: float,
) -> float:
    """单阶段证据评分——基于 PHASE_CHARACTERISTICS 阈值的高斯隶属度。

    每个指标按到目标区间中心的距离计算隶属度（0-1），多指标取加权平均。
    权重：涨停数 0.25 + 跌停数 0.15 + 炸板率 0.20 + 次日溢价 0.20 + 连板高度 0.10 + 量能 0.10
    """
    ch = PHASE_CHARACTERISTICS[target]

    s_lu = _membership_in_range(limit_up, ch.limit_up_range)
    s_ld = _membership_in_range(limit_down, ch.limit_down_range)
    s_exp = _membership_in_range(explosion_rate, ch.explosion_rate_range)
    s_prem = _membership_in_range(next_day_premium, ch.next_day_premium_range)
    s_consec = _membership_in_range(highest_consec, ch.consecutive_height)

    # 量能：amount_ratio < 0.5 偏冰点，0.5-1.0 偏反核，1.0-1.5 偏主升，>1.5 偏疯狂，<0.6 且下跌偏退潮
    if target == SentimentPhase.FREEZING:
        s_amt = 1.0 if amount_ratio < 0.5 else max(0.0, 1.0 - (amount_ratio - 0.5) / 0.5)
    elif target == SentimentPhase.STARTING:
        s_amt = 1.0 - abs(amount_ratio - 0.7) / 0.5
    elif target == SentimentPhase.FERMENTING:
        s_amt = 1.0 - abs(amount_ratio - 1.2) / 0.6
    elif target == SentimentPhase.CONSENSUS:
        s_amt = 1.0 if amount_ratio > 1.5 else max(0.0, (amount_ratio - 1.0) / 0.5)
    else:  # EBING
        s_amt = 1.0 if amount_ratio < 0.6 else max(0.0, 1.0 - (amount_ratio - 0.6) / 0.6)

    score = (
        0.25 * s_lu + 0.15 * s_ld + 0.20 * s_exp + 0.20 * s_prem
        + 0.10 * s_consec + 0.10 * max(0.0, min(1.0, s_amt))
    )
    return max(0.0, min(1.0, score))


def _membership_in_range(value: float, rng: tuple) -> float:
    """高斯隶属度：在区间内=1，越偏离越小。"""
    lo, hi = rng
    if lo <= value <= hi:
        return 1.0
    # 区间外按距离衰减
    center = (lo + hi) / 2 if hi != 999 else lo
    span = max((hi - lo), 1.0) if hi != 999 else 10.0
    dist = abs(value - center)
    import math
    return math.exp(-(dist / span) ** 2)


def _apply_transition_smoothing(
    prior: dict[SentimentPhase, float],
    order: list[SentimentPhase],
    diag_weight: float = 0.6,
) -> dict[SentimentPhase, float]:
    """转移平滑——情绪周期有惯性，不会一日内跨多阶段跳跃。

    对角线权重 diag_weight，邻阶段分得 (1-diag_weight)/2，其余阶段分 0。
    """
    n = len(order)
    smoothed = {p: 0.0 for p in order}
    for i, p in enumerate(order):
        # 同阶段
        smoothed[p] += diag_weight * prior[p]
        # 邻阶段
        neighbor_weight = (1.0 - diag_weight) / 2
        if i > 0:
            smoothed[order[i - 1]] += neighbor_weight * prior[p]
        else:
            # 冰点的左侧邻居回退自身（无前一阶段）
            smoothed[p] += neighbor_weight * prior[p]
        if i < n - 1:
            smoothed[order[i + 1]] += neighbor_weight * prior[p]
        else:
            smoothed[p] += neighbor_weight * prior[p]
    total = sum(smoothed.values())
    return {p: v / total for p, v in smoothed.items()} if total > 0 else smoothed


def _compute_tradability(
    dominant: SentimentPhase,
    confidence: float,
    fallback_triggered: bool,
    promotion_rate: float,
    explosion_rate: float,
) -> tuple[bool, float]:
    """可交易性 + 仓位缩放——综合置信度与阶段特征。

    返回 (is_tradable, position_scale)。
    position_scale 是 sleeve 可直接乘到目标仓位的系数（0.0-1.0）。
    """
    # 各阶段基础仓位缩放（黄一鸣 2026-04 + 24_daban §3.2）
    base_scale = {
        SentimentPhase.FREEZING: 0.0,    # 冰点空仓
        SentimentPhase.STARTING: 0.5,     # 反核半仓试错
        SentimentPhase.FERMENTING: 1.0,   # 主升满仓
        SentimentPhase.CONSENSUS: 0.5,    # 疯狂减半（退潮风险）
        SentimentPhase.EBING: 0.0,        # 退潮空仓
    }

    # 兜底触发 → 强制 ≤0.3（宁保守不激进）
    if fallback_triggered:
        return False, 0.2

    # 置信度折扣：置信度 0.6-1.0 线性映射到 0.5-1.0 的折扣
    discount = 0.5 + 0.5 * (confidence - 0.6) / 0.4 if confidence >= 0.6 else 0.5

    scale = base_scale[dominant] * discount

    # 黄一鸣可交易性判据：涨停≥30 + 晋级率≥50%
    if dominant in (SentimentPhase.FERMENTING, SentimentPhase.CONSENSUS):
        is_tradable = True
    elif dominant == SentimentPhase.STARTING:
        is_tradable = promotion_rate >= 0.50  # 启动期需晋级率确认
    else:
        is_tradable = False

    # 炸板率 > 70% 强制不可交易（24_daban §3.10 should_halt_daban）
    if explosion_rate > 0.70:
        is_tradable = False
        scale = min(scale, 0.1)

    return is_tradable, max(0.0, min(1.0, scale))
```

### 3.4 各阶段买卖纪律算法

```python
@dataclass
class PhaseTradingDiscipline:
    """各阶段买卖纪律——sleeve 内 alpha 择时的硬约束。

    字段说明：
    - position_scale: 仓位缩放系数（0.0-1.0），sleeve 目标仓位 × 此值
    - throttle_factor: 节流因子（0.0-1.0），对 sleeve 新开仓的节流（1.0=不节流，0.0=禁止新开）
    - allow_new_open: 是否允许新开仓（False=只允许平仓/调仓）
    - strategy_affinity: 各策略亲和性（>0=适配加仓，<0=不适配减仓，0=中性）
    - exit_discipline: 退出纪律描述
    - entry_discipline: 入场纪律描述
    """
    phase: SentimentPhase
    position_scale: float
    throttle_factor: float
    allow_new_open: bool
    strategy_affinity: dict[str, float]   # {"daban": x, "multifactor": y, "event_driven": z}
    entry_discipline: str
    exit_discipline: str


# 五阶段买卖纪律表（sleeve 内 alpha 择时真源）
PHASE_DISCIPLINE: dict[SentimentPhase, PhaseTradingDiscipline] = {
    SentimentPhase.FREEZING: PhaseTradingDiscipline(
        phase=SentimentPhase.FREEZING,
        position_scale=0.0,
        throttle_factor=0.0,
        allow_new_open=False,
        strategy_affinity={"daban": -1.0, "multifactor": +0.5, "event_driven": -0.5},
        entry_discipline="空仓防守，严禁抄底。多因子可开始左侧布局低估标的（估值分位<15%），但仓位≤1成试错",
        exit_discipline="所有短周期持仓无条件清仓，仅保留多因子底仓",
    ),
    SentimentPhase.STARTING: PhaseTradingDiscipline(
        phase=SentimentPhase.STARTING,
        position_scale=0.5,
        throttle_factor=0.5,
        allow_new_open=True,
        strategy_affinity={"daban": +0.3, "multifactor": +1.0, "event_driven": +0.5},
        entry_discipline="试错新题材首板或空间板，仓位2-3成。多因子左侧加仓低位横截面，事件驱动布局利好公告",
        exit_discipline="打板错了就砍，对了加仓。多因子持有不动，事件驱动按衰减曲线退出",
    ),
    SentimentPhase.FERMENTING: PhaseTradingDiscipline(
        phase=SentimentPhase.FERMENTING,
        position_scale=1.0,
        throttle_factor=1.0,
        allow_new_open=True,
        strategy_affinity={"daban": +1.0, "multifactor": 0.0, "event_driven": +0.8},
        entry_discipline="打换手龙/空间板回封，仓位5-7成。事件驱动冲击 rising phase 重仓",
        exit_discipline="趋势龙持有不动，打板按 T+1 卖出纪律，连板晋级者持有至分歧/破板",
    ),
    SentimentPhase.CONSENSUS: PhaseTradingDiscipline(
        phase=SentimentPhase.CONSENSUS,
        position_scale=0.5,
        throttle_factor=0.5,
        allow_new_open=False,
        strategy_affinity={"daban": -0.5, "multifactor": -0.3, "event_driven": -0.5},
        entry_discipline="锁仓不新开！打板禁止追高后排，仅允许前排龙头锁仓。高潮期最忌换股",
        exit_discipline="准备在分歧时减仓。后排跟风全部砍掉，趋势龙破 10 日线减仓",
    ),
    SentimentPhase.EBING: PhaseTradingDiscipline(
        phase=SentimentPhase.EBING,
        position_scale=0.0,
        throttle_factor=0.0,
        allow_new_open=False,
        strategy_affinity={"daban": -1.0, "multifactor": -0.5, "event_driven": -1.0},
        entry_discipline="无条件空仓！谁打谁亏。退潮反弹都是诱多，唯一正确动作是空仓",
        exit_discipline="无条件清仓所有短周期持仓。多因子降仓至 3 成以下防守",
    ),
}


def apply_phase_discipline(
    sleeve_name: str,
    target_position: float,
    locator_output: SentimentLocatorOutput,
    is_new_open: bool,
) -> tuple[float, bool, str]:
    """将情绪周期买卖纪律应用到 sleeve 的目标仓位。

    Args:
        sleeve_name: 策略名（"daban" / "multifactor" / "event_driven"）
        target_position: sleeve 原始目标仓位（0.0-1.0）
        locator_output: 情绪周期定位器输出
        is_new_open: 是否为新开仓（True=新开，False=调仓/平仓）

    Returns:
        (adjusted_position, allowed, reason)
        - adjusted_position: 调整后仓位
        - allowed: 是否允许执行
        - reason: 调整理由（用于归因日志）
    """
    phase = locator_output.dominant_phase
    discipline = PHASE_DISCIPLINE[phase]

    # 新开仓受 throttle_factor 节流
    if is_new_open:
        if not discipline.allow_new_open:
            return 0.0, False, f"phase_{phase.value}_禁止新开仓"
        if discipline.throttle_factor <= 0.0:
            return 0.0, False, f"phase_{phase.value}_throttle=0"

    # 仓位缩放 = 原始 × position_scale × 置信度折扣（来自 locator）
    scale = discipline.position_scale * locator_output.position_scale
    affinity = discipline.strategy_affinity.get(sleeve_name, 0.0)

    # 亲和性调整：亲和性>0 放大（最多 1.2x），<0 缩小（最多 0.5x）
    if affinity > 0:
        affinity_mult = 1.0 + 0.2 * min(affinity, 1.0)
    elif affinity < 0:
        affinity_mult = 1.0 - 0.5 * min(abs(affinity), 1.0)
    else:
        affinity_mult = 1.0

    adjusted = target_position * scale * affinity_mult
    adjusted = max(0.0, min(1.0, adjusted))

    # 兜底强收缩
    if locator_output.fallback_triggered:
        adjusted = min(adjusted, 0.2)

    reason = (
        f"phase={phase.value} scale={scale:.2f} affinity={affinity:+.1f} "
        f"mult={affinity_mult:.2f} fallback={locator_output.fallback_triggered}"
    )
    return adjusted, True, reason
```

### 3.5 情绪周期与 regime 12 态的映射关系（分工裁定）

> **本节是 [20_first_batch_strategies §5 待裁定-4](20_first_batch_strategies.md) 的落地**：澄清情绪周期与 regime 12 态的分工边界。

#### 3.5.1 分工裁定（正交）

| 维度 | 情绪周期（BM-SEL-23-B） | regime 12 态（BM-SEL-03-B 升级） |
|---|---|---|
| **角色** | sleeve 内 alpha 择时信号 | 市场级风险节流 |
| **回答问题** | 现在该买卖什么 | 现在该多谨慎 |
| **时间尺度** | 短周期 1-2 周 | 中周期 1-3 月 |
| **视角** | 微观（题材/连板/游资） | 宏观（趋势×波动率×危机） |
| **消费者** | sleeve 选股/择时（决定买卖什么） | RegimeMetaAllocator Shrinkage（决定总暴露） |
| **输出** | 5 维灰度概率 P(冰点)...P(退潮) | 12 维灰度概率 P(r1)...P(r12) |
| **正交保证** | 策略选股**不读** regime 输出（[20_first_batch_strategies §1.4](20_first_batch_strategies.md)） | regime **不参与**选股（[30_multi_strategy_concurrency §2.2](30_multi_strategy_concurrency.md)） |

#### 3.5.2 映射表（情绪周期软影响 12 态概率）

> 对齐 [10_regime_detector_spec §3.3](10_regime_detector_spec.md) 与 §2.5.4 弱静态映射起步裁定。
> **情绪周期不作为第 13-17 态硬叠加**，而是通过映射表**软调** 12 态概率。

| 情绪阶段 | 大致对应 12 态 | 软影响方向 | 说明 |
|---|---|---|---|
| 冰点 | Bear-Low / Neutral-Low | 上调 P(Bear-Low) | 量能枯竭，无人交易 |
| 反核 | RECOVERY | 上调 P(RECOVERY) | 从冰点恢复，首批试探 |
| 主升 | Bull-Medium / BREAKOUT | 上调 P(Bull-Medium) | 趋势确立，主线明确 |
| 疯狂 | Bull-High | 上调 P(Bull-High) | 加速赶顶，波动放大 |
| 退潮 | Bear-Medium / Bear-High | 上调 P(Bear-Medium) | 主线断裂，开始回落 |

**软影响机制（弱静态映射，Phase 1 起步）**：

```python
# 情绪周期 → 12 态概率软调（弱静态映射，对齐 10_regime §2.5.4）
SENTIMENT_TO_REGIME_MAP: dict[SentimentPhase, dict[str, float]] = {
    # 情绪阶段 → {12态名: 软调权重}（权重作用于 P 更新：P_new = P_old * (1 + weight * P_sentiment)）
    SentimentPhase.FREEZING: {"Bear-Low": +0.15, "Neutral-Low": +0.10},
    SentimentPhase.STARTING: {"RECOVERY": +0.20},
    SentimentPhase.FERMENTING: {"Bull-Medium": +0.15, "BREAKOUT": +0.10},
    SentimentPhase.CONSENSUS: {"Bull-High": +0.20},
    SentimentPhase.EBING: {"Bear-Medium": +0.15, "Bear-High": +0.10},
}


def apply_sentiment_soft_influence(
    regime_prob: dict[str, float],          # 12 态原始概率（来自 BM-SEL-03-B）
    sentiment_output: SentimentLocatorOutput,  # 情绪周期定位器输出
) -> dict[str, float]:
    """情绪周期对 12 态概率的软影响（弱静态映射，Phase 1）。

    对齐 10_regime_detector_spec §2.5.4：
    - Phase 1（起步）：静态映射表
    - Phase 2（回测微调）：人工调参
    - Phase 3（最终升级）：HMM/小模型学权重

    本函数实现 Phase 1。情绪周期不直接被 Shrinkage 消费，只软调 12 态概率。
    """
    adjusted = dict(regime_prob)
    for phase, weight_map in SENTIMENT_TO_REGIME_MAP.items():
        p_sentiment = sentiment_output.phase_prob.get(phase, 0.0)
        if p_sentiment <= 0:
            continue
        for regime_state, weight in weight_map.items():
            if regime_state in adjusted:
                # 软调：P_new = P_old * (1 + weight * p_sentiment)，后归一化
                adjusted[regime_state] *= (1.0 + weight * p_sentiment)

    # 归一化
    total = sum(adjusted.values())
    if total > 0:
        adjusted = {k: v / total for k, v in adjusted.items()}
    return adjusted
```

#### 3.5.3 关键纪律

- **情绪周期不直接被 Shrinkage 消费**（[10_regime §2.5.1](10_regime_detector_spec.md)）：Shrinkage = ConfidenceSignal × RiskSignal，ConfidenceSignal 来自 12 态 max(P)，情绪周期只软调 12 态概率分布
- **策略选股不读 regime 输出**（[20_first_batch_strategies §1.4](20_first_batch_strategies.md) charter §3 约束三）：情绪周期是 sleeve 内信号，与 regime 输出正交
- **两者时间尺度不同**（[10_regime §3.3](10_regime_detector_spec.md)）：情绪周期更细（短周期 1-2 周），12 态更粗（中周期 1-3 月），不矛盾可共存

### 3.6 各策略在不同情绪阶段的部署策略

> **本节是 [20_first_batch_strategies §2.5](20_first_batch_strategies.md) 差异化矩阵的补充**：定义各策略在五阶段的具体部署。

| 策略 | 冰点 | 反核 | 主升 | 疯狂 | 退潮 |
|---|---|---|---|---|---|
| **打板** | 空仓，禁止打板 | 试错首板 2-3 成 | 重仓换手龙/空间板 5-7 成 | 锁仓不新开，仅前排龙头 | 无条件空仓 |
| **多因子** | 左侧布局低估值 1 成 | 左侧加仓 3-5 成 | 持有不动 | 减仓至 3 成 | 降仓至 3 成以下防守 |
| **事件驱动** | 防守，仅高确定性事件 | 布局利好公告 | 重仓 rising phase | 减仓 | 无条件清仓 |

**部署原则**：
- **打板是情绪周期的纯多头**：只在主升/疯狂重仓，冰点/退潮空仓。打板 80% 时间应在发酵+疯狂前半，20% 在反核试错，退潮期应"看不见人"（55188 2026-07）
- **多因子是情绪周期的逆向者**：冰点/反核期布局（估值低位），疯狂/退潮期减仓（估值高位）。与打板形成天然对冲，是相关性低的基础
- **事件驱动跨阶段**：事件冲击本身与情绪周期弱相关，但事件冲击的**衰减速度**是 regime-dependent 的（[20_first_batch_strategies §2.4](20_first_batch_strategies.md) Yukka 2026），rising phase 在主升期最强

### 3.7 情绪周期作为"隐形驱动"的验证方法

> **本节是 [30_multi_strategy_concurrency §1.3](30_multi_strategy_concurrency.md) + §6.2](30_multi_strategy_concurrency.md) 的落地**：定义"情绪周期是隐形驱动→策略间相关性高于直觉"的验证方法。

#### 3.7.1 假设

[30_multi_strategy_concurrency §1.3](30_multi_strategy_concurrency.md) 假设：情绪周期是所有短周期策略的共同隐形驱动 → 策略间相关性可能高于直觉。若各阶段相关性都 >0.6，"多策略"实为"情绪 beta 穿多件衣服"。

#### 3.7.2 验证方法（G07 施工前必做）

```python
@dataclass
class SentimentStratificationTest:
    """情绪周期分层相关性验证——G07 施工前必做（30_multi_strategy_concurrency §6.2）。

    方法：
    1. 用历史数据跑三策略（打板/多因子/事件驱动）的日度收益序列
    2. 用情绪周期定位器给历史每日打阶段标签
    3. 按阶段分层计算策略两两相关矩阵
    4. 对比"全样本相关性"与"分层后相关性"

    判据：
    - 若分层后各阶段相关性显著下降（如全样本 ρ=0.5 → 分层后各阶段 ρ<0.3）
      → 验证"情绪周期是隐形驱动"假设成立，分层有效
    - 若分层后各阶段相关性仍 >0.6
      → "多策略实为情绪 beta 穿多件衣服"，需重新审视策略组合
    """
    phase: SentimentPhase
    n_days: int                                  # 该阶段样本天数
    correlation_matrix: dict[str, dict[str, float]]  # {策略: {策略: ρ}}
    is_pass: bool                                # 该阶段是否通过（ρ_max < 0.6）


def validate_sentiment_hidden_driver(
    daily_returns: dict[str, list[float]],        # {策略: 日收益序列}
    daily_phases: list[SentimentPhase],           # 每日情绪阶段标签
    correlation_threshold: float = 0.6,
) -> dict[SentimentPhase, SentimentStratificationTest]:
    """验证情绪周期是否为策略间相关性的隐形驱动。

    核心逻辑：若情绪周期是隐形驱动，则按阶段分层后相关性应显著下降
    （因为分层后控制了共同驱动变量）。

    Returns:
        各阶段的分层相关性测试结果 + 全样本基准对比
    """
    import numpy as np

    strategies = list(daily_returns.keys())
    n = len(daily_phases)

    # 全样本相关矩阵（基准）
    full_matrix = _compute_corr_matrix(daily_returns, list(range(n)))
    full_max_rho = max(
        abs(full_matrix[s1][s2])
        for i, s1 in enumerate(strategies)
        for j, s2 in enumerate(strategies)
        if i < j
    )

    # 按阶段分层
    results: dict[SentimentPhase, SentimentStratificationTest] = {}
    for phase in SentimentPhase:
        idx = [i for i, p in enumerate(daily_phases) if p == phase]
        if len(idx) < 30:
            # 样本不足（稀有态），跳过但记录
            results[phase] = SentimentStratificationTest(
                phase=phase, n_days=len(idx),
                correlation_matrix={}, is_pass=False,
            )
            continue

        phase_returns = {s: [daily_returns[s][i] for i in idx] for s in strategies}
        matrix = _compute_corr_matrix(phase_returns, idx)
        max_rho = max(
            abs(matrix[s1][s2])
            for i, s1 in enumerate(strategies)
            for j, s2 in enumerate(strategies)
            if i < j
        )

        results[phase] = SentimentStratificationTest(
            phase=phase, n_days=len(idx),
            correlation_matrix=matrix,
            is_pass=(max_rho < correlation_threshold),
        )

    return results


def _compute_corr_matrix(
    returns: dict[str, list[float]],
    idx: list[int],
) -> dict[str, dict[str, float]]:
    """计算策略间相关矩阵。"""
    import numpy as np
    strategies = list(returns.keys())
    matrix = {s1: {s2: 0.0 for s2 in strategies} for s1 in strategies}
    for s1 in strategies:
        for s2 in strategies:
            r1 = [returns[s1][i] for i in idx]
            r2 = [returns[s2][i] for i in idx]
            if len(r1) > 1 and len(r2) > 1:
                corr = float(np.corrcoef(r1, r2)[0, 1])
                matrix[s1][s2] = corr
    return matrix
```

#### 3.7.3 验证结论的处置

| 验证结果 | 处置 |
|---|---|
| 分层后各阶段 ρ < 0.3（显著下降） | 假设成立，情绪周期是隐形驱动，分层有效，三策略组合可施工 |
| 分层后各阶段 ρ 0.3-0.6（中等相关） | 假设部分成立，需在 G13 FirmRiskAggregator 加情绪周期暴露硬上限 |
| 分层后各阶段 ρ > 0.6（仍高相关） | 假设成立但策略组合失效，"多策略实为情绪 beta 穿多件衣服"，需重新审视策略组合（[30_multi_strategy_concurrency §6.2](30_multi_strategy_concurrency.md)） |

## 4. 考虑过的替代方案

### 4.1 情绪周期作为第 13-17 态硬叠加到 regime —— 拒绝
- **拒绝理由**：[10_regime_detector_spec §2.2](10_regime_detector_spec.md) C-prime 已裁定"情绪周期 4+1 不作为第 13-17 态硬叠加"。时间尺度不同（情绪短 1-2 周，regime 中 1-3 月），硬叠加会产生尺度混淆；行业实证（WallStreetCourier/UMwai）用"多信号加权融合"，情绪作为软输入调整概率而非硬叠加为独立态
- **处置**：通过 §3.5.2 映射表软影响 12 态概率（弱静态映射起步，Phase 1）

### 4.2 情绪周期做 sleeve 内 alpha 择时 + regime 做 alpha 择时（双择时）—— 拒绝
- **拒绝理由**：[30_multi_strategy_concurrency §2.2](30_multi_strategy_concurrency.md) Morwane 实证（OOS 2013-2026）：regime 做 alpha 择时 Sharpe 1.43→0.87（摧毁价值），做风险节流 Sharpe 1.43 + MaxDD -14.2%→-10.3%（改善回撤）。双择时会产生信号冲突与归因纠缠，且 regime 检测误差被主动重定向放大
- **处置**：情绪周期做 sleeve 内 alpha 择时（决定买卖什么），regime 仅做 Shrinkage 风险节流（决定多谨慎），两者正交

### 4.3 情绪周期定位器用硬标签而非灰度概率 —— 拒绝
- **拒绝理由**：[10_regime_detector_spec §2.5.4](10_regime_detector_spec.md) 用户裁定"输出应为灰度概率，不是硬标签"。硬标签在阶段过渡期会产生频繁切换（如冰点↔反核来回跳），导致 sleeve 仓位抖动；灰度概率可用概率加权，天然实现软影响。错判代价大，灰度输出还便于"置信度<60%→默认保守"的兜底
- **处置**：定位器输出 5 维灰度概率分布 P(冰点)...P(退潮)，Σ=1

### 4.4 用 LLM 实时解读新闻情绪替代指标化定位 —— 拒绝
- **拒绝理由**：指标化定位（涨停数/炸板率/连板高度等）是盘后可复现的客观数据，LLM 新闻解读有幻觉风险且不可复盘。情绪周期定位器是 production 资产，须稳定可追溯。新闻情绪可作为 RiskSignal 13 参数之一（[10_regime §5.2](10_regime_detector_spec.md)）软影响 Shrinkage，但不替代定位器
- **处置**：定位器用多维客观指标，新闻情绪归 regime RiskSignal 处理

### 4.5 情绪周期五阶段合并为三阶段（扩张/顶点/收缩） —— 拒绝
- **拒绝理由**：游资圈实战共识五阶段（55188 2026-07 / xueqiu 2026-06 / eastmoney 2026-03），各阶段买卖纪律显著不同（如反核试错 vs 主升重仓 vs 疯狂锁仓）。合并三阶段会丢失反核/疯狂的差异化买卖纪律，导致"该试错时重仓"或"该锁仓时追高"
- **处置**：保持五阶段，与 regime 12 态映射时可在 §3.5.2 表中粗化对应

## 5. 上限定义

| 上限 | 值 | 理由 |
|---|---|---|
| **情绪阶段数** | 5（冰点/反核/主升/疯狂/退潮） | 游资圈实战共识，再多过拟合，再少丢失差异化买卖纪律 |
| **定位器输入维度** | ≤ 10（涨跌停/连板/炸板率/溢价/换手/量能/龙虎榜/北向） | 多于 10 个指标会让定位器过拟合，且 production 实时性要求 |
| **定位器置信度阈值** | 60% | [30_multi_strategy_concurrency §6.3](30_multi_strategy_concurrency.md) 要求"置信度<60%→默认保守"兜底 |
| **主升期打板总仓位** | ≤ 7 成 | 55188 2026-07 实战上限，主升期满仓有分歧风险 |
| **疯狂期新开仓** | 禁止 | 高潮期最忌换股/追高，锁仓不新开是唯一正确动作 |
| **退潮期所有短周期 sleeve** | 空仓 | 退潮反弹都是诱多，唯一正确动作是空仓 |
| **兜底 position_scale** | ≤ 0.2 | 置信度<60% 强制收缩到 0.2 以下，宁保守不激进 |

### 5.1 演进路径

- **Phase 1（立即施工）**：定位器用多维客观指标 + 弱静态映射表（§3.5.2）；G07 相关性验证施工前必做
- **Phase 2（各策略 3-6 月实盘后）**：根据 G07 验证结果校准定位器阈值与映射权重；若分层后相关性仍高，加情绪周期暴露硬上限
- **Phase 3（数据充足后）**：升级为 HMM/小模型学习映射权重（对齐 [10_regime §2.5.4](10_regime_detector_spec.md) Phase 3 路径）

### 5.2 为何这是上限而非妥协

- 五阶段是游资圈 10+ 年实战提炼的最小完备集，再多是过拟合温床（[20_first_batch_strategies §4.3](20_first_batch_strategies.md) charter §3 约束五少而精）
- 定位器 ≤10 维输入是 production 实时性与过拟合风险的平衡（[10_regime §2.2.2 实证 6](10_regime_detector_spec.md)：特征>模型，但特征过多也过拟合）
- 兜底 0.2 是"宁保守不激进"原则的工程化（错判代价不对称：主升判成冰点=机会成本，冰点判成主升=主动亏损）

## 6. 待裁定

| 暂缓项 | 暂缓理由 | 重评条件 | 责任方 |
|---|---|---|---|
| 定位器准确率历史回测 | [30_multi_strategy_concurrency §6.3](30_multi_strategy_concurrency.md) 要求评估 BM-SEL-23-B 历史准确率，错判代价大 | G07 验证施工时同步评估 | G07/G21 |
| 映射表权重标定（Phase 2） | §3.5.2 当前用弱静态映射，权重为经验值 | 各策略 3-6 月实盘后回测微调 | G21 |
| HMM/模型学权重（Phase 3） | 静态映射跑通 + 数据充足 + 发现明显不够用后升级 | [10_regime §2.5.4](10_regime_detector_spec.md) Phase 3 触发条件 | G21/G02 |
| BM-SEL-23-B 输出契约变更 | 当前 production 输出 4+1 硬标签，若改 5 维灰度概率需评估对 BM-SEL-25 双引擎融合消费的影响 | 设计态准入时处理 | G05/G08 |
| 情绪周期暴露硬上限 | §3.7.3 验证若分层后相关性 0.3-0.6 需加硬上限 | G07 验证结果 | G13/G21 |

## 7. 待定问题（讨论要点对齐）

- [x] ① 5 阶段（冰点/反核/主升/疯狂/退潮）各阶段的买卖纪律 → §3.2 五阶段定义 + §3.4 `PHASE_DISCIPLINE` 各阶段 position_scale/throttle_factor/allow_new_open/策略亲和性
- [x] ② 情绪周期定位器准确率评估（[30_multi_strategy_concurrency §6.3](30_multi_strategy_concurrency.md)）→ §3.3 `locate_sentiment_phase` 算法化 + §6 待裁定（G07 施工时同步评估）+ §3.3 兜底机制（置信度<60%→默认保守）
- [x] ③ 情绪周期与 regime 12 态的映射关系 → §3.5 分工裁定（正交）+ §3.5.2 映射表（软影响）+ §3.5.3 关键纪律
- [x] ④ 各策略在不同情绪阶段的部署策略 → §3.6 部署矩阵（打板主升重仓/多因子冰点布局/事件驱动跨阶段）
- [x] ⑤ 情绪周期是"隐形驱动"（[30_multi_strategy_concurrency §1.3](30_multi_strategy_concurrency.md)）→策略间相关性来源 → §3.7 验证方法（分层相关性测试）+ §3.7.3 处置结论

## 8. 引用

### 8.1 相关设计备忘
- [00_index_trading_decision](00_index_trading_decision.md) §3 G21
- [30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) §1.3 / §6.2 / §6.3（隐形驱动+相关性验证+定位器准确率）
- [20_first_batch_strategies](20_first_batch_strategies.md) §2.2（打板依赖情绪周期4+1）+ §2.5（差异化矩阵）+ §5 待裁定-4（边界澄清）
- [10_regime_detector_spec](10_regime_detector_spec.md) §2.5（探测器分工）+ §2.5.4（软影响三阶段）+ §3.3（映射表）+ §6.6
- [24_daban_strategy_detail](24_daban_strategy_detail.md) §3.2（情绪周期定位）+ §3.10（打板熔断）

### 8.2 相关作战地图
- [battle_map_05_stock_selection.md](../battle_map/battle_map_05_stock_selection.md)
  - BM-SEL-23-B：情绪周期 4+1 阶段定位器（production，本讨论真源）
  - BM-SEL-25：双引擎融合（情绪周期下游消费者）

### 8.3 2026-08 研究引用
- 东方财富 (2026-03-14) "A股情绪周期判断体系（具体实操版）" — 五大核心指标（涨停数/跌停数/炸板率/赚钱效应/板块联动）+ 四大阶段实操口诀
- 雪球 MysteriousBird鬼鸟 (2026-06-01) "硬核拆解A股情绪周期" — 五阶段标准模型（冰点/修复/升温/狂热/退潮）+ 量化信号 + 短周期 40 天核心交易周期
- 55188 (2026-07-15) "情绪周期解读：短线交易的核心天气预报" — 启动/发酵/高潮/分歧/退潮五段循环 + 各阶段玩法口诀
- yueniuzq (2026-06-16) "复盘炸板率与跌停数：科学量化市场情绪的转折点" — 炸板率与跌停数量评分模型（亏钱效应先行指标）
- 东方财富 股海浮沉录25 (2026-06-11) "因子挖掘：从模糊感知到可交易信号" — 龙虎榜情绪温度 + 资金流/席位属性/买卖对比三层分析
- 东方财富 盘大牛 (2026-06-06) "游资的血槽与墓碑，拆解龙虎榜底层密码" — 机构/游资/量化资金属性 + 龙虎榜四维解析框架
- 新浪财富汇 (2026-02-22) "龙虎榜核心作用、实操应用及顶部判断" — 席位性质/买卖结构/上榜阶段顶部判断
- toutiao (2026-08-10) "A股极致高低切换" — V2.5.2 情绪评分实战（涨停家数/跌停家数/封板率/连板高度/涨跌比五维打分）

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行：由 00_index G21 讨论要点占位，待讨论填空 |
| 2026-08-10 | 1.0.0 | 落地 spec 定稿 | 五阶段情绪周期定义（FREEZING冰点→STARTING反核→FERMENTING主升→CONSENSUS疯狂→EBING退潮）+ 各阶段市场特征指标；BM-SEL-23-B 定位器算法升级（多维指标评分+贝叶斯更新+兜底机制+灰度概率输出）；各阶段买卖纪律算法（position_scale/throttle_factor/allow_new_open/策略亲和性）；情绪周期与 regime 12 态映射关系（正交分工裁定+软影响映射表）；各策略在不同情绪阶段部署策略（打板主升重仓/多因子冰点布局/事件驱动跨阶段）；情绪周期作为"隐形驱动"的验证方法（分层相关性测试）；整合 2026-08 研究（eastmoney 情绪周期实操体系/yueniuzq 炸板率评分模型/龙虎榜情绪温度/55188 五段循环口诀） |
