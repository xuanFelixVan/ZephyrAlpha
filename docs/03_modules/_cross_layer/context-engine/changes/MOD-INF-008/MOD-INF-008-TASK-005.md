---
task_id: "MOD-INF-008-TASK-005"
task_title: "Inject 阶段实现 — context_injector.py 四层结构化注入"
module_id: "MOD-INF-008"
blueprint_section: "§2.4 Inject + §5.4 Stage 4 Inject YAML 规则"
status: "backlog"
priority: "P0"
layer: "cross_layer"
assigned_agent: "DeepSeek-V4-Pro"
review_agent: "GLM-4.7"
execution_model: ["DeepSeek-V4-Pro", "GLM-4.7"]
task_type: "CODE_GEN"
estimated_effort_hours: 6
actual_effort_hours: null
deadline: null
depends_on:
  - task_id: "MOD-INF-008-TASK-004"
    why: "Validate 阶段的校验上下文是 Inject 的输入"
parent_task_id: "MOD-INF-008-TASK-001"
child_task_ids: []
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\context-engine\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\prompt_registry.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\context_budget_tracker.py"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\context_injector.py"
  - "D:\\ZephyrAlpha\\tests\\test_context_injector.py"
tags: ["context-engine", "inject-stage", "structured-injection", "four-layer", "session"]
acceptance_criteria:
  - "AC-001: context_injector.py 实现 inject(session: AgentSession, context: ValidatedContext) -> InjectionResult (返回 token_count + sources)"
  - "AC-002: INJECT-C00 四层结构化注入正确实现：Layer1(system)/Layer2(rules)/Layer3(knowledge)/Layer4(examples)"
  - "AC-003: Layer1 AGENTS.md core rules → always-on, 不受 token 预算约束"
  - "AC-004: Layer2 CT-* 相关合同 + blueprints → 按 task_type 注入"
  - "AC-005: Layer3 KE + failure_patterns → priority 排序注入"
  - "AC-006: Layer4 类似任务成功案例 → 仅相似度 > 0.7 注入"
  - "AC-007: INJECT-C01 验证条件：session.system_prompt 包含所有 4 层 AND 总 tokens ≤ session_limit"
  - "AC-008: 超出 limit → 重新 compress → 降低 knowledge 层 top_k"
  - "AC-009: 注入加 provenance 溯源字段 (DD8, beta a 范围)"
  - "AC-010: test_context_injector.py 通过"
rollback_instructions: "恢复 context_injector.py 到骨架状态，删除测试新增内容"
context_assembly_manifest:
  required_blueprints:
    - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\context-engine\\blueprint.md §2.4, §5.4, §16 (DD8)"
  required_standards: []
  required_templates: []
  required_references:
    - "D:\\ZephyrAlpha\\architecture-model\\layers\\b_context_engine.yaml"
---
# MOD-INF-008-TASK-005: Inject 阶段实现

## 1. Purpose

实现四阶段流水线第四阶段 INJECT：将校验通过的上下文以四层结构注入到 Agent session 的 system_prompt 中。

## 2. Core Implementation — context_injector.py (§2.4)

```python
def inject(session: AgentSession, context: ValidatedContext) -> InjectionResult:
    full_context = format_context(context)
    session.system_prompt += full_context
    return InjectionResult(token_count, sources)
```

## 3. Four-Layer Structured Injection (§5.4 INJECT-C00)

```
Layer1 (system): AGENTS.md core rules → always-on, 不受 token 预算
Layer2 (rules):  CT-* 相关合同 + blueprints → 按 task_type 注入
Layer3 (knowledge): KE + failure_patterns → priority 排序
Layer4 (examples): 类似任务成功案例 → 仅相似度 > 0.7 注入
```

Anti-Pattern AP3 直接破解——禁止 Flat string concat 注入（system/rules/knowledge/examples 混在一起）。

## 4. Injection Verification (§5.4 INJECT-C01)

```
check: "session.system_prompt 包含所有 4 层 AND 总 tokens ≤ session_limit"
on_failure: auto_fix
fix_hint: "超出 limit → 重新 compress → 降低 knowledge 层 top_k"
```

## 5. Key Design Decision: DD8 Provenance

Provenance 全覆盖——注入时附加溯源字段 (blueprint_id, §, ke_id)。上下文致错时的唯一追溯链。

## 6. Acceptance Criteria

- inject() 返回 InjectionResult 含 token_count + sources
- format_context() 按四层结构输出，不混合层级
- Layer1 注入的 AGENTS.md rules 不计入 token budget
- Layer4 仅注入相似度 > 0.7 的 examples
- 超出 token limit 时自动降低 knowledge 层 top_k
- 注入响应含 provenance 字段
- pytest test_context_injector.py 通过
