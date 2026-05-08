---


task_id: TASK-MOD-INF-001-0011
module_id: MOD-INF-001
title: "跨模块集成实现：CT-1 至 CT-4 + OTel + DR + 预测模型 + 语义缓存集成"
doc_type: task_card
status: done
priority: P0
layer: L01
layer_name: infrastructure
functional_domain: observability
owner: ZephyrAlpha-Owner
assignee: AI-GLM-5.1
created_by: AI-GLM-5.1
created_at: 2026-05-07T03:01:00+08:00
valid_from: 2026-05-07
ttl: permanent
belongs_to: MOD-INF-001
dependencies:
  - TASK-MOD-INF-001-0004
  - TASK-MOD-INF-001-0005
  - TASK-MOD-INF-001-0006
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\capacity-assurance\\blueprint.md"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\capacity_assurance\\cross_module_integration.py"
acceptance_criteria:
  - "CT-1: predict-router 收到容量告警后自动切换模型路由"
  - "CT-2: market-data-ingestor 收到熔断信号后暂停数据采集中高风险通道"
  - "CT-3: task-system Token 扣减失败时返回限流响应而非崩溃"
  - "CT-4: iguana-rebalancer 资本账户熔断保护触发后禁止新开仓"
  - "OTel Span 传播贯穿全部跨模块调用链路"
  - "DR 恢复流程包含跨模块状态一致性校验"
rollback_instructions:
  - "断开跨模块集成连接，恢复各模块独立运行"
  - "每对集成有隔离开关，支持逐对禁用"
context_assembly_manifest:
  - source: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\capacity-assurance\\blueprint.md"
    sections: ["§17 跨模块集成设计 L846-955", "CT-1/CT-2/CT-3/CT-4", "§12 OTel 语义规范", "§15 灾难恢复", "§16 容量预测", "§11 语义缓存", "§13 触发条件与扩展路径"]
    purpose: "提取全部跨模块集成契约、OTel 传播要求、DR 和预测模型细节"
tags:
  - capacity-assurance
  - cross-module-integration
  - CT-1-to-CT-4
phase: phase_2_enhance
estimated_effort_minutes: 180
ai_autonomy: AI-Modifiable
governance_layer: GOV-P1
runtime_plane: RP-3
source_blueprint: "MOD-INF-001"
source_section: "蓝图 CT-1~CT-4 跨模块集成 + §13 触发条件与扩展路径"
description: "跨模块集成实现：CT-1 至 CT-4 + OTel + DR + 预测模型 + 语义缓存集成"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\capacity_assurance\\cross_module_integration.py"
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
estimated_tokens: 54000
timeout_minutes: 180
depends_on:
  - TASK-MOD-INF-001-0004
  - TASK-MOD-INF-001-0005
  - TASK-MOD-INF-001-0006
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



# 跨模块集成实现：CT-1 至 CT-4 + OTel + DR + 预测模型 + 语义缓存集成

## 1. 任务来源

从蓝图 §17 跨模块集成设计 + §12 OTel + §15 DR + §16 容量预测 + §11 语义缓存提取。

**四条核心集成契约：**

| 契约 | 上游模块 | 下游模块 | 触发条件 | 响应动作 |
|------|---------|---------|---------|---------|
| CT-1 | capacity-assurance | predict-router | Error Budget L3+ | 自动模型路由切换 |
| CT-2 | capacity-assurance | market-data-ingestor | Kill Switch ON | 高风险通道暂停 |
| CT-3 | task-system | capacity-assurance | Token Budget 耗尽 | Token 扣减返回限流 |
| CT-4 | capacity-assurance | iguana-rebalancer | 资本容量告警 | 禁止新开仓 |

## 2. 施工内容

### 2.1 CT-1: capacity-assurance → predict-router

在 `cross_module_integration.py` 中实现 `PredictRouterIntegration`：
- `send_capacity_alert(alert_level, slo_id)`: 推送到 predict-router
- `register_switch_callback(callback)`: predict-router 注册切换回调
- predict-router 收到 L3+ Error Budget 事件后调用 `degradation_manager.switch_model(target)`
- OTel Span: `capacity.alert.sent` → `predict.router.received`

### 2.2 CT-2: capacity-assurance → market-data-ingestor

在 `cross_module_integration.py` 中实现 `MarketDataIngestorIntegration`：
- `broadcast_kill_switch(status)`: 推送全局熔断状态
- market-data-ingestor 检查 `dangerous_channels` 列表，暂停高风险通道
- 低风险通道（国债、货币市场）不受影响
- OTel Span: `capacity.kill_switch` → `market_data.channel_pause`

### 2.3 CT-3: task-system → capacity-assurance

在 `cross_module_integration.py` 中实现 `TaskSystemIntegration`：
- `check_and_deduct_tokens(task_id, estimated_tokens) -> TokenResult`
- 返回 `{allowed: bool, remaining: int, reason: str}`
- 失败时 task-system 标记任务为 RATE_LIMITED 而非 FAILED
- OTel Span: `task.token_deduct` → `capacity.token_budget`

### 2.4 CT-4: capacity-assurance → iguana-rebalancer

在 `cross_module_integration.py` 中实现 `IguanaRebalancerIntegration`：
- `check_capital_capacity(account_id) -> CapacityCheck`
- 资本容量告警时返回 `{can_open_new: false, reason: "capital_capacity_threshold"}`
- OTel Span: `capacity.capital_check` → `iguana.rebalance.gate`

### 2.5 OTel 语义规范跨模块传播

所有跨模块集成调用必须：
- 创建新的 OTel Span，手工设定 `traceparent`/`tracestate`
- 包含 `gen_ai.integration.name` 属性 = 集成契约 ID
- 包含错误状态码（OK/UNAVAILABLE/THROTTLED/DEGRADED）

### 2.6 DR 跨模块一致性校验

在 DR 恢复流程中（M-21），增加：
- `validate_cross_module_state()`: 检查跨模块状态一致性
- 各集成下游模块的状态快照对比

### 2.7 容量预测模型集成

在 `cross_module_integration.py` 中：
- `notify_prediction_alert(prediction)`: 将容量预测告警推送到相关模块

### 2.8 语义缓存集成

在 `cross_module_integration.py` 中：
- `SemanticCache.invalidate(module_pattern)`: 跨模块缓存失效广播

## 3. 验收标准

1. CT-1 在 Error Budget L3 触发后 5s 内完成模型路由切换
2. CT-2 在 Kill Switch 触发后 3s 内暂停高风险通道
3. CT-3 Token 耗尽时 task-system 收到限流响应而非异常
4. CT-4 资本容量告警后 iguana-rebalancer 不再开新仓
5. 所有跨模块集成有完整 OTel Span 链路
6. DR 恢复后跨模块状态一致