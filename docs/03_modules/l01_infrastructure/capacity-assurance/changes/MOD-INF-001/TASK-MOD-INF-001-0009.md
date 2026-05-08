---


task_id: TASK-MOD-INF-001-0009
module_id: MOD-INF-001
title: "SLI 注册表实现：CAP-001 至 CAP-008（扩容至 ≥8 个 SLI + 插桩点）"
doc_type: task_card
status: done
priority: P0
layer: L01
layer_name: infrastructure
functional_domain: observability
owner: ZephyrAlpha-Owner
assignee: AI-GLM-5.1
created_by: AI-GLM-5.1
created_at: 2026-05-07T03:00:00+08:00
valid_from: 2026-05-07
ttl: permanent
belongs_to: MOD-INF-001
dependencies:
  - TASK-MOD-INF-001-0001
  - TASK-MOD-INF-001-0005
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\capacity-assurance\\blueprint.md"
downstream_outputs:
  - "D:\\ZephyrAlpha\\config\\capacity\\capacity_slo.yaml"
  - "D:\\ZephyrAlpha\\src\\zephyr\\capacity_assurance\\sli_instrumentation.py"
acceptance_criteria:
  - "capacity_slo.yaml 包含全部 13 个 SLI（CAP-001~CAP-014）的完整定义"
  - "每个 SLI 含: id, name, metric, target, window, severity, burn_rate_thresholds（CAP-010~CAP-014 为盲点派生SLI，结构含 description/target/instrumentation）"
  - "sli_instrumentation.py 提供 SLIInstrumentation 类，含插桩采集 + v2.2.0 扩展插桩点"
  - "v2.2.0 新增插桩点：capacity_assurance_insert_time, capacity_assurance_correction_latency, contract_bus_validation_time"
  - "SLO 窗口分层 fast/medium/slow cycle 在 YAML 中结构体现"
rollback_instructions:
  - "git checkout -- config/capacity/capacity_slo.yaml"
  - "删除 sli_instrumentation.py"
context_assembly_manifest:
  - source: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\capacity-assurance\\blueprint.md"
    sections: ["§13 SLI 注册表 L614-673", "§20 #5 SLI 数量验证", "§20.v2.2.0 插桩点扩展 L1123-1164", "§20.v2.2.0 SLO 窗口分层 L1176-1194", "§21.1 盲点#17 CAP-010 context-injection-size", "§21.1 盲点#18 CAP-011 spiral-detection-rate", "§21.2 盲点#20 CAP-012 write-buffer-lag", "§22 盲点#35 CAP-013 handle-count", "§23.5 盲点#41 CAP-014 vibe-experiment-count"]
    purpose: "提取全部 13 个 SLI 定义和 v2.2.0 插桩点扩展"
tags:
  - capacity-assurance
  - sli-registry
  - CAP-001-to-CAP-014
phase: phase_1_scaffold
estimated_effort_minutes: 90
ai_autonomy: AI-Modifiable
governance_layer: GOV-P1
runtime_plane: RP-3
source_blueprint: "MOD-INF-001"
source_section: "蓝图 §13 + §21 + §22 + §23 SLI Registry CAP-001~CAP-014"
description: "SLI 注册表实现：CAP-001 至 CAP-014（13 个 SLI + 插桩点）"
allowed_touch:
  - "D:\\ZephyrAlpha\\config\\capacity\\capacity_slo.yaml"
  - "D:\\ZephyrAlpha\\src\\zephyr\\capacity_assurance\\sli_instrumentation.py"
forbidden_touch:
  - "D:\ZephyrAlpha\docs\01_policies_and_standards\**\*.md"
  - "D:\ZephyrAlpha\src\zephyr\shared\schemas.py"
applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "任务卡编号格式 TASK-{DOMAIN}-{NNNN}"
  - module_id: "PS-STD-011"
  - module_id: "ADR-0040"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 27000
timeout_minutes: 90
depends_on:
  - TASK-MOD-INF-001-0001
  - TASK-MOD-INF-001-0005
