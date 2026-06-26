---
module_id: KE-1909----------d-0-004
status: active
title: 2.4 Skill Factory 与自举机制（决策 D-019-05）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2.4 Skill Factory 与自举机制（决策 D-019-05）

2.4 Skill Factory 与自举机制（决策 D-019-05）

> **决策 D-019-05（新增）**：每个 Domain Skill 的目录下包含一个 **Factory Agent**（AGENT.md），包含"创建这个 Skill 时问了哪 3 个问题 + 标准脚手架模板"。新模块创建时，Factory Agent 自动生成对应的 Domain Skill。
>
> **决策依据**：
> - Codified Context 提供了三个 Factory Agent（constitution-factory / agent-factory / context-factory）用于自举
> - ZephyrAlpha 将从 19 份蓝图扩展到 14 层 × 多模块 = 100+ 模块——人工编写每个 Domain Skill 在 1 人 + AI 维护下不可持续
> - Factory Agent 确保所有 Domain Skill 格式一致（cross-session consistency）

```yaml
skill_factory:
  description: "Domain Skill 自举工厂——自动化创建新模块的 Domain Skill"

  factory_questions:
    "Q1": "这个模块的核心操作是什么？（数据库：迁移/查询；MCP：创建工具/注册协议）"
    "Q2": "这个模块有哪些独特约束/模式？（数据库：ATM两阶段提交 + SQLite WAL；MCP：stdio协议 + FastMCP装饰器）"
    "Q3": "这个模块的常见错误模式是什么？（数据库：忘记WAL模式、事务未提交；MCP：工具未注册、stdio hang）"

  factory_structure:
    domain_skill_template: |
      ---
      name: "{module_name}-specialist"
      description: "{module_description} specialist. Use when {trigger_description}."
      tools: [Read, Grep, Glob, Edit, Write, Bash, mcp__context_retrieval]
      model: "{recommended_model}"
      ---
      ## CRITICAL: Operation Mode Rules
      {role_constraints}

      ## Key Context Documents
      Load via context retrieval: `{key_context_docs}`

      ## Domain Patterns
      {domain_specific_patterns}

      ## Common Bug Patterns
      {bug_pattern_table}

      ## Key Files
      {file_reference_table}

      ## Checklist
      {execution_checklist}

  factory_path: "src/zephyr/agent-spec/skills/domain/{module}/AGENT.md"
  factory_description: "Factory Agent——新模块创建时运行此 Agent 生成 Domain Skill 的 SKILL.md"

  bootstrap_sequence:
    step_1: "创建新蓝图 blueprint.md → 运行 factory/AGENT.md"
    step_2: "Factory Agent 问 3 个问题 → 生成 SKILL.md 骨架"
    step_3: "人工审查 SKILL.md → 批准 → 注册到 skill-registry.yaml"
    step_4: "更新 AGENTS.md 触发表（新增 task_type → Domain Skill 映射）"
```

**Factory 目录结构**：

```
skills/
  factory/
    AGENT.md              # 工厂 Agent——所有 Domain Skill 的生成器
    SKILL_TEMPLATE.md     # Domain Skill 模板（L1+L2+L3 结构）
    role_templates/       # Role Skill 模板
      architect.md
      implementer.md
      governor.md
  domain/
    database/
      SKILL.md            # Domain Skill body（L1+L2）
      AGENT.md            # 创建此 Skill 时使用的 Factory Agent（参考用）
      references/         # L3 references
        atm_pattern.md
        migration_guide.md
        common_bugs.md
    mcp-server/
      SKILL.md
      AGENT.md
      references/
    context-engine/
      SKILL.md
      AGENT.md
      references/
    feedback-loop/
      SKILL.md
      AGENT.md
      references/
    # ... 每个模块一个子目录
  role/
    architect/
      SKILL.md            # 架构师角色——怎么读蓝图、怎么设计接口
      references/
    implementer/
      SKILL.md            # 实现者角色——怎么写代码、怎么跑测试
      references/
    governor/
      SKILL.md            # 治理员角色——怎么跑审计、怎么修漂移
      references/
```
