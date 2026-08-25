---
blueprint_id: MOD-ML-011
module_name: patchtst_density_encoder
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
path: src/zephyr/ml_train/implementations/patchtst_density_encoder.py
granularity: file
---

# MOD-ML-011 patchtst_density_encoder 蓝图（§29.7 Transformer时序架构密度预测增强）

> **module_id**: MOD-ML-011 | **域**: D_ML_TRAIN | **优先级**: P1
> **来源**: B10-01831（AUD-DRAFT-001-DIGEST P1 波 W-P1-20，CAND-MLT-015，A1交易决策架构 §29.7）
> 代码：`src/zephyr/ml_train/implementations/patchtst_density_encoder.py`

## 0. 定位

§29.7 Transformer 时序架构密度预测增强：Transformer 四家族
（Informer/PatchTST/TimesNet/iTransformer）中先落地 PatchTST 单家族，作
QNN Stage1 前置特征提取器（Phase2 路线，TSV 原文裁定）。

查重分工（W-P1-20 铁律⑤探查——**时序特征编码器缺口，双路线互补非竞争**）：

| 既有件 | module_id | 职责 | 与本模块边界 |
|---|---|---|---|
| mamba_ssm_temporal_enhancer | MOD-SIG-051 | 信号域 Mamba 单家族时序增强器 | Transformer 家族缺失，本件=PatchTST 编码器；家族不同、域不同（信号层 vs 训练层） |
| density_quantile_trainer | MOD-ML-DENSITY | 轻量密度头（消费扁平特征矩阵） | 本件=**前置特征编码器**（时序→特征），输出供密度头/QNN 消费，非预测器 |
| qnn_two_stage | MOD-ML-010 | A2 两阶段 QNN（训练架构） | 双路线互补：两阶段=训练架构，PatchTST=Stage1 前置特征提取器（TSV §29.7 Phase2 原文），非同物 |

torch 仅在可选 ml-train extra（非核心依赖）→ 本件 numpy/sklearn MVP：
patchify + 通道独立 + 数据驱动线性 patch embedding（SVD）+ 单头内容注意力
池化，零新重依赖。B-009：全部产物 testing 封顶，禁实盘生效。

## 1. 规则（确定性，B-009 testing 封顶）

- **patchify**：输入 (n, lookback, n_channels) 时序（默认 60天×60因子）→
  每通道切 patch（patch_len=16, stride=8），通道独立（同一变换作用于每通道，
  PatchTST channel-independence 核心）。
- **patch embedding**：全样本全通道 patch 合并做 SVD，取 top-d_proj 主成分
  为投影矩阵（数据驱动、确定性、numpy 闭式）；patch → d_proj 维 embedding。
- **注意力池化**：单头内容注意力——query=拟合集 embedding 均值（fit 时存储），
  softmax(embedding·query/√d) 对 patch 维加权 → 每通道一个 d_proj 向量。
- **输出**：PatchtstFeatures（channel_embeddings (n, C, d) + pooled (n, d)），
  作密度预测（MOD-ML-DENSITY / MOD-ML-010 Stage1）前置特征矩阵。
- Fail-Closed：输入维度非法/patch 参数非法/未 fit 先 transform/样本不足 →
  PatchtstEncoderError。

## 2. 接口

```python
@dataclass(frozen=True)
class PatchtstEncoderConfig:
    patch_len=16, stride=8, d_proj=16, min_samples=8

@dataclass(frozen=True)
class PatchtstFeatures: channel_embeddings, pooled, n_patches

class PatchtstDensityEncoder:
    fit(x: (n, L, C)) -> metrics(dict)
    transform(x: (n, L, C)) -> PatchtstFeatures  # 需先 fit

class PatchtstEncoderError(Exception): 占位 ZA-MLT-UNREGISTERED-PATCHTST-ENCODER
```

## 3. 错误契约

- `PatchtstEncoderError`（未登记错误码-申请中，占位 ZA-MLT-UNREGISTERED-PATCHTST-ENCODER，
  建议顺延 ZA-MLT-0004 见 W-P1-20 fragment）

## 4. 测试

- `tests/ml_train/test_patchtst_density_encoder.py`
- 覆盖：patchify 形状与通道独立性、SVD 投影确定性、注意力池化权重和为1、
  pooled 特征维度、未 fit 报错、输入校验

## 5. 依赖

- numpy（零新重依赖；torch 不引入——仅 ml-train extra）
- 下游（运行时装配，不 import）：MOD-ML-DENSITY 密度头 / MOD-ML-010 QNN
  Stage1 前置特征消费
