---
module_id: KE-3345------defense-in-depth-005
title: 5.4 纵深防御（Defense in Depth）
category: documentation
ttl: permanent
---

# 5.4 纵深防御（Defense in Depth）

5.4 纵深防御（Defense in Depth）

Vibe Coding 社区验证的两条规则系统设计原则：

| 设计原则 | 内容 | 社区来源 |
|---------|------|---------|
| **距离递减遵从** | 同一文件中越靠后的规则越容易被 AI 忽略。宪法 §2（分类标准）放在文件前部，§6（一致性校验）是事后参考，布局符合此规律 | AI Harness 社区 |
| **纵深防御** | 一条值得强制执行的约束至少应在两个位置声明。§2（二元分类标准）的结果应至少出现在 AGENTS.md 或 `.cursor/rules/core-governance.mdc` 中作为引用点。单一宪法文件丢失不应导致治理体系失能 | AI Harness 社区 + Codified Context |

---
