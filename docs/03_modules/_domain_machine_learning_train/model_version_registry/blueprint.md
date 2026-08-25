---
blueprint_id: MOD-ML-012
module_name: model_version_registry
domain: D_ML_TRAIN
doc_type: blueprint
ttl: permanent
design_maturity: design
stability: evolving
safety_level: H
ai_autonomy: human_gated
version: "0.1.0"
created: 2026-08-25
last_updated: 2026-08-25
owner: ZephyrAlpha-Owner
priority: P1
blueprint_level: module
domain_id: D_ML_TRAIN
path: src/zephyr/ml_train/core/model_version_registry.py
granularity: file
---

# MOD-ML-012 model_version_registry 蓝图（D-ML-TRAIN 训练域 Model 聚合 + 版本生命周期 + INV-011 影子验证门）

> **module_id**: MOD-ML-012 | **域**: D_ML_TRAIN | **优先级**: P1
> **来源**: B4-06880（AUD-DRAFT-001-DIGEST P1 波 W-P1-21，CAND-MLT-016，D-ML-TRAIN §0）
> 代码：`src/zephyr/ml_train/core/model_version_registry.py`

## 0. 定位

训练域总纲候选的最小独立可施工缺口：AGG-008 Model 聚合 + ENT-006 ModelVersion
实体 + 版本生命周期状态机（TRAINED→VALIDATED→SHADOW_VERIFIED→ACTIVATED→
DEPRECATED）+ E-ML-01 ModelTrained / E-RS-03 ModelValidated 事件 + INV-011
影子验证门（TRAIN 产出模型必须经影子验证后方可激活进 Warm）。

查重分工（W-P1-21 铁律①细读 TSV——域级泛条目，但 min_build_spec 有独立缺口）：

| 既有件 | module_id | 职责 | 与本模块边界 |
|---|---|---|---|
| trainer_base.ModelRegistry | MOD-L11-001 | 训练器**类**注册（OCP 扩展点，id→trainer class） | 本件=模型**版本实例**聚合与生命周期，非类注册 |
| experiment_tracking | MOD-OBS-001 | 实验运行记录/指标跟踪（实验管理归一） | 本件不管实验参数/日志，只管版本阶段推进与事件 |
| gray_release_shadow_deployer | MOD-ML-004 | 影子部署会话执行面（只记录不生效，B-009） | 本件消费其影子验证**结论**（proof 注入，不 import）做 INV-011 门禁 |
| factor_factory | MOD-L02-001 | 因子发现流水线（TSV spec 该句已由其承载） | 不重复建 |

TSV 裁定原文（做 P1）："AGG-008 Model+ENT-006 ModelVersion聚合+实验管理归一+
因子发现流水线+ModelTrained/ModelValidated事件+INV-011影子验证对接"——实验管理
归一/因子发现流水线既有件承载，本件落剩余独立缺口。

## 1. 规则（确定性，B-009 testing 封顶）

- **生命周期（ENT-006）**：TRAINED → VALIDATED → SHADOW_VERIFIED → ACTIVATED；
  任意非终态 → DEPRECATED（终态，不可逆）。非法迁移/终态再迁移 → 抛错。
- **VALIDATED 前置**：validation_metrics 非空且全为有限值。
- **INV-011 影子验证门**：仅 SHADOW_VERIFIED 可 ACTIVATED；record_shadow_verified
  须注入 shadow_proof（证据串非空，真源=MOD-ML-004 会话结论，调用方注入）。
- **人工闸门**：activate 须 approved_by 非空（human_gated，严禁自动上线）。
- **事件**：register_trained 产 E-ML-01 ModelTrainedEvent；record_validated 产
  E-RS-03 ModelValidatedEvent；经 event_sink 回调外发（委托装配批落账）。
- 每模型同一时刻至多一个 ACTIVATED 版本（激活新版本自动废弃旧激活版本？否——
  拒绝并存，须先 deprecate；Fail-Closed）。
- Fail-Closed：空 model_id/version、非法阶段迁移、缺证明/缺批准 →
  ModelVersionRegistryError。

## 2. 接口

- `ModelVersionStage`（枚举 5 阶段）/ `ModelTrainedEvent` / `ModelValidatedEvent`
  / `ModelVersionRecord`（frozen 快照）
- `ModelVersionRegistry(event_sink=None, clock=None)`
  - `register_trained(model_id, version, training_metrics=None, lineage=None) -> ModelVersionRecord`
  - `record_validated(model_id, version, validation_metrics) -> ModelVersionRecord`
  - `record_shadow_verified(model_id, version, shadow_proof) -> ModelVersionRecord`
  - `activate(model_id, version, approved_by) -> ModelVersionRecord`
  - `deprecate(model_id, version, reason) -> ModelVersionRecord`
  - `get(model_id, version)` / `active_version(model_id)` / `list_versions(model_id)`

## 3. 不做什么

不跑训练（trainer 职责）、不做影子部署执行（MOD-ML-004）、不做实验跟踪
（MOD-OBS-001）、不直连事件总线（event_sink 回调注入）。
