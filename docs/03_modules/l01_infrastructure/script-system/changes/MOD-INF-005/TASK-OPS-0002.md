---
task_id: TASK-OPS-0002
module_id: MOD-INF-005
title: "术语落地 — 蓝图 §1 核心概念与自动化边界落地为可验证脚本"
status: TODO
priority: P0
created_date: 2026-05-06
created_by: session-20260506-011
owner: ZephyrAlpha-Owner
tags:
  - script-system
  - terminology
  - governance
  - automation-boundary
  - three-line-system
description: |
  将蓝图 §1 中定义的 13 项核心概念落地为可被脚本验证的约束。
  
  覆盖范围：
  - §1.1 模块身份：module_id MOD-INF-005、层级 L01、优先级 P0
  - §1.2 核心职责：5 项职责（治理脚本管理、三件套入库、run_all.py 调度、pre-commit 门禁、任务系统集成）
  - §1.3 三线体系定位：第三条生产线——横切审计
  - §1.5 目标：5 项目标（统一入口、统一输出、pre-commit 自动化、12/12 覆盖、任务闭合）
  - §1.6 不包含目标：4 项明确排除（Web UI、Auto-Fixer、GitHub Actions、entity-graph 完全体）
  - §1.7 自动化不可逾越的边界：6 条红线（禁止自动修改源码/删除文件/修改配置/跳过门禁/修改登记表/自我修改）

acceptance_criteria:
  - "存在验证脚本能检测任何脚本是否触及 §1.7 的 6 条红线"
  - "§1.5 的 5 项目标均有对应的可度量检查点"
  - "§1.6 的 4 项排除在施工 Phase 规划中不出现"
  - "run_all.py --list 输出中能显示模块身份信息（module_id + priority）"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\script-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\task\\task-card-standard.md"
  - "D:\\ZephyrAlpha\\scripts\\governance\\quality-standard.md"

downstream_outputs:
  - "D:\\ZephyrAlpha\\scripts\\governance\\meta\\validate_automation_boundary.py"
  - "D:\\ZephyrAlpha\\scripts\\governance\\d11_compliance\\validate_manifest_admission.py"

rollback_instructions: "git checkout -- scripts/governance/meta/validate_automation_boundary.py"

context_assembly_manifest:
  - source: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\script-system\\blueprint.md"
    sections: ["§1.1", "§1.2", "§1.3", "§1.5", "§1.6", "§1.7"]
  - source: "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"
    sections: ["automation_boundary"]

phase: phase_0_setup
effort_estimate: M
risk_level: MEDIUM
depends_on_task: ["TASK-OPS-0001"]
blocks_task: ["TASK-OPS-0004"]
related_blind_spots: []
related_risks: ["R4"]
related_contracts: []
card_type: implementation
upstream_blueprint_version: "5.2.1"
autonomy_level: ai_allowed_review
---

# TASK-OPS-0002: 术语落地 — 蓝图 §1 核心概念与自动化边界落地为可验证脚本

## 1. 任务概述

蓝图 §1 定义了脚本系统的基础概念和边界。这些概念必须转化为可被脚本验证的硬约束，而非停留在文档层面。

## 2. 施工步骤

### Step 1: 自动化边界验证脚本
新建 `D:\ZephyrAlpha\scripts\governance\meta\validate_automation_boundary.py`：
- 检测任何治理脚本是否包含自动修改源码的逻辑（§1.7 红线 1）
- 检测任何治理脚本是否包含 `os.remove` / `shutil.rmtree` / `Path.unlink` 调用（红线 2）
- 检测任何治理脚本是否自动修改 `pyproject.toml` / `.pre-commit-config.yaml`（红线 3）
- 检测任何治理脚本是否调用 `--no-verify` 逻辑（红线 4）
- 检测任何治理脚本是否自动写入 `registry-master-index.yaml`（红线 5）
- 检测 D11/Meta 维度脚本是否修改同维度其他脚本（红线 6）

### Step 2: 目标度量实现
在 `status.py` 中增加对 §1.5 5 项目标的度量输出：
- 目标 1：run_all.py 可执行性检查
- 目标 2：脚本输出 Finding Schema 合规率
- 目标 3：pre-commit 钩子有效性
- 目标 4：12/12 维度覆盖率
- 目标 5：CRITICAL/HIGH Finding → 任务自动创建率

### Step 3: 三线体系定位落地
确保 `run_all.py --list` 输出中标注"第三条生产线"角色。

## 3. 验收标准
- [ ] `validate_automation_boundary.py` 覆盖 6 条红线
- [ ] `status.py --json` 输出包含 §1.5 5 项目标的度量值
- [ ] §1.6 的 4 项排除在本蓝图 Phase 规划中不出现
- [ ] 自动化边界脚本纳入 pre-commit 硬阻断（exit 2）
