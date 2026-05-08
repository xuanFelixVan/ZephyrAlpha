---
task_id: "MOD-INF-008-TASK-008"
task_title: "设计决策 DD1-DD10 全部实现 — 核心决策代码落地"
module_id: "MOD-INF-008"
blueprint_section: "§6 设计决策 DD1-DD6 + §16 新设计决策 DD7-DD10"
status: "backlog"
priority: "P0"
layer: "cross_layer"
assigned_agent: "DeepSeek-V4-Pro"
review_agent: "GLM-4.7"
execution_model: ["DeepSeek-V4-Pro", "GLM-4.7"]
task_type: "CODE_GEN"
estimated_effort_hours: 4
actual_effort_hours: null
deadline: null
depends_on:
  - task_id: "MOD-INF-008-TASK-002"
    why: "DD4 intent_parser 依赖 Build 阶段"
  - task_id: "MOD-INF-008-TASK-003"
    why: "DD1-DD3, DD5-DD6 依赖 Compress 阶段"
  - task_id: "MOD-INF-008-TASK-005"
    why: "DD8 Provenance 依赖 Inject 阶段"
parent_task_id: "MOD-INF-008-TASK-001"
child_task_ids: []
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\context-engine\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\context_assembler.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\context_budget_tracker.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\doc_compressor.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\context_injector.py"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\config\\compression\\policy.yaml"
tags: ["context-engine", "design-decisions", "DD1-DD10", "cross-cutting"]
acceptance_criteria:
  - "AC-001: DD1: 4 阶段流水线独立失败域 + 降级——各阶段异常不传播到下一阶段"
  - "AC-002: DD2: Token 预算三级阈值在 context_budget_tracker.py 中实现"
  - "AC-003: DD3: CompressionPolicy 为 Pydantic frozen——运行时不可修改"
  - "AC-004: DD4: intent_parser 10 分类枚举完整可用"
  - "AC-005: DD5: DocCompressor 三级降级代码就位——规则基→LLM→截断"
  - "AC-006: DD6: DEFAULT_CONTEXT_TOKEN_BUDGET=8000 常量定义"
  - "AC-007: DD7: ContextRot 幂函数 n^{-k} 在 context_rot_model.py 中实现（beta a）"
  - "AC-008: DD8: Provenance 全覆盖——所有 inject 输出含 (blueprint_id, §, ke_id)"
  - "AC-009: DD9: Eviction 三维排序 (优先级×新鲜度×相关性) 在 context_evictor.py 中实现（beta a）"
  - "AC-010: DD10: Per-Turn 增量注入——Curation Loop 不重复注入相同上下文"
rollback_instructions: "回退各文件中的 DD 实现代码到决策前状态"
context_assembly_manifest:
  required_blueprints:
    - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\context-engine\\blueprint.md §6, §16"
  required_standards: []
  required_templates: []
  required_references:
    - "D:\\ZephyrAlpha\\architecture-model\\layers\\b_context_engine.yaml"
---
# MOD-INF-008-TASK-008: 核心设计决策 DD1-DD10 实现

## 1. Purpose

确保 §6 (DD1-DD6) 和 §16 (DD7-DD10) 中所有设计决策已在代码中落地，交叉验证每个决策有对应的代码实现。

## 2. Decision Checklist

| ID | 决策 | 验证方式 |
|----|------|---------|
| DD1 | 4 阶段 vs 3 或 5 | 流水线编排代码中阶段数=4，每阶段独立 try/except |
| DD2 | Token 预算三级 80%/90%/95% | check_budget() 返回 L1/L2/L3 三种状态 |
| DD3 | DocCompressor Pydantic frozen | CompressionPolicy.model_config = {"frozen": True} |
| DD4 | intent_parser 10 分类 | len(IntentType) == 10 |
| DD5 | DocCompressor 三级降级 | compress() 含三个 fallback 分支 |
| DD6 | token_budget=8000 | DEFAULT_CONTEXT_TOKEN_BUDGET 常量 |
| DD7 | ContextRot 幂函数 n^{-k} | 数学函数在 context_rot_model.py |
| DD8 | Provenance 全覆盖 | InjectionResult.sources 含 provenance |
| DD9 | Eviction 三维排序 | sort key = priority * freshness * relevance |
| DD10 | Per-Turn 增量注入 | curation_loop 跟踪已注入 KE ID 集合 |

## 3. Acceptance Criteria

- 每一项决策可通过对应代码行/配置验证
- DD3 frozen 验证：修改 CompressionPolicy 属性抛出 ValidationError
- DD7-DD10 在 beta a 范围内实现
