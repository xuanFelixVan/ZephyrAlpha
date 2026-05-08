---
task_id: "TASK-INF-0009"
title: "并发竞争控制——乐观并发 + AI施工优先（D-023-11）"
module_id: "MOD-INF-023"
feature_id: "MOD-INF-023"
task_type: "implementation"
priority: "P0"
status: "draft"
estimated_effort: "4h"
depends_on: ["TASK-INF-0006"]
blocks: []
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\reconciler.py"  # 追加并发控制
acceptance_criteria:
  - "auto_fix_guard: pre-fix快照记录文件mtime+T0→提交前检查mtime，若>T0则ABORT转为suggestion"
  - "ai_construction_guard: 施工前注入模块漂移上下文(active events+DEEP scan摘要+已知漂移修复状态)"
  - "lock_free_design: 不引入文件锁，乐观并发+冲突检测+max_retry=3 + exponential backoff 1s/2s/4s"
  - "priority_rule: AI施工 > 自动修复；施工优先，修复等施工完成"
rollback_instructions: "git checkout src/zephyr/drift_detector/reconciler.py"
context_assembly_manifest:
  - file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"
    sections: ["§2.8"]
tags: ["drift-detector","concurrency","optimistic-locking","D-023-11"]
compliance_tags: ["GOV-DOC-002"]
risks:
  - risk_id: "R-INF-023-06"
    description: "AI施工与自动修复真正并发冲突导致数据损坏"
    mitigation: "mtime检查粒度细化到秒级；retry with exponential backoff"
---

# TASK-INF-0009: 并发竞争控制（D-023-11）

## 目标

在 reconciler.py 中追加乐观并发控制机制，防止 drift detector 自动修复与 AI 施工同时修改同一文件。对标 blueprint §2.8。

## 执行步骤

### Step 1: auto_fix_guard

- pre-fix快照扩展为 `(content, mtime, sha256)`
- 提交前：`os.path.getmtime(target) > T0` → ABORT → 记录 CONCURRENCY_CONFLICT
- mtime == T0 → 安全提交

### Step 2: ai_construction_guard

- `get_module_drift_context(module_id)`: 查询 active events + last DEEP scan + known drift status
- 注入到 task context 的 drift_context 字段

### Step 3: 冲突解决

- priority_rule: AI_CONSTRUCTION > AUTO_FIX
- 自动修复冲突后：记录冲突事件 → 等待施工完成 → 重新评估

## 验收标准

- auto_fix_guard mtime检查生效
- ai_construction_guard 可查询模块漂移上下文
- retry with exponential backoff 1s/2s/4s, max 3次
