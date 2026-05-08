---
task_id: "TASK-MST-0013"
source_blueprint: "MOD-MASTER-001"
source_section: "蓝图 §十四 标准化 HealthCheck 三态探针协议——CT-HEALTH-001"

title: "实现 12 系统标准化三态 HealthCheck 探针协议(CT-HEALTH-001)"
description: |
  实现 §十四 定义的标准化 HealthCheck 三态探针协议：
  liveness(存活探针)——GET /_health/{system}/livez——仅检查主线程心跳；
  readiness(就绪探针)——GET /_health/{system}/readyz——检查依赖+初始化完成；
  degraded(降级探针)——GET /_health/{system}/healthz——慢/部分功能缺失检测。
  每个系统暴露独立的三态探针端点。Telemetry 作为 aggregator 每 15s 轮询所有端点。
  Per-system 特殊规则：(1)Orc 待调度队列>100→degraded；(2)CE Token预算>7200→degraded；
  (3)LSG 无 degraded 路径(fail-closed)；(4)db WAL checkpoint 延迟>5s→degraded。
  年度健康审计：计算 uptime_ratio/mean_time_to_recovery/degradation_ratio_per_system。

priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\telemetry\\health_probes.py"
    description: "三态探针协议——12系统 liveness/readiness/degraded 统一端点"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\telemetry\\health_aggregator.py"
    description: "健康聚合器——每15s轮询12系统探针→生成健康面板"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_health_probes.py"
    description: "HealthCheck 探针单元测试"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_health_aggregator.py"
    description: "健康聚合器单元测试"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\telemetry\\health_probes.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\telemetry\\health_aggregator.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_health_probes.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_health_aggregator.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\**\\circuit_breaker*"

applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "任务卡编号格式"
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "路径架构合规创建"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"
    reason: "§十四——CT-HEALTH-001 三态探针完整定义 + 各系统特殊规则表 + 年度审计"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 15000
timeout_minutes: 60

acceptance_criteria:
  - "health_probes.py 为 12 个系统各自实现 livez/readyz/healthz 三态端点"
  - "GET /_health/{system}/livez → 200 {status:'alive', pid, uptime_s}"
  - "GET /_health/{system}/readyz → 200 {status:'ready', dependencies:{dep:'ok'|'degraded'|'down'}}"
  - "GET /_health/{system}/healthz → 200 + X-Degraded: true/false"
  - "health_aggregator.py 每 15s 轮询并生成健康面板 → liveness 连续 3 次 FAIL=ALERT"
  - "各系统特殊 degraded 条件: CE Token>7200、Orc queue>100、LSG fail-closed 无degraded"
  - "Pydantic V2 BaseModel 实现"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\telemetry\health_probes.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\telemetry\health_aggregator.py
  3. 删除新增的测试文件

depends_on: []
blocked_by: []

status: "done"

tags_fn:
  - "infra"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-MASTER-001"

completed_gates: []
blocked_gates: {}

artifact_paths: []
audit_findings: []
ke_entries: []

ai_autonomy_level: "supervised"
autonomy_checklist: []
---
