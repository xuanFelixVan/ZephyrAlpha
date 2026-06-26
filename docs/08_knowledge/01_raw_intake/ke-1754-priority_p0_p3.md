---
module_id: KE-1663------p0-p3-003
status: active
title: 2.1.4 priority（优先级——P0~P3，基于引用频率 + 依赖链深度）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2.1.4 priority（优先级——P0~P3，基于引用频率 + 依赖链深度）

2.1.4 priority（优先级——P0~P3，基于引用频率 + 依赖链深度）

```python
class AssetPriority(str, Enum):
    P0 = "P0"  # 关键资产——被 5+ 文件 import / 10+ 文档引用 / Gate 直接依赖
    P1 = "P1"  # 重要资产——被 2-4 文件 import / 3-9 文档引用
    P2 = "P2"  # 常规资产——被 0-1 文件 import / 0-2 文档引用
    P3 = "P3"  # 低优资产——临时文件 / 生成产物 / 缓存
```
