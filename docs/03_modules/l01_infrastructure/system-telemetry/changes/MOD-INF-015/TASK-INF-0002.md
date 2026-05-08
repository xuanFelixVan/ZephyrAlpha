---
task_id: "TASK-INF-0002"
source_blueprint: "MOD-INF-015"
source_section: "蓝图 §2 四大黄金信号 + §2b USE 信号 + §2c 事件标注"

title: "实现三层信号采集基础设施：Golden Signals + USE Method + Annotations"
description: |
  实现 Google SRE 三层信号采集体系：
  1. 4 Golden Signals（Latency/Errors/Traffic/Saturation）——业务级信号
  2. USE Method（Utilization/Saturation/Errors）——资源层信号
  3. Annotations（部署/配置变更/模型切换/蓝图变更/FeatureFlag变更）——事件时间线标注
  所有信号通过 TelemetryEmitter 契约采集，携带 environment 标签。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\system-telemetry\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\contracts\\telemetry_emitter.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\lifecycle\\hooks.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\metrics\\golden_signals.py"
    description: "4 Golden Signals 采集器：latency_collector / error_tracker / traffic_monitor / saturation_checker"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\metrics\\use_method.py"
    description: "USE Method 采集器：utilization / saturation / resource_errors"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\metrics\\annotations.py"
    description: "事件标注注入器：deploy/config/model/blueprint/featureflag 五类事件"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\metrics\\golden_signals.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\metrics\\use_method.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\metrics\\annotations.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2 强制——信号数据类使用 BaseModel"
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "路径合规创建"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\system-telemetry\\blueprint.md"
    reason: "§2/§2b/§2c——Golden Signals/USE/Annotations 的完整定义和阈值"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\contracts\\telemetry_emitter.py"
    reason: "CTR-P1-013 TelemetryEmitter 契约——信号数据类必须兼容此接口"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 8000
timeout_minutes: 30

acceptance_criteria:
  - "Golden Signaler 4 信号采集（latency/errors/traffic/saturation）全部可调用"
  - "USE Method 3 维度采集（utilization/saturation/errors）全部可调用"
  - "Annotations 5 类事件注入（deploy/config/model/blueprint/flag）全部可调用"
  - "所有信号携带 environment 标签"
  - "所有数据类继承 Pydantic BaseModel"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\metrics\golden_signals.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\metrics\use_method.py
  3. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\metrics\annotations.py

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

# TASK-INF-0002: 实现三层信号采集基础设施

## 目标
实现 Google SRE 三层信号采集体系：业务层 4 Golden Signals、资源层 USE Method、变更事件 Annotations，全部通过 TelemetryEmitter 契约采集并携带 environment 标签。

## 触发条件
- TASK-INF-0001（模块目录骨架）已通过
- shared/contracts/telemetry_emitter.py 可读取

## 执行步骤

### 读
- 蓝图 §2/§2b/§2c：信号定义、维度、阈值
- shared/contracts/telemetry_emitter.py：CTR-P1-013 接口契约

### 做
1. 实现 `golden_signals.py`：LatencyCollector/ErrorTracker/TrafficMonitor/SaturationChecker 四个类
2. 实现 `use_method.py`：UtilizationCollector/SaturationChecker/ResourceErrorDetector 三个类
3. 实现 `annotations.py`：AnnotationInjector 类，支持 deploy/config/model/blueprint/flag 五类事件

### 产
- golden_signals.py / use_method.py / annotations.py

### 检
```bash
python -c "from zephyr.l12_system_telemetry.metrics.golden_signals import LatencyCollector; print('OK')"
```

## 验收标准
| # | 指标 | 目标 |
|---|------|------|
| 1 | build | 三个模块均可成功 import |
| 2 | coverage | 每个 collector 至少 1 个单元测试 |
| 3 | lint | 0 errors |

## 风险与缓解
| 风险 | 缓解 |
|------|------|
| 与 TelemetryEmitter 契约不兼容 | 对照 CTR-P1-013 逐字段验证 |
| 阈值硬编码 | 所有阈值从 config/flags.yaml 读取 |
