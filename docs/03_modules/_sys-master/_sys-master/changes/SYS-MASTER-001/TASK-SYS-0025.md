---

task_id: "TASK-SYS-0025"
source_blueprint: "SYS-MASTER-001"
source_section: "§35 第三方依赖管理 + §38 SPOF消除 + §39 WQA氛围编程质量保障"

title: "第三方依赖三级分级(Tier1核心/Tier2增强/Tier3可选)管理体系 + SPOF四型消除(经纪商/数据源/LLM/Owner) + WQA七维评分(W1-W7)体系搭建"
description: |
  将 §35 第三方依赖管理 + §38 SPOF消除 + §39 氛围编程质量保障三合一落地为依赖韧性与质量度量体系。
  §35 定义 3 级依赖分级：
  Tier1 核心（行情API + 经纪商API + DB）→ 双源冗余。
  Tier2 增强（LLM API）→ 多模型路由（§12.3）。
  Tier3 可选（备用数据源）→ best-effort，不告警。
  §38 定义 4 类 SPOF 消除：
  （1）单一经纪商API → 多经纪商备份 + 应急平仓（§51）。
  （2）单一数据源 → 双源交叉验证（§29）。
  （3）单一 LLM 模型 → 多模型路由 + Fallback（§12.3）。
  （4）Owner 离线 → 冻结模式 + 分级响应（§70）。
  §39 定义 WQA 七维加权评分（每 Session）：
  W1 Test增量（0.20）：新代码的新增测试覆盖率。
  W2 蓝图对齐（0.15）：产出是否符合蓝图设计。
  W3 ruff 0 warning（0.10）：Lint 基线检查。
  W4 Gate不新增失败（0.20）：G0-G7门禁全绿？
  W5 Owner不回退（0.15）：是否被Owner revert。
  W6 Session完成率（0.10）：（产出数）/（承诺数）× 100%。
  W7 Token效率（0.10）：消耗Token/产出实用性（§12）。
  本卡搭建 dependency_manager.py + spof_checker.py + wqa_scorer.py。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\dependency_manager.py"
    description: "§35 3级依赖分级 Tier1核心(Trade/Broker/DB)→Tier2增强(LLM)→Tier3可选(BestEffort)"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\spof_checker.py"
    description: "§38 4类 SPOF消除——Broker/DataSource/LLM/Owner→冗余检测→SPOF report"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\wqa_scorer.py"
    description: "§39 WQA 7维评分 W1-W7——Test增量/蓝图对齐/ruff/Gate/Owner不回退/Session完成率/Token效率"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\dependency_manager.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\spof_checker.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\wqa_scorer.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l*\\**\\*.py"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"
    reason: "§35 T1/T2/T3依赖分级 + §38 4类SPOF消除 + §39 W1-W7 WQA评分"

assigned_model: "deepseek"
assigned_pipeline: "A/B hybrid"
pipeline_modules:
  - "M1"
  - "M2"
  - "M3"
estimated_tokens: 22000
timeout_minutes: 60

acceptance_criteria:
  - "dependency_manager.py 实现 DependencyTier 枚举（T1_CORE/T2_ENHANCED/T3_OPTIONAL）——每级 config list（APIs/Libs/DataSources）+ redundancy Boolean——T1 MUST 双源验证· register all deps→ validate tier→ output DEP_REGISTRY"
  - "spof_checker.py 实现 SPOFChecker——check 4 domain（BrokerPool≥2?/DataSource交叉验证?/LLMRoute fallback?/Owner离线响应?)——output SPOF_Report（per domain: is_SPOF+风险+消除建议）"
  - "wqa_scorer.py 实现 WQA 7维加权评分——W1（test_cov Δ%）/W2（blueprint_align check）/W3（ruff warn count）/W4（gate G0-G7 0 new fail）/W5（owner_revert Boolean）/W6（session_completion rate）/W7（token_efficiency ratio）→ composite WQA = Σ w_i×s_i"
  - "script_manifest.yaml 注册全部 3 个 .py"

rollback_instructions: |
  1. 删除 dependency_manager.py / spof_checker.py / wqa_scorer.py
  2. 从 script_manifest.yaml 移除注册

depends_on:
  - "TASK-SYS-0023"
blocked_by: []
status: "done"
tags_fn:
  - "qa"
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
blueprint_id: DOM-GOV-001
---
