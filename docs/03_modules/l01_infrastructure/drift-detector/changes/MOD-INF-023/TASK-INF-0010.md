---
task_id: "TASK-INF-0010"
title: "漂移预算与施工门禁实现（D-023-12）"
module_id: "MOD-INF-023"
feature_id: "MOD-INF-023"
task_type: "implementation"
priority: "P0"
status: "draft"
estimated_effort: "4h"
depends_on: ["TASK-INF-0002","TASK-INF-0005"]
blocks: []
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\gates\\"  # MOD-INF-007 Gate Engine
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\drift_models.py"  # 追加 DriftBudget 模型
  - "D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\drift_engine.py"  # 追加预算检查
acceptance_criteria:
  - "三级预算：P0=3/月(耗尽阻断G1)、P1=8/月(耗尽降级P3)、P2=15/月(耗尽仅警告)"
  - "budget_consumption: 每产生非FALSE_POSITIVE漂移消耗1预算，每月1日重置，不累积"
  - "enforcement: G1门禁evaluate(task)时检查目标模块漂移预算"
  - "BREAK_GLASS: 可绕过(需Owner审批+完整审计链)"
rollback_instructions: "git checkout src/zephyr/drift_detector/drift_models.py drift_engine.py"
context_assembly_manifest:
  - file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"
    sections: ["§2.9"]
tags: ["drift-detector","drift-budget","gate","D-023-12"]
compliance_tags: ["GOV-DOC-002"]
risks: []
---

# TASK-INF-0010: 漂移预算与施工门禁（D-023-12）

## 目标

实现 SRE 式漂移预算机制——每个模块每月漂移上限，预算耗尽后阻断新施工。对标 blueprint §2.9。

## 执行步骤

### Step 1: DriftBudget 数据模型

`tier(P0/P1/P2)`, `monthly_budget(3/8/15)`, `consumed(int)`, `remaining(int)`, `hard_limit_reached(bool)`, `reset_date(date)`

### Step 2: 预算消耗

- drift_engine 写入新 DETECTED（非 FALSE_POSITIVE）→ `budget.consume(1)`
- `budget.is_exhausted()` → P0=阻断G1, P1=降级P3, P2=警告

### Step 3: Gate Engine 集成

- `evaluate(task)` → 检查 `drift_budget.remaining <= 0 and is_hard_limit`
- BREAK_GLASS: `evaluate(task, break_glass=True)` → Owner审批 + 审计链
