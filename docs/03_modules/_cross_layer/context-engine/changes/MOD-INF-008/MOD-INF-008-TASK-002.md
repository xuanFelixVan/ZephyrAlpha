---
task_id: "MOD-INF-008-TASK-002"
task_title: "Build 阶段实现 — context_assembler.py + intent_parser.py + intent_keyword_mapper.py"
module_id: "MOD-INF-008"
blueprint_section: "§2.1 Build 检索 + §5.1 Stage 1 Build YAML 规则 + DD4 intent_parser 10分类"
status: "backlog"
priority: "P0"
layer: "cross_layer"
assigned_agent: "DeepSeek-V4-Pro"
review_agent: "GLM-4.7"
execution_model: ["DeepSeek-V4-Pro", "GLM-4.7"]
task_type: "CODE_GEN"
estimated_effort_hours: 8
actual_effort_hours: null
deadline: null
depends_on:
  - task_id: "MOD-INF-008-TASK-001"
    why: "模块骨架已创建，可填充实现"
  - task_id: "MOD-INF-011"
    why: "VMS 蓝图以理解 search() API 契约"
parent_task_id: "MOD-INF-008-TASK-001"
child_task_ids: []
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\context-engine\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\__init__.py"
  - "D:\\ZephyrAlpha\\architecture-model\\layers\\b_context_engine.yaml"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\context_assembler.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\intent_parser.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\intent_keyword_mapper.py"
tags: ["context-engine", "build-stage", "intent-parsing", "retrieval", "vms"]
acceptance_criteria:
  - "AC-001: context_assembler.py 实现 build_context(task: TaskCard) -> RawContext，从 4 个 Collection 检索"
  - "AC-002: 4 个 Collection 检索参数符合 §2.1 表格：ke_entries×5, vibe_rules×3, blueprints×2, failure_patterns×3"
  - "AC-003: intent_parser.py 实现 IntentType 10 类枚举 (CODE_GEN, CODE_REVIEW, ANALYSIS, OPS_FIX, DOC, REFACTOR, TEST, AUDIT, QUERY, DEBUG)"
  - "AC-004: intent_parser.classify(user_prompt) 返回 IntentType，匹配 BUILD-C00 条件"
  - "AC-005: intent_keyword_mapper.py 实现 _MAP 映射表，BUILD-C01 条件：intent→keywords 非空"
  - "AC-006: 缺少映射时触发 reject（非 flag），返回 BUILD-C01 fix_hint"
  - "AC-007: 三个文件的单元测试已存在或新建：test_intent_parser.py, test_intent_keyword_mapper.py"
rollback_instructions: "恢复 context_assembler.py/intent_parser.py/intent_keyword_mapper.py 到 TASK-001 骨架状态，删除新增的测试代码"
context_assembly_manifest:
  required_blueprints:
    - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\context-engine\\blueprint.md §2.1, §5.1, §6 (DD4)"
  required_standards: []
  required_templates: []
  required_references:
    - "D:\\ZephyrAlpha\\architecture-model\\layers\\b_context_engine.yaml"
---
# MOD-INF-008-TASK-002: Build 阶段实现

## 1. Purpose

实现四阶段流水线的第一阶段 BUILD：从用户意图解析出发，通过 VMS 向量检索组装原始上下文。

## 2. Core Implementation — context_assembler.py (§2.1)

```python
def build_context(task: TaskCard) -> RawContext:
    ke_list = VMS.search("ke_entries", task.embedding, top_k=5)
    rules = VMS.search("vibe_rules", task_type_match, top_k=3)
    blueprints = VMS.search("blueprints", layer_match, top_k=2)
    failures = VMS.search("failure_patterns", task_type_match, top_k=3)
    return RawContext(ke_list, rules, blueprints, failures)
```

检索参数表：

| Collection | 检索条件 | top_k | 用途 |
|------|------|:---:|------|
| ke_entries | task_type + target_layer 语义相似 | 5 | 历史经验 |
| vibe_rules | task_type 相关治理规则 | 3 | 合规约束 |
| blueprints | target_layer 相关蓝图 | 2 | 架构参考 |
| failure_patterns | task_type 历史失败模式 | 3 | 避坑指南 |

## 3. Intent Parser — intent_parser.py (§5.1 BUILD-C00)

实现 `IntentType` 枚举 (10 类):
- CODE_GEN, CODE_REVIEW, ANALYSIS, OPS_FIX, DOC, REFACTOR, TEST, AUDIT, QUERY, DEBUG

`classify(user_prompt: str) -> IntentType`:
- on_failure: flag（仅标记，不阻断后续流程）

## 4. Keyword Mapper — intent_keyword_mapper.py (§5.1 BUILD-C01)

`_MAP: dict[IntentType, list[str]]` 映射表
`map(intent: IntentType) -> list[str]`
- 若映射结果为空：on_failure=reject, fix_hint="补充 intent→keyword 映射到 intent_keyword_mapper.py"

## 5. Key Design Decision: DD4

- 10 分类覆盖 task_type 枚举 + QUERY/DEBUG 辅助模式
- 否决方案: "30+ 细粒度" — 分类过多→keyword 精度下降
- 重评条件: 混淆率 > 10%

## 6. Acceptance Criteria

- build_context() 返回的 RawContext 包含 4 个 List
- classify("帮我修复安全漏洞") → OPS_FIX
- classify("审查这段代码") → CODE_REVIEW
- map(CODE_GEN) 返回非空关键词列表
- map(UNKNOWN) → reject + fix_hint
- pytest test_intent_parser.py test_intent_keyword_mapper.py 全部通过
