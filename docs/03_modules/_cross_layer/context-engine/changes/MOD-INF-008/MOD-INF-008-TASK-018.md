---
task_id: "MOD-INF-008-TASK-018"
task_title: "第十四轮终审落地 — B21-B22 + AP30-AP31 + DD95-DD96 + 跨模块契约修补"
module_id: "MOD-INF-008"
blueprint_section: "§21 第十四轮终审 B21-B22 + §21.2 DD95-DD96 + §21.3 AP30-AP31"
status: "backlog"
priority: "P1"
layer: "cross_layer"
assigned_agent: "DeepSeek-V4-Pro"
review_agent: "GLM-4.7"
execution_model: ["DeepSeek-V4-Pro", "GLM-4.7"]
task_type: "CODE_GEN"
estimated_effort_hours: 6
actual_effort_hours: null
deadline: null
depends_on:
  - task_id: "MOD-INF-008-TASK-005"
    why: "Inject 阶段需要 authority_level boost"
  - task_id: "MOD-INF-008-TASK-010"
    why: "CT-ORC-CE-001 契约需要扩展优先级规则"
parent_task_id: "MOD-INF-008-TASK-001"
child_task_ids: []
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\context-engine\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\context_injector.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\context_assembler.py"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\context_injector.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\context_assembler.py"
tags: ["context-engine", "round-14", "cross-module", "authority-level", "contract-precedence"]
acceptance_criteria:
  - "AC-001: B21 (KE Authority Chain): KE 元数据添加 authority_level 字段 — Human-Verified(2) > Agent-Generated(1) > Agent-Inferred(0) (DD95)"
  - "AC-002: B21: 检索排序时 authority_level 作为 boost factor (1.2 / 1.0 / 0.8)"
  - "AC-003: B22 (Context-Prompt Collision): CT-ORC-CE-001 契约扩展优先级规则 — CE context 优先级高于 Orc 系统提示 (DD96)"
  - "AC-004: B22: inject 阶段冲突时标记 [CE_OVERRIDES_SYSTEM_PROMPT] 让 Agent 知道以 CE 为准"
  - "AC-005: AP30 (Flat-Authority): 所有 KE 在检索/注入中按 authority_level boost"
  - "AC-006: AP31 (Split-Brain-Guidance): CE 上下文与 Orc 冲突时 CE overrides"
rollback_instructions: "恢复 context_injector.py/context_assembler.py 中的 authority/precedence 变更，移除 CT-ORC-CE-001 优先级扩展"
context_assembly_manifest:
  required_blueprints:
    - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\context-engine\\blueprint.md §21"
    - "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md §2.3"
  required_standards: []
  required_templates: []
  required_references:
    - "D:\\ZephyrAlpha\\architecture-model\\layers\\b_context_engine.yaml"
---
# MOD-INF-008-TASK-018: 第十四轮终审落地

## 1. Purpose

将第十四轮终审（源码对轨+跨模块契约审计）发现的 2 个跨模块边界盲点落地为代码修补。

## 2. KE Authority Chain (B21) — DD95

KE 元数据添加 `authority_level` 字段：
- Human-Verified: 2 (boost factor 1.2)
- Agent-Generated: 1 (boost factor 1.0)
- Agent-Inferred: 0 (boost factor 0.8)

防止珍贵的人工验证信号被 AI 噪声稀释。

## 3. CE-Orc Precedence (B22) — DD96

CE 上下文优先级高于 Orc 系统提示：

```
CE context = "task-specific ground truth"
Orc prompt = "general guidance"
```

冲突时 inject 标记 `[CE_OVERRIDES_SYSTEM_PROMPT]`，Agent 明确知道以 CE 为准。

## 4. Anti-Patterns

| ID | 破解 |
|----|------|
| AP30 (Flat-Authority) | Authority Level boost: human-verified KE 优先 |
| AP31 (Split-Brain-Guidance) | CE-Orc Precedence: CE overrides system prompt |

## 5. Acceptance Criteria

- KE 模型含 authority_level 字段（0/1/2）
- build() 检索排序应用 authority boost
- inject() 当 context 与 system prompt 冲突时标记 [CE_OVERRIDES_SYSTEM_PROMPT]
- CT-ORC-CE-001 契约文档已更新含优先级规则
