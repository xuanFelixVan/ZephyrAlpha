---
blueprint_id: MOD-ML-010
module_name: qnn_two_stage
domain: D_ML_TRAIN
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
domain_id: D_ML_TRAIN
path: src/zephyr/ml_train/implementations/qnn_two_stage.py
granularity: file
---

# MOD-ML-010 qnn_two_stage 蓝图（A2 分位数神经网络两阶段架构 QNN Two-Stage）

> **module_id**: MOD-ML-010 | **域**: D_ML_TRAIN | **优先级**: P1
> **来源**: B10-01408（AUD-DRAFT-001-DIGEST P1 波 W-P1-20，CAND-MLT-014 ★当前即做，A1交易决策架构 §4.5.1-A2）
> 代码：`src/zephyr/ml_train/implementations/qnn_two_stage.py`

## 0. 定位

A2 分位数神经网络两阶段架构（UBS Quant Hub 2025）：Stage1 跨标的共性分位数
网络（市场共性剥离、跨标的复用）+ Stage2 市场缩放头（per-symbol 仿射缩放，
体制切换时几分钟级快速重训）。

查重分工（W-P1-20 铁律④探查——**新模型类，非推倒既有件**）：

| 既有件 | module_id | 职责 | 与本模块边界 |
|---|---|---|---|
| density_quantile_trainer | MOD-ML-DENSITY | 单标的逐分位 HGB 轻量密度头（P0 已加 A1 左尾加权） | 本件=**两阶段结构新模型类**（跨标的共性+缩放头），HGB quantile 依赖面同族但不 import 其私有件，density trainer 保留不动 |
| conditional_density_predictor | MOD-SIG-043 | 信号域条件经验分布法（矩+分位数网格） | 信号层推理件，非训练架构；不同层不重叠 |
| trainer_base | MOD-L11-001 | 训练器抽象基类（OCP 扩展点） | 本件继承实现 train/validate |

TSV 裁定原文："分位数训练器已有但无 Stage1 市场共性剥离/Stage2 体制快速重训
结构，增量明确"——施工形态=1 个新模块，核心类 TwoStageQnn。

## 1. 规则（确定性，B-009 testing 封顶）

- **Stage1（共性剥离）**：全部标的样本合并池化，逐分位数拟合 sklearn
  HistGradientBoostingRegressor(loss="quantile") → 共性基座分位数
  q_base(x)（跨标的复用，一次训练）。
- **Stage2（市场缩放头）**：per-symbol 仿射缩放
  `q_s(x) = m(x) + a_s·(q_base(x) − m(x)) + b_s`（m(x)=基座中位数预测）；
  (a_s, b_s) 以该标的子样本对残差做闭式 OLS 估计（numpy，确定性）；
  子样本不足 min_symbol_samples → 回退 a_s=1.0, b_s=0.0（degraded，纯 Stage1）。
- **体制快速重训**：`retrain_stage2(features, target)` 只重估仿射头
  （Stage1 冻结，分钟级），供体制切换场景。
- **输出契约**：predict_quantiles(x, symbol_ids) → {quantile: (n,)}，
  分位数序列 np.maximum.accumulate 单调不交叉修正（口径对齐 MOD-ML-DENSITY）。
- **晋升纪律**：build_registry_entry 只产 candidate 草稿（恒 candidate，
  治理流程串行合并，禁直改注册表；禁止实盘生效 B-009）。
- Fail-Closed：特征缺失/维度非法/样本不足/symbol_ids 不齐 → TwoStageQnnError。

## 2. 接口

```python
@dataclass(frozen=True)
class TwoStageQnnConfig:
    quantiles=(0.1,0.25,0.5,0.75,0.9), max_iter=200, learning_rate=0.06,
    max_depth=3, min_samples_leaf=20, random_state=42,
    min_train_samples=30, min_symbol_samples=20

class TwoStageQnn(ModelTrainerBase):  # __model_id__ = "ML-QNN2S-001"
    train(features{X,symbol_ids[,feature_names]}, target, idempotency_key) -> metrics
    retrain_stage2(features{X,symbol_ids}, target) -> metrics  # Stage1 冻结
    validate(features, target) -> {pinball_mean, coverage_10_90, n}
    predict_quantiles(x, symbol_ids) -> dict[quantile, np.ndarray]
    build_registry_entry(metrics) -> candidate 草稿

class TwoStageQnnError(Exception): 占位 ZA-MLT-UNREGISTERED-QNN-TWO-STAGE
```

## 3. 错误契约

- `TwoStageQnnError`（未登记错误码-申请中，占位 ZA-MLT-UNREGISTERED-QNN-TWO-STAGE，
  建议顺延 ZA-MLT-0003 见 W-P1-20 fragment）

## 4. 测试

- `tests/ml_train/test_qnn_two_stage.py`
- 覆盖：两阶段训练链、缩放头拟合与 degraded 回退、retrain_stage2 冻结 Stage1、
  分位数单调性、validate 指标、晋升草稿恒 candidate、输入校验

## 5. 依赖

- `zephyr.ml_train.trainer_base`（ModelTrainerBase/ModelMetadata）+ sklearn + numpy
- 下游（运行时装配，不 import）：D_REGIME 体制标签可作 Stage2 分组扩展；
  Phase2 前置特征接 MOD-ML-011 patchtst_density_encoder（§29.7 路线衔接）
