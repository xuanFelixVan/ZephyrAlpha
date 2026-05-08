---
task_id: TASK-INF-0202
task_title: "四层架构实现——L0 AGENTS.md宪法 + L1 Domain Skills + L2 Role Skills + L3 Cold Memory + 触发表路由"
parent_ticket: TASK-INF-0201
module: MOD-INF-019
blueprint_file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-spec\\blueprint.md"
blueprint_sections: ["§2.1 四层架构", "§2.2 Skill触发表"]
status: backlog
priority: P0
type: implementation
estimated_effort: "8h"
assignee: implementer-skill
reviewer: governor-skill
created_date: 2026-05-06
target_completion_date: 2026-05-06
dependencies:
  - TASK-INF-0201
decisions:
  - D-019-01
  - D-019-02
tags:
  - four-layer-architecture
  - trigger-table
  - routing
severity: critical
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-spec\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_model.py"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\trigger_router.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_registry.yaml"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\AGENTS.md"
acceptance_criteria:
  - "AGENTS.md 包含完整四层架构描述（L0 ~800 tokens, L1 Domain Skills 列表, L2 Role Skills 列表, L3 Cold Memory 检索说明）"
  - "trigger_router.py 实现 stage_routing + task_routing + default fallback 三种路由模式"
  - "触发匹配精度：按七施工阶段 + 任务类型关键词双重匹配"
  - "Domain Skill 与 Role Skill 组合加载逻辑正确"
  - "冲突消除规则已内建：Domain > Role"
rollback_instructions: "删除 trigger_router.py，回退 AGENTS.md 和 skill_registry.yaml 到上版本"
context_assembly_manifest:
  blueprint_content: "§2.1 四层架构——L0 AGENTS.md宪法(always loaded ~800 tokens) → L1 Domain Skills(per-module, ~500 tokens) → L2 Role Skills(architect/implementer/governor, ~300 tokens) → L3 Cold Memory(蓝图+MCP检索, ~8000 tokens). §2.2 触发表——七施工阶段映射 + 任务类型映射表 + 默认规则fallback"
  decisions:
    - "D-019-01: 四层架构——Domain与Role分层解耦，冲突时Domain优先"
    - "D-019-02: AGENTS.md触发表路由触发加载"
  template_version: "task-card-template.md v1.0.0"
---

# TASK-INF-0202: 四层架构与触发表实现

## 1. 任务描述

实现蓝图 §2.1 定义的四层 Skill 架构（L0-L3）和 §2.2 定义的 Skill 触发表路由系统。四层架构按加载策略分层：L0 热记忆常驻、L1 Domain Skills 按需加载、L2 Role Skills 按操作模式组合、L3 Cold Memory 通过 MCP 检索。触发表对接 ZephyrAlpha 七施工阶段，提供 stage_routing + task_routing 双模式路由。

## 2. 实施方案

### 2.1 AGENTS.md 结构

```markdown
# ZephyrAlpha Agent Skills System

## L0: Constitution (~800 tokens, always loaded)
- Project topology and critical path index
- Build/Test/Lint standard commands
- Session resume protocol
- Trigger table (condensed)

## L1: Domain Skills (loaded on trigger match)
- database-specialist, mcp-specialist, context-specialist
- feedback-specialist, gate-specialist, agent-specialist
- master-blueprint, drift-detector, knowledge-specialist

## L2: Role Skills (loaded in combination with Domain)
- architect: blueprint reading, interface design
- implementer: code writing, testing, lint fixing
- governor: auditing, drift fixing, compliance

## L3: Cold Memory (MCP on-demand retrieval)
- Blueprint full text via MCP context retrieval
```

### 2.2 trigger_router.py 实现

```python
from typing import Optional, Tuple
from enum import Enum


class ConstructionStage(str, Enum):
    IDEA = "想法/草稿"
    PRE_AUDIT = "审计（施工前）"
    BLUEPRINT = "蓝图/设计"
    CONSTRUCTION = "施工/实现"
    VERIFICATION = "验收/验证"
    POST_AUDIT = "审计（施工后）"


class TriggerRouter:
    STAGE_ROUTING = {
        ConstructionStage.IDEA: {"role": "architect", "domain_default": "master-blueprint"},
        ConstructionStage.PRE_AUDIT: {"role": "governor", "domain_default": "gate-engine"},
        ConstructionStage.BLUEPRINT: {"role": "architect", "domain_match": "topic"},
        ConstructionStage.CONSTRUCTION: {"role": "implementer", "domain_match": "module"},
        ConstructionStage.VERIFICATION: {"role": "governor", "domain_match": "module"},
        ConstructionStage.POST_AUDIT: {"role": "governor", "domain_default": "drift-detector"},
    }

    TASK_ROUTING = {
        "database|migration|sql|atm": {"domain": "database-specialist", "role": "implementer"},
        "mcp server|tool|protocol": {"domain": "mcp-specialist", "role": "implementer"},
        "context|pipeline": {"domain": "context-specialist", "role": "implementer"},
        "feedback|loop": {"domain": "feedback-specialist", "role": "implementer"},
        "gate|rule|policy": {"domain": "gate-specialist", "role": "governor"},
        "permission|rbac": {"domain": "agent-specialist", "role": "governor"},
        "blueprint": {"domain": "master-blueprint", "role": "architect"},
        "audit|compliance|governance": {"domain": "drift-detector", "role": "governor"},
        "knowledge|ke": {"domain": "knowledge-specialist", "role": "implementer"},
    }

    DEFAULT = {"role": "implementer", "domain_default": None}

    def route(self, stage: Optional[ConstructionStage], task_description: str) -> Tuple[str, str]:
        ...
```

### 2.3 冲突消除规则

Domain Skill > Role Skill：当两者对同一操作给出不同指令时，Domain Skill 优先。

## 3. 验收标准

- [ ] AGENTS.md 包含完整四层架构和触发表
- [ ] 触发表能正确匹配七阶段 + 所有任务类型
- [ ] 组合加载时 Domain + Role 不超 token 预算
- [ ] Keyword+Regex 双重匹配生效

## 4. 回滚说明

删除 `trigger_router.py`，用 git revert 回退 AGENTS.md。
