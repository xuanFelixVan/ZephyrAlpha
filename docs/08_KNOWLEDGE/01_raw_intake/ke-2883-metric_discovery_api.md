---
module_id: KE-2783
status: active
title: Metric Discovery API 命名空间过滤
category: module_blueprint
ttl: permanent
---

# Metric Discovery API 命名空间过滤

Metric Discovery API 命名空间过滤

```
list_metrics(module="MOD-INF-008")
  → 仅返回 FQMN 前缀为 "MOD-INF-008::" 的指标

search_metrics("llm_calls")
  → 返回所有 module_id 下匹配的指标，按 module_id 分组显示
  → AI 看到: {MOD-INF-008::llm_calls_total: "LLM API调用总数", MOD-INF-012::llm_calls_total: "数据库LLM查询统计"}
```

---
