---
task_id: "TASK-INF-0125"
source_blueprint: "MOD-INF-006"
source_section: "蓝图 §4.1 约束 #29 + 盲点 #38"

title: "实现多文件原子写入——任务关联多个产出物的一次性写入"
description: |
  多文件原子写入——任务产出物（downstream_outputs）可一次性写入多文件。
  事务语义——either all succeed or none applied。
  回滚支持——任一文件写失败→回滚所有已写文件。
  冲突检测——写入前验证无其他进行中任务冲突。
priority: "P2"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\models.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\core\\reliability\\atomic_writer.py"
    description: "AtomicWriter——多文件原子写入 + 回滚"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\reliability\\atomic_writer.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

applicable_rules:
  - module_id: "MOD-INF-006"
    section: "§4.1 约束 #29"
    reason: "多文件原子写入"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
    reason: "§4.1 约束 #29 + 盲点 #38"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M4"
estimated_tokens: 6000
timeout_minutes: 20

acceptance_criteria:
  - "atomic_write(files) 全成功——无部分写入"
  - "任一失败→已写文件全部回滚（恢复原始内容）"
  - "file_conflict 检测——与 WIP 任务字段重叠 → 拒绝写入"

rollback_instructions: |
  1. 移除 atomic_writer.py

depends_on: ["TASK-INF-0102"]
blocked_by: []

status: "created"

tags_fn:
  - "infra"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-006"

completed_gates: []
blocked_gates: {}

artifact_paths: []
audit_findings: []
ke_entries: []

ai_autonomy_level: "semi_autonomous"
autonomy_checklist: []
---

# 实现多文件原子写入

## 目标

1. 原子写入——全成功或全失败
2. 回滚——失败时恢复原始内容
3. 冲突检测——与进行中任务冲突

## 触发条件

- TASK-INF-0102 完成

## 执行步骤

### 做
1. AtomicWriter 实现：
   - write(files_dict)——原子写入
   - rollback(written_files)——恢复备份
   - check_conflicts(tasks)——WIP冲突

### 产
- atomic_writer.py

### 检
```python
writer = AtomicWriter()
writer.write({"path1.md": "content1", "path2.py": "content2"})
```

## 验收标准

| # | 指标 | 目标 |
|---|------|------|
| 1 | build | import 无错误 |
| 2 | test | 原子写入/回滚/冲突 均有测试 |
| 3 | lint | 0 errors |
