---
module_id: KE-917
status: active
title: 4.3 Step 3：残留物检测
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# 4.3 Step 3：残留物检测

4.3 Step 3：残留物检测

任务完成后，检查任务操作路径下是否有不属于本次任务的残留文件：

```bash
python src/zephyr/gates/task_completion_gate.py \
  --task-id {TASK_ID} \
  --scope-paths "{scope_path_1}" "{scope_path_2}"
```

检测逻辑：
1. 扫描 `--scope-paths` 下所有文件
2. 与 deliverables + files_in_scope 做差集
3. 差集文件按以下规则分类：

| 分类 | 判定条件 | 处置 |
|------|---------|------|
| ORPHAN_SHELL | 文件大小 < 100 bytes 且内容为空壳/占位 | 删除 |
| STALE_SKELETON | import 路径指向已不存在的模块 | 删除 |
| DUPLICATE | 与项目其他文件内容完全相同 | 删除老副本 |
| LEGACY_TEST | 测试文件引用已删除的源代码 | 删除 |
| VALID_FILE | 不属于以上任何分类 | 在报告中声明，由 Owner 判定 |
