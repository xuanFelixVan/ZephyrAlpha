---
task_id: TASK-INF-0201
task_title: "Agent Spec 模块骨架搭建——§1概述与模块定位落地"
parent_ticket: null
module: MOD-INF-019
blueprint_file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-spec\\blueprint.md"
blueprint_sections: ["§1 概述与模块定位"]
status: backlog
priority: P0
type: scaffolding
estimated_effort: "4h"
assignee: implementer-skill
reviewer: governor-skill
created_date: 2026-05-06
target_completion_date: 2026-05-06
dependencies:
  - MOD-INF-020 (audit-trail)
  - MOD-INF-021 (rollback)
  - MOD-INF-010 (feedback-loop)
  - MOD-INF-018 (rbac)
  - MOD-INF-024 (budget-enforcer)
  - MOD-INF-005 (script-system)
  - MOD-INF-022 (escalation)
  - MOD-KB-001 (knowledge-base)
tags:
  - agent-spec
  - scaffold
  - infrastructure
  - l01
severity: critical
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-spec\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\document\\directory-structure-standard.md"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\__init__.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_model.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_loader.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_registry.yaml"
acceptance_criteria:
  - "模块目录 src/zephyr/agent_spec/ 已创建，含 __init__.py"
  - "skill_model.py 定义 Skill 核心 Pydantic V2 数据模型（Domain/Role/TriggerTable）"
  - "skill_loader.py 实现四层架构 L0-L3 加载骨架"
  - "skill_registry.yaml 初始注册表结构已建立"
  - "所有 imports 路径符合目录结构标准"
rollback_instructions: "删除 src/zephyr/agent_spec/ 整个目录，回退 __init__.py 到空白状态"
context_assembly_manifest:
  blueprint_content: "§1 概述——Agent Spec 是 ZephyrAlpha 的 Multi-Skill Agent 系统定义模块（MOD-INF-019），提供 19+ AI Agent 的领域/角色知识、执行约束和工作流协议"
  cross_references:
    - "MOD-INF-020: audit-trail 模块——Skill 事件审计日志写入"
    - "MOD-INF-021: rollback 模块——Skill 执行前 checkpoint"
    - "MOD-INF-010: feedback-loop 模块——Skill 成功/失败反馈"
    - "MOD-INF-018: rbac 模块——每 Skill allowed-tools"
    - "MOD-INF-024: budget-enforcer 模块——Skill token 预算"
    - "MOD-INF-005: script-system 模块——Skill 脚本集成"
    - "MOD-INF-022: escalation 模块——Skill 升级委托路径"
    - "MOD-KB-001: knowledge-base 模块——Skill 知识双向同步"
  decisions:
    - "D-019-01: 四层架构 L0 AGENTS.md → L1 Domain → L2 Role → L3 Cold Memory"
    - "D-019-02: AGENTS.md 触发表路由触发加载"
  risks:
    - "R1: 蓝图与 Skill 漂移——蓝图更新但 Skill 未同步"
  template_version: "task-card-template.md v1.0.0"
---

# TASK-INF-0201: Agent Spec 模块骨架搭建

## 1. 任务描述

根据蓝图 §1 概述与模块定位，创建 Agent Spec 模块的基础骨架代码与目录结构。Agent Spec 是 ZephyrAlpha L01 基础设施层的核心模块，负责定义和管理 Multi-Skill Agent 系统——包括 Skill 加载/路由/执行/治理的全生命周期。

## 2. 实施方案

### 2.1 目录创建

```
src/zephyr/agent_spec/
├── __init__.py
├── skill_model.py
├── skill_loader.py
├── skill_registry.yaml
├── skills/
│   ├── factory/
│   │   └── AGENT.md
│   ├── domain/
│   └── role/
├── scripts/
├── references/
└── tests/
```

### 2.2 skill_model.py 核心数据模型

```python
from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional, List, Dict
from datetime import datetime


class SkillTier(str, Enum):
    L0_CONSTITUTION = "L0"
    L1_DOMAIN = "L1"
    L2_ROLE = "L2"
    L3_COLD_MEMORY = "L3"


class SkillType(str, Enum):
    DOMAIN = "domain"
    ROLE = "role"


class SkillStatus(str, Enum):
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    RETIRED = "retired"
    REMOVED = "removed"


class ProgressiveLevel(str, Enum):
    L1_METADATA = "L1"
    L2_BODY = "L2"
    L3_REFERENCES = "L3"


class SkillModel(BaseModel):
    skill_id: str = Field(..., pattern=r"^SKILL-[A-Z]{3}-[A-Z]{2,3}-\d{3}$")
    name: str
    description: str
    skill_type: SkillType
    tier: SkillTier
    status: SkillStatus = SkillStatus.DEPRECATED
    allowed_tools: List[str]
    model_hint: Optional[str] = None
    freshness_score: float = Field(default=100.0, ge=0.0, le=100.0)
    last_validated: Optional[datetime] = None
    version: str = "0.1.0"
    token_budget_l1: int = 50
    token_budget_l2: int = 500
    author: str = "factory-agent"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    path: str
    references: List[str] = []
    upstream_modules: List[str] = []
```

### 2.3 skill_loader.py 加载器骨架

```python
class SkillLoader:
    def load_l0(self) -> dict: ...
    def load_l1_metadata(self, skill_id: str) -> dict: ...
    def load_l2_body(self, skill_id: str) -> str: ...
    def load_l3_references(self, skill_id: str, ref_name: str) -> str: ...
    def progressive_load(self, skill_id: str, level: ProgressiveLevel) -> dict: ...
```

### 2.4 skill_registry.yaml 初始注册表

```yaml
registry_version: "1.0.0"
last_updated: "2026-05-06T00:00:00Z"
skills:
  domain: {}
  role: {}
metadata:
  total_skills: 0
  active_skills: 0
  deprecated_skills: 0
```

## 3. 验收标准

- [ ] 模块目录完整创建
- [ ] Pydantic V2 数据模型可序列化/反序列化
- [ ] SkillLoader 四层加载框架可运行
- [ ] 注册表 YAML 格式合法

## 4. 回滚说明

删除整个 `src/zephyr/agent_spec/` 目录即可完全回滚。
