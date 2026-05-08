---
task_id: "TASK-INF-0005"
source_blueprint: "MOD-INF-015"
source_section: "蓝图 §2f OpenTelemetry GenAI + AI Agent 语义约定对齐"

title: "实现 OTel GenAI + AI Agent 语义约定对齐：gen_ai.* 字段映射与 Span 命名规范"
description: |
  对齐 OTel GenAI Semantic Conventions（v1.37+）和 Traceloop/OpenLLMetry AI Agent Observability RFC：
  1. AIBehaviorEvent 字段一对一映射到 gen_ai.* 标准属性（12 项映射）
  2. traces Span 名称遵循 gen_ai.<component>.<operation> 风格（13 种 span 类型）
  3. gen_ai.client.token.usage / gen_ai.client.operation.duration 指标对齐
  4. AI 施工约定：禁止为已有 OTel 标准属性发明替代命名
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\system-telemetry\\blueprint.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\otel_mapping.py"
    description: "OTel 语义映射表：gen_ai.* 属性→Telemetry 字段双向映射 + Span 命名注册表"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\otel_mapping.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\system-telemetry\\blueprint.md"
    reason: "§2f——完整 OTel 属性映射表 + Agent Span 类型 + GenAI Metrics 对齐 + AI 施工约束"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 6000
timeout_minutes: 25

acceptance_criteria:
  - "12 项 OTel GenAI 属性→AIBehaviorEvent 映射全部可查"
  - "13 种 OTel Agent Span 类型→ZephyrAlpha 场景映射全部可查"
  - "gen_ai.client.token.usage / gen_ai.client.operation.duration 指标映射已注册"
  - "禁止为已有 OTel 标准属性发明替代命名的检查已实现"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\otel_mapping.py

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

# TASK-INF-0005: 实现 OTel GenAI + AI Agent 语义约定对齐

## 目标
实现 Telemetry 与 OTel GenAI Semantic Conventions 的完整对齐，确保 AI 行为相关字段命名可一对一映射到 gen_ai.* 属性，Span 名称遵循标准命名规范。

## 触发条件
- TASK-INF-0001 通过

## 执行步骤

### 读
- 蓝图 §2f：OTel GenAI 属性映射表、Agent Span 类型、GenAI Metrics 对齐、AI 施工约定

### 做
1. 创建 otel_mapping.py：双向映射表（OTel↔Telemetry）、Span 命名注册表、指标映射
2. 实现属性命名冲突检测——发现非标准命名时告警

### 产
- otel_mapping.py

### 检
```bash
python -c "from zephyr.l12_system_telemetry.otel_mapping import OTEL_GENAI_ATTRS; assert len(OTEL_GENAI_ATTRS) == 12; print('OK')"
```

## 验收标准
| # | 指标 | 目标 |
|---|------|------|
| 1 | mapping | 12 项属性 + 13 种 Span + 2 个指标全部映射 |
| 2 | build | 可成功 import |
