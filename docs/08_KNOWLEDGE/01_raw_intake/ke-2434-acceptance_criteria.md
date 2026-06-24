---
module_id: KE-2339
status: active
title: 6. Acceptance Criteria
category: module_blueprint
---

# 6. Acceptance Criteria

6. Acceptance Criteria

- inject() 返回 InjectionResult 含 token_count + sources
- format_context() 按四层结构输出，不混合层级
- Layer1 注入的 AGENTS.md rules 不计入 token budget
- Layer4 仅注入相似度 > 0.7 的 examples
- 超出 token limit 时自动降低 knowledge 层 top_k
- 注入响应含 provenance 字段
- pytest test_context_injector.py 通过
