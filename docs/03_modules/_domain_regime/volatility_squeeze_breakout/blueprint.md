---
blueprint_id: MOD-REGIME-013
module_name: volatility_squeeze_breakout
domain: D_REGIME
doc_type: blueprint
ttl: permanent
design_maturity: design
stability: evolving
safety_level: M
ai_autonomy: ai_modifiable
version: "0.1.0"
created: 2026-08-25
last_updated: 2026-08-25
owner: ZephyrAlpha-Owner
priority: P1
blueprint_level: module
domain_id: D_REGIME
path: src/zephyr/regime/volatility_squeeze_breakout.py
granularity: file
---

# MOD-REGIME-013 volatility_squeeze_breakout 蓝图（模块51 波动率压缩与突破模型）

> **module_id**: MOD-REGIME-013 | **域**: D_REGIME | **优先级**: P1
> **来源**: B10-01387（AUD-DRAFT-001-DIGEST P1 波 W-P1-17，CAND-CYCLE-005，A1 交易决策架构 §3 模块51）
> 代码：`src/zephyr/regime/volatility_squeeze_breakout.py`

## 0. 定位

模块51 波动率压缩与突破模型——TTM Squeeze 类经典波动率交易模式的判定核心：
**强压缩标记 + 突破方向概率 + 3 日维持确认**。查重铁律④细读 TSV 裁定=
**扩展施工**（非重复）：MOD-REGIME-011 只出 rv_ratio<0.8 早标记且其 docstring
明示"<0.5 强压缩归模块51 B10-01387 联动"；突破方向判定与维持确认无任何既有件。

查重分工（W-P1-17 探查结论，均不复制）：

| 既有件 | module_id | 职责 | 与本模块边界 |
|---|---|---|---|
| volatility_regime_alerter | MOD-REGIME-011 | GARCH 波动预测 + rv_ratio<0.8 压缩**早标记** + 突变告警（shift≥1.5） | 本模块=强压缩（<0.5）+布林带宽分位<10% 双腿压缩定量 + **突破方向概率** + **3日维持确认**（早标记不含方向与确认） |
| regime_detector | MOD-REGIME-001 | 4态HMM 灰度概率 | 不做波动压缩定量 |
| overlay_signals_builder | MOD-REGIME-002 | overlay_dims 契约消费侧 | 本模块按同一契约供数（score∈[0,100]/flag∈{0,1}/无信号=0） |

不做什么：不重造 GARCH（MOD-REGIME-011/MOD-RK-26 职责）、不做买卖点信号
（信号层职责）、不做 IV 期限结构（无数据源，留扩展位）。

## 1. 判定规则（确定性，纯函数；降级哲学对齐 MOD-REGIME-011）

- **强压缩双腿**（TSV 最小施工形态）：rv_ratio=RV_5d/RV_20d（年化，复用
  alerter 口径）<0.5 **且** 布林带宽（20 窗 2σ，(upper−lower)/mid）处于历史
  分位 <10% → squeeze_flag=1；单腿命中只出分项不出联合标记。
- **突破方向概率**：价格位置（close 在近 N=20 日区间归一位置）与量能方向
  （近 N 日上涨日成交量占比）等权混合 → p_up∈[0,1]，p_down=1−p_up
  （仅 squeeze 窗口内有语义；非压缩期置中性 0.5 不干预）。
- **3 日维持确认**：RV 扩张（rv_ratio>1.5，RV_5d>1.5×RV_20d）且放量
  （近 5 日均量/20 日均量>1.5）逐日判定，尾部连续命中 ≥3 日 → confirmed=1，
  方向取窗口内价格位移符号。
- 降级：样本不足（<min_history 默认 60）/非有限值 → 全维度=0 + degraded +
  reason，不抛错；仅配置非法 Fail-Closed（SqueezeConfigError）。
- overlay_dims()：squeeze flag / breakout_dir score（p_up×100）/ confirm flag，
  无信号=0（平时不干预，对齐 overlay 契约）。

## 2. 接口

```python
@dataclass(frozen=True)
class SqueezeConfig: rv thresholds / bb window / percentile / sustain_days / volume expansion ...
@dataclass(frozen=True)
class SqueezeBreakoutSignal: rv_ratio / bb_width_percentile / squeeze_flag /
    p_up / p_down / confirmed / confirm_direction / degraded / degrade_reason + overlay_dims()
class VolatilitySqueezeBreakout: assess(closes, volumes) -> SqueezeBreakoutSignal
class SqueezeConfigError(ValueError)
```

## 3. 依赖前置

- MOD-REGIME-011 volatility_regime_alerter（RV 年化口径/降级哲学/overlay 契约对齐；
  <0.8 早标记 vs <0.5 强压缩分工）。
- numpy（数值计算，同族既有依赖）。

## 4. 验收标准

- 单测全绿（双腿压缩联合判定/分位计算/方向概率口径/3日维持确认与方向/降级
  不抛错/配置非法 Fail-Closed/overlay_dims 契约）；相关域集成零回归。
