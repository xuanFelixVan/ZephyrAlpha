---
module_id: KE-documentat-3_3__governance___vs__operatio-004
title: 3.3 `governance/` vs `operational/` 边界判据
category: documentation
---

# 3.3 `governance/` vs `operational/` 边界判据

3.3 `governance/` vs `operational/` 边界判据

这是本目录最重要的架构边界。判据如下：

| 我要放一个文件…… | 对照问题 | 放 governance/ 如果…… | 放 operational/ 如果…… |
|:----------------|:--------|:---------------------|:----------------------|
| | "这个文件描述什么？" | 描述 **期望状态**（声明式） | 描述 **执行步骤**（过程式） |
| | "怎么判断？" | 能用 `policy`/`standard`/`protocol` 做 doc_type | 能用 `operational_rule` 做 doc_type |
| | 对标 | K8s Declarative Config / ITIL Policy | K8s Imperative Command / ITIL Procedure |

**正例（放对了）**：
- `governance/architecture/architecture-review-policy.md` ← 声明式：定义了"什么变更必须评审"（期望状态）
- `operational/vibe_coding/vibe-coding-session-state-runbook.md` ← 过程式：定义了"AI 加载上下文的步骤"（执行步骤）
- `operational/devops/architecture-change-playbook.md`（OPS-DEV-002）← 过程式：定义了"架构变更 L1~L4 四级操作步骤+回滚方案"（执行步骤）。该文件曾错放在 `operational/architecture/`，已于 2026-05-01 审查后迁至 `operational/devops/`——`architecture` 既是 governance 域名又是 operational 路径名违反 AGENTS.md §5.1 原则 2（责任唯一）。

---
