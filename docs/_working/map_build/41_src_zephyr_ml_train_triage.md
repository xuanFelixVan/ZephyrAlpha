---
ttl: task_bound
completes_when: 孤儿分诊战役终裁落地（chief 终审+处置执行）后本册随 30/31 号转归档
title: 孤儿分诊证据包：src.zephyr.ml_train（41 台）
owner: st-orphtriage-20261004
---

# 41 号·分诊证据包：src.zephyr.ml_train（41 台）

> 宇宙口径=裁定#481；数据真源=30_attribution_table.yaml（join checker 机生）；处置=证据班建议，终裁归 GLM-5.3 chief，退役执行归 Owner 门位。
>
> tier 分布：suspect_orphan=9，wired=10，wired_by_header=21，wired_dynamic=1；初判汇总：dispute=9，mount=32

## 逐台证据（四字段+初判）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `src/zephyr/ml_train/_extensions/__init__.py` | ml_train/_extensions | 2026-09-15（19天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 19 天内有 commit（活着但零线零引）；①mount→FACTORY（策略工厂） ②retire→Owner 门位） |
| `src/zephyr/ml_train/ai_operator/__init__.py` | ml_train/ai_operator — MOD-ML-002 AI 操作员包 | 2026-09-15（19天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 19 天内有 commit（活着但零线零引）；①mount→FACTORY（策略工厂） ②retire→Owner 门位） |
| `src/zephyr/ml_train/api/__init__.py` | ml_train/api | 2026-09-15（19天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 19 天内有 commit（活着但零线零引）；①mount→FACTORY（策略工厂） ②retire→Owner 门位） |
| `src/zephyr/ml_train/core/__init__.py` | NOTE(2026-08-25 P1W21): scaffold 注册器斜杠非法 import 变种复发（同 #ARCH-228 族）， | 2026-09-17（17天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 17 天内有 commit（活着但零线零引）；①mount→FACTORY（策略工厂） ②retire→Owner 门位） |
| `src/zephyr/ml_train/infrastructure/__init__.py` | ml_train/infrastructure | 2026-09-15（19天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 19 天内有 commit（活着但零线零引）；①mount→FACTORY（策略工厂） ②retire→Owner 门位） |
| `src/zephyr/ml_train/models/__init__.py` | ml_train/models | 2026-09-15（19天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 19 天内有 commit（活着但零线零引）；①mount→FACTORY（策略工厂） ②retire→Owner 门位） |
| `src/zephyr/ml_train/services/__init__.py` | ml_train/services | 2026-09-15（19天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 19 天内有 commit（活着但零线零引）；①mount→FACTORY（策略工厂） ②retire→Owner 门位） |
| `src/zephyr/ml_train/training_dataset_manager/__init__.py` | ml_train/training_dataset_manager — MOD-ML-003 训练数据集管理包 | 2026-09-15（19天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 19 天内有 commit（活着但零线零引）；①mount→FACTORY（策略工厂） ②retire→Owner 门位） |
| `src/zephyr/ml_train/training_pipeline/__init__.py` | ml_train/training_pipeline — MOD-ML-001 训练管线编排包 | 2026-09-15（19天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 19 天内有 commit（活着但零线零引）；①mount→FACTORY（策略工厂） ②retire→Owner 门位） |
| `src/zephyr/ml_train/__init__.py` | D_ML_TRAIN — ML Training Domain | 2026-09-15（19天） | in=0/out=0·wired_dynamic | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/ml_train/adversarial_robustness_validator.py` | 对抗鲁棒性验证器（MOD-ML-005）——轻量可单测实现。 | 2026-09-15（19天） | in=0/out=0·wired_by_header | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/ml_train/ai_operator/operator.py` | D_ML_TRAIN — MOD-ML-002 AI 操作员。 | 2026-09-15（19天） | in=1/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/ml_train/continual_learning_antiforget.py` | ContinualLearningAntiForget — 持续学习抗遗忘框架（MOD-ML-018）。 | 2026-09-15（19天） | in=0/out=0·wired_by_header | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/ml_train/core/model_version_registry.py` | Model Version Registry — 训练域 Model 聚合 + 版本生命周期 + INV-011 影子验证门 (MOD-ML-012, CAND-MLT-016, B4-06880) | 2026-09-15（19天） | in=1/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/ml_train/core/sample_weights.py` | D_ML_TRAIN — 半衰期样本权重（90 号 Phase2 项，#9 数据分层修订采纳） | 2026-09-15（19天） | in=0/out=0·wired_by_header | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/ml_train/decision_annotation_dataset.py` | DecisionAnnotationDataset — 交易决策标注数据集（MOD-ML-014）。 | 2026-09-15（19天） | in=0/out=0·wired_by_header | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/ml_train/experiment_anomaly_detector.py` | ExperimentAnomalyDetector — 实验指标异常检测（MOD-ML-023）。 | 2026-09-15（19天） | in=1/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/ml_train/gray_release_shadow_deployer.py` | D_ML_TRAIN — MOD-ML-004 灰度/影子部署器。 | 2026-09-15（19天） | in=0/out=0·wired_by_header | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/ml_train/implementations/__init__.py` | D_ML_TRAIN — ML Training Concrete Implementations | 2026-09-15（19天） | in=0/out=0·wired_by_header | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/ml_train/implementations/default_inference_engine.py` | D_ML_TRAIN — Default Inference Engine | 2026-09-15（19天） | in=2/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/ml_train/implementations/density_quantile_trainer.py` | D_ML_TRAIN — GAP-F-34 密度预测主路线 MVP（ML-DENSITY-001 轻量密度头）。 | 2026-09-15（19天） | in=0/out=0·wired_by_header | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/ml_train/implementations/kan_density_head.py` | KanDensityHead — KAN 密度预测头（MOD-ML-017）。 | 2026-09-15（19天） | in=0/out=0·wired_by_header | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/ml_train/implementations/limit_up_classifier.py` | D_ML_TRAIN — GAP-F-35 打板涨停概率分类器骨架（ML-CLS-001）。 | 2026-09-15（19天） | in=0/out=0·wired_by_header | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/ml_train/implementations/patchtst_density_encoder.py` | PatchTST 密度前置特征编码器 (MOD-ML-011, B10-01831 §29.7)。 | 2026-09-17（17天） | in=0/out=0·wired_by_header | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/ml_train/implementations/qnn_two_stage.py` | A2 分位数神经网络两阶段架构 (MOD-ML-010, B10-01408 ★当前即做)。 | 2026-09-17（17天） | in=0/out=0·wired_by_header | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/ml_train/implementations/seat_pattern_classifier.py` | D_ML_TRAIN — GAP-F-35 席位形态分类器骨架（ML-CLS-002）。 | 2026-09-15（19天） | in=0/out=0·wired_by_header | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/ml_train/implementations/sentiment_sft_trainer.py` | MOD-L11-001 SentimentSFTTrainer — Qwen2.5-7B-Instruct LoRA SFT（P1-E3 Phase 4）。 | 2026-09-15（19天） | in=1/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/ml_train/inference_base.py` | D_ML_TRAIN — ML Inference Base | 2026-09-15（19天） | in=2/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/ml_train/learning_effect_feedback.py` | D_ML_TRAIN — MOD-ML-009 学习效果反馈回喂。 | 2026-09-15（19天） | in=0/out=0·wired_by_header | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/ml_train/meta_learning_evolution.py` | D_ML_TRAIN — MOD-ML-007 元学习演进（跨任务经验库，轻量）。 | 2026-09-15（19天） | in=0/out=0·wired_by_header | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/ml_train/meta_learning_rsi.py` | 元学习 RSI（MOD-ML-008）——轻量可单测实现。 | 2026-09-15（19天） | in=0/out=0·wired_by_header | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/ml_train/ml_model_factory.py` | MlModelFactory — ML 模型工厂（MOD-ML-013）。 | 2026-09-15（19天） | in=0/out=0·wired_by_header | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/ml_train/reproducibility_manager.py` | ReproducibilityManager — 可复现性管理器（MOD-ML-020）。 | 2026-09-15（19天） | in=0/out=0·wired_by_header | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/ml_train/research_asset_versioning.py` | ResearchAssetVersioning — 研究资产版本化管理器（MOD-ML-022）。 | 2026-09-15（19天） | in=0/out=0·wired_by_header | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/ml_train/research_data_manager.py` | ResearchDataManager — 研究数据管理器（MOD-ML-019）。 | 2026-09-15（19天） | in=0/out=0·wired_by_header | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/ml_train/research_data_sandbox.py` | ResearchDataSandbox — 研究数据沙箱（MOD-ML-021）。 | 2026-09-15（19天） | in=0/out=0·wired_by_header | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/ml_train/services/sentiment_sft_entry.py` | D_ML_TRAIN — GAP-F-35 舆情情感 SFT 训练入口桩（ML-SFT-001）。 | 2026-09-15（19天） | in=2/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/ml_train/strategy_digital_twin.py` | 策略数字孪生（MOD-ML-006）——轻量可单测实现。 | 2026-09-15（19天） | in=0/out=0·wired_by_header | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/ml_train/trainer_base.py` | D_ML_TRAIN — ML Training Base | 2026-09-15（19天） | in=10/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/ml_train/training_dataset_manager/manager.py` | D_ML_TRAIN — MOD-ML-003 训练数据集管理器。 | 2026-09-15（19天） | in=1/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
| `src/zephyr/ml_train/training_pipeline/pipeline_orchestrator.py` | D_ML_TRAIN — MOD-ML-001 训练管线编排器。 | 2026-09-15（19天） | in=1/out=0·wired | **mount**→FACTORY（策略工厂）（活线在身未挂线） |
