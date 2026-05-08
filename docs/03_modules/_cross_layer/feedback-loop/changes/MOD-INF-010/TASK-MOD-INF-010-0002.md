---
task_id: TASK-MOD-INF-010-0002
module_id: MOD-INF-010
blueprint_ref: D:\ZephyrAlpha\docs\03_modules\_cross_layer\feedback-loop\blueprint.md
blueprint_sections: ["§2 三相流水线（Three-Phase Pipeline）", "§2.1-§2.5 核心引擎"]
status: pending
priority: P0
created_date: 2026-05-06
assigned_to: null
depends_on: ["TASK-MOD-INF-010-0001"]
blocked_by: []
blocks: ["TASK-MOD-INF-010-0003", "TASK-MOD-INF-010-0023"]
estimated_effort_hours: 12
actual_effort_hours: null
tags: [core-pipeline, collect-detect-dispatch, three-phase, EMA-anomaly]
upstream_files:
  - D:\ZephyrAlpha\docs\03_modules\_cross_layer\feedback-loop\blueprint.md
  - D:\ZephyrAlpha\src\zephyr\feedback_loop\__init__.py
  - D:\ZephyrAlpha\src\zephyr\feedback_loop\config.py
  - D:\ZephyrAlpha\src\zephyr\feedback_loop\protocols.py
downstream_outputs:
  - D:\ZephyrAlpha\src\zephyr\feedback_loop\collectors\metrics_collector.py
  - D:\ZephyrAlpha\src\zephyr\feedback_loop\collectors\feedback_collector.py
  - D:\ZephyrAlpha\src\zephyr\feedback_loop\detectors\anomaly_detector.py
  - D:\ZephyrAlpha\src\zephyr\feedback_loop\diagnosers\diagnosis_engine.py
  - D:\ZephyrAlpha\src\zephyr\feedback_loop\actors\action_selector.py
  - D:\ZephyrAlpha\src\zephyr\feedback_loop\verifiers\verification_engine.py
  - D:\ZephyrAlpha\src\zephyr\feedback_loop\fitness_functions.py
  - D:\ZephyrAlpha\src\zephyr\feedback_loop\eval_harness.py
  - D:\ZephyrAlpha\src\zephyr\feedback_loop\evolution_engine.py
  - D:\ZephyrAlpha\src\zephyr\feedback_loop\auto_evolution.py
acceptance_criteria:
  - AC-0002-01: metrics_collector.py 实现 system_cpu/memory/disk/network_error/detection_latency 五维采集，EMA baseline 训练（window=100），异常检测（z-score > 2.5）
  - AC-0002-02: feedback_collector.py 实现 action_result（收集修复执行前/后对比）和 owner_ack 两种 feedback 通道
  - AC-0002-03: anomaly_detector.py 在 5 分钟内完成 detect，调用 NOTIFY_OWNER 时附带 anomaly_id + severity + evidence
  - AC-0002-04: diagnosis_engine.py 接收 anomaly_id，查询因果推断引擎，返回 diagnosis_id + root_cause + confidence
  - AC-0002-05: action_selector.py 同一 action_type 连续 3 次无效自动退役
  - AC-0002-06: verification_engine.py 验证 repair 效果，含 pre-post metric delta，若 delta 为负标记为 HARMFUL
  - AC-0002-07: eval_harness.py 构建 scaffold 评估框架（含 EMA baseline 验证和 anomaly detection precision@k）
  - AC-0002-08: fitness_functions.py 定义 4 个 fitness 函数：anomaly_detection_precision、false_positive_rate、mtti_seconds、owner_override_rate
  - AC-0002-09: evolution_engine.py + auto_evolution.py 实现 RL 驱动的 action selection 在线进化（Q-learning + EWC 防灾难性遗忘）
rollback_instructions: |
  1. 删除本次创建的 10 个核心文件
  2. 如已注册 blueprint-registry.yaml 状态变更，回滚
  3. 回滚 __init__.py 中新增的 submodule import
