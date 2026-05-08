---


task_id: TASK-MOD-INF-001-0006
module_id: MOD-INF-001
title: "v2.0.0 新增模块施工：M-11~M-16 辅助模块 + M-21~M-24 核心新模块"
doc_type: task_card
status: done
priority: P0
layer: L01
layer_name: infrastructure
functional_domain: observability
owner: ZephyrAlpha-Owner
assignee: AI-GLM-5.1
created_by: AI-GLM-5.1
created_at: 2026-05-07T02:58:30+08:00
valid_from: 2026-05-07
ttl: permanent
belongs_to: MOD-INF-001
dependencies:
  - TASK-MOD-INF-001-0003
  - TASK-MOD-INF-001-0005
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\capacity-assurance\\blueprint.md"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\contract_tester.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\config_validator.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\fault_isolator.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\warm_hot_gate.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\pydantic_v2_migrator.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\event_bus_upgrade.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\error_budget_tracker.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\kill_switch.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\sandbox_executor.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\degradation_chain.py"
acceptance_criteria:
  - "M-11 contract_tester.py: 契约测试框架"
  - "M-12 config_validator.py: 配置参数Pydantic v2校验"
  - "M-13 fault_isolator.py: 故障域隔离（≥3故障域）"
  - "M-14 warm_hot_gate.py: Warm→Hot阻断门"
  - "M-15 pydantic_v2_migrator.py: Pydantic v2迁移工具"
  - "M-16 event_bus_upgrade.py: 事件总线升级"
  - "M-21 error_budget_tracker.py: Error Budget五级响应追踪+Burn Rate多窗口监控"
  - "M-22 kill_switch.py: 全局一键熔断（信号文件+环境变量双通道）"
  - "M-23 sandbox_executor.py: 高风险操作沙箱隔离"
  - "M-24 degradation_chain.py: Graceful Degradation模型降级链"
rollback_instructions:
  - "每个模块独立回滚"
  - "Kill Switch回滚需Owner确认"
context_assembly_manifest:
  - source: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\capacity-assurance\\blueprint.md"
    sections: ["§6.1 M-11~M-16", "§6.2 v2.0.0 新增模块 M-21~M-27", "§8 Error Budget 五级响应", "§10 Kill Switch + Sandbox", "§11 Graceful Degradation"]
    purpose: "提取辅助模块和v2.0.0新增核心模块的完整规格"
tags:
  - capacity-assurance
  - new-modules
  - M-11-to-M-16
  - M-21-to-M-24
  - kill-switch
  - error-budget
  - sandbox
  - degradation
phase: phase_0_foundation
estimated_effort_minutes: 300
ai_autonomy: Human-Gated
governance_layer: GOV-P1
runtime_plane: RP-3
source_blueprint: "MOD-INF-001"
source_section: "蓝图 §6.1+§6.2 新增模块 M-11~M-24"
description: "v2.0.0 新增模块施工：M-11~M-16 辅助模块 + M-21~M-24 核心新模块"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\contract_tester.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\config_validator.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\fault_isolator.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\warm_hot_gate.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\pydantic_v2_migrator.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\event_bus_upgrade.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\error_budget_tracker.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\kill_switch.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\sandbox_executor.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\degradation_chain.py"
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
estimated_tokens: 90000
timeout_minutes: 300
depends_on:
  - TASK-MOD-INF-001-0003
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



# v2.0.0 新增模块施工：M-11~M-16 + M-21~M-24

## 1. 模块清单

### 1.1 M-11~M-16 辅助模块（蓝图 §6.1）

| 模块ID | 模块名称 | 实际路径 | 权限 |
|--------|---------|---------|------|
| M-11 | contract_tester.py | `src/zephyr/shared/contract_tester.py` | Human-Gated |
| M-12 | config_validator.py | `src/zephyr/shared/config_validator.py` | Human-Gated |
| M-13 | fault_isolator.py | `src/zephyr/shared/fault_isolator.py` | Human-Gated |
| M-14 | warm_hot_gate.py | `src/zephyr/shared/warm_hot_gate.py` | Human-Gated |
| M-15 | pydantic_v2_migrator.py | `src/zephyr/shared/pydantic_v2_migrator.py` | Human-Gated |
| M-16 | event_bus_upgrade.py | `src/zephyr/shared/event_bus_upgrade.py` | Human-Gated |

### 1.2 M-21~M-24 v2.0.0 新增（蓝图 §6.2）

