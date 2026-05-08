---
task_id: "TASK-INF-0006"
title: "自动对账器 reconciler.py 实现（D-023-02 + D-023-05 增量扫描完整版）"
module_id: "MOD-INF-023"
feature_id: "MOD-INF-023"
task_type: "implementation"
priority: "P0"
status: "draft"
estimated_effort: "8h"
actual_effort: null
assigned_to: null
created_by: "AI-Decomposer"
created_date: "2026-05-06"
updated_date: "2026-05-06"
depends_on: ["TASK-INF-0002","TASK-INF-0004","TASK-INF-0005"]
blocks: ["TASK-INF-0009","TASK-INF-0040"]
related_adrs: ["ADR-0022"]
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\"  # MOD-INF-021 回滚接口
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\reconciler.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\incremental_scanner.py"
acceptance_criteria:
  - "reconciler.py: AutoFixer 类含 pre_fix_snapshot()拍摄受影响文件备份+SHA256、auto_fix()执行自动修复、verify_fix()修复后重跑检测器、rollback_fix()从 pre-fix 快照恢复、verify_rollback()回滚后验证"
  - "auto_fixable 场景：路径索引自动更新、YAML注册表追加、统计数字重算、requirements.txt同步"
  - "needs_suggestion 场景：接口不一致生成结构化diff、缺失章节生成模板、幻觉引用生成删除建议、重复功能生成合并建议"
  - "incremental_scanner.py: git diff 驱动，变更影响范围计算，仅触发变更文件关联的检测器"
  - "增量依赖图：文件A变更 → 仅触发 import A 的模块关联检测器"
rollback_instructions: "git checkout src/zephyr/drift_detector/reconciler.py src/zephyr/drift_detector/incremental_scanner.py"
context_assembly_manifest:
  - file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"
    sections: ["§2.4","§2.5"]
tags: ["drift-detector","reconciler","auto-fix","D-023-02","D-023-05"]
compliance_tags: ["GOV-DOC-002"]
risks:
  - risk_id: "R-INF-023-05"
    description: "自动修复引入新漂移"
    impact: "级联失败——修复A→产生B→修B→产生C"
    likelihood: "medium"
    mitigation: "pre-fix快照保证可回滚；级联检测（TASK-INF-0040）独立监控修复链路"
    owner: "TASK-INF-0006执行者"
---

# TASK-INF-0006: 自动对账器 + 增量扫描器

## 目标

实现 `reconciler.py`（自动修复→验证→回滚闭环）和 `incremental_scanner.py`（git diff 驱动增量扫描）。对标 blueprint §2.4、§2.5。

## 执行步骤

### Step 1: Reconciler 实现

核心流程：`pre-fix快照 → 乐观并发检查(mtime) → 自动修复 → 修复后验证 → 审计日志`

- `AutoFixer.pre_fix_snapshot(files)`: 复制受影响文件到 temp + 记录 SHA256 + mtime(T0)
- `AutoFixer.auto_fix(event)`: 根据 drift_dimension 执行修复（更新路径索引/追加YAML条目/重算统计/同步requirements.txt）
- `AutoFixer.verify_fix(event)`: 重跑触发检测器
- `AutoFixer.rollback_fix(event)`: 从 pre-fix 快照恢复 → SHA256 校验 → 如校验失败 → P0 CRITICAL
- `AutoFixer.generate_suggestion(event)`: 生成结构化修复建议（diff/模板/删除建议/合并建议）

### Step 2: IncrementalScanner 实现

- `git diff HEAD~1 --name-only` → 变更文件列表
- 查 detector scope 映射缓存（哪个检测器覆盖哪些文件模式）
- 仅调度匹配的检测器
- 维护缓存：`{file_pattern: [detector_ids]}`

## 验收标准

- Reconciler 完整闭环：快照→修复→验证→回滚
- 四类 auto_fixable 场景代码实现
- 四类 needs_suggestion 场景代码实现
- IncrementalScanner LIGHT scan < 5s

## 回滚指令

`git checkout src/zephyr/drift_detector/reconciler.py src/zephyr/drift_detector/incremental_scanner.py`
