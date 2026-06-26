---
module_id: KE-2930
status: active
title: src/zephyr/vector-memory/cascade.py (experimental 产出)
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# src/zephyr/vector-memory/cascade.py (experimental 产出)

src/zephyr/vector-memory/cascade.py (experimental 产出)

from enum import Enum

class CascadeStrategy(str, Enum):
    SUPERSEDE = "supersede"   # ADR 替代 / 规范版本迭代
    REORDER   = "reorder"     # 任务依赖调整
    DELETE    = "delete"      # 源文件删除
    MERGE     = "merge"       # 重复条目合并

CASCADE_SCENARIOS = {
    "supersede": {
        "trigger":        "新 ADR/契约明确替代旧版",
        "action":         "旧条目 metadata.superseded_by = 新条目ID，旧 chunks 保留",
        "search_weight":  0.1,   # 检索权重降级到 10%，除非 include_superseded=True
        "gc_eligible":    False, # gc() 不清理（历史留档）
    },
    "reorder": {
        "trigger":        "任务依赖关系变更（task_deps 字段）",
        "action":         "相关条目 metadata.task_deps 更新，chunks 保持不变",
        "search_weight":  1.0,   # 正常检索
        "gc_eligible":    False,
    },
    "delete": {
        "trigger":        "git rm 源文件 / 明确声明删除",
        "action":         "所有 Collection 中该 doc_id 的 chunks 物理删除（硬删除）",
        "search_weight":  0.0,
        "gc_eligible":    True,  # 立即清理
    },
    "merge": {
        "trigger":        "去重检测（MinHash LSH / content_hash 完全相同）发现重复",
        "action":         "被合并条目 metadata.merged_into = 保留条目ID，chunks 软删除",
        "search_weight":  0.0,
        "gc_eligible":    True,  # gc() 清理被合并方
    },
}
```
