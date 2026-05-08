---
task_id: TASK-INF-0203
task_title: "Progressive Disclosure 三层递进加载策略实现——D-019-04"
parent_ticket: TASK-INF-0202
module: MOD-INF-019
blueprint_file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-spec\\blueprint.md"
blueprint_sections: ["§2.3 Progressive Disclosure加载策略"]
status: backlog
priority: P0
type: implementation
estimated_effort: "6h"
assignee: implementer-skill
reviewer: governor-skill
created_date: 2026-05-06
target_completion_date: 2026-05-06
dependencies:
  - TASK-INF-0202
decisions:
  - D-019-04
tags:
  - progressive-disclosure
  - loading-strategy
  - token-efficiency
severity: high
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-spec\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_model.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_loader.py"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_loader.py"
acceptance_criteria:
  - "L1 metadata (~50 tokens) always loaded——包含 skill_id/name/description/allowed-tools/model_hint/freshness_score/last_validated"
  - "L2 body (~300-500 tokens) task-match时加载——包含 CRITICAL规则/Checklist/常量速查表/reference列表"
  - "L3 references (2000+ tokens per file) 按需探取——AI主动读取或MCP检索"
  - "SKILL.md 文件中 L1 使用 YAML frontmatter, L2 使用正文"
  - "所有 Skill 加载 token 预算 ≤ 800 tokens (Domain L2 + Role L2)"
rollback_instructions: "回退 skill_loader.py 到 progressive_load 实现前一版本"
context_assembly_manifest:
  blueprint_content: "§2.3 Progressive Disclosure——Anthropic白皮书证实frontmatter~50+body~500最优粒度，三层递进避免一次性加载2000-3000 tokens稀释AI注意力"
  decisions:
    - "D-019-04: Progressive Disclosure 三层递进加载"
  template_version: "task-card-template.md v1.0.0"
---

# TASK-INF-0203: Progressive Disclosure 加载策略实现

## 1. 任务描述

实现 D-019-04 Progressive Disclosure 三层递进加载策略。所有 Skill 采用 L1 metadata always loaded → L2 body task-match时加载 → L3 references 按需探取的递进模式。

## 2. 实施方案

### 2.1 SkillLoader.progressive_load()

```python
class SkillLoader:
    def progressive_load(self, skill_id: str) -> dict:
        l1 = self._load_l1_frontmatter(skill_id)
        l2 = self._load_l2_body(skill_id)
        result = {"l1": l1, "l2": l2}
        result["l3_available"] = self._list_l3_references(skill_id)
        return result

    def _load_l1_frontmatter(self, skill_id: str) -> dict:
        """从 SKILL.md YAML frontmatter 加载 ~50 tokens metadata"""
        with open(self._resolve_skill_path(skill_id), 'r', encoding='utf-8') as f:
            content = f.read()
        frontmatter = self._parse_yaml_frontmatter(content)
        return {
            "skill_id": frontmatter.get("skill_id"),
            "name": frontmatter.get("name"),
            "description": frontmatter.get("description"),
            "allowed_tools": frontmatter.get("allowed-tools", []),
            "model_hint": frontmatter.get("model_hint"),
            "freshness_score": frontmatter.get("freshness_score", 100.0),
            "last_validated": frontmatter.get("last_validated"),
        }

    def _load_l2_body(self, skill_id: str) -> str:
        """从 SKILL.md 正文加载 ~500 tokens body"""
        body = self._extract_body_from_skill_file(skill_id)
        if len(self._tokenize(body)) > 500:
            body = self._compress_to_critical_rules(body)
        return body

    def load_l3_reference(self, skill_id: str, ref_name: str) -> str:
        """按需加载 L3 reference 文件"""
        ref_path = self._resolve_reference_path(skill_id, ref_name)
        with open(ref_path, 'r', encoding='utf-8') as f:
            return f.read()

    def _compress_to_critical_rules(self, body: str) -> str:
        """提取仅 CRITICAL 规则段落，文本降级为关键词列表"""
        ...
```

### 2.2 SKILL.md 标准格式

```markdown
---
skill_id: SKILL-DOM-DB-001
name: database-specialist
description: "Database domain specialist for migrations, queries, and schema design"
allowed-tools: [Read, Grep, Glob, Edit, Write, Bash, mcp__context_retrieval]
model_hint: DeepSeek
freshness_score: 100.0
last_validated: 2026-05-06
---

# Domain Skill: Database Specialist

## CRITICAL: Always use ATM two-phase commit pattern

## Checklist
- [ ] BEGIN TRANSACTION before any DML
- [ ] COMMIT / ROLLBACK at end
- [ ] WAL mode enabled for SQLite

## Key Constants
| Pattern | Value |
|---------|-------|
| ATM_TIMEOUT_MS | 5000 |

## References (L3, on-demand)
- atm_pattern.md
- migration_guide.md
- common_bugs.md
```

## 3. 验收标准

- [ ] Skill 文件 YAML frontmatter 解析正确
- [ ] L1/L2/L3 加载层次分明
- [ ] Domain L2 + Role L2 ≤ 800 tokens
- [ ] L3 reference 按需检索可用

## 4. 回滚说明

`git checkout <previous_commit> -- src/zephyr/agent_spec/skill_loader.py`
