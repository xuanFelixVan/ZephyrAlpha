---
blueprint_id: MOD-SIG-108
module_name: multi_factor_timing_overlay
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

# MOD-SIG-108 multi_factor_timing_overlay 蓝图

> 设计真源：AUD-DRAFT-001 深挖批 B10-01482（模块57 多因子叠加择时模型，裁定=做 P1）+ 候选注册表 CAND-TESTB-025。
> 代码：`src/zephyr/signal_ashare/multi_factor_timing_overlay.py`

## 0. 定位

场内对账（查重铁律⑤⑥探查在案）：

- timing_analyst_agent（MOD-AU-010）= 择时 **Agent 裁决层**（状态×预测×做T点
  →时机与执行建议，L1 建议级+人工确认回路）；本件=决策编排器上游**信号合成
  层**（6 源叠加+共振检测），为其供给合成读数，不替代其裁决；
- strength_ic_weight_calibrator = 短线强度 6 维**子分** IC 校准（维度族正交）；
  bma_signal_weighter（MOD-L02-001，D_FACTOR）= 信号级 BMA 后验权重**生产方**
  （其 CONSUMERS 在案预留本件装配批）——本件消费 IC/BMA 权重注入，不自建
  校准/后验；
- 各择时单件（MOD-SIG-099 情绪反转/MOD-SIG-039 体制转换/波动突破/日历/
  量能/北向）= 单源**生产方**（本件上游，读数鸭子类型注入）；
- **6 源择时信号库 + IC 加权或 BMA 叠加 + ≥3 同向共振高置信标记无实现**
  （深挖批 min_build_spec 明示缺口，Rapach&Zhou 2013 组合预测），本模块落地。

## 1. 接口

```python
TIMING_SOURCES  # 6源封闭集（sentiment_reversal 情绪反转 / regime_shift 体制转换 /
                # volatility_breakout 波动突破 / calendar 日历 / volume 量能 / northbound 北向）
@dataclass(frozen=True) class TimingSignal        # source+direction(-1/0/1)+strength[0,1]
@dataclass(frozen=True) class TimingOverlayConfig # 共振阈≥3/方向阈±0.10/权重下限
@dataclass(frozen=True) class TimingOverlayResult # 合成分+方向+共振计数+高置信+权重归因
class MultiFactorTimingOverlay:
    def overlay(self, signals, *, ic_weights=None, bma_weights=None) -> TimingOverlayResult
```

- **加权叠加**：composite=Σw_i×direction_i×strength_i；权重优先级
  bma_weights>ic_weights>等权兜底（均按非负 clip 后 Σ=1 归一；全零/缺失维
  回退等权+fallback_used 留痕，语义对齐 IC 加权工程修正惯例）。
- **方向判定**：composite>+0.10 bullish / <−0.10 bearish / 其余 neutral
  （文档化 MVP 初拍阈值，待回验标定批替换）。
- **共振检测**（min_build_spec 既定）：≥3 独立源同向（非零）→
  high_confidence=True + resonance_direction；反向混杂按多数向计数。
- 输入源缺漏（<6 源）不阻断：按在场源归一化加权 + notes 留痕（降级不抛）。

## 2. 纪律

- 未知 source/重复 source/direction 非 {-1,0,1}/strength 越界/非有限/非法
  配置 → ValueError（fail-closed）；空信号序列 → ValueError。
- 合成语义非异常：neutral/低置信经返回值表达，不抛错。
- frozen dataclass asdict JSON 可序列化；不做 Agent 裁决（MOD-AU-010 职责）、
  不自建 IC 校准或 BMA 后验（上游注入）、不荐股。

## 3. 依赖

- 无 zephyr import（纯函数核，与 MOD-SIG-089/092~107 同构纪律）。
- 语义上游（鸭子类型注入，生产接线留集成批）：6 源择时生产方（MOD-SIG-099
  情绪反转/MOD-SIG-039 体制转换/波动突破/日历/量能/北向读数）；
  strength_ic_weight_calibrator IC 口径 / bma_signal_weighter（MOD-L02-001）
  BMA 后验权重（TSV dependencies 在案）。
- 下游候选：决策编排器（注册表归属"决策编排器模块57"）与 MOD-AU-010 裁决层。

## 4. 测试

`tests/signal_ashare/test_multi_factor_timing_overlay.py`：
6 源封闭集、IC/BMA/等权权重优先级与归一、负权重 clip、合成分与方向阈、
≥3 同向共振高置信（含反向混杂）、缺源降级、非法输入 fail-closed、
frozen/JSON 契约。
