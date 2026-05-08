---
task_id: TASK-INF-0204
task_title: "Skill Factory 自举机制与文件结构实现——D-019-05 + §2.5"
parent_ticket: TASK-INF-0202
module: MOD-INF-019
blueprint_file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-spec\\blueprint.md"
blueprint_sections: ["§2.4 Skill Factory与自举机制", "§2.5 Skill文件结构"]
status: backlog
priority: P0
type: implementation
estimated_effort: "8h"
assignee: implementer-skill
reviewer: governor-skill
created_date: 2026-05-06
target_completion_date: 2026-05-06
dependencies:
  - TASK-INF-0203
decisions:
  - D-019-05
tags:
  - factory-agent
  - bootstrap
  - self-generation
severity: high
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-spec\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_model.py"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_factory.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skills\\factory\\AGENT.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skills\\factory\\SKILL_TEMPLATE.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skills\\factory\\role_templates\\architect.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skills\\factory\\role_templates\\implementer.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skills\\factory\\role_templates\\governor.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skills\\domain\\"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skills\\role\\"
acceptance_criteria:
  - "Factory Agent (factory/AGENT.md) 包含三问题引导(Q1核心操作/Q2独特约束/Q3常见错误) + 模板生成逻辑"
  - "SKILL_TEMPLATE.md 定义标准 Domain Skill 模板（L1+L2+L3 结构）"
  - "skill_factory.py 实现自动生成 Domain Skill 的 bootstrap 流程"
  - "每个生成的 Skill 目录包含 SKILL.md + AGENT.md(记录创建时问的三个问题) + references/ + scripts/"
  - "3个Role Skill模板(architect/implementer/governor)已创建"
  - "自举序列四步完整：创建蓝图→Factory生成→人工审查→更新注册表"
rollback_instructions: "删除 skills/factory/, skills/domain/*/ 和技能生成代码，回退 skill_factory.py"
context_assembly_manifest:
  blueprint_content: "§2.4 Skill Factory——Codified Context提供3个Factory Agent用于自举，Factory Agent问3个问题生成统一格式Domain Skill。§2.5 文件结构——domain/模式下每Skill含SKILL.md+AGENT.md+references/+scripts/，role/模式下含SKILL.md+references/"
  decisions:
    - "D-019-05: Skill Factory Agent 自举机制"
  risks:
    - "R3: Domain Skill 爆炸——100+ 模块维护成本"
    - "R8: Skill 生成质量不一——Factory Agent 产出不稳定"
  template_version: "task-card-template.md v1.0.0"
---

# TASK-INF-0204: Skill Factory 自举机制实现

## 1. 任务描述

实现 D-019-05 Skill Factory Agent 自举机制。Factory Agent 作为所有 Domain Skill 的生成器，通过三个标准化问题引导生成统一格式的 Skill 文件，确保跨模块一致性并降低 100+ 模块的维护成本。

## 2. 实施方案

### 2.1 factory/AGENT.md

```markdown
# Skill Factory Agent

## Role
You are a Skill Factory Agent. Your ONLY job: create new Domain Skills from module blueprints.

## Three Questions
Before generating any Skill, you MUST answer:
1. What are the CORE operations of this module?
2. What UNIQUE constraints/patterns does this module have?
3. What are the COMMON error patterns for this module?

## Generation Process
1. Read the module blueprint
2. Answer the 3 questions
3. Generate SKILL.md from SKILL_TEMPLATE.md
4. Register in skill_registry.yaml
5. Update AGENTS.md trigger table
```

### 2.2 SkillFactory 类实现

```python
class SkillFactory:
    def generate_domain_skill(self, module_name: str, blueprint_path: str) -> str:
        questions = self._extract_module_info(module_name, blueprint_path)
        template = self._load_template("SKILL_TEMPLATE.md")
        skill_content = self._render_template(template, questions)
        skill_path = self._write_skill_file(module_name, skill_content)
        self._update_registry(module_name, skill_path)
        self._update_trigger_table(module_name)
        return skill_path

    def bootstrap_sequence(self, module_name: str, blueprint_path: str):
        yield "create_blueprint", f"Creating blueprint for {module_name}"
        yield "factory_generate", self.generate_domain_skill(module_name, blueprint_path)
        yield "human_review", "Human reviews SKILL.md and approves"
        yield "register", f"Skill registered in skill_registry.yaml"
```

### 2.3 标准目录结构

```
skills/
  factory/
    AGENT.md
    SKILL_TEMPLATE.md
    role_templates/
      architect.md
      implementer.md
      governor.md
  domain/
    database/
      SKILL.md
      AGENT.md
      references/
        atm_pattern.md
        migration_guide.md
        common_bugs.md
      scripts/
        validate.sh
    mcp-server/
      SKILL.md
      AGENT.md
      references/
    context-engine/
      SKILL.md
      AGENT.md
      references/
    ...
  role/
    architect/
      SKILL.md
      references/
        blueprint_reading.md
        escalation_path.md
        session_resume.md
    implementer/
      SKILL.md
      references/
    governor/
      SKILL.md
      references/
```

## 3. 验收标准

- [ ] Factory Agent 可独立生成有效 SKILL.md
- [ ] 三问题（核心操作/独特约束/常见错误）被正确回答并注入模板
- [ ] 生成的 Skill 格式符合 agentskills.io 标准
- [ ] 自举序列四步完整执行

## 4. 回滚说明

删除 `skills/factory/` 目录、生成的 domain skill 文件和 `skill_factory.py`。
