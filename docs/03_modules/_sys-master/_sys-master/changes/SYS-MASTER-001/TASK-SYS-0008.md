---
task_id: "TASK-SYS-0008"
source_blueprint: "SYS-MASTER-001"
source_section: "§11 施工指南 + §12 成本架构与Token预算"

title: "三步施工规划(Phase 0→Phase 2) + 大模型成本路由矩阵与TCO模型搭建"
description: |
  将 SYS-MASTER-001 §11 施工指南与 §12 成本架构&Token预算工程化落地。
  §11 施工指南定义三阶段规划：
  Step 1-基础设施（会话管理+环境变量）/ Step 2-数据层（供应商集成）/ Step 3-策略层+执行层+实时层+全链路测试。
  §12 成本架构含大模型选择矩阵（deepseek/glm-4.7/4.6/4.5/kimi-k2/claude-sonnet-4.5/o4-mini/gpt-5.1-codex/grok-4/gpt-5.2/qwen3-coder）
  按 cost_per_1000_tokens × estimated_tokens_per_task → route_min_cost。
  Token Budget Tiered Model（context_budget_table 按 archive/project/alerts/trade 分配）。
  TCO Model——infra/dev/ops/risk/metrics precision budget 全生命周期成本。
  本卡搭建 phase_manager.py + cost_router.py + tco_model.py。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\task\\task-lifecycle-standard.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\phase_manager.py"
    description: "§11 三步施工规划——Phase 0骨架→Phase 1功能→Phase 2全链路集成，gate check 自动化"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\cost_router.py"
    description: "§12 11个模型×cost_per_1k→route_min_cost + A/B routing 策略"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\tco_model.py"
    description: "§12 TCO 全生命周期预算——infra/dev/ops/risk/metrics 5柱"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\phase_manager.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\cost_router.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\tco_model.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l0*\\**\\*.py"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"
    reason: "§11 三步施工规划(Step1/Step2/Step3) + §12 11模型成本路由矩阵 + TCO"

assigned_model: "deepseek"
assigned_pipeline: "A/B hybrid"
pipeline_modules:
  - "M1"
  - "M2"
  - "M3"
estimated_tokens: 22000
timeout_minutes: 60

acceptance_criteria:
  - "ConstructionPhase 枚举 3 成员——PHASE_0_SKELETON / PHASE_1_FUNCTIONAL / PHASE_2_E2E——每成员含依赖+gate_check"
  - "gate_check: pass=绿色→next / warn=黄色→log+继续 / fail=红色→block"
  - "cost_router.py 按 11 模型×cost_per_1k_tokens 表→给定 estimated_tokens → 返回 min_cost_model"
  - "route(policy=THROUGHPUT or COST_MIN): A/B 双路由策略"
  - "tco_model.py 含 infra/dev/ops/risk/metrics 5柱 annual_cost + precision_budget + tolerance"

rollback_instructions: |
  git rm src/zephyr/governance/phase_manager.py cost_router.py tco_model.py
  从 script_manifest.yaml 移除注册

depends_on:
  - "TASK-SYS-0002"
blocked_by: []
status: "done"
tags_fn:
  - "infra"
tags_ly: "cross_layer"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "SYS-MASTER-001"
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
