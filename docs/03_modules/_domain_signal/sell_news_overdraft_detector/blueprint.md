---
blueprint_id: MOD-SIG-106
module_name: sell_news_overdraft_detector
domain: D_ASHARE_SIGNAL
doc_type: blueprint
ttl: permanent
design_maturity: testing
stability: evolving
safety_level: M
ai_autonomy: ai_modifiable
version: "0.1.0"
created: 2026-08-25
last_updated: 2026-08-25
owner: ZephyrAlpha-Owner
---

# MOD-SIG-106 sell_news_overdraft_detector 蓝图

> 设计真源：AUD-DRAFT-001 深挖批 B10-01453（模块28 利好落地变利空（预期透支）模块，裁定=做 P1）+ 候选注册表 CAND-TESTB-023。
> 代码：`src/zephyr/signal_ashare/sell_news_overdraft_detector.py`

## 0. 定位

场内对账（查重铁律③⑥探查在案）：

- market_sentiment_analyzer（MOD-SIG-025）/ sentiment_cycle = 情绪状态与周期
  **生产方**（本件情绪透支度维度的上游，读数注入）；
- extreme_sentiment_reversal_detector（MOD-SIG-099）= 极端情绪**反转**事件检测
  （双冰点+Capitulation，管恐慌底，方向相反）；
- sentiment_price_divergence（MOD-SIG-101）= 情绪-价格**背离**指数（背离≠透支）；
- expectation_governance（D_DATA_ENG）= 数据质量期望套件门控（数据域，语义正交）；
- event_driven_screener（MOD-SIG-049）= 漏斗第四层事件方向剔除（利空剔除，
  不管"利好兑现反噬"）；event_score 等 intelligence/event_* = 事件源（上游注入）；
- **事件可预测性分类 + 预期透支度量化（价格/时间/资金/情绪 4 维）+ 时间轴
  5 阶段标注 + 落地前减仓信号无实现**（深挖批 min_build_spec 明示缺口，
  sell-the-news 利好兑现效应），本模块落地。

## 1. 接口

```python
EVENT_PREDICTABILITY  # 事件5类→可预测性映射（policy/earnings→high、industry/geopolitical→medium、
                      # black_swan→unpredictable 不适用本模型）
TimelinePhase         # 时间轴5阶段封闭集（early_accumulation T-30~T-15 / mid_fermentation T-15~T-5
                      # / late_sprint T-5~T-1 / landing_day T=0 / post_landing）
OverdraftLevel        # 判定3档封闭集（none<0.8 / mild 0.8~1.2 / severe>1.2）
@dataclass(frozen=True) class NewsEventContext   # 事件类型+落地天数+四维读数（注入）
@dataclass(frozen=True) class OverdraftConfig    # 严重阈1.20/温和阈0.80/落地窗3天/资金阈1.0/情绪峰阈0.85
@dataclass(frozen=True) class OverdraftAssessment # 可预测性+四维透支度+综合档+阶段+动作+归因
class SellNewsOverdraftDetector:
    def assess(self, ctx: NewsEventContext) -> OverdraftAssessment
```

- **透支度 4 维**（注册表 problem 既定口径）：价格透支=累计涨幅/历史均值
  （>120% 严重）；时间透支=提前天数/30 钳制；资金透支=5日净流入/5日均成交额
  （>1.0 严重）；情绪透支=当前热度/峰值热度（≥0.85 近峰）。
- **综合判定**：四维等权综合，>1.2 severe / 0.8~1.2 mild / <0.8 none。
- **落地前减仓信号**（min_build_spec：>120% 落地≤3天→落地前减仓清仓）：
  severe ∧ 0≤落地天数≤3 → reduce（落地前减仓）；severe ∧ 已落地 → clear；
  severe 且尚早 / mild → watch；none → none。
- **黑天鹅不适用**：unpredictable → applicable=False + action=not_applicable
  （事件不可预测则预期透支逻辑不适用，注册表原文口径）。

## 2. 纪律

- 未知事件类型/历史均值≤0/峰值热度≤0/成交额<0/非有限读数/非法配置 → ValueError
  （fail-closed）；天数为整数语义（T+N 正=未落地，0=落地日，负=已落地）。
- 信号语义非异常：动作经返回值表达（none/watch/reduce/clear/not_applicable），
  不抛错；仅输入非法才 ValueError。
- frozen dataclass asdict JSON 可序列化；不直连事件源/情绪库、不做空（减仓/
  清仓仅作用于持仓侧）、不荐股。

## 3. 依赖

- 无 zephyr import（纯函数核，与 MOD-SIG-089/092~105 同构纪律）。
- 语义上游（鸭子类型注入，生产接线留集成批）：intelligence/event_* 事件源
  （事件类型/落地日）；market_sentiment_analyzer（MOD-SIG-025）情绪热度；
  资金净流入读数（资金流生产方）。
- 下游候选：L2-C 日历约束升级 / L2-A 落地日卖出信号装配层（注册表归属在案）。

## 4. 测试

`tests/signal_ashare/test_sell_news_overdraft_detector.py`：
事件5类可预测性映射、四维透支度计算与边界、3档判定、5阶段标注（含 T=0/负天）、
落地前减仓/已落地清仓/尚早 watch、黑天鹅不适用、非法输入 fail-closed、
frozen/JSON 契约。
