---
task_id: "TASK-INF-0112"
source_blueprint: "MOD-INF-006"
source_section: "蓝图 §4.1 约束 #21 + 盲点 #31"

title: "实现 Prompt 版本化管理——版本标签 + 变更 diff 追踪 + 回退机制"
description: |
  Prompt 版本化管理——prompt_version 字段（semver 格式）记录使用的提示词版本。
  Prompt 变更 diff 追踪——不同版本间提示词的差异记录。
  回退机制——发现新版本性能退化时回退到上一个已知良好版本。
priority: "P2"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\models.py"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\prompt-registry.yaml"

downstream_outputs:
  - path: "D:\ZephyrAlpha\src\zephyr\core\adaptation\prompt_version_manager.py"
    description: "PromptVersionManager——版本标签 + diff + 回退"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\quality\\prompt_version_manager.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\prompt-registry.yaml"

applicable_rules:
  - module_id: "MOD-INF-006"
    section: "§4.1 约束 #21"
    reason: "Prompt 版本化管理"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
    reason: "§4.1 约束 #21 + 盲点 #31"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M4"
estimated_tokens: 8000
timeout_minutes: 30

acceptance_criteria:
  - "prompt_version 字段写入任务卡——使用 semver 格式"
  - "Prompt diff——两个版本间提示词差异可计算"
  - "回退——性能退化检测触发→自动回退到上一个 good_version"

rollback_instructions: |
  1. 移除 prompt_version_manager.py

depends_on: ["TASK-INF-0102"]
blocked_by: []

status: "done"

tags_fn:
  - "infra"
  - "quality"
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

ai_autonomy_level: "supervised"
autonomy_checklist: []
---

# 实现 Prompt 版本化管理

## 目标

1. Prompt 版本标签——semver 格式追踪
2. 变更 diff——版本间差异记录
3. 回退机制——性能退化自动回退

## 触发条件

- TASK-INF-0102 完成

## 执行步骤

### 做
1. PromptVersionManager 实现：
   - tag()——标记当前提示词版本
   - diff()——比较两版本差异
   - rollback()——回退到 good_version

### 产
- prompt_version_manager.py

### 检
```python
mgr = PromptVersionManager()
mgr.tag("0.4.0", prompt_content)
mgr.rollback(task, "0.3.5")
```

## 验收标准

| # | 指标 | 目标 |
|---|------|------|
| 1 | build | import 无错误 |
| 2 | test | 版本标记/diff/回退 均有测试 |
| 3 | lint | 0 errors |
