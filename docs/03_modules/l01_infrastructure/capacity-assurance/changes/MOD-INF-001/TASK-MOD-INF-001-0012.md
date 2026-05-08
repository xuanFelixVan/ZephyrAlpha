---

task_id: TASK-MOD-INF-001-0012
module_id: MOD-INF-001
title: "已实现代码完整路径索引验证（蓝图 §19 + 蓝图外已有实现 §6.3）"
doc_type: task_card
status: done
priority: P0
layer: L01
layer_name: infrastructure
functional_domain: observability
owner: ZephyrAlpha-Owner
assignee: AI-GLM-5.1
created_by: AI-GLM-5.1
created_at: 2026-05-07T03:00:30+08:00
valid_from: 2026-05-07
ttl: permanent
belongs_to: MOD-INF-001
dependencies:
  - TASK-MOD-INF-001-0001
  - TASK-MOD-INF-001-0005
  - TASK-MOD-INF-001-0006
  - TASK-MOD-INF-001-0007
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\capacity-assurance\\blueprint.md"
downstream_outputs: []
acceptance_criteria:
  - "§19.1 蓝图内模块(M-01~M-27)已实现文件: 27个模块表格+实现状态+文件路径完整"
  - "§19.2 蓝图外已有实现: 11个外部模块映射正确"
  - "§19.4 部署文件清单: 4个文件(.gitignore/Verifiable-Lock/atomics/shell)路径正确"
  - "§6.3 蓝图外已有实现: 7个核心模块引用验证"
  - "ging验证: module_id:path映射 与 blueprint_id:repo 无断裂"
  - "验证标准: 蓝图§19中声称'✅已实现'的模块，路径在磁盘上存在；'⚠️部分实现'的模块，定位到已交付文件"
rollback_instructions:
  - "索引仅文档验证，无回滚风险"
context_assembly_manifest:
  - source: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\capacity-assurance\\blueprint.md"
    sections: ["§19 已实现代码完整路径索引(v2.0.0新增)", "§6.3 蓝图外已有实现"]
    purpose: "提取已实现代码的完整路径索引+验证模块实现状态"
tags:
  - capacity-assurance
  - code-path-index
  - implementation-status
  - M-01-to-M-27
  - external-modules
phase: phase_0_foundation
estimated_effort_minutes: 120
ai_autonomy: Human-Gated
governance_layer: GOV-P1
runtime_plane: RP-3
source_blueprint: "MOD-INF-001"
source_section: "蓝图 §19 已实现代码完整路径索引"
description: "已实现代码完整路径索引验证（蓝图 §19 + 蓝图外已有实现 §6.3）"
allowed_touch: []
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
estimated_tokens: 36000
timeout_minutes: 120
depends_on:
  - TASK-MOD-INF-001-0001
  - TASK-MOD-INF-001-0005
  - TASK-MOD-INF-001-0006
  - TASK-MOD-INF-001-0007
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


# 已实现代码完整路径索引验证（蓝图 §19 + 蓝图外已有实现 §6.3）

## 1. 任务来源

从蓝图 §19 "已实现代码完整路径索引"（v2.0.0 新增）和 §6.3 "蓝图外已有实现" 提取，验证所有模块的实现状态和路径。

## 2. 蓝图内模块（M-01~M-27）已实现文件（§19.1）

