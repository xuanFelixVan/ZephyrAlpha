---
task_id: TASK-OPS-0005
module_id: MOD-INF-005
title: "脚本三件套入库流程落地 — §4 四阶段预检 + 13项验证矩阵 + Plugin Contract v1.0"
status: TODO
priority: P0
created_date: 2026-05-06
created_by: session-20260506-011
owner: ZephyrAlpha-Owner
tags:
  - script-system
  - onboarding
  - validation-matrix
  - plugin-contract
  - three-piece-suite
description: |
  将蓝图 §4 的脚本三件套入库流程全部转化为可执行验证。
  
  覆盖子节：
  - §4.1 设计原则：合法落位三目录（scripts/governance/ / src/zephyr/ / tests/）
  - §4.2 四阶段预检：A0查重 → A1定位 → A2例外论证
  - §4.3 三件套强制清单：A落位 + B manifest注册 + C运行验证
  - §4.4 入库验证矩阵 13项（V1-V13）：文件位置/前缀/manifest完整性/UTF-8/stdout/独立运行/全量回归/docstring/shebang/退出码/--warn-only/绝对路径/异常捕获/无重叠
  - §4.5 插件接口契约 Plugin Contract v1.0：CLI/退出码/输出格式/manifest注册四部分

acceptance_criteria:
  - "validate_script_onboarding.py 覆盖 V1-V12 共 12 项自动检查"
  - "Plugin Contract YAML schema 在 scripts/governance/_shared/plugin_contract_schema.yaml 中定义"
  - "新脚本入库时三件套（A/B/C）任一缺失 → run_all.py 拒绝调度"
  - "A2例外论证的脚本在 Session Log 中有完整论证记录"
  - "generate_script_manifest.py 支持 __manifest__ dict 字面量和三引号 YAML 双形态解析"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\script-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\AGENTS.md"
  - "D:\\ZephyrAlpha\\scripts\\governance\\script_manifest.yaml"
  - "D:\\ZephyrAlpha\\scripts\\governance\\check_registry_consistency.py"
  - "D:\\ZephyrAlpha\\scripts\\governance\\generators\\generate_script_manifest.py"

downstream_outputs:
  - "D:\\ZephyrAlpha\\scripts\\governance\\meta\\validate_script_onboarding.py"
  - "D:\\ZephyrAlpha\\scripts\\governance\\_shared\\plugin_contract_schema.yaml"

rollback_instructions: "git checkout -- scripts/governance/meta/validate_script_onboarding.py scripts/governance/_shared/plugin_contract_schema.yaml"

context_assembly_manifest:
  - source: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\script-system\\blueprint.md"
    sections: ["§4.1", "§4.2", "§4.3", "§4.4", "§4.5"]
  - source: "D:\\ZephyrAlpha\\AGENTS.md"
    sections: ["§6.5"]

phase: phase_1_core
effort_estimate: L
risk_level: HIGH
depends_on_task: ["TASK-OPS-0004"]
blocks_task: ["TASK-OPS-0006"]
related_blind_spots: ["B95", "B102", "B105"]
related_risks: ["R3"]
related_contracts: ["CT-Plugin-v1.0"]
card_type: implementation
upstream_blueprint_version: "5.2.1"
autonomy_level: ai_allowed_review
---

# TASK-OPS-0005: 脚本三件套入库流程落地 — §4 四阶段预检 + 13项验证矩阵 + Plugin Contract v1.0

## 1. 任务概述

蓝图 §4 定义了什么才算一个脚本"入库完成"，包含四阶段预检、三件套清单、13项验证矩阵和 Plugin Contract。当前 validate_script_onboarding.py 尚未实现，Plugin Contract 尚未独立为 YAML schema 文件。

## 2. 施工步骤

### Step 1: validate_script_onboarding.py 实现
新建 `D:\ZephyrAlpha\scripts\governance\meta\validate_script_onboarding.py`，覆盖 V1-V12：
- V1: 文件存在于正确维度目录
- V2: 文件名遵循 5 前缀约定（validate_/detect_/audit_/check_/register_）
- V3: manifest 条目完整性（dimensions + priority + timeout + args + description）
- V4: `sys.stdout.reconfigure(encoding='utf-8')` 已添加
- V5: 脚本可独立运行（subprocess 调用，exit ≤ 1）
- V6: 全量回归不破坏（调用 run_all.py）
- V7: docstring 覆盖参数/返回值/副作用（AST 解析）
- V8: shebang 已添加
- V9: 退出码约定遵守
- V10: --warn-only 参数已实现
- V11: 绝对路径使用
- V12: 异常全捕获（顶层 try/except → exit 3）

### Step 2: Plugin Contract schema 文件
新建 `D:\ZephyrAlpha\scripts\governance\_shared\plugin_contract_schema.yaml`，将蓝图 §4.5 的 YAML 代码块独立为可验证的 schema 文件。

### Step 3: run_all.py 入库检查集成
run_all.py 启动时调用 validate_script_onboarding.py 检查新脚本，三件套不完整 → 拒绝调度。

## 3. 验收标准
- [ ] validate_script_onboarding.py 对全部已注册脚本 exit ≤ 1
- [ ] plugin_contract_schema.yaml 存在且格式有效
- [ ] run_all.py 在脚本三件套不完整时拒绝调度
- [ ] __manifest__ dict 字面量解析测试通过
