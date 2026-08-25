---
blueprint_id: MOD-REGIME-012
module_name: market_forecast_fusion
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
path: src/zephyr/regime/market_forecast_fusion.py
granularity: file
---

# MOD-REGIME-012 market_forecast_fusion 蓝图（C-014 大盘预测三层融合）

> **module_id**: MOD-REGIME-012 | **域**: D_REGIME | **优先级**: P1
> **来源**: B1-00154（AUD-DRAFT-001-DIGEST P1 波 W-P1-17，CAND-CYCLE-004，跨域元文档 §功能域模块·D-SIGNAL）
> 代码：`src/zephyr/regime/market_forecast_fusion.py`

## 0. 定位

C-014 大盘预测**三层融合判定核心**：系统内部模型 + 外部主播信号采集打分 +
滚动准确率动态加权 → 次日 8 态分布与置信度，预测日志入 prediction_log_writer
供复盘加权更新。TSV 现状注记：8 态预测单点（MOD-SIG-037）在，三层融合未成。

查重分工（W-P1-17 探查结论，均不复制）：

| 既有件 | module_id | 职责 | 与本模块边界 |
|---|---|---|---|
| regime_detector | MOD-REGIME-001 | 4态HMM+overlay 7维灰度概率+Shrinkage 节流 | 管 regime 灰度概率，不做次日 8 态点分布融合 |
| overlay_signals_builder | MOD-REGIME-002 | 8转换 overlay 输入构造（score/flag 契约） | 不管多源预测加权 |
| volatility_regime_alerter | MOD-REGIME-011 | 波动率体制转换预警（GARCH+RV压缩+突变） | 不管次日走势态分布 |
| next_day_8state_forecast | MOD-SIG-037 | 次日 8 态内部单点模型（一阶马尔可夫+平稳分布修正） | 本模块的**内部层输入**，不重造 8 态引擎 |
| prediction_log_writer | MOD-RPT-028 | 预测日志统一落库（append-only 幂等） | 本模块只产 payload+回调，写库委托装配批 |

不做什么：不重造 8 态预测引擎（MOD-SIG-037 内部层直用）、不直接写库
（log_sink 回调委托 MOD-RPT-028，装配批接线）、不采集主播信号（外部层信号
经构造器注入，D_ALT_DATA 采集面归其域）、不出点位/买卖信号（对齐 90 号 §7
裁定：只出概率分布与置信度）。

## 1. 三层融合规则（确定性，纯函数）

- **层1 内部模型**：MOD-SIG-037 NextDayForecast（8 态分布+置信度）。
- **层2 外部主播信号**：ExternalForecast（source_id + 8 态分布 + 自报置信度），
  Fail-Closed 校验（态键全集/概率非负/Σ>0 归一/置信度∈[0,1]）。
- **层3 滚动准确率动态加权**：RollingAccuracyTracker（窗口默认 60 日，
  Beta 先验 p0=1/8 八态随机命中率/强度 α=16 初拟待标定）按源记录预测众数态
  命中；weight_i = max(accuracy_i, min_weight=0.05) 归一。
- 融合分布 = Σ w_i × dist_i 再归一（Σ=1.0 不变量）；众数态 + top_probability；
  confidence = top_probability × 众数态源一致度（权重占比，∈[0,1]）。
- 复盘闭环：settle(actual_state) 记录各源命中 → 权重次日滚动更新；预测 payload
  经 log_sink 入 prediction_log（同键保首条不覆写语义归写入器）。

## 2. 接口

```python
@dataclass(frozen=True)
class ExternalForecast: source_id / probabilities / confidence
@dataclass(frozen=True)
class FusedForecast: probabilities / top_state / top_probability / confidence / weights
class RollingAccuracyTracker: record(source, predicted_top, actual) / accuracy(source) / weight(source)
class MarketForecastFusion: fuse(internal, external) / settle(actual) / build_log_payload(...)
class FusionConfigError(ValueError) / InvalidExternalForecastError(ValueError)
```

## 3. 依赖前置

- MOD-SIG-037 next_day_8state_forecast（内部层 8 态分布与态枚举唯一真源）。
- MOD-RPT-028 prediction_log_writer（预测日志落库契约，payload 对齐其唯一键）。
- MOD-REGIME-001 regime_detector（概率分布 Σ=1 / 降级哲学对齐，不消费其输出）。

## 4. 验收标准

- 单测全绿（融合归一/权重动态滚动/先验冷启动/畸形外部信号 Fail-Closed/置信度
  口径/日志 payload 唯一键字段/settle 命中回写）；相关域集成零回归。
