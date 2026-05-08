---
task_id: TASK-INF-0101
status: planned
priority: P0
severity: critical
module_id: MOD-INF-007
phase: 1
category: foundation
effort_estimated: 3h
effort_actual: null
assigned_to: null
reviewer: null
approver: null
source_section: §1、§3.1、§12
reference_docs:
  - D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate-engine\blueprint.md
  - D:\ZephyrAlpha\docs\01_policies_and_standards\governance\document\directory-structure-standard.md
upstream_files: []
downstream_outputs:
  - D:\ZephyrAlpha\src\zephyr\gates\gate_engine.py
  - D:\ZephyrAlpha\src\zephyr\gates\gate_context.py
  - D:\ZephyrAlpha\src\zephyr\gates\gate_pipeline.py
  - D:\ZephyrAlpha\src\zephyr\gates\gate_simulator.py
  - D:\ZephyrAlpha\src\zephyr\gates\gate_override.py
  - D:\ZephyrAlpha\src\zephyr\gates\gate_health.py
  - D:\ZephyrAlpha\src\zephyr\gates\task_completion_gate.py
  - D:\ZephyrAlpha\src\zephyr\gates\circuit_breaker.py
  - D:\ZephyrAlpha\src\zephyr\gates\contract_template_manager.py
  - D:\ZephyrAlpha\src\zephyr\gates\adaptive_threshold.py
  - D:\ZephyrAlpha\src\zephyr\gates\gate_integrity_guard.py
  - D:\ZephyrAlpha\src\zephyr\gates\audit_chain_verifier.py
  - D:\ZephyrAlpha\src\zephyr\gates\g1_ingest.yaml
  - D:\ZephyrAlpha\src\zephyr\gates\g2_dependency_check.yaml
  - D:\ZephyrAlpha\src\zephyr\gates\g3_environment.yaml
  - D:\ZephyrAlpha\src\zephyr\gates\g4_tracking.yaml
  - D:\ZephyrAlpha\src\zephyr\gates\g5_extract.yaml
  - D:\ZephyrAlpha\src\zephyr\gates\g6_blueprint_compliance.yaml
  - D:\ZephyrAlpha\src\zephyr\gates\task\g0_orc_gate_engine.yaml
  - D:\ZephyrAlpha\src\zephyr\gates\task\g7_orc_gate_engine.yaml
  - D:\ZephyrAlpha\src\zephyr\gates\admission\mad_001.yaml
  - D:\ZephyrAlpha\src\zephyr\gates\admission\mad_002.yaml
  - D:\ZephyrAlpha\src\zephyr\gates\admission\mad_003.yaml
  - D:\ZephyrAlpha\src\zephyr\gates\admission\mad_004.yaml
  - D:\ZephyrAlpha\src\zephyr\gates\g7_position_limits.yaml
  - D:\ZephyrAlpha\src\zephyr\gates\g8_risk_budget.yaml
  - D:\ZephyrAlpha\src\zephyr\gates\g9_strategy_correlation.yaml
  - D:\ZephyrAlpha\src\zephyr\gates\g7d_depth_compliance.yaml
  - D:\ZephyrAlpha\src\zephyr\gates\g7c_cross_gate_consistency.yaml
  - D:\ZephyrAlpha\src\zephyr\gates\_registry.yaml
  - D:\ZephyrAlpha\src\zephyr\gates\_template.yaml
acceptance_criteria:
  - "AC1: 按蓝图 §3.1 文件组成地图创建全部 29 个文件（12 个 .py + 17 个 .yaml）"
  - "AC2: D:\\ZephyrAlpha\\src\\zephyr\\gates\\gate_engine.py 作为主入口包含 GateEngine 类"
  - "AC3: _registry.yaml 包含全部门禁注册表，与蓝图 §3.1 文件列表完全一致"
  - "AC4: _template.yaml 为标准门禁模板，含 entry_conditions [{id,name,type,check,severity,on_failure,fix_hint}] 字段骨架"
  - "AC5: 目录结构符合 directory-structure-standard.md，子目录 task/ 和 admission/ 均已创建"
  - "AC6: 蓝图 construction_progress 已标记为 phase_1_complete（15 个 .py 已实现，YAML 为模板状态）"
rollback_instructions:
  - 删除 D:\ZephyrAlpha\src\zephyr\gates\ 目录及全部内容
  - 确认 Python import 报 ModuleNotFoundError
  - 检查全项目无对 zephyr.gates 的交叉引用
created_at: 2026-05-06T23:30:00Z
updated_at: 2026-05-07T00:30:00Z
closed_at: null
dependencies: []
blocked_by: []
blocks:
  - TASK-INF-0104
  - TASK-INF-0105
  - TASK-INF-0106
tags:
  - gate-engine
  - module-skeleton
  - §3.1
  - file-composition
  - blueprint-v0.5.0
version: 2.0.0
change_log: |
  v2.0.0 (2026-05-07): 二次核查修正——完全对齐蓝图 §3.1 的 29 个文件清单：12 .py + 17 .yaml。此前 v1.0.0 的文件列表为错误推断。
  v1.0.0 (2026-05-06): 初始创建（错误版本——已废弃）
context_assembly_manifest:
  documents:
    - D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate-engine\blueprint.md
  sections:
    - §1 概述与模块定位
    - §3.1 文件组成地图
    - §3.3 熔断器模式
    - §12 已实现代码路径索引
  keywords:
    - gate-engine
    - skeleton
    - §3.1
    - 29-files
    - _registry.yaml
    - _template.yaml
  ai_reads_for_inference: true
---

# TASK-INF-0101: Gate Engine 模块骨架搭建（v2.0.0 修正版）

## 背景与动机

`gate-engine` 是 ZephyrAlpha 横向切面模块，承担任务全生命周期（G0-G7）和决策治理（G1-G5 KMS）的双重门控职责。蓝图 v0.5.0 **construction_progress = phase_1_complete**：15 个 .py 已实现，17 个 YAML 为门禁标准模板状态。

本卡确保 §3.1 文件组成地图的 29 个文件全部创建或验证存在。

## 蓝图 §3.1 文件清单（精确对齐）

| # | 文件 | 类型 |
|---|------|:---:|
| 1 | `gate_engine.py` | .py |
| 2 | `gate_context.py` | .py |
| 3 | `gate_pipeline.py` | .py |
| 4 | `gate_simulator.py` | .py |
| 5 | `gate_override.py` | .py |
| 6 | `gate_health.py` | .py |
| 7 | `task_completion_gate.py` | .py |
| 8 | `circuit_breaker.py` | .py |
| 9 | `contract_template_manager.py` | .py |
| 10 | `adaptive_threshold.py` | .py |
| 11 | `gate_integrity_guard.py` | .py |
| 12 | `audit_chain_verifier.py` | .py |
| 13 | `g1_ingest.yaml` | YAML |
| 14 | `g2_dependency_check.yaml` | YAML |
| 15 | `g3_environment.yaml` | YAML |
| 16 | `g4_tracking.yaml` | YAML |
| 17 | `g5_extract.yaml` | YAML |
| 18 | `g6_blueprint_compliance.yaml` | YAML |
| 19 | `task/g0_orc_gate_engine.yaml` | YAML |
| 20 | `task/g7_orc_gate_engine.yaml` | YAML |
| 21 | `admission/mad_001.yaml` | YAML |
| 22 | `admission/mad_002.yaml` | YAML |
| 23 | `admission/mad_003.yaml` | YAML |
| 24 | `admission/mad_004.yaml` | YAML |
| 25 | `g7_position_limits.yaml` | YAML |
| 26 | `g8_risk_budget.yaml` | YAML |
| 27 | `g9_strategy_correlation.yaml` | YAML |
| 28 | `g7d_depth_compliance.yaml` | YAML |
| 29 | `g7c_cross_gate_consistency.yaml` | YAML |
| — | `_registry.yaml` | YAML（全部门禁注册表） |
| — | `_template.yaml` | YAML（门禁标准模板） |

共计：12 .py + 17 门禁 YAML + _registry + _template = 31 个文件（§3.1 正文统计 29 不含 _registry/_template）

## 实施计划

1. 确认 15 个 .py 已实现（construction_progress=phase_1_complete）；如未创建则创建空桩
2. 创建 17 个 YAML 门禁配置，使用 `_template.yaml` 的 `entry_conditions` 格式
3. 创建 `_registry.yaml`（全部门禁注册表）和 `_template.yaml`（门禁标准模板）
4. 创建 `task/`和 `admission/` 子目录

## 回退方案

删除 `src/zephyr/gates/` 全部 → 确认 import 失败。

## 验收标准

| # | 标准 | 验证 |
|---|------|------|
| AC1 | 31 个文件全存在 | `Get-ChildItem -Recurse -File` 计数 ≥ 29 |
| AC2 | gate_engine.py 含 GateEngine 类 | import 验证 |
| AC3 | _registry.yaml 门禁注册表完整 | YAML parse |
| AC4 | _template.yaml 含 entry_conditions 骨架 | YAML parse |
| AC5 | task/ + admission/ 子目录存在 | `Test-Path` |
| AC6 | construction_progress 标记为 phase_1_complete | 蓝图 §3.3/§11 对照 |
