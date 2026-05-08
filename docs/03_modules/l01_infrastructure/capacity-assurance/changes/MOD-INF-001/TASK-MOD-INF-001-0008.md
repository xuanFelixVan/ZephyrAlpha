---

task_id: TASK-MOD-INF-001-0008
module_id: MOD-INF-001
title: "施工路线图：Phase 0 Foundation + Phase 1a/1b + Phase 2 Harden"
doc_type: task_card
status: done
priority: P0
layer: L01
layer_name: infrastructure
functional_domain: observability
owner: ZephyrAlpha-Owner
assignee: AI-GLM-5.1
created_by: AI-GLM-5.1
created_at: 2026-05-07T02:59:30+08:00
valid_from: 2026-05-07
ttl: permanent
belongs_to: MOD-INF-001
dependencies:
  - TASK-MOD-INF-001-0001
  - TASK-MOD-INF-001-0002
  - TASK-MOD-INF-001-0003
  - TASK-MOD-INF-001-0004
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\capacity-assurance\\blueprint.md"
downstream_outputs: []
acceptance_criteria:
  - "Phase 0 Foundation: 骨架模块完成(validate_ssot/capacity_slo/ai_audit_guard)"
  - "Phase 1a Scaffold: ContractBus批1/importer/config/pre-commit分层/sandbox_gate/immutable_registry/多级Token Budget+Reasoning Spans"
  - "Phase 1b X-Bridge: ContractBus批2/auto_fixer/session_carryover/audit_rules/governance_loop/Sandbox沙箱执行器+Graceful Degradation降级链"
  - "Phase 2 Harden: ContractBus批3/fault_isolator/故障域隔离≥3/AISG容量预算/成本预估器+语义缓存+容量预测模型"
  - "每个阶段门禁: ruff+mypy+pytest全部PASS"
rollback_instructions:
  - "每个阶段可独立回滚"
  - "Phase顺序不可颠倒"
context_assembly_manifest:
  - source: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\capacity-assurance\\blueprint.md"
    sections: ["§7 施工路线图", "§7.1 任务卡→施工阶段的映射", "§7.2 施工阶段+模块-来源映射"]
    purpose: "提取四阶段施工路线图的完整规划"
tags:
  - capacity-assurance
  - phase-roadmap
  - phase-0-foundation
  - phase-1a-scaffold
  - phase-1b-x-bridge
  - phase-2-harden
phase: phase_0_foundation
estimated_effort_minutes: 60
ai_autonomy: Human-Gated
governance_layer: GOV-P1
runtime_plane: RP-3
source_blueprint: "MOD-INF-001"
source_section: "蓝图 §7 施工路线图 Phase 0/1a/1b/2"
description: "施工路线图：Phase 0 Foundation + Phase 1a/1b + Phase 2 Harden"
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
estimated_tokens: 18000
timeout_minutes: 60
depends_on:
  - TASK-MOD-INF-001-0001
  - TASK-MOD-INF-001-0002
  - TASK-MOD-INF-001-0003
  - TASK-MOD-INF-001-0004
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


# 施工路线图：Phase 0 Foundation + Phase 1a Scaffold + Phase 1b X-Bridge + Phase 2 Harden

## 1. 任务来源

从蓝图 §7 "施工路线图" 提取，分为四个施工阶段。

## 2. 施工阶段

### Phase 0: Foundation（骨架）

| # | 模块 | 角色 | 来源 | 状态 |
|---|------|------|------|:---:|
| 1 | validate_ssot.py | SSoT 验证脚本 | 已有脚本 | ✅ 已实现 |
| 2 | capacity_slo.yaml | 容量 SLI/SLO | TASK-0011 决策驱动 | ⚠️ 首版 |
| 3 | ai_audit_guard.py | AI 修改审计守卫 | 先有守卫设计 | 需实现 |

### Phase 1a: Scaffold（脚手架）

| # | 模块 | 来源 |
|---|------|------|
| 1 | ContractBus 批1（15合约） | TASK-0004 |
| 2 | importer 自动注册 | 结构支持 |
| 3 | config 验证器 | config_validator.py |
| 4 | pre-commit 分层 | M-05（部分） |
| 5 | sandbox_gate 初版 | TASK-0004 设计决策 |
| 6 | immutable_registry | 配置 | 
| 7 | 多级 Token Budget (L0-L2) | §9 设计 |
| 8 | Reasoning Spans (OTel) | TASK-0004 跨模块集成 |

### Phase 1b: X-Bridge（跨桥）

| # | 模块 | 来源 |
|---|------|------|
| 1 | ContractBus 批2（15合约） | TASK-0004 |
| 2 | auto_fixer | M-10+ 事件总线修复 |
| 3 | session_carryover | 跨 session 状态转移 |
| 4 | audit_rules (守护 IRS) | M-17 从 config 加载 |
| 5 | governance_loop 初版 | M-19 |
| 6 | Sandbox 沙箱执行器 | §10 设计 |
| 7 | Graceful Degradation 降级链 | §11 设计 |

### Phase 2: Harden（加固）

| # | 模块 | 来源 |
|---|------|------|
| 1 | ContractBus 批3（14合约） | TASK-0004 |
| 2 | fault_isolator.py | §6.1 M-13 |
| 3 | 故障域隔离 ≥3 | fault_isolator.py 实现 |
| 4 | AISG 容量预算 | error_budget.py 扩展 |
| 5 | 成本预估器 | M-26 |
| 6 | 语义缓存 | M-27 + ChromaDB |
| 7 | 容量预测模型 | error_budget 增强 |

## 3. 绑销责任追索（蓝图 §7 施工责任）

| 来源 | 任务卡 | 绑定 | 归档 |
|------|--------|------|------|
| 施工决定 | TASK-0002 | DG-1 - DG-16 全部施工决策 | 蓝图 §6.2 |
| 蓝图 | 所有任务卡 | 原需 16+ 架构决策、≥48 合约、8 SLI、≥4 Token Budget | 到最终交付 |
| 高层视野 | CT1 - CT4 | 跨模块集成进度 | 各模块的后续深化 |
| 风险 | 全部 R1 - R16 | 风险登记册 with 权重 | `risk_register.yaml` |
| 成本节约 | 语义缓存、成本预估器 | 构建蓝图的成本节约累积效应 | 每轮交付 |
| 盲点深度审计 | 1-67 | 由本蓝图全量覆盖、逐步闭合 | audit_trail/untracked |

## 4. 施工里程碑

| 里程碑 | Phase | 预期 | 依赖 |
|--------|:---:|------|------|
| M0 | 0 | SSoT + SLO 落地 | 无 |
| M1 | 1a | 首批合约 + Token Budget | M0 |
| M2 | 1b | 治理闭环 + Sandbox | M1 |
| M3 | 2 | 全模块 + Cache + 成本 | M2 |

## 5. 验收标准

1. Phase 0 Foundation：validate_ssot + capacity_slo + ai_audit_guard 三模块可运行
2. Phase 1a Scaffold：ContractBus 批1 + Token Budget 三级 + Reasoning Spans 正确
3. Phase 1b X-Bridge：治理闭环 + Sandbox + 降级链集成通过
4. Phase 2 Harden：全部模块 + 语义缓存 + 成本预估通过
5. 每个阶段门禁：ruff + mypy + pytest 全部 PASS