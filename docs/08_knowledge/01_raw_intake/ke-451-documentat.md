---
module_id: KE-406
status: active
title: 5.2 反幸存者偏差的查询契约
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 5.2 反幸存者偏差的查询契约

5.2 反幸存者偏差的查询契约

凡构建历史投资域（universe），**必须**经过统一接口：

```text
universe = build_universe(
    asof=T,                     # PIT 时点
    exchange='SSE,SZSE',
    include_delisted=True,      # 默认 True；False 必须在 ADR 中说明理由
    index_filter=('CSI300', T)  # PIT 指数成分过滤
)
```

**禁止**直接 `SELECT * FROM security WHERE status = 'active'`——这是幸存者偏差的最常见入口。`scripts/fitness_functions/` 应有 `test_no_survivorship_bias.py` 扫描代码中此类反模式。
