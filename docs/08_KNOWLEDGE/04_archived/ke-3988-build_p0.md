---
module_id: KE-3835
title: 12.1 Build P0
category: module_blueprint
ttl: permanent
---

# 12.1 Build P0

12.1 Build P0

| # | 用例 | 前置 | 动作 | 预期 |
|:-:|------|------|------|------|
| P0-B1 | 四源合并基本通路 | VMS 有数据 + entity-graph 存在 | `await ce.build(request)` | slots 7 个非空，total_tokens ≤ budget×1.3（未压缩） |
| P0-B2 | slot_overrides 生效 | 同上 | request.slot_overrides={'code_refs':0.5} | code_refs.token_count/total ≈ 0.5 ±5% |
| P0-B3 | VMS degraded 降级 | mock VMS 返回 degraded=True | build | bundle.degraded=True，fs_fallback 激活（DEGRADE-001） |
| P0-B4 | entity-graph 缺失不阻塞 | 删除 entity_graph.json | build | 相关 slot 空但不抛异常，其他 slot 正常 |
