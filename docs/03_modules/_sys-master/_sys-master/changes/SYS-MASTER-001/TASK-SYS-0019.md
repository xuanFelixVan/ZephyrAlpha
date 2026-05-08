---
task_id: "TASK-SYS-0019"
source_blueprint: "SYS-MASTER-001"
source_section: "§26 可观测性仪表板 + §27 性能基线 + §89 DORA指标"

title: "可观测性仪表板(4面板:系统健康11SLI/成本/订单流/模型漂移) + 性能基线(200ms→500ms E2E) + DORA 4指标(DF≥1d,LT<1h,CFR<5%,MTTR<1h)体系"
description: |
  将 SYS-MASTER-001 §26 可观测性仪表板 + §27 性能基线 + §89 DORA 指标三合一落地。
  §26 定义 4 个 Grafana 仪表板面板：
  ① 系统健康——11 SLI(CPU/内存/磁盘IO/网络吞吐/上下文长度/Token消耗/决策准确率/状态感知率/知识检索率/反馈采纳率/数据新鲜度)
  ② 成本仪表板——模型人均成本 ③ 订单流——订单耗时 ④ 模型漂移——漂移分数
  §27 性能基线: 行情→信号<200ms / 信号→风控<10ms / 风控→订单<50ms / E2E总<500ms。
  §89 DORA 4 指标目标值: Deployment Frequency≥1次/天 / Lead Time for Changes<1小时 /
  Change Failure Rate<5% / MTTR<1小时。
  本卡搭建 observability_dashboard.py + performance_baseline.py + dora_metrics.py。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\observability_dashboard.py"
    description: "§26 Grafana 4面板——系统健康11SLI/成本/订单流/模型漂移"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\performance_baseline.py"
    description: "§27 3段延迟——行情→信号<200ms/信号→风控<10ms/风控→订单<50ms→E2E<500ms"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\dora_metrics.py"
    description: "§89 DORA 4 metrics——DF≥1d/LT<1h/CFR<5%/MTTR<1h—— collector+report"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\observability_dashboard.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\performance_baseline.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\dora_metrics.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l0*\\**\\*.py"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"
    reason: "§26 4面板(系统健康11SLI/成本/订单流/模型漂移)+§27 3段延迟(E2E<500ms)+§89 DORA 4目标"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 18000
timeout_minutes: 50

acceptance_criteria:
  - "dashboard: 4 panels——system_health(11 SLI)/cost(daily)/order_flow(order_latency_p95)/model_drift(drift_score)"
  - "performance_baseline: market→signal<200ms / signal→risk<10ms / risk→order<50ms / total E2E<500ms"
  - "dora_metrics: DF≥1day/LT<1h/CFR<5%/MTTR<1h——quarter trend report"

rollback_instructions: |
  git rm src/zephyr/governance/observability_dashboard.py performance_baseline.py dora_metrics.py
  从 script_manifest.yaml 移除注册

depends_on:
  - "TASK-SYS-0002"
blocked_by: []
status: "done"
tags_fn:
  - "ops"
tags_ly: "cross_layer"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "SYS-MASTER-001"
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
