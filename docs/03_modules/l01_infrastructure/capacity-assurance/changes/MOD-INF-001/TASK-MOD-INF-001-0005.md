---


task_id: TASK-MOD-INF-001-0005
module_id: MOD-INF-001
title: "原有模块施工：M-01~M-10 基础设施模块 + M-17~M-20 核心运行时"
doc_type: task_card
status: done
priority: P0
layer: L01
layer_name: infrastructure
functional_domain: observability
owner: ZephyrAlpha-Owner
assignee: AI-GLM-5.1
created_by: AI-GLM-5.1
created_at: 2026-05-07T02:58:00+08:00
valid_from: 2026-05-07
ttl: permanent
belongs_to: MOD-INF-001
dependencies:
  - TASK-MOD-INF-001-0001
  - TASK-MOD-INF-001-0002
  - TASK-MOD-INF-001-0003
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\capacity-assurance\\blueprint.md"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\__init__.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\event_bus.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\contract_bus.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\zephyr_logger.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\ai_audit_guard.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\capacity_governance_loop.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\ttl_cleanup_engine.py"
  - "D:\\ZephyrAlpha\\config\\capacity\\capacity_slo.yaml"
acceptance_criteria:
  - "M-04 __init__.py: 模块懒加载实现"
  - "M-07 event_bus.py: 事件总线背压机制"
  - "M-09 contract_bus.py: 跨层通信抽象+Schema Enforcement"
  - "M-10 zephyr_logger.py: 结构化日志+OTel Metrics集成"
  - "M-17 ai_audit_guard.py: AI修改审计守卫规则引擎（⚠️部分实现：日志已有，守卫待实现）"
  - "M-18 capacity_slo.yaml: 容量SLI/SLO标准（⚠️首版已落地：≥8 SLI + arch_guard阈值；插桩点TBD）"
  - "M-19 capacity_governance_loop.py: 容量治理闭环（EMA评估→告警→自愈）"
  - "M-20 ttl_cleanup_engine.py: 派生文件TTL清理（7天TTL + WAL checkpoint前清理）"
  - "所有模块 ruff 零错误 + mypy strict 通过"
rollback_instructions:
  - "每个模块独立回滚"
  - "M-18 capacity_slo.yaml 回滚到上一版"
context_assembly_manifest:
  - source: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\capacity-assurance\\blueprint.md"
    sections: ["§6.1 原有模块（M-01~M-20）", "§7 架构视图", "§8 Error Budget 五级响应", "§12 OTel AI Agent语义规范"]
    purpose: "提取M-04~M-20原有模块的规格和接口定义"
tags:
  - capacity-assurance
  - core-modules
  - M-04-to-M-20
  - governance-loop
  - ttl-cleanup
  - ai-audit-guard
phase: phase_0_foundation
estimated_effort_minutes: 360
ai_autonomy: Human-Gated
governance_layer: GOV-P1
runtime_plane: RP-3
source_blueprint: "MOD-INF-001"
source_section: "蓝图 §6.1 原有模块 M-01~M-20"
description: "原有模块施工：M-01~M-10 基础设施模块 + M-17~M-20 核心运行时"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\__init__.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\event_bus.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\contract_bus.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\zephyr_logger.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\ai_audit_guard.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\capacity_governance_loop.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\ttl_cleanup_engine.py"
  - "D:\\ZephyrAlpha\\config\\capacity\\capacity_slo.yaml"
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
estimated_tokens: 108000
timeout_minutes: 360
depends_on:
  - TASK-MOD-INF-001-0001
  - TASK-MOD-INF-001-0002
  - TASK-MOD-INF-001-0003
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



# 原有模块施工：M-01~M-20（基础设施 + 核心运行时）

## 1. 模块清单（蓝图 §6.1）

| 模块ID | 模块名称 | 职责 | 实际路径 | 实现状态 | AI自治权限 |
|--------|---------|------|---------|:---:|-----------|
| M-01 | CTR-001修复 | 修复 CTR-001 字段 | 已归档 | ✅ 已完成 | Immutable Core |
| M-02 | 源码树统一 | 统一为单一 src/zephyr/ | `src/zephyr/` | ✅ 已完成 | Immutable Core |
| M-03 | validate_ssot.py | SSoT 验证脚本 | `scripts/governance/d5_architecture/validate_ssot.py` | ✅ 已实现 | Immutable Core |
| M-04 | lazy_loader.py | 模块懒加载 | `src/zephyr/__init__.py` | ❌ 未实现 | Human-Gated |
| M-05 | pre-commit分层 | 分层 pre-commit | `.pre-commit-config.yaml` | ⚠️ 部分实现 | Immutable Core |
| M-06 | dmypy配置 | 增量类型检查 | `mypy.ini` | ❌ 未实现 | AI-Modifiable |
| M-07 | event_bus背压 | 事件总线背压 | `src/zephyr/shared/event_bus.py` | ❌ 未实现 | AI-Modifiable |
| M-08 | import-linter | 层依赖规则 | `.importlinter` | ❌ 未实现 | Human-Gated |
| M-09 | ContractBus接口 | 跨层通信抽象 | `src/zephyr/shared/contract_bus.py` | ❌ 未实现 | Human-Gated |
| M-10 | ZephyrLogger+OTel | 结构化日志+Metrics | `src/zephyr/shared/zephyr_logger.py` | ❌ 未实现 | AI-Modifiable |
| M-11 | contract_tester.py | 契约测试框架 | `src/zephyr/shared/contract_tester.py` | ❌ 未实现 | Human-Gated |
| M-12 | config_validator.py | 配置参数验证 | `src/zephyr/shared/config_validator.py` | ❌ 未实现 | Human-Gated |
| M-13 | fault_isolator.py | 故障域隔离 | `src/zephyr/shared/fault_isolator.py` | ❌ 未实现 | Human-Gated |
| M-14 | warm_hot_gate.py | Warm→Hot 阻断门 | `src/zephyr/shared/warm_hot_gate.py` | ❌ 未实现 | Human-Gated |
| M-15 | pydantic_v2_migrator.py | Pydantic v2 迁移 | `src/zephyr/shared/pydantic_v2_migrator.py` | ❌ 未实现 | Human-Gated |
| M-16 | event_bus_upgrade.py | 事件总线升级 | `src/zephyr/shared/event_bus_upgrade.py` | ❌ 未实现 | Human-Gated |
| M-17 | ai_audit_guard.py | AI修改审计守卫 | `src/zephyr/shared/ai_audit_guard.py`（规则引擎）| ⚠️ 部分实现 | Immutable Core |
| M-18 | capacity_slo.yaml | 容量SLI/SLO标准 | `config/capacity/capacity_slo.yaml` | ⚠️ 首版已落地 | Human-Gated |
| M-19 | capacity_governance_loop.py | 容量治理闭环 | `src/zephyr/shared/capacity_governance_loop.py` | ❌ 未实现 | AI-Modifiable |
| M-20 | ttl_cleanup_engine.py | 派生文件TTL清理 | `src/zephyr/shared/ttl_cleanup_engine.py` | ❌ 未实现 | AI-Modifiable |