| 模块ID | 模块名称 | 实现状态 | 实际路径 |
|--------|---------|:---:|------|
| M-01 | CTR-001修复 | ✅ 已完成 | 已归档 |
| M-02 | 源码树统一 | ✅ 已完成 | `src/zephyr/` |
| M-03 | validate_ssot.py | ✅ 已实现 | `scripts/governance/d5_architecture/validate_ssot.py` |
| M-04 | lazy_loader.py | ❌ 未实现 | `src/zephyr/__init__.py` |
| M-05 | pre-commit分层 | ⚠️ 部分实现 | `.pre-commit-config.yaml` |
| M-06 | dmypy配置 | ❌ 未实现 | `mypy.ini` |
| M-07 | event_bus背压 | ❌ 未实现 | `src/zephyr/shared/event_bus_backpressure.py` |
| M-08 | import-linter | ❌ 未实现 | `.importlinter` |
| M-09 | ContractBus接口 | ❌ 未实现 | `src/zephyr/shared/contract_bus.py` |
| M-10 | ZephyrLogger+OTel | ❌ 未实现 | `src/zephyr/shared/zephyr_logger.py` |
| M-11 | contract_tester.py | ❌ 未实现 | `src/zephyr/shared/contract_tester.py` |
| M-12 | config_validator.py | ❌ 未实现 | `src/zephyr/shared/config_validator.py` |
| M-13 | fault_isolator.py | ❌ 未实现 | `src/zephyr/shared/fault_isolator.py` |
| M-14 | warm_hot_gate.py | ❌ 未实现 | `src/zephyr/shared/warm_hot_gate.py` |
| M-15 | pydantic_v2_migrator.py | ❌ 未实现 | `src/zephyr/shared/pydantic_v2_migrator.py` |
| M-16 | event_bus_upgrade.py | ❌ 未实现 | `src/zephyr/shared/event_bus_upgrade.py` |
| M-17 | ai_audit_guard.py | ⚠️ 部分实现 | `src/zephyr/shared/ai_audit_guard.py`（规则引擎，日志已有，守卫待实现） |
| M-18 | capacity_slo.yaml | ⚠️ 首版已落地 | `config/capacity/capacity_slo.yaml`（≥8 SLI，插桩点TBD） |
| M-19 | capacity_governance_loop.py | ❌ 未实现 | `src/zephyr/shared/capacity_governance_loop.py` |
| M-20 | ttl_cleanup_engine.py | ❌ 未实现 | `src/zephyr/shared/ttl_cleanup_engine.py` |
| M-21 | error_budget_tracker.py | ❌ 未实现 | `src/zephyr/shared/error_budget_tracker.py` |
| M-22 | kill_switch.py | ❌ 未实现 | `src/zephyr/shared/kill_switch.py` |
| M-23 | sandbox_executor.py | ❌ 未实现 | `src/zephyr/shared/sandbox_executor.py` |
| M-24 | degradation_chain.py | ❌ 未实现 | `src/zephyr/shared/degradation_chain.py` |
| M-25 | reasoning_spans.py | ❌ 未实现 | `src/zephyr/shared/reasoning_spans.py` |
| M-26 | cost_estimator.py | ❌ 未实现 | `src/zephyr/shared/cost_estimator.py` |
| M-27 | semantic_cache.py | ❌ 未实现 | `src/zephyr/shared/semantic_cache.py` |

## 3. 蓝图外已有实现（§19.2 + §6.3）

| 模块名称 | 实际路径 | 归属蓝图 | 验证要点 |
|---------|---------|---------|---------|
| Token 预算管理器 (L1/L2/L3) | `src/zephyr/context_engine/context_budget_tracker.py` | context-engine | Level 2 session级 |
| 上下文压缩器 (DocCompressor) | `src/zephyr/context_engine/doc_compressor.py` | context-engine | Doc size压缩 |
| 熔断器 (CBGManager + L08) | `src/zephyr/gates/circuit_breaker.py` | gate-engine | M-13 fault_isolator子集 |
| Agent SLO 监控 (5项SLO) | `src/zephyr/orchestrator/agent_health_monitor.py` | orchestrator | 5-SLO + 三态健康 |
| AI 行为审计日志 | `src/zephyr/llm_security/behavior_audit_logger.py` | llm-security | 4种事件 + JSONL |
| 输入消毒器 (InputSanitizer) | `src/zephyr/llm_security/input_sanitizer.py` | llm-security | 输入过滤 |
| 原子事务管理器 (ATM) | `src/zephyr/db/atomic_transaction_manager.py` | database | DB原子性 |
| SQLite Schema DDL + init_db | `src/zephyr/db/sqlite_schema.py` | database | DDL |
| MCP 工具限流 | `src/zephyr/mcp/tool_contracts.yaml` | mcp-servers | rate_limit_qps |
| L12 Metrics 骨架 | `src/zephyr/l12_system_telemetry/metrics/__init__.py` | system-telemetry | Metrics |
| 任务反馈收集器 | `src/zephyr/feedback_loop/feedback_collector.py` | feedback-loop | Feedback |
| **不在此清单但存在**: 本蓝图依赖的 `event_bus.py`、`pydantic2.yaml`、`prisma.yaml` 等 |

## 4. 部署文件清单（§19.4）

| # | 文件 | 用途 | 状态 |
|---|------|------|:---:|
| 1 | `.gitignore` | G5 .py 限制性门控，排除非法路径 | ⚠️ 需检查 |
| 2 | `Verifiable-Lock` | `.post_install` | ❌ 未创建 |
| 3 | `atomic_locks` | 构建完成，防止并发修改 | ❌ 未创建 |
| 4 | `shell` | `.sql` 构建脚本（自动清除 dev junk） | ❌ 未处理 |

## 5. 验证方法

1. **ging 验证**: `module_id → path` 映射与 `blueprint_id → repo` 无断裂——通过 `scripts/governance/d5_architecture/validate_ssot.py` 和 `metadata-registry.yaml` 交叉验证。

2. **路径存在性**: `✅ 已实现` 模块的路径在磁盘上存在；`⚠️ 部分实现` 模块定位到已交付文件。

3. **依赖一致性**: 蓝图外模块路径与 `import-linter` 层规则一致。

## 6. 验收标准

1. 27 个 M-01~M-27 模块实现状态 + 路径与蓝图 §19.1 完全一致
2. 11 个蓝图外模块路径验证通过
3. 部署文件清单路径正确
4. ging 验证无断裂
5. `✅ 已实现` 路径在磁盘上存在
6. 全部模块的 `layer → repo → module` 上下游链完整