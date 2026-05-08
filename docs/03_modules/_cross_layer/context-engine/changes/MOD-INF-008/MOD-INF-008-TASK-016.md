---
task_id: "MOD-INF-008-TASK-016"
task_title: "氛围编程与1人+AI维护语境优化 — §17 落地"
module_id: "MOD-INF-008"
blueprint_section: "§17 100% AI施工 + 氛围编程语境优化建议 (§17.1, §17.2)"
status: "backlog"
priority: "P2"
layer: "cross_layer"
assigned_agent: "DeepSeek-V4-Pro"
review_agent: "GLM-4.7"
execution_model: ["DeepSeek-V4-Pro", "GLM-4.7"]
task_type: "CODE_GEN"
estimated_effort_hours: 5
actual_effort_hours: null
deadline: null
depends_on:
  - task_id: "MOD-INF-008-TASK-015"
    why: "氛围编程优化基于第十二轮 beta v/w 基础设施"
parent_task_id: null
child_task_ids: []
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\context-engine\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\context_playground.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\ContextHealthScore.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\shadow_canary.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\adversarial_robustness.py"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\ce_vibe_shortcuts.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\ce_explain_cli.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\ce_playground_v2.py"
tags: ["context-engine", "vibe-coding", "solo-dev", "cli", "dx"]
acceptance_criteria:
  - "AC-001: CE 作为 pair programmer 上下文：注入内容像 pair programming 中的开发者——知道当前 sprint 目标、最近改动、prior art"
  - "AC-002: CE 支持 spec-first + vibe-then 迭代：Build 阶段先基于 spec strict 检索；Compress 阶段 CE LLM judge 决定保留 vibe 部分"
  - "AC-003: Playground 升级为 ce_playground_v2.py：展示完整决策链 + per-KE rationale → 支持"排除此 KE"重新 build"
  - "AC-004: ce_explain_cli.py 实现 /ce:explain KE-0127 → 展示完整 inclusion_rationale"
  - "AC-005: ce_vibe_shortcuts.py 实现 /ce:vibe → 切换 vibe mode (expand top_k+降低 threshold) → /ce:strict → 恢复"
  - "AC-006: §17.2 运维决策精简对照：健康监控/成本优化/质量告警/策略动刀/安全检查 各自确认关联 DD 已实现"
rollback_instructions: "删除 ce_vibe_shortcuts.py/ce_explain_cli.py/ce_playground_v2.py，恢复被修改文件"
context_assembly_manifest:
  required_blueprints:
    - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\context-engine\\blueprint.md §17"
  required_standards: []
  required_templates: []
  required_references:
    - "D:\\ZephyrAlpha\\architecture-model\\layers\\b_context_engine.yaml"
---
# MOD-INF-008-TASK-016: 氛围编程与1人+AI语境优化

## 1. Purpose

将 §17 中的氛围编程和 1 人+AI 语境优化建议落地为具体的 CLI 工具和代码优化，提升 Owner 在 vibe coding 中的 Context Engine 交互体验。

## 2. Vibe Coding Specific Requirements (§17.1)

1. **CE as Pair Programmer**: CE 注入像 pair programming 中的开发者
2. **Spec-First + Vibe-Then**: Build 阶段 strict→Compress 阶段允许 vibe
3. **Playground as Context Unit Test**: context-as-experiment

## 3. CLI Implementation

| 文件 | 命令 | 功能 |
|------|------|------|
| ce_playground_v2.py | /sc:dry-run | 展示完整决策链 + per-KE rationale |
| ce_explain_cli.py | /ce:explain | 展示 KE inclusion_rationale |
| ce_vibe_shortcuts.py | /ce:vibe /ce:strict | 快速切换模式 |

## 4. Solo-Dev Operations (§17.2)

| 维度 | 精简策略 | 关联 DD |
|------|---------|:---:|
| 健康监控 | 1 行 Health Score dashboard; <70 发邮件 | DD80 |
| 成本优化 | 月 KE ROI report 自动淘汰 bottom-20% | DD76 |
| 质量告警 | CE Error Budget 可视化 | DD86 |
| 策略动刀 | Shadow Canary = 新策略影子 run | DD78 |
| 安全检查 | CIAgitation 每周 fuzz | DD82 |

## 5. Acceptance Criteria

- /ce:vibe 切换后 top_k 扩大、threshold 降低
- /ce:strict 恢复严格参数
- /ce:explain KE-0127 返回 JSON 包含 similarity/keyword_match/authority_boost/freshness/final_weight
- ce_playground_v2 的 dry-run 输出可展示排除某 KE 后重建的差异
