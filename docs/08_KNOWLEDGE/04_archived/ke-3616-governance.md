---
module_id: KE-3471
title: 1.3 本视图的三层治理**管什么？**
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# 1.3 本视图的三层治理**管什么？**

1.3 本视图的三层治理**管什么？**

**核心澄清**：治理三层**横切整个系统的所有层**——业务层（src/ 14 层）、文档层（docs/ 21 抽屉）、前端层（frontend/）、治理层自己（scripts/ + .cursor/rules/）。治理三层和业务层是**平级正交**的"尺子 + 纪委 + 审计处"。

| 被管对象 | 管的规矩 | 涉及治理层 |
|---|---|---|
| `src/zephyr/l00-l14/*.py` 业务代码 | ruff/mypy/bandit/PIT/fitness functions | Policy→Factory→Runtime |
| `docs/**/*.md` 文档 | frontmatter schema/INDEX/孤儿检查 | Policy→Factory→Runtime |
| `frontend/**/*.tsx` 前端代码 | ESLint/TypeScript strict/A11y | Policy→Factory→Runtime |
| KB:decisions namespace 架构决策 | append-only/14 天实现 Gate | Policy→Factory→Runtime |
| `shared/contracts/*.py` 契约基类 | OCP 冻结（release 后不可改）| Policy→Factory→Runtime |
| **治理层自己** | 治理规则变更 review/治理脚本测试 | Policy→Factory→Runtime（自治）|

---