## 2. 施工范围

本任务卡覆盖 M-04~M-10（结构层/运行时层）和 M-17~M-20（治理层核心）共 11 个模块。

已完成或部分实现（M-01/02/03/05）不在本任务范围内。

## 3. 施工内容

### 3.1 M-04: lazy_loader.py

`D:\ZephyrAlpha\src\zephyr\__init__.py`

包级懒加载机制，延迟模块导入直到首次使用，降低启动成本。

### 3.2 M-07: event_bus.py

`D:\ZephyrAlpha\src\zephyr\shared\event_bus.py`

事件总线背压——队列深度 > CAP-006 阈值时，生产者减速或拒绝。

### 3.3 M-09: contract_bus.py

`D:\ZephyrAlpha\src\zephyr\shared\contract_bus.py`

跨层通信抽象层——ContractBus Schema Enforcement。所有模块间调用必须通过 ContractBus 接口，Pydantic v2 校验。

### 3.4 M-10: zephyr_logger.py

`D:\ZephyrAlpha\src\zephyr\shared\zephyr_logger.py`

structlog + OTel SDK 集成的结构化日志：
- 所有日志关联 Trace ID
- 自动生成 OTel Metrics Span
- 容量相关日志带 capacity_metrics 标签

### 3.5 M-17: ai_audit_guard.py

`D:\ZephyrAlpha\src\zephyr\shared\ai_audit_guard.py`

AI 修改审计守卫：
- 已有：`behavior_audit_logger.py` 日志记录
- 待实现：守卫规则引擎——拦截未经审批的 AI 操作
- 规则从 `config/audit/audit_rules.yaml` 加载

### 3.6 M-18: capacity_slo.yaml

`D:\ZephyrAlpha\config\capacity\capacity_slo.yaml`

容量 SLI/SLO 标准（≥8 SLI + 8 CAP-xxx 指标）：
- CAP-001~008 已定义（8 项 SLI）
- 首版已落地（含 arch_guard 阈值校验）
- 插桩点（instrumentation points）仍 TBD
- **新增** CAP-009~013（Saturation SLI 维度）

### 3.7 M-19: capacity_governance_loop.py

`D:\ZephyrAlpha\src\zephyr\shared\capacity_governance_loop.py`

容量治理闭环引擎：
- `evaluate()`: 读取 capacity_metrics → 计算 EMA → 判定 level
- `act()`: 根据 Error Budget 级别触发响应（L0~L4）
- `report()`: 输出治理报告到飞书/日志
- 采样间隔：300s（可配置 `CAPACITY_GOVERNANCE_INTERVAL_SECONDS`）

### 3.8 M-20: ttl_cleanup_engine.py

`D:\ZephyrAlpha\src\zephyr\shared\ttl_cleanup_engine.py`

派生文件 7 天 TTL 清理：
- 扫描 `capacity_metrics` / `error_budget` / `token_budget_usage` 表中过期数据
- 清理前强制 `PRAGMA wal_checkpoint(TRUNCATE)`（关联盲点 #62）
- 清理 `.audit_cache/` 中的临时文件

## 4. OTel 语义集成

- M-10：Reasoning Spans（`agent.reasoning` span + steps events）
- M-10：W3C TraceContext 传播——所有 ContractBus 调用自动注入 `traceparent` + `tracestate`

## 5. 验收标准

1. M-04 lazy_loader 延迟导入正确，首次访问时加载
2. M-07 背压机制：队列深度 > CAP-006 → 生产者减速
3. M-09 ContractBus Schema Enforcement：Pydantic v2 校验
4. M-10 ZephyrLogger：所有日志含 Trace ID
5. M-17 ai_audit_guard 规则引擎可拦截高风险 AI 操作
6. M-18 capacity_slo.yaml ≥ 8 SLI + Pydantic 校验通过
7. M-19 capacity_governance_loop EMA 评估 + 五级响应正确
8. M-20 TTL 清理：过期数据清理 + WAL checkpoint
9. ruff 零错误 + mypy strict 通过
10. pytest 覆盖率 > 80%