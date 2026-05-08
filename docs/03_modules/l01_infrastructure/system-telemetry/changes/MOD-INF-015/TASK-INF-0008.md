---
task_id: "TASK-INF-0008"
source_blueprint: "MOD-INF-015"
source_section: "蓝图 §3b 与 shared 基础设施的对接映射表"

title: "实现 Telemetry 与 shared 基础设施对接：复用清单落地 + 新建组件边界明确"
description: |
  将蓝图 §3b 的复用/新建清单落地为代码：
  1. 复用层：确保 Telemetry 各子系统正确使用 shared/logging(TraceContext+get_logger)、shared/lifecycle(LifecycleAware)、
     shared/flags(FeatureFlag)、shared/observer(EventBus)、shared/contracts/backpressure(Throttle/Pause/Resume)、
     shared/contracts/telemetry_emitter(CTR-P1-013)、shared/contracts/trace_context(CTR-TRACE-001)
  2. 新建层：明确 Telemetry 独有组件的边界——MetricPoint/JSONLFileWriter/Span/AIBehaviorEvent/SchemaRegistry/BurnRateAlerts/Watchdog/ProfileCollector
  3. AI 施工约束：MUST 使用 shared 组件，禁止定义第二个 TraceContext
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\system-telemetry\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\logging.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\lifecycle\\hooks.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\flags.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\observer.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\contracts\\telemetry_emitter.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\contracts\\trace_context.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\contracts\\backpressure\\"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\shared_integration.py"
    description: "shared 基础设施集成检查器——验证 Telemetry 是否正确使用 shared 组件，检测重复造轮子"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\shared_integration.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\system-telemetry\\blueprint.md"
    reason: "§3b——复用清单（8 项 shared 组件 + AI 施工约束）+ 新建清单（8 项独有组件）"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 6000
timeout_minutes: 25

acceptance_criteria:
  - "shared_integration 可检测：是否使用了 shared.logging.TraceContext（非自定义）"
  - "shared_integration 可检测：是否正确使用 LifecycleManager.health_check()（非自探测）"
  - "shared_integration 可检测：Backpressure 信号发送顺序（THROTTLE→PAUSE→丢弃）"
  - "新建组件清单作为运行时 whitelist 检查"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\shared_integration.py

depends_on:
  - "TASK-INF-0001"
blocked_by: []
status: "created"

tags_fn:
  - "observability"
  - "infra"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-015"

completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---

# TASK-INF-0008: 实现 Telemetry 与 shared 基础设施对接

## 目标
确保 Telemetry 正确复用 shared/ 基础设施组件，不重复造轮子；明确新建组件的边界和责任。

## 触发条件
- TASK-INF-0001 通过
- shared/ 下所有被引用组件存在

## 执行步骤

### 读
- 蓝图 §3b：复用清单（8 项 + AI 施工约束）+ 新建清单（8 项）
- 所有被引用的 shared/ 源文件

### 做
1. 创建 shared_integration.py：集成检查器——验证 shared 组件使用正确性
2. 实现"禁止重定义 TraceContext"的运行时检查
3. 实现 Backpressure 信号顺序校验

### 产
- shared_integration.py

### 检
```bash
python -c "from zephyr.l12_system_telemetry.shared_integration import verify_shared_usage; verify_shared_usage(); print('OK')"
```

## 验收标准
| # | 指标 | 目标 |
|---|------|------|
| 1 | check | TraceContext 非重复定义 |
| 2 | check | Backpressure 顺序正确 |
| 3 | check | lifecycle 使用正确 |
