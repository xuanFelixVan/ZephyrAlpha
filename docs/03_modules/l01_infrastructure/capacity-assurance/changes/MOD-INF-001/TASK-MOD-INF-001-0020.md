---

task_id: TASK-MOD-INF-001-0020
module_id: MOD-INF-001
title: "YAML 配置文件创建：Error Budget、Token Budget、Sandbox、Degradation Chain 配置真源"
doc_type: task_card
status: done
priority: P0
layer: L01
layer_name: infrastructure
functional_domain: observability
owner: ZephyrAlpha-Owner
assignee: AI-GLM-5.1
created_by: AI-GLM-5.1
created_at: 2026-05-07T03:05:30+08:00
valid_from: 2026-05-07
ttl: permanent
belongs_to: MOD-INF-001
dependencies:
  - TASK-MOD-INF-001-0001
  - TASK-MOD-INF-001-0005
  - TASK-MOD-INF-001-0009
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\capacity-assurance\\blueprint.md"
  - "D:\\ZephyrAlpha\\config\\capacity\\capacity_slo.yaml"
downstream_outputs:
  - "D:\\ZephyrAlpha\\config\\capacity\\error_budget_config.yaml"
  - "D:\\ZephyrAlpha\\config\\capacity\\token_budget.yaml"
  - "D:\\ZephyrAlpha\\config\\capacity\\sandbox_policy.yaml"
  - "D:\\ZephyrAlpha\\config\\capacity\\degradation_chain.yaml"
acceptance_criteria:
  - "error_budget_config.yaml 定义五级响应 L0-L4 的阈值、动作、Burn Rate 多窗口参数"
  - "token_budget.yaml 定义四级限流 L0(全局)→L1(模块)→L2(代理)→L3(模型) 的令牌桶参数"
  - "sandbox_policy.yaml 定义子进程资源限制（CPU/内存/磁盘/超时）和命名空间隔离策略"
  - "degradation_chain.yaml 定义模型降级链、双向切换条件、渐进式切换速率参数"
  - "全部 4 个配置文件通过 Pydantic v2 Schema 校验"
rollback_instructions:
  - "删除 4 个 YAML 文件回滚到空白配置"
context_assembly_manifest:
  - source: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\capacity-assurance\\blueprint.md"
    sections: ["§8 Error Budget 五级响应 L340-431", "§9 Token Budget 四级限流 L433-465", "§10 Kill Switch + Sandbox L467-516", "§11 Graceful Degradation + 语义缓存 L518-552", "v2.2.0 Kill Switch 联动修正 L1268-1287"]
    purpose: "提取全部配置参数和阈值定义"
tags:
  - capacity-assurance
  - yaml-config
  - error-budget
  - token-budget
  - sandbox
  - degradation-chain
phase: phase_1_scaffold
estimated_effort_minutes: 60
ai_autonomy: AI-Modifiable
governance_layer: GOV-P1
runtime_plane: RP-3

source_blueprint: "MOD-INF-001"
source_section: "蓝图 §8-§11 YAML配置文件"
description: "YAML 配置文件创建：Error Budget、Token Budget、Sandbox、Degradation Chain 配置真源"
allowed_touch:
  - "D:\\ZephyrAlpha\\config\\capacity\\error_budget_config.yaml"
  - "D:\\ZephyrAlpha\\config\\capacity\\token_budget.yaml"
  - "D:\\ZephyrAlpha\\config\\capacity\\sandbox_policy.yaml"
  - "D:\\ZephyrAlpha\\config\\capacity\\degradation_chain.yaml"
forbidden_touch:
  - "D:\ZephyrAlpha\docs\01_policies_and_standards\**\*.md"
  - "D:\ZephyrAlpha\src\zephyr\shared\schemas.py"
applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "任务卡编号格式"
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "路径架构合规创建"
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 18000
timeout_minutes: 60
depends_on:
  - TASK-MOD-INF-001-0001
  - TASK-MOD-INF-001-0005
  - TASK-MOD-INF-001-0009
blocked_by: []
status: done
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


# YAML 配置文件创建：Error Budget、Token Budget、Sandbox、Degradation Chain 配置真源

## 1. 任务来源

从蓝图 §8 Error Budget、§9 Token Budget、§10 Kill Switch + Sandbox、§11 Graceful Degradation 提取四类核心配置参数。

## 2. 施工内容

### 2.1 error_budget_config.yaml

创建 `D:\ZephyrAlpha\config\capacity\error_budget_config.yaml`：

