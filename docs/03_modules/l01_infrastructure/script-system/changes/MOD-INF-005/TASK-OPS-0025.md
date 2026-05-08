---
task_id: TASK-OPS-0025
module_id: MOD-INF-005
title: "迁移与废弃 + 依赖关系 联合落地 — §9 废弃路径/候选池 + §11 7模块依赖声明验证"
status: TODO
priority: P1
created_date: 2026-05-06
created_by: session-20260506-011
owner: ZephyrAlpha-Owner
tags:
  - script-system
  - migration
  - deprecation
  - dependency
  - contract
description: |
  将蓝图 §11（依赖关系）落地为可验证。
  
  §11：
  - 7 条依赖声明：MOD-INF-001(runtime) / MOD-INF-003(runtime) / MOD-INF-004(contract) / MOD-INF-006(contract,P0) / PS-STD-012(contract) / PS-STD-001(contract) / SCRIPT-QUALITY-001(contract)
  - 每条有版本要求

acceptance_criteria:
  - "7 条依赖（5 模块 MOD-INF-001/003/004/006/KB-001 + 2 标准 PS-STD-001/012）版本满足 §11 要求"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\script-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\module-registry.yaml"

downstream_outputs: []

rollback_instructions: "无需回滚——本任务卡仅验证现有状态"

context_assembly_manifest:
  - source: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\script-system\\blueprint.md"
    sections: ["§11"]

phase: phase_2_extend
effort_estimate: S
risk_level: LOW
depends_on_task: ["TASK-OPS-0018"]
blocks_task: ["TASK-OPS-0026"]
related_blind_spots: ["B52", "B83", "B84"]
related_risks: ["R5"]
related_contracts: []
card_type: validation
upstream_blueprint_version: "5.2.1"
autonomy_level: ai_allowed
---

# TASK-OPS-0025: 迁移与废弃 + 依赖关系 联合落地 — §9 + §11

## 1. 任务概述

蓝图 §9 定义废弃路径/候选池的处理策略。§11 定义与其他 7 个模块的契约依赖。两者均属于"蓝图层声明的承诺——验证是否兑现"。

## 2. 施工步骤

### Step 1: 废弃路径引用扫描
```bash
grep -r "_DO_NOT_USE" scripts/governance/ src/zephyr/ 2>/dev/null || echo "PASS"
```
应返回 0 结果。

### Step 2: 废弃路径残留引用检查
搜索所有 `audit_factory` 引用——应只在历史文档中出现。

### Step 3: 7 条依赖的版本约束验证
逐条检查 MOD-INF-001/003/004/006 在 module-registry.yaml 中的版本 ≥ §11 要求。

## 3. 验收标准
- [ ] 废弃路径零引用
- [ ] audit_factory 零残留
- [ ] 7 依赖模块版本满足要求
- [ ] 废弃路径在代码中已全部更新
