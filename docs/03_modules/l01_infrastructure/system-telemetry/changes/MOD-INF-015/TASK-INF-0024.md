---
task_id: "TASK-INF-0024"
source_blueprint: "MOD-INF-015"
source_section: "蓝图 §14 AI 可消费性设计——MCP 工具集 + Session 冷启动工作流 + Metric Discovery API"

title: "实现 AI 可消费性：MCP Server Telemetry × 6 工具 + Session 冷启动一键诊断 + Metric Discovery API"
description: |
  使 AI Agent 能够程序化消费 Telemetry 数据：
  1. MCP Server 6 Tools：
     - get_service_health()→"全绿，LLM响应P50=320ms"
     - get_metrics("module_id", "time_range")→当前指标值
     - get_recent_errors("module_id")→30min 内 errors
     - get_cost_summary()→当日$/token/调用量
     - query_logs("query_filter")→关键词限10条
     - get_dlq_summary()→DLQ各reason分类统计
  2. Session 冷启动一问三连：对连续 2 个 session 活动→自动触发"预热-健康-知识"三问→6 returns
     支持自然语言 query decompose（"性能怎么样"→health+metrics+cost 三问并行）
  3. Metric Discovery API：GET /api/v1/discovery?module=MOD-INF-008→按 module 过滤 / 
     GET /api/v1/discovery?search=llm_calls→全项目搜索 / 
     GET /api/v1/discovery?status=active→活跃指标 / 
     排除 telemetry_meta 前缀指标
  4. AI 施工约束（3 条）：MCP 工具仅读 / 通用 websearch 禁止→internal MCP / 禁止 AI Session 插入遥测数据
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\system-telemetry\\blueprint.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\mcp_tools.py"
    description: "MCP Server 6 工具注册——get_service_health/get_metrics/get_recent_errors/get_cost_summary/query_logs/get_dlq_summary"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\cold_start.py"
    description: "Session 冷启动工作流——自动检测+三问并行+自然语言 decompose"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\mcp_tools.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\cold_start.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\system-telemetry\\blueprint.md"
    reason: "§14——6 MCP Tools 完整定义+示例 + Session 冷启动工作流 + Metric Discovery API 设计 + AI 施工约束(3条)"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 10000
timeout_minutes: 40

acceptance_criteria:
  - "6 MCP 工具均已注册到 MCP Server"
  - "get_service_health() 返回人类可读状态"
  - "连续 2 session 活动→自动触发冷启动三问"
  - "自然语言 '性能怎么样'→health+metrics+cost 并行调用"
  - "Metric Discovery API 支持按 module/search/status 过滤"
  - "telemetry_meta 指标不出现在 Discovery 结果中"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\mcp_tools.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\cold_start.py

depends_on:
  - "TASK-INF-0001"
  - "TASK-INF-0012"
  - "TASK-INF-0021"
blocked_by: []
status: "created"

tags_fn:
  - "observability"
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

# TASK-INF-0024: AI 可消费性实现

## 目标
使 AI Agent 能够程序化消费 Telemetry：6 MCP 工具、Session 冷启动一键诊断、Metric Discovery API。

## 执行步骤

### 读
- 蓝图 §14：MCP Tools 定义 + 冷启动工作流 + Discovery API

### 做
1. mcp_tools.py：注册 6 MCP 工具
2. cold_start.py：连续 session 检测 + 三问并行 + NL decompose

### 产
- mcp_tools.py + cold_start.py

### 检
```python
result = await get_service_health()
assert "全绿" in result
```

## 验收标准
| # | 指标 | 目标 |
|---|------|------|
| 1 | mcp | 6 tools registered |
| 2 | cold_start | auto-detect + 3 parallel |
| 3 | discovery | 3 filter modes |