context_assembly_manifest:
  required_contexts:
    - context_id: CTX-BLUEPRINT-§2
      source: D:\ZephyrAlpha\docs\03_modules\_cross_layer\feedback-loop\blueprint.md
      sections: ["§2 三相流水线"]
      description: 核心流水线架构——collect→detect→dispatch 三阶段设计
    - context_id: CTX-BLUEPRINT-§1.3
      source: D:\ZephyrAlpha\docs\03_modules\_cross_layer\feedback-loop\blueprint.md
      sections: ["§1.3 防循环依赖设计"]
      description: Protocol 适配器 fire-and-forget 单向依赖——FLE 不直接 import 其他模块
  assembly_notes: |
    这是 FLE 的核心引擎实现。三阶段流水线 (collect → detect → dispatch) 是 FLE 的主循环。
    dispatch 阶段包含 diagnose → repair → verify 子循环。
    所有跨模块调用通过 Protocol 适配器走 fire-and-forget 模式，防止循环依赖。
---

# TASK-MOD-INF-010-0002: 三相流水线核心引擎实现

## 1. 任务目标

实现 FLE 的核心三阶段流水线（collect→detect→dispatch）及自进化评估框架。

## 2. 架构概览

```
collect (metrics_collector + feedback_collector)
  ↓
detect (anomaly_detector: EMA baseline + z-score > 2.5)
  ↓
dispatch
  ├── diagnose (diagnosis_engine: 因果推断 → root_cause)
  ├── repair  (action_selector: action_type → execution)
  └── verify  (verification_engine: pre/post metric delta)
```

自进化层：
```
eval_harness → fitness_functions → evolution_engine → auto_evolution
                                                  ↓
                                          action_selector (在线RL更新)
```

## 3. 实现步骤

### Step 1: metrics_collector.py
- 采集维度：system_cpu、memory_usage_pct、disk_io_wait、network_errors_count、detection_latency_ms
- EMA baseline：window=100，alpha=0.1
- 异常判定：z-score > 2.5 → 触发 anomaly_event
- OTel span 导出

### Step 2: feedback_collector.py
- action_result 通道：pre/post metric delta + action_type + success_flag
- owner_ack 通道：Owner 对 NOTIFY_OWNER 的响应（ack/override/ignore）
- 时间窗口聚合：5min sliding window

### Step 3: anomaly_detector.py
- 输入：metrics_collector 实时 EMA 残差 + feedback_collector 的 repair_failure_rate
- 输出：anomaly_event {anomaly_id, severity(0-10), evidence{metric_name, value, baseline, z_score}, timestamp}
- 首次触发：NOTIFY_OWNER（待 Owner 校准 severity baseline）

### Step 4: diagnosis_engine.py
- 输入：anomaly_id
- 因果推断：correlation_matrix → causal_graph → root_cause ranking
- 输出：diagnosis {diagnosis_id, root_cause, confidence(0-1), evidence_chain}

### Step 5: action_selector.py
- action_type 优先级：NOTIFY_OWNER > ADJUST_THRESHOLD > REPAIR > DEPLOY > SELF_UPGRADE > REBALANCE
- 退役规则：同一 action_type 连续 3 次无效（repair 后 anomaly 未恢复/恶化） → 自动退役 7 天
- RL 驱动：Q(s, a) ← Q(s, a) + α[r + γ·max_a'Q(s', a') - Q(s, a)]

### Step 6: verification_engine.py
- pre/post metric delta 对比
- delta < 0 → 标记为 HARMFUL
- delta ≈ 0 → 标记为 INEFFECTIVE
- delta > 0且anomaly恢复 → 标记为 EFFECTIVE

### Step 7-10: 自进化层
- eval_harness.py：评估框架 scaffold（EMA baseline验证、anomaly detection precision@k）
- fitness_functions.py：4维fitness（precision、FP_rate、MTTI、override_rate）
- evolution_engine.py：Q-learning + EWC（Elastic Weight Consolidation）防灾难性遗忘
- auto_evolution.py：定期（每24h）触发 evolution_engine.optimize()

## 4. 关键设计决策

| 决策 | 内容 |
|------|------|
| 异常检测方法 | EMA baseline + z-score > 2.5（初版不引入 LLM） |
| 防循环依赖 | 所有跨模块调用通过 FeedbackProtocolAdapter.fire_and_forget() |
| 自进化周期 | 24h（auto_evolution cron）|
| LLM 引入时机 | v0.3.0+（diagnosis_engine 因果推断阶段）|
