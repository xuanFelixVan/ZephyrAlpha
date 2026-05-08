---
module_id: KE-agent_inst-6_18_ai____________ai_load_pat-005
title: 6.18 AI 加载路径不可漂移铁律（AI Load Path Anti-Drift Mandate）
category: agent_instruction
---

# 6.18 AI 加载路径不可漂移铁律（AI Load Path Anti-Drift Mandate）

6.18 AI 加载路径不可漂移铁律（AI Load Path Anti-Drift Mandate）

> **v1.0.0（2026-05-04）**：对标 Cursor globs + alwaysApply + description 三层激活机制。

**核心原则**：§8.2 任务菜单是 AI 找到规则文件的**唯一入口**。AI 不得依赖"搜索文件系统"来找规则——路径映射必须在 §8.2 中显式声明。

- 任何规则文件创建/移动/删除 → AI MUST 同步更新 §8.2 任务菜单
- 任何文件路径变更 → AI MUST 立即 grep 检查 §8.2 中是否引用旧路径
- 任何新增规则文件 → AI MUST 判定归属任务类型并在 §8.2 添加路径
- 任何不再有效的路径 → AI MUST 立即从 §8.2 移除

**为什么不是重组目录结构**：业界一致做法——加载机制决定"AI 读什么"（globs/alwaysApply/progressive-disclosure），目录结构仍按人类逻辑组织。重组物理目录边际收益极低（§8.2 已实现按任务加载），但破坏性极大（82 目录 × 139+ 文档 × 80+ 脚本的全量引用链重构）。
