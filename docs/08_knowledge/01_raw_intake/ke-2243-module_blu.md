---
module_id: KE-2149----18-004
status: active
title: 3.8 三轨 18 类知识分类体系
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 3.8 三轨 18 类知识分类体系

3.8 三轨 18 类知识分类体系

**问题**：当前 `KeCategory` 枚举（`schemas.py` L130-142）定义了 10 个 category——其中 6 个是金融域（`strategy` / `factor` / `risk_control` / `data_governance` / `compliance` / `operations`），为量化金融系统设计的。但当前 KB 实际存储的全是**项目施工知识**（ruff 选型、AGENTS.md 规则、Session Log 教训）——分类体系和实际内容严重不匹配。

**对标**：

| 来源 | 知识分类维度 | 关键发现 |
|------|-------------|---------|
| **Vasilopoulos Codified Context**（283 sessions 实证数据） | 65% 领域知识 / 35% 行为指令 | `codebase_facts`(35%) / `domain_formulas`(20%) / `failure_modes`(15%) / `coding_conventions`(15%) / `tool_config`(10%) / `behavioral_instructions`(5%) |
| **vibe-init (Vishal)** | 10 大类 59 条治理策略 | 按"责任域"分类——每个 AI 施工动作对应一个责任域：`architecture_decisions` / `coding_standards` / `context_engineering` / `dependency_management` / `error_handling` / `git_workflow` / `project_structure` / `security` / `testing` / `tooling` |
| **n1n.ai 3-Tier Memory** | 知识优先级三分法 | HIGH（不可变核心身份）→ 直接 LTM；MID（可变偏好）→ MTM 晋升队列；LOW（瞬时上下文）→ 丢弃 |

**三轨 18 类设计**：
