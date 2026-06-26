---
module_id: KE-2947
status: active
title: 三相流水线核心 (TASK-0002)
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 三相流水线核心 (TASK-0002)

三相流水线核心 (TASK-0002)
- `collectors/metrics_collector.py` — 5维EMA基线 + z-score异常检测 (Z_THRESHOLD=2.5)
- `collectors/feedback_collector.py` — 双通道反馈(action_result + owner_ack) + 滑动窗口评分
- `detectors/anomaly_detector.py` — 异常事件检测 + 协议适配器fire-and-forget通知
- `diagnosers/diagnosis_engine.py` — 根因推理 + 置信度评估
- `actors/action_selector.py` — RL驱动动作选择 + 连续失败退役 + 退休冷却
- `verifiers/verification_engine.py` — pre/post修复验证 + HARMFUL/INEFFECTIVE/EFFECTIVE判定
- `fitness_functions.py` — 4项适应度函数(precision/MD/FP/N_PARAM_NEW)
- `eval_harness.py` — EMA基线RMSE + anomaly precision@k
- `evolution_engine.py` — Q-learning + EWC(弹性权重巩固) 防灾难遗忘
- `auto_evolution.py` — 周期自进化调度(默认24h)