```yaml
version: "2.6.0"
error_budget:
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

  response_tiers:
    - tier: L0 (GREEN)
      burn_rate_range: [0, 1.0)
      action: "指标仪表板更新"
      notification_channel: "metrics_dashboard"
      auto_recovery: true
    
    - tier: L1 (YELLOW)
      burn_rate_range: [1.0, 3.0)
      action: "模块日志告警 + 频率限制建议"
      notification_channel: "module_logs"
      auto_recovery: true
    
    - tier: L2 (ORANGE)
      burn_rate_range: [3.0, 6.0)
      action: "AI 代理工作区通知 + Token Budget 收紧"
      notification_channel: "ai_workspace"
      auto_recovery: false
      escalation_timeout_minutes: 30
    
    - tier: L3 (RED)
      burn_rate_range: [6.0, 14.4)
      action: "模型路由切换 + 全局通知"
      notification_channel: "global_notification"
      auto_recovery: false
      triggers: ["CT-1 模型路由切换"]
      escalation_timeout_minutes: 15
    
    - tier: L4 (BLACK)
      burn_rate_range: [14.4, inf)
      action: "全平台通知 + Kill Switch 触发"
      notification_channel: "platform_wide"
      auto_recovery: false
      triggers: ["Kill Switch"]

  burn_rate_calculation:
    formula: "burn_rate = (error_ratio / (1 - slo_target)) * (alert_window / evaluation_window)"
    
  conservation:
    max_budget_consumption_pct: 100.0
    min_budget_remaining_pct: 0.0
    invariant_check: "|累计消耗 - Σ(分窗口消耗)| ≤ 1%"
```

### 2.2 token_budget.yaml

创建 `D:\ZephyrAlpha\config\capacity\token_budget.yaml`：

```yaml
version: "2.6.0"
token_budget:
  levels:
    - level: L0 (GLOBAL)
      budget_id: "global_total"
      tokens_per_window: 10000000
      window_size_seconds: 86400
      algorithm: "token_bucket"
      burst_ratio: 1.5
    
    - level: L1 (MODULE)
      budget_id_pattern: "module_{module_id}"
      tokens_per_window: 1000000
      window_size_seconds: 86400
      algorithm: "token_bucket"
    
    - level: L2 (AGENT)
      budget_id_pattern: "agent_{agent_id}"
      tokens_per_window: 100000
      window_size_seconds: 3600
      algorithm: "sliding_window"
    
    - level: L3 (MODEL)
      budget_id_pattern: "model_{model_name}"
      tokens_per_window: 500000
      window_size_seconds: 3600
      algorithm: "token_bucket"
      cost_tracking: true

  preflight_estimation:
    enabled: true
    algorithm: "heuristic + linear_regression"
    calibration_window: 1000

  cycle_reset:
    modes: ["sliding_window", "natural_cycle"]
    natural_cycles: ["hour", "day", "week"]
```

### 2.3 sandbox_policy.yaml

创建 `D:\ZephyrAlpha\config\capacity\sandbox_policy.yaml`：

```yaml
version: "2.6.0"
sandbox:
  isolation:
    namespace_pattern: "CAP-SANDBOX-NS-{module}-{agent_id}"
    process_isolation: "subprocess"
    
  resource_limits:
    cpu:
      max_time_seconds: 300
      max_percent: 50
    memory:
      max_mb: 512
      swap_mb: 0
    disk:
      max_mb: 100
      read_only_paths: ["/system", "/config"]
    network:
      allowed: false
      
  timeout:
    hard_timeout_seconds: 600
    kill_signal: "SIGKILL"
    
  policy_lifecycle:
    valid_state_transitions:
      draft: [active]
      active: [deprecated]
      deprecated: [archived]
    states: ["draft", "active", "deprecated", "archived"]
    
  modes:
    - mode: STRICT
      description: "完全隔离执行"
    - mode: REPORT_ONLY
      description: "执行不隔离，记录行为日志"
```

### 2.4 degradation_chain.yaml

创建 `D:\ZephyrAlpha\config\capacity\degradation_chain.yaml`：

```yaml
version: "2.6.0"
degradation:
  chain:
    - level: 0 (PRIMARY)
      model: "GLM-5.1"
      provider: "zhipu"
      
    - level: 1 (FALLBACK_A)
      model: "GLM-4-Flash"
      provider: "zhipu"
      trigger: "连续 2 个窗口异常 (OR)"
      
    - level: 2 (FALLBACK_B)
      model: "DeepSeek-V4-Pro"
      provider: "deepseek"
      trigger: "L2 fallback 同样异常"
      
    - level: 3 (LOCAL)
      model: "quantized-7B-gguf"
      provider: "local"
      trigger: "远程均不可用"

  bidirectional_switch:
    degrade_trigger:
      condition: "连续 2 个窗口异常 (OR 逻辑)"
      metric: "error_rate / latency / availability"
    restore_trigger:
      condition: "连续 3 个窗口正常 (AND 逻辑)"
      metric: "全部指标合格"

  output_truncation:
    max_tokens: 2048
    truncation_strategy: "intelligent (段落边界)"
    
  progressive_switch:
    enabled: true
    default_rate_pct_per_second: 5
    max_switch_duration_seconds: 60
```

## 3. 验收标准

1. 4 个配置文件全部通过 Pydantic v2 Schema 校验
2. `error_budget_engine.py` 加载 error_budget_config.yaml 后五级阈值计算正确
3. `token_budget_engine.py` 加载 token_budget.yaml 后四级预算正确
4. `sandbox_manager.py` 加载 sandbox_policy.yaml 后资源限制生效
5. `degradation_manager.py` 加载 degradation_chain.yaml 后降级链可执行
6. YAML 文件编码: UTF-8 (BOM: 否)
