---
module_id: KE-1071
status: active
title: AI 幻觉自动检测规则集
category: governance_rule
ttl: permanent
doc_type: knowledge_entry
---

# AI 幻觉自动检测规则集

AI 幻觉自动检测规则集

> **目的**：定义可被 pre-commit hook / CI gate / 架构门禁脚本自动执行的 AI 幻觉检测规则。与 `ai-hallucination-self-check-policy.md`（GOV-AI-003）的手动自检清单形成双层防护——GOV-AI-003 在 session 开始前由 AI 自检，本文档在代码提交时自动拦截。
>
> **来源**：提取自《开发流程七合一方案 v2.2.0》§7.4。基于七方审计融合报告的 35 条修改建议，将核心规则从 WARNING 升级为 ERROR，并扩展覆盖遗漏的幻觉模式。

---
