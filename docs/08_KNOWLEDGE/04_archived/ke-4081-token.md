---
module_id: KE-3927
title: 15.6 Token 预算与成本追踪
category: module_blueprint
ttl: permanent
---

# 15.6 Token 预算与成本追踪

15.6 Token 预算与成本追踪

| 条目 | 预算 | 追踪粒度 | 实施 |
|------|------|:---:|:---:|
| 单 Session LLM 成本 | ≤ $2.00 | Session | 📋 工具端无计数 |
| 单 tool call 预估 | ≤ 8000 tokens | 调用 | 📋 待 YAML 新增 `estimated_tokens` |
| 超预算处理 | 返回 `budget_exceeded` error | 实时 | 📋 待实现 |

---
