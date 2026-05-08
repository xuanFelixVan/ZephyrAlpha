---
module_id: KE-module_blu-2_1_build______context_assembl-004
title: 2.1 Build（检索）— context_assembler.py
category: module_blueprint
---

# 2.1 Build（检索）— context_assembler.py

2.1 Build（检索）— context_assembler.py

```python
def build_context(task: TaskCard) -> RawContext:
    ke_list = VMS.search("ke_entries", task.embedding, top_k=5)
    rules = VMS.search("vibe_rules", task_type_match, top_k=3)
    blueprints = VMS.search("blueprints", layer_match, top_k=2)
    failures = VMS.search("failure_patterns", task_type_match, top_k=3)
    return RawContext(ke_list, rules, blueprints, failures)
```

| Collection | 检索条件 | top_k | 用途 |
|------|------|:---:|------|
| ke_entries | task_type + target_layer 语义相似 | 5 | 历史经验 |
| vibe_rules | task_type 相关治理规则 | 3 | 合规约束 |
| blueprints | target_layer 相关蓝图 | 2 | 架构参考 |
| failure_patterns | task_type 历史失败模式 | 3 | 避坑指南 |
