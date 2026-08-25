---
blueprint_id: MOD-SIG-099
module_name: extreme_sentiment_reversal_detector
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

# MOD-SIG-099 extreme_sentiment_reversal_detector 蓝图

> 设计真源：AUD-DRAFT-001 深挖批 B10-01369（模块14 极端情绪反转与恐慌底部检测模型，
> 裁定=做 P1）+ 候选注册表 CAND-TESTB-014。
> 代码：`src/zephyr/signal_ashare/extreme_sentiment_reversal_detector.py`

## 0. 定位

场内对账（查重铁律③探查分工在案）：
- sentiment_cycle（28 号 memo）= 五阶段定位器（冰点/反核/主升/疯狂/退潮相位+仓位纪律），
  管"现在处于情绪周期哪个阶段"；
- market_sentiment_analyzer（MOD-SIG-025）= 7 维情绪分生产方；
- regime 域 s2_capitulation_score（overlay_features）= 指数级 S2 CRISIS→RECOVERY
  体制见底维度（vol_z+pct_change 两维，regime 域）。
- **双冰点确认规则（情绪冰点≤22% 分位 × 指数冰点 RSI<30 双触发 ≤2 日）/
  Capitulation 打分卡（跌幅/量能/广度三维 0-100）/收回比例区分 shakeout 与真破位
  均无实现**（深挖批 min_build_spec 明示缺口）。本模块落地，消费情绪分与指数
  OHLCV/广度序列（鸭子类型注入），为 A 股短生态事件检测器（信号域），与 regime
  指数级体制维度粒度正交。

## 1. 接口

```python
@dataclass(frozen=True) class SentimentReversalConfig   # 阈值+修复概率查表（构造即校验）
@dataclass(frozen=True) class DoubleIceStatus           # 双冰点状态（两冰点/确认/滞后/修复概率）
@dataclass(frozen=True) class CapitulationScorecard     # 三维打分卡（跌幅/量能/广度/总分）
@dataclass(frozen=True) class BreakdownVerdict          # shakeout/真破位/未定/无破位
@dataclass(frozen=True) class ExtremeReversalReport     # 综合报告（三件套+反转标记+置信度）
class ExtremeSentimentReversalDetector:
    def detect_double_ice(self, sentiment_scores, index_closes) -> DoubleIceStatus
    def capitulation_score(self, day_drop, volume_ratio, advance_ratio) -> CapitulationScorecard
    def classify_breakdown(self, level, day_low, close) -> BreakdownVerdict
    def detect(self, sentiment_scores, index_closes, index_lows,
               index_volumes, advance_ratios, *, support_level=None) -> ExtremeReversalReport
```

- **双冰点**：情绪冰点=当日情绪分 ≤ 扩展窗 22% 分位（可配）；指数冰点=RSI14<30
  （Wilder，指标核自算不 import，MOD-SIG-095 同先例）；两冰点各取最近 max_lag+1
  根内触发日，|Δ|≤2 日 → 配对；修复概率查表（0/1/2 日 → 默认 0.72/0.74/0.71），
  ≥0.70 → confirmed。
- **Capitulation 打分卡**（总分 100，阈值≥70 判恐慌投降）：跌幅 40（≤−5%→40/
  ≤−3%→32/≤−2%→22/≤−1%→10）+ 量能 30（今日量/前 20 日均量 ≥2.5→30/≥2.0→26/
  ≥1.5→18/≥1.2→10）+ 广度 30（上涨家数占比 ≤10%→30/≤20%→22/≤30%→12）。
- **Shakeout vs 真破位**：破位幅度=level−day_low（day_low<level 才判）；
  收回比例=(close−day_low)/(level−day_low)；>0.5→shakeout（假破位洗盘），
  <0.2→true_breakdown（真破位），其间→undetermined；未破位→none。
- **综合反转**：双冰点 confirmed 且打分卡≥70 且非真破位 → reversal_detected；
  confidence=(打分卡/100)×修复概率。

## 2. 纪律

- 序列等长/≥min_history/有限值/价格>0/量≥0/广度∈[0,1] 校验；非法 → ValueError。
- 配置构造即校验：分位∈(0,0.5)、RSI 周期≥2、滞后≥0、修复概率表键=0..max_lag
  且值∈(0,1)、shakeout>true_breakdown 比率。
- PIT：分位/RSI/均量全部扩展窗 ≤ 当根；修复概率为静态查表（非实时频率估计）。
- frozen dataclass asdict JSON 可序列化；纯内存统计不直连 DB、不荐股。

## 3. 依赖

- import：标准库（math/statistics/dataclasses）——无 zephyr 内部 import 边。
- 上游注入：market_sentiment_analyzer（MOD-SIG-025）情绪分序列、指数 OHLCV/广度
  （D_DATA 装配层）、support_level（D_FACTOR 压力位层）；下游候选：
  情绪页极端反转告警、买入侧底部情景装配层。