blocked_by: []
tags_fn: ["infra"]
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo: ["MOD-INF-001"]
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []


---



# SLI 注册表实现：CAP-001 至 CAP-014（13 个 SLI + 插桩点）

## 1. 任务来源

从蓝图 §13 SLI 注册表提取，含 v2.2.0 插桩点扩展和 v2.2.0 SLO 窗口分层，以及 §21-§23 盲点审计中派生的 5 个 SLI（CAP-010~CAP-014）。

**基线 13 个 SLI（CAP-001~CAP-014）：**

| SLI ID | 名称 | 指标 | 目标 |
|--------|------|------|------|
| CAP-001 | AI 审计覆盖完整率 | 有 Provenance 记录的修改 / 总修改 | ≥ 99.9% |
| CAP-002 | 容量 SLO 达标率 | 达标窗口 / 总窗口 | ≥ 99.5% |
| CAP-003 | ContractBus 校验通过率 | 通过校验的契约传输 / 总传输 | ≥ 99.9% |
| CAP-004 | Kill Switch 响应时间 | Kill Switch 触发到生效的时间 | ≤ 5s |
| CAP-005 | Token Budget 准确性 | 预估 tokens / 实际 tokens | ±10% |
| CAP-006 | Sandbox 隔离有效性 | 沙箱进程外溢事件 / 总执行 | 0 |
| CAP-007 | Error Budget 消耗告警准确率 | 有效告警 / 总告警 | ≥ 95% |
| CAP-008 | Graceful Degradation 切换时间 | 降级触发到新模型生效时间 | ≤ 2s |
| CAP-010 | 上下文注入大小 | AI session 启动注入的上下文 token 数 | ≤ 32000 |
| CAP-011 | 退化螺旋检测率 | 同一任务连续门禁驳回 ≥3 次/周 | < 1/week |
| CAP-012 | 写入缓冲延迟 | 容量指标写入缓冲刷新延迟 P99 | ≤ 100ms |
| CAP-013 | 文件句柄数 | 进程打开文件句柄数 | warn>400 critical>500 |
| CAP-014 | 氛围编程实验计数 | 每日 vibe 实验 token/文件/时长追踪 | 日上限告警 |

## 2. 施工内容

### 2.1 创建 / 更新 capacity_slo.yaml

创建 `D:\ZephyrAlpha\config\capacity\capacity_slo.yaml`，包含完整 SLI 定义：

