---
blueprint_id: MOD-SIG-102
module_name: limit_up_potential_scorer
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

# MOD-SIG-102 limit_up_potential_scorer 蓝图

> 设计真源：AUD-DRAFT-001 深挖批 B10-01380（模块33 IC加权多因子涨停板潜力评分模型，裁定=做 P1）+ 候选注册表 CAND-TESTB-017。
> 代码：`src/zephyr/signal_ashare/limit_up_potential_scorer.py`

## 0. 定位

场内对账（查重铁律③⑥探查分工在案）：
- limit_up_classifier（MOD-ML-CLS1，D_ML_TRAIN）= 打板涨停概率 ML 分类器骨架（骨架态禁真训练，ZA-MLT-0003）——ML 路线，与本件规则评分路线正交；
- strength_ic_weight_calibrator = 量化短线强度 6 维子分（price_momentum/industry_strength/relative_strength/capital/technical/risk）IC 校准——同为 IC 加权**技术**，维度族与用途（短线强度 vs 涨停潜力）正交；
- bma_signal_weighter（MOD-L02-001，D_FACTOR）= 多信号 BMA 后验权重（信号级，softmax(κ·ic·icir)）——粒度（信号 vs 涨停七分）与域均正交；
- lhb_premium_analyzer（MOD-SIG-057）= 龙虎榜溢价单分生产方；limit_up_ecosystem_leadership（MOD-SIG-097）= 连板高度/封板时间/梯队因子生产方；market_sentiment_analyzer（MOD-SIG-025）= 情绪分生产方——均为本件上游单分供给（鸭子类型注入，不 import）；
- **涨停潜力七分 IC 验证后 IC 加权整合评分无实现**（深挖批 min_build_spec 明示缺口，注册表 problem：IC>0.03、ICIR>0.5、w_i=IC_i/Σ），本模块落地。

## 1. 接口

```python
LIMIT_UP_FACTOR_NAMES  # 七分封闭集（ladder_height/seal_strength/sector_momentum/chip_concentration/lhb_premium/volume_confirmation/market_sentiment）
EMPIRICAL_WEIGHTS      # 经验权重 Σ=1（全分 IC 出局回退用）
@dataclass(frozen=True) class LimitUpPotentialConfig  # IC/ICIR 门+样本窗+分档（构造即校验）
@dataclass(frozen=True) class FactorEvidence          # 分名+当前标准化分[0,1]+(分值,前瞻收益)样本对
@dataclass(frozen=True) class FactorEvaluation        # IC/ICIR/有效/权重/样本数/notes
@dataclass(frozen=True) class LimitUpPotentialReport  # 综合分/分档/逐分评估/回退/充分
class LimitUpPotentialScorer:
    def evaluate(self, symbol: str, factors: Sequence[FactorEvidence]) -> LimitUpPotentialReport
```

- **IC 验证**：Spearman 秩相关（平均秩处理并列，纯标准库零 numpy/scipy）；
  样本连续等分 5 块逐块 IC → ICIR=mean/pstdev（零方差且均值>0 → 999.0 极稳定，
  文档化 MVP 初拍）；有效块<2 → ICIR=0+notes。
- **配权**：IC>0.03 且 ICIR>0.5 → 有效；w_i=IC_i/Σ_有效 IC_j（Σ=1），无效分归 0。
- **回退**：全分出局（含全样本不足 <30）→ 经验权重按在场分重归一，
  fallback_used=True 且 sufficient=False（显式降级不静默）。
- **评分**：composite=Σ w_i×current_score_i×100；分档 ≥70 A / ≥50 B / ≥30 C / 其余 D。

## 2. 纪律

- 空 symbol/空分列表/未知分名/重复分名/分越界[0,1]/非有限样本/非法配置 → ValueError（fail-closed）。
- 样本 PIT：注入样本须为已实现前瞻收益对（调用方责任，本件仅用给定对计算）。
- 分值或收益零方差 → IC 不可验证，该分出局+notes（不伪造 IC）。
- frozen dataclass asdict JSON 可序列化；纯内存统计不直连 DB、不荐股。

## 3. 依赖

- 无 zephyr import（纯函数核，与 MOD-SIG-089/092~101 同构纪律）。
- 语义上游（鸭子类型注入，生产接线留集成批）：MOD-SIG-097 连板高度/封板时间因子、
  MOD-SIG-057 龙虎榜溢价、MOD-SIG-025 情绪分、板块动量/筹码/量能分生产方。
- IC/IR 语义对齐 factor/analysis/ic_ir_calc（MOD-L02-002）PIT 铁律（INV-004），不 import。

## 4. 测试

`tests/signal_ashare/test_limit_up_potential_scorer.py`（24 用例）：
配置/证据 fail-closed、RankIC 单调±1/噪声出局、权重比例与归一、回退语义、
样本不足出局不阻断、综合分与分档边界、frozen/JSON 契约。
