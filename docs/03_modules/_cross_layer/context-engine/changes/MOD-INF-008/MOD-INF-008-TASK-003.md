---
task_id: "MOD-INF-008-TASK-003"
task_title: "Compress 阶段实现 — doc_compressor.py + context_budget_tracker.py + Token 三级预算"
module_id: "MOD-INF-008"
blueprint_section: "§2.2 Compress + §5.2 Stage 2 Compress YAML 规则 + §6 DD1, DD2, DD3, DD5, DD6 + §16 DD7-DD10 中压缩相关"
status: "backlog"
priority: "P0"
layer: "cross_layer"
assigned_agent: "DeepSeek-V4-Pro"
review_agent: "GLM-4.7"
execution_model: ["DeepSeek-V4-Pro", "GLM-4.7"]
task_type: "CODE_GEN"
estimated_effort_hours: 12
actual_effort_hours: null
deadline: null
depends_on:
  - task_id: "MOD-INF-008-TASK-001"
    why: "模块骨架已创建"
  - task_id: "MOD-INF-008-TASK-002"
    why: "Build 阶段的 RawContext 是 Compress 的输入"
parent_task_id: "MOD-INF-008-TASK-001"
child_task_ids: []
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\context-engine\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\context_assembler.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\config\\compression\\policy.yaml"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\doc_compressor.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\context_budget_tracker.py"
  - "D:\\ZephyrAlpha\\tests\\test_doc_compressor.py"
tags: ["context-engine", "compress-stage", "token-budget", "doc-compressor", "immutable-core"]
acceptance_criteria:
  - "AC-001: context_budget_tracker.py 实现三级预算管理 L1 80%/L2 90%/L3 95% (DD2)"
  - "AC-002: check_budget(session_id) ≤ L1_WARNING 返回状态，COMPRESS-C00 条件通过"
  - "AC-003: doc_compressor.py 实现三级压缩回退：Level1 Qwen2.5-3B 本地摘要 → Level2 规则基 → Level3 截断 (DD5)"
  - "AC-004: DocCompressor 的 CompressionPolicy 为 Pydantic frozen 不可变策略 (DD3)"
  - "AC-005: CompressionPolicy frozen 5 不变量全部通过：preserve_structure=true, preserve_provenance=true, min_chars≥100, max_chars≤10000, immutable_blocks preserved"
  - "AC-006: Token 预算分配表实现：KE 0-3000 / 规则 0-2000 / 蓝图 0-2000 / 日志 0-1000 / 总计 8000 (DD6)"
  - "AC-007: compress() 永远保留 raw_text——压缩+原始同时维护"
  - "AC-008: test_doc_compressor.py 单元测试通过"
rollback_instructions: "恢复 doc_compressor.py/context_budget_tracker.py 到骨架状态，删除 test_doc_compressor.py 新增内容"
context_assembly_manifest:
  required_blueprints:
    - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\context-engine\\blueprint.md §2.2, §5.2, §6 (DD1-DD6), §16 (DD7-DD10)"
  required_standards: []
  required_templates: []
  required_references:
    - "D:\\ZephyrAlpha\\architecture-model\\layers\\b_context_engine.yaml"
---
# MOD-INF-008-TASK-003: Compress 阶段实现

## 1. Purpose

实现四阶段流水线第二阶段 COMPRESS：在 Token 预算约束下压缩上下文，确保不溢出、不丢失关键信息。

## 2. Token Budget — context_budget_tracker.py (§2.2 + DD2 + DD6)

三级预算管理：

| 级别 | 阈值 | 行为 |
|:---:|:---:|------|
| L1_WARNING | 80% (6400/8000) | 预警——有余量做最后 compress |
| L2_CRITICAL | 90% (7200/8000) | 触发 DocCompressor.compress() → max_chars=4000, preserve_structure=true |
| L3_HARD_STOP | 95% (7600/8000) | 硬截断——不追加 context，仅保留 Always-on |

Token 预算分配表：

| 类型 | Token 预算 | 优先级 |
|------|:---:|:---:|
| KE 条目 | 0-3000 | 最高 |
| 规则/策略 | 0-2000 | 高 |
| 蓝图 | 0-2000 | 中 |
| 运行时日志 | 0-1000 | 低 |
| **总计** | **8000** | — |

## 3. DocCompressor — doc_compressor.py (§5.2 + DD3 + DD5)

三级压缩回退：

```
Level 1: Qwen2.5-3B 本地摘要模型 → 语义压缩
Level 2: 规则基摘要 → 关键段落提取
Level 3: 截断 → 超出预算直接截断
```

CompressionPolicy (Pydantic frozen, Immutable Core):
- preserve_structure=true — 保留文档结构
- preserve_provenance=true — 保留溯源信息
- min_chars≥100, max_chars≤10000
- immutable_blocks preserved — 不可变块不被压缩

COMPRESS-C01 不变量校验：
- ALL 5 不变量 PASS → 压缩通过
- 任一不变量 FAIL → CompressionInvariantError → 回退降级策略 beta 本地 LLM

## 4. Key Design Decisions

| ID | 决策 | 理由 |
|----|------|------|
| DD1 | 4 阶段流水线 | Build/Compress/Validate/Inject 各有独立失败域和降级 |
| DD2 | Token 预算三级 80%/90%/95% | 区分预警和紧急 |
| DD3 | DocCompressor Pydantic frozen | 不变量不可运行时修改 |
| DD5 | DocCompressor 三级降级 | Phase1 规则基, beta 本地 LLM, Phase3 截断 |
| DD6 | token_budget=8000 默认 | 主流模型 context window 的 10-15% |

## 5. Critical Rule: Never Drop raw_text

compress 阶段永远保留 raw_text——LSG 的 Validate 阶段需要 raw_text 做注入检测。缺失 raw_text → 安全失效。

## 6. Acceptance Criteria

- check_budget(session_id) 正确返回 L1/L2/L3 状态
- L2 触发后 doc_compressor.compress() 自动执行
- CompressionPolicy 加载后不可运行时修改 (frozen=True 验证)
- 5 不变量全部通过单元测试
- compress() 输出含 compressed_text + raw_text 双字段
- pytest test_doc_compressor.py 全部通过