| 模块ID | 模块名称 | 预期路径 | 对标来源 |
|--------|---------|---------|---------|
| M-21 | error_budget_tracker.py | `src/zephyr/shared/error_budget_tracker.py` | Google SRE Workbook §4-§5 |
| M-22 | kill_switch.py | `src/zephyr/shared/kill_switch.py` | AI Agent Observability Best Practices |
| M-23 | sandbox_executor.py | `src/zephyr/shared/sandbox_executor.py` | AI Agent Observability Best Practices |
| M-24 | degradation_chain.py | `src/zephyr/shared/degradation_chain.py` | AI Agent Cost Crisis Report |

## 2. 施工内容

### 2.1 M-11: contract_tester.py

契约测试框架——验证所有 ContractBus 合约的输入/输出类型一致性。

### 2.2 M-12: config_validator.py

配置参数 Pydantic v2 校验——所有 `config/capacity/*.yaml` 加载时 Schema 验证。

### 2.3 M-13: fault_isolator.py

故障域隔离——≥3 个故障域，单一故障域失效不影响其他。

### 2.4 M-14: warm_hot_gate.py

Warm→Hot 阻断门——模块从 warm 状态（被动监控）升级到 hot 状态（主动干预）前需要 Owner 审批。

### 2.5 M-15: pydantic_v2_migrator.py

Pydantic v2 迁移工具——检查并迁移所有 Pydantic v1 模型。

### 2.6 M-16: event_bus_upgrade.py

事件总线升级——支持事件版本化 + 增量升级。

### 2.7 M-21: error_budget_tracker.py

**核心模块**。对标 Google SRE Workbook §4 Error Budgets + §5.4 Multi-Window Multi-Burn-Rate Alerts。

- 五级响应追踪（Healthy/Warning/Cautious/Critical/Emergency）
- Burn Rate 多窗口监控（1h/6h/3d/30d 四个窗口）
- 自动恢复机制（Emergency→Critical 6h冷却, Critical→Cautious 24h冷却）
- Error Budget 消耗归因

### 2.8 M-22: kill_switch.py

**核心模块**。全局一键熔断。

双通道确认：
- 环境变量：`ZEPHYR_KILL_SWITCH=1`
- 信号文件：`.audit_cache/kill_switch_active`

`activate(reason)`: 写入信号文件 + 记录 reason
`deactivate()`: 移除信号文件
`is_active()`: 检查环境变量 OR 信号文件

触发条件：
- Error Budget Critical 持续 1h
- Owner 手动激活
- 单日成本 > $100
- 1h Burn Rate > 14.4×

### 2.9 M-23: sandbox_executor.py

高风险操作沙箱隔离。

`sandbox_policy.yaml` 配置：
- `file_delete`: 沙箱 + dry_run + 需确认
- `config_modify`: 沙箱 + diff_before_apply
- `external_api_call`: 无沙箱 + cost_limit ¥1.00

### 2.10 M-24: degradation_chain.py

Graceful Degradation 模型降级链。

`degradation_chain.yaml` 配置：
- 链1：cost_per_day > ¥5 → deepseek-chat(2000) → qwen2.5-3b-onnx(1000)
- 链2：latency_p99 > 10000ms → deepseek-chat(5000) → qwen2.5-3b-onnx(2000)

## 3. 关键联动

| 组件 | 联动对象 | 联动方式 |
|------|---------|---------|
| Kill Switch (M-22) | Circuit Breaker (gate-engine) | conservative模式→CBG阈值降低50%；只读模式→全部CBG OPEN |
| Kill Switch (M-22) | Error Budget Tracker (M-21) | Critical持续1h→自动触发conservative |
| Sandbox (M-23) | CapacityDigitalTwin (M-40) | G5模拟在Sandbox副本中运行 |
| Degradation (M-24) | Cost Estimator (M-26) | 成本超限→触发降级链 |

## 4. 验收标准

1. M-11 contract_tester 可验证 ContractBus 合约
2. M-12 config_validator 可校验所有 capacity YAML
3. M-13 fault_isolator ≥3故障域隔离
4. M-21 error_budget_tracker 五级响应+Burn Rate多窗口正确
5. M-22 kill_switch 双通道触发+恢复
6. M-23 sandbox_executor 沙箱隔离（文件删除/配置修改需确认）
7. M-24 degradation_chain 模型降级链可执行
8. ruff 零错误 + mypy strict 通过 + pytest > 80%