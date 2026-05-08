---
module_id: KE-agent_inst-8-003
title: 8. 规则加载策略 — 三层记忆模型
category: agent_instruction
---

# 8. 规则加载策略 — 三层记忆模型

8. 规则加载策略 — 三层记忆模型

> **对标**：Cursor Rules globs（`alwaysApply` vs `globs: "*.py"`，文件级自动过滤）+ Codified Context（arXiv 2602.20478，三层记忆：热记忆 ≤400 行 → 领域触发 → 冷记忆）+ Kubernetes RBAC（最小权限原则——只加载当前任务需要的规则）。
>
> 本策略的核心理念：**AI 是"按菜单点菜"，不是"把整个厨房搬上桌"。**
