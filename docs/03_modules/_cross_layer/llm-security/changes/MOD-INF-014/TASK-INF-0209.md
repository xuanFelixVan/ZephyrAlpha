---
task_id: "TASK-INF-0209"
source_blueprint: "MOD-INF-014"
source_section: "§9 L6 + §36 Promptware + §51 侧信道"
title: "L6 可观测性层完整实现——安全事件日志+异常检测+告警+仪表板+审计报告+Promptware追踪+侧信道防御"
description: |
  实现 ObservabilityLayer整合现有 behavior_audit_logger.py: 8种新安全事件类型(PROMPT_BLOCKED/LEAK_DETECTED等)、
  频率异常检测(EMA基线+2σ)、Webhook告警(CRITICAL/WARNING/INFO三级)、DashboardMetrics汇总供Streamlit、
  日报/周报自动生成、Promptware Kill Chain 7阶段轨迹追踪、Side-Channel Defense(流量填充+时序噪声+审计)。
priority: "P1"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\llm-security\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\behavior_audit_logger.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\protocol.py"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\layers\\l6_observability.py"
    description: "L6 ObservabilityLayer——事件+异常+告警+仪表板+报告+Promptware+侧信道"
  - path: "D:\\ZephyrAlpha\\tests\\llm_security\\test_l6_observability.py"
    description: "L6 可观测性单元测试——10条用例"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\layers\\l6_observability.py"
  - "D:\\ZephyrAlpha\\tests\\llm_security\\test_l6_observability.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\behavior_audit_logger.py"
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\_cross_layer\\llm-security\\blueprint.md"
    reason: "§9+§36+§51"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1","M3"]
estimated_tokens: 12000
timeout_minutes: 60
acceptance_criteria:
  - "ObservabilityLayer 含 log_security_event/detect_frequency_anomaly/send_alert/collect_metrics/generate_daily_report/generate_weekly_report 6个方法"
  - "9 种新 SecurityEventType 枚举值: PROMPT_BLOCKED/LEAK_DETECTED/SENSITIVE_REDACTED/HALLUCINATION_DETECTED/AGENT_PERMISSION_DENIED/HITL_APPROVAL/BUDGET_EXCEEDED/CIRCUIT_BREAKER_TRIPPED/ANOMALY_DETECTED"
  - "detect_frequency_anomaly() 使用 EMA baseline + 2σ 阈值"
  - "send_alert() Webhook POST 含 payload: severity/timestamp/module/event_type/message"
  - "DashboardMetrics Pydantic V2 model 含12字段"
  - "日报/周报含事件统计+趋势分析+TOP告警+X天对比"
  - "PromptwareKillChainTracker: trajectory_store + 深搜索 Prompt 样本 + Stage 0-7定义"
  - "SideChannelDefender: traffic_padding + timing_noise + side_channel_audit"
  - "10条单元测试全部通过"
rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\llm_security\layers\l6_observability.py
  2. 删除 D:\ZephyrAlpha\tests\llm_security\test_l6_observability.py
depends_on: ["TASK-INF-0201"]
blocked_by: []
status: "done"
tags_fn: ["security","observability"]
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo: ["MOD-INF-014"]
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---

# 目标

实现 L6 可观测性层——LSG 自身的运维安全可见性。整合行为审计日志，新增 8 类安全事件，实现异常检测和告警。

## 触发条件
- TASK-INF-0201 已通过

## 执行步骤

### 读
- `D:\ZephyrAlpha\docs\03_modules\_cross_layer\llm-security\blueprint.md` §9+§36+§51
- `D:\ZephyrAlpha\src\zephyr\llm_security\behavior_audit_logger.py`

### 做
1. 实现 ObservabilityLayer 整合现有 behavior_audit_logger
2. 扩展 SecurityEventType 枚举
3. 实现异常检测+告警+指标收集+报告生成
4. 实现 Promptware Kill Chain 追踪 + 侧信道防御
5. 编写 10 条单元测试

### 产
- `l6_observability.py` / `test_l6_observability.py`

### 检
```bash
pytest tests/llm_security/test_l6_observability.py -v
```
