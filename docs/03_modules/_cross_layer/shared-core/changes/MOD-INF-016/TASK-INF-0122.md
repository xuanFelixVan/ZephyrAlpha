---
task_id: "TASK-INF-0122"
source_blueprint: "MOD-INF-016"
source_section: "蓝图 §16 AD-003"

title: "AD-003 实现——Resilience 纯内存运行架构（M5）：遥测 = 指标 + 审计轨 + 健康状态"
description: |
  按 AD-003 决策——Resilience（退避/熔断/回退）完全纯内存运行。
  不依赖 Redis/DB 或外部存储——遥测仅积累三要素：指标（Prometheus 风格 push metrics）、
  审计轨迹（SessionAuditTrail）、健康状态（CircuitState open/half-open/closed）。
  实现要求：
  1. retry.py/circuit_breaker.py/fallback.py 不引入任何 DB 依赖。
  2. metrics 推送器——每 60s 推一批指标到 Prometheus pushgateway（或无外部监控则 stdout）。
  3. 健康状态——CircuitBrain.health() 返回 OPEN/HALF_OPEN/CLOSED JSON（-1=CRASH）。
  4. 红线规则——任何 Resilience 模块 commit 包含 DB import（sqlite3/sqlalchemy/redis）即 fail CI。
  5. 在 CI 中增加 resilience_check——run retry.py / circuit_breaker.py / fallback.py 纯内存单元测试。
  专业对标：Netflix Hystrix PtTracker / Resilience4j Metrics / Prometheus Pushgateway。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\retry.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\circuit_breaker.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\fallback.py"

downstream_outputs:
  - path: "D:\ZephyrAlpha\src\zephyr\feedback_loop\diagnosers\dr_resilience_metrics.py"
    description: "ResilienceMetrics——Prometheus 指标推送器 + health() 状态 Query"
  - path: "D:\\ZephyrAlpha\\scripts\\governance\\check_resilience_db.py"
    description: "CI check——扫描 Resilience 4 文件，禁止 DB import"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_resilience_metrics.py"
    description: "单元测试——验证 metrics 推送、health JSON 输出"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\resilience_metrics.py"
  - "D:\\ZephyrAlpha\\scripts\\governance\\check_resilience_db.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_resilience_metrics.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\__init__.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\SHARED-QUICKREF.yml"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\retry.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\circuit_breaker.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\fallback.py"

applicable_rules:
  - module_id: "GOV-DOC-002"
    section: "§5.5"
    reason: "shared/ 准入规则——resilience_metrics 被 CI + M5 共享"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
    reason: "本蓝图 §16——AD-003 决策上下文与红线规则"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\circuit_breaker.py"
    reason: "circuit_breaker.py——AD-003 纯内存的核心 Circuit 状态机"

assigned_model: "glm-5.1"
assigned_pipeline: "B"
pipeline_modules:
  - "M3"
estimated_tokens: 10000
timeout_minutes: 25

acceptance_criteria:
  - "resilience_metrics.py: CircuitBrain.health() 返回 OPEN/HALF_OPEN/CLOSED JSON（-1=CRASH）"
  - "resilience_metrics.py: push_metrics() 每 60s 推 metrics 到 stdout（可选 Prometheus）"
  - "check_resilience_db.py 扫描 retry.py/circuit_breaker.py/fallback.py/structured_fallback.py——阻止 DB import"
  - "pytest tests/unit/test_resilience_metrics.py -v 全部通过"
  - "CI/CD 中 resilience_check 无 DB 依赖——MUST 全内存运行"
  - "SHARED-QUICKREF.yml 更新——新增 resilience_metrics 入口"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\shared\resilience_metrics.py
  2. 删除 D:\ZephyrAlpha\scripts\governance\check_resilience_db.py
  3. 删除 D:\ZephyrAlpha\tests\unit\test_resilience_metrics.py
  4. 还原 __init__.py 导出
  5. 还原 SHARED-QUICKREF.yml 对应条目

depends_on: ["TASK-INF-0110"]
blocked_by: []

status: "done"

tags_fn:
  - "infra"
tags_ly: "cross_layer"
tags_md: "glm-5.1"
tags_st: "active"
tags_mo:
  - "MOD-INF-016"

completed_gates: []
blocked_gates: {}

artifact_paths: []

audit_findings: []

ke_entries: []

ai_autonomy_level: "supervised"
autonomy_checklist: []
---
