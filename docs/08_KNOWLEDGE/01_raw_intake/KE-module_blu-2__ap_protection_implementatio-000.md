---
module_id: KE-module_blu-2__ap_protection_implementatio-000
title: 2. AP Protection Implementation
category: module_blueprint
---

# 2. AP Protection Implementation

2. AP Protection Implementation

| # | Anti-Pattern | 防护代码 |
|---|-------------|---------|
| AP1 | 无 LSG 审查直接注入 | `inject()` 入口添加 `assert context.lsg_passed` |
| AP2 | compress 丢弃 raw_text | `CompressedContext` 类必须同时含 `compressed_text` + `raw_text` |
| AP3 | Flat string concat 注入 | `format_context()` 按 Layer1-4 结构化输出 |
| AP4 | 重复查 VMS | `@lru_cache(maxsize=128)` 或 `session_cache[query_hash]` |
| AP5 | 注入不存在文件路径 | `VALIDATE-C01: os.path.exists(source)` |
| AP6 | 旧 KE 与新 KE 权重相同 | `freshness_weight = exp(-age_days / half_life)` |
| AP7 | Token 预算耗尽后强行注入 | `if budget > L3_HARD_STOP: return AlwaysOnOnly` |
