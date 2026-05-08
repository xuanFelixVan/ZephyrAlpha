---
task_id: TASK-MOD-INF-010-0027
module_id: MOD-INF-010
blueprint_ref: D:\ZephyrAlpha\docs\03_modules\_cross_layer\feedback-loop\blueprint.md
blueprint_sections: ["§4 指标体系（4.1-4.29）"]
status: pending
priority: P1
created_date: 2026-05-06
assigned_to: null
depends_on: ["TASK-MOD-INF-010-0002"]
blocked_by: []
blocks: []
estimated_effort_hours: 12
actual_effort_hours: null
tags: [metrics, DR-resilience, SLO, capacity, KPI]
upstream_files:
  - D:\ZephyrAlpha\docs\03_modules\_cross_layer\feedback-loop\blueprint.md
downstream_outputs:
  - D:\ZephyrAlpha\src\zephyr\feedback_loop\diagnosers\dr_resilience_metrics.py
  - D:\ZephyrAlpha\src\zephyr\feedback_loop\diagnosers\api_dependency_metrics.py
  - D:\ZephyrAlpha\src\zephyr\feedback_loop\diagnosers\slo_capacity_metrics.py
  - D:\ZephyrAlpha\src\zephyr\feedback_loop\diagnosers\fle_self_slo_metrics.py
acceptance_criteria:
  - AC-0027-01: DRResilienceMetrics 实现 RPO/RTO/drill_pass_rate 采集
  - AC-0027-02: APIDependencyMetrics 实现 CVE/license/sunset 追踪
  - AC-0027-03: SLOCapacityMetrics 实现 SLO budget burn rate + time_to_exhaustion
  - AC-0027-04: FLESelfSLO 实现七维SLO（MTTD/MTTR/MTTI/FP_RATE/AVAILABILITY/NET_VALUE/ACTION_HARMFUL）
rollback_instructions: |
  删除本次创建的 metrics 文件
context_assembly_manifest:
  required_contexts:
    - context_id: CTX-BLUEPRINT-§4
      source: D:\ZephyrAlpha\docs\03_modules\_cross_layer\feedback-loop\blueprint.md
      sections: ["§4.1-4.29"]
      description: 完整的指标体系——从DR指标到SLO到容量
  assembly_notes: 指标体系是FLE自我度量的基础。FLESelfSLO (七维SLO) 是 FLE 从"活着"到"用数学证明自己活得好"的转折点。
---

# TASK-MOD-INF-010-0027: 指标体系实现

## 1. 任务目标
实现蓝图 §4 中定义的全部指标数据类和采集逻辑。

## 2. 指标层级
| 层级 | 指标类 | 来源 |
|------|------|------|
| DR层 | DRResilienceMetrics | §4.27 |
| API依赖层 | APIDependencyMetrics | §4.28 |
| SLO层 | SLOCapacityMetrics | §4.29 |
| 自SLO层 | FLESelfSLO (七维) | v0.22.0 |

## 3. 七维自SLO
| 维度 | 缩写 | 目标 |
|------|------|------|
| Mean Time To Detect | MTTD | < 5min |
| Mean Time To Repair | MTTR | < 15min |
| Mean Time To Innocence | MTTI | < 3min |
| False Positive Rate | FP_RATE | < 5% |
| Availability | AVAILABILITY | > 99.9% |
| Net Value | NET_VALUE | > $0/天 |
| Action Harmful Rate | ACTION_HARMFUL | < 1% |
