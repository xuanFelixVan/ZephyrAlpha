---
module_id: KE-1776---------owner---jit-------000
status: active
title: 2.20 紧急覆盖令牌——Owner签发的JIT临时越权令牌（决策 D-018-18）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2.20 紧急覆盖令牌——Owner签发的JIT临时越权令牌（决策 D-018-18）

2.20 紧急覆盖令牌——Owner签发的JIT临时越权令牌（决策 D-018-18）

> **决策 D-018-18**：在紧急情况下（生产事故、关键修复），Owner需要让Agent快速执行一个被blocked的操作。当前唯一的办法是手动修改GOV-AI-001 → 等auto-derive → 不可接受。引入紧急覆盖令牌。
>
> **可信主体**：NIST AI Agent标准——"高风险操作需要临时令牌（revocable）"。AWS STS——`assume-role` 签发临时凭证。Claude Code `bypassPermissions`——临时禁用权限检查但必须声明。

```python
