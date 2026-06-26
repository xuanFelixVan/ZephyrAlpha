---
module_id: KE-2481
status: active
title: 8.3 扩展触发条件
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 8.3 扩展触发条件

8.3 扩展触发条件

触发维度扩容的阈值：
- 单维度脚本数 ≥ 8 → 结构审查——是否需要拆子维度
- 全局脚本数 ≥ 150 → 架构审查——manifest 是否需要分层
- 扫描耗时 ≥ 300s → 性能审查——是否需要增量扫描/缓存
