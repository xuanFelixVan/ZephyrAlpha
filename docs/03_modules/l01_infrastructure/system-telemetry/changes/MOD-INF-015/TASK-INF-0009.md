---
task_id: "TASK-INF-0009"
source_blueprint: "MOD-INF-015"
source_section: "蓝图 §3c 模块集成 DX：统一接入点"

title: "实现 Telemetry 门面类 + Graceful Shutdown：一行接入获得全部九子系统能力"
description: |
  实现统一门面类 Telemetry(module_id)，使各模块一行代码即获得全部九子系统接入能力：
  1. Telemetry 门面类 API：metrics(gauge/counter/histogram/summary)、logs(info/warning/error)、
     traces(span context manager)、ai_behavior(record)、health(register)、shutdown()
  2. Graceful Shutdown：冻结入站→flush ring buffer→关闭连接→注销→emergency_shutdown.jsonl
  3. 内部约束：自动读取 environment、注册 LifecycleManager、注入 TraceContext
  4. 测试模式：Telemetry(test_mode=True) 返回 Mock 版本
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\system-telemetry\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\logging.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\lifecycle\\hooks.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\__init__.py"
    description: "Telemetry 门面类实现——含所有便捷方法 + shutdown()"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\facade.py"
    description: "Telemetry 门面类核心逻辑（如从 __init__.py 抽出）"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\__init__.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\facade.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\system-telemetry\\blueprint.md"
    reason: "§3c——Telemetry 门面类 Python API 完整代码 + Graceful Shutdown 9 步流程 + emergency_shutdown.jsonl 设计 + AI 施工约定（4 条）"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 10000
timeout_minutes: 40

acceptance_criteria:
  - "Telemetry(module_id, environment) 初始化成功"
  - "telemetry.metrics.gauge/counter/histogram/summary 可调用"
  - "telemetry.logs.info/warning/error 可调用"
  - "with telemetry.traces.span(...) as span: 上下文管理器可工作"
  - "telemetry.ai_behavior.record(...) 可调用"
  - "await telemetry.shutdown() 执行完整 9 步 flush 流程"
  - "Telemetry(test_mode=True) 返回 Mock 版本——所有操作 noop"
  - "shutdown 超时 60s，强制退出前写入 emergency_shutdown.jsonl"
  - "启动时检测上次是否正常 shutdown"

rollback_instructions: |
  1. 还原 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\__init__.py 到骨架版本
  2. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\facade.py

depends_on:
  - "TASK-INF-0001"
  - "TASK-INF-0004"
  - "TASK-INF-0008"
blocked_by: []
status: "done"

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

# TASK-INF-0009: 实现 Telemetry 门面类 + Graceful Shutdown

## 目标
实现统一门面类 Telemetry(module_id)，使各模块一行代码获得全部九子系统接入能力，并确保 shutdown 时所有 buffer 中数据不丢失。

## 触发条件
- TASK-INF-0001（目录骨架）、TASK-INF-0004（FeatureFlags）、TASK-INF-0008（shared集成）通过

## 执行步骤

### 读
- 蓝图 §3c：完整 Python API 示例 + Shutdown 9 步流程 + 超时策略 + 应急丢失检测

### 做
1. 实现 Telemetry 门面类：初始化自动读取 environment/config、注册 LifecycleManager、注入 TraceContext、设置默认标签
2. 实现 metrics/logs/traces/ai_behavior/health 子属性代理
3. 实现 shutdown()：9 步 flush 流程 + 60s 总超时 + emergency_shutdown.jsonl
4. 实现 test_mode=True Mock 版本

### 产
- __init__.py（重写）+ facade.py

### 检
```python
telemetry = Telemetry("MOD-TEST", test_mode=True)
telemetry.metrics.counter("test", 1)
await telemetry.shutdown()
```

## 验收标准
| # | 指标 | 目标 |
|---|------|------|
| 1 | api | 全部便捷方法可调用 |
| 2 | shutdown | 9 步流程完整执行 |
| 3 | test_mode | Mock 模式 noop |
| 4 | emergency | emergency_shutdown.jsonl 写入正确 |