```yaml
version: "2.6.0"
module_id: MOD-INF-001
slis:
  - id: CAP-001
    name: "AI 审计覆盖完整率"
    metric: "ai_provenance_coverage_ratio"
    target: 0.999
    window: "7d"
    severity: critical
    burn_rate_thresholds:
      fast_cycle: {threshold: 14.4, window: "1h"}
      medium_cycle: {threshold: 6.0, window: "6h"}
      slow_cycle: {threshold: 3.0, window: "24h"}
    instrumentation:
      enabled: true
      insert_timing: true
      correction_latency: true
      
  - id: CAP-002
    name: "容量 SLO 达标率"
    metric: "capacity_slo_attainment_ratio"
    target: 0.995
    window: "7d"
    severity: critical
    burn_rate_thresholds:
      fast_cycle: {threshold: 14.4, window: "1h"}
      medium_cycle: {threshold: 3.0, window: "6h"}
      slow_cycle: {threshold: 1.0, window: "24h"}
    instrumentation:
      enabled: true

  - id: CAP-003
    name: "ContractBus 校验通过率"
    metric: "contract_bus_validation_ratio"
    target: 0.999
    window: "30d"
    severity: high
    burn_rate_thresholds:
      fast_cycle: {threshold: 14.4, window: "1h"}
      medium_cycle: {threshold: 6.0, window: "6h"}
    instrumentation:
      enabled: true
      validation_timing: true

  - id: CAP-004
    name: "Kill Switch 响应时间"
    metric: "kill_switch_response_seconds"
    target: 5.0
    window: "30d"
    severity: critical
    instrumentation:
      enabled: true

  - id: CAP-005
    name: "Token Budget 准确性"
    metric: "token_budget_accuracy_ratio"
    target: 0.1
    window: "7d"
    severity: high
    instrumentation:
      enabled: true

  - id: CAP-006
    name: "Sandbox 隔离有效性"
    metric: "sandbox_breach_count"
    target: 0
    window: "30d"
    severity: critical
    instrumentation:
      enabled: true

  - id: CAP-007
    name: "Error Budget 消耗告警准确率"
    metric: "error_budget_alert_accuracy"
    target: 0.95
    window: "30d"
    severity: medium
    instrumentation:
      enabled: true

  - id: CAP-008
    name: "Graceful Degradation 切换时间"
    metric: "degradation_switch_seconds"
    target: 2.0
    window: "30d"
    severity: high
    instrumentation:
      enabled: true

  - id: CAP-010-context-injection-size
    description: "每次 AI session 启动注入的上下文 token 数"
    target: 32000
    instrumentation:
      hook_point: "context_engine.ContextInjector.inject.exit"
      measurement: "token_counter on assembled context string"
      aggregation: "p50 + p99"
    degradation_alert: "p50 > 40000 for 3 consecutive sessions"

  - id: CAP-011-spiral-detection-rate
    description: "退化螺旋检测——同一任务连续门禁驳回 ≥3 次的事件率"
    target: "< 1 / week"
    instrumentation:
      hook_point: "DegradationSpiralDetector.detect.exit"
      measurement: "events per week"
      aggregation: "count"
    critical_threshold: "> 3 / week"
    critical_action: "auto_trigger_blueprint_audit + notify_owner"

  - id: CAP-012-write-buffer-lag
    description: "容量指标写入缓冲刷新延迟 P99"
    target: 100
    instrumentation:
      hook_point: "MetricsWriteBuffer._flush.exit"
      measurement: "elapsed_ms"
      aggregation: "p99"
    critical_threshold: "p99 > 500"
    critical_action: "reduce_flush_frequency + suggest_sqlite_vacuum"

  - id: CAP-013-handle-count
    description: "进程打开文件句柄数——防范 Windows 默认 512 上限"
    measurement: "len(psutil.Process().open_files())"
    warning: "> 400"
    critical: "> 500"
    critical_action: "auto_increase_setmaxstdio + notify_owner"

  - id: CAP-014-vibe-experiment-count
    description: "氛围编程快速实验的容量消耗追踪"
    track: ["token_used", "files_created", "duration_seconds", "owner_kept"]
    weekly_report: true
    alert_if: "daily_limit_exceeded"

windows:
  fast_cycle:
    intervals: ["1h", "6h"]
    burn_rate_multiplier: 14.4
  medium_cycle:
    intervals: ["24h", "7d"]
    burn_rate_multiplier: 6.0
  slow_cycle:
    intervals: ["28d"]
    burn_rate_multiplier: 3.0
```

### 2.2 创建 sli_instrumentation.py

创建 `D:\ZephyrAlpha\src\\zephyr\\shared\\sli_instrumentation.py`，实现 `SLIInstrumentation` 类：
- `record_insert_timing(sli_id, duration_ms)`: 记录写入耗时（盲点 #4 插桩点）
- `record_correction_latency(sli_id, duration_ms)`: 记录修正延迟（盲点 #4 插桩点）
- `record_validation_timing(sli_id, duration_ms)`: 记录校验耗时
- `get_sli_stats(sli_id) -> SLIStats`: 获取统计信息

## 3. 验收标准

1. `capacity_slo.yaml` 通过 Pydantic v2 Schema 校验
2. 13 个 SLI 定义完整（CAP-001~CAP-008 含 id/name/metric/target/window/severity/burn_rate_thresholds；CAP-010~CAP-014 含 description/target/instrumentation）
3. `sli_instrumentation.py` 插桩方法可正常采集
4. SLO 窗口分层 fast/medium/slow cycle 结构正确