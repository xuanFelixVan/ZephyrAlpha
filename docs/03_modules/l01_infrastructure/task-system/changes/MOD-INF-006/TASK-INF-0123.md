---
task_id: "TASK-INF-0123"
source_blueprint: "MOD-INF-006"
source_section: "蓝图 §4.1 约束 #38 + 盲点 #47"

title: "实现跨 Session 上下文复用——context_cache_key 索引 + 上下文缓存"
description: |
  跨 Session 上下文复用——context_cache_key 索引已完成任务的上下文组装结果。
  上下文缓存——任务完成时将 context_assembly_manifest 关联内容缓存。
  新任务复用——新任务可通过 context_cache_key 快速拉取已有的上下文。
  缓存有效期——每次 upstream_files 变更 → 相关缓存失效。
priority: "P2"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\models.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\task_repo.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\core\\session\\context_cache.py"
    description: "ContextCache——cache_key + 缓存写入 + 读取 + 失效"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\session\\context_cache.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

applicable_rules:
  - module_id: "MOD-INF-006"
    section: "§4.1 约束 #38"
    reason: "跨Session上下文复用"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
    reason: "§4.1 约束 #38 + 盲点 #47"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M4"
estimated_tokens: 6000
timeout_minutes: 20

acceptance_criteria:
  - "context_cache_key 按 upstream_files 组合生成唯一键"
  - "缓存写入——任务完成时将上下文写入缓存"
  - "新任务读取——命中 cache_key → O(1) 获取上下文"
  - "失效——upstream_files 任一文件修改 → 缓存键失效"

rollback_instructions: |
  1. 移除 context_cache.py

depends_on: ["TASK-INF-0102"]
blocked_by: []

status: "created"

tags_fn:
  - "infra"
  - "session"
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

# 实现跨 Session 上下文复用

## 目标

1. 上下文缓存——context_cache_key 索引
2. 写入——任务完成时缓存
3. 读取——新任务命中
4. 失效——文件变更

## 执行步骤

### 做
1. ContextCache 实现：
   - generate_key(task)——生成缓存键
   - save(task, context)——缓存上下文
   - load(task)——读取缓存
   - invalidate(file_path)——失效

### 产
- context_cache.py

### 检
```python
cache = ContextCache()
key = cache.generate_key(task)
cache.save(task, context_data)
loaded = cache.load(task)
assert loaded is not None
```

## 验收标准

| # | 指标 | 目标 |
|---|------|------|
| 1 | build | import 无错误 |
| 2 | test | 写入/读取/失效 均有测试 |
| 3 | lint | 0 errors |
