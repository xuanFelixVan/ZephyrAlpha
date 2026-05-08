---
task_id: "TASK-KB-0040"
source_blueprint: "MOD-KB-001"
source_section: "§3.5 知识衰减模型——freshness 指数衰减 + per-category half_life 表 + decay_dashboard"

title: "知识衰减模型实现——freshness = 0.5 ^ (days / half_life) + 18类默认半衰期表 + decay趋势可视化"
description: |
  实现蓝图 §3.5 定义的知识衰减模型：
  (1) 衰减公式落地——`freshness = 0.5 ^ (days_since_verified / half_life_days)`——对应 §3.2 27 freshness_score 字段；
  (2) per-category 默认半衰期表（8 Track A + 7 Track B + 3 Track C = 18 类，D1-D4 预留 365d）：
     - Track A 施工类：A1/A3/A5=180d，A2/A6/A7/A8=90d，A4=365d
     - Track B 金融类：B1=180d，B2/B5/B7=90d，B3/B6=365d，B4=90d
     - Track C 偏好类：C1/C2/C3=365d
  (3) 可视化——decay_dashboard.py——生成 KE 衰减曲线图——"哪些KE即将 < 0.5 freshness" → 红色预警线+推push；
  (4) half_life 动态调整——若 KE 被大量采用 (adoption_count>10) → half_life +50%（但 max ≤ 730d），确保高频使用的KE不被半衰期冲掉。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\kb_repo.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\decay_model.py"
    description: "新建——freshness_formula() + per_category_half_life map + boost_by_adoption()"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\decay_dashboard.py"
    description: "新建——KE衰减曲线可视化+红色预警线+ push decaying KE to Owner"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
    description: "追加 freshness_score 公式引用 + category_half_life 常量"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\decay_model.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\decay_dashboard.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\ingest.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\triage.py"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2"
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "路径合规"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
    reason: "§3.5 定义了完整的知识衰减模型——公式+半衰期表+boost机制"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 8000
timeout_minutes: 30

acceptance_criteria:
  - "decay_model.py compute_freshness(ke_entry)→float 0-1——使用 §3.5 公式 0.5^(days/half_life)"
  - "per_category_half_life 表覆盖 A1-A8/B1-B7/C1-C3 共18类——D1-D4 预留365d"
  - "boost_by_adoption(ori_half_life, adoption_count)——adoption_count>10→half_life+50%→max 730d——防止高频KE过快衰减"
  - "decay_dashboard.py 扫描全KE→0.5 freshness 红线标注——KE freshness<0.5→push Owner + NEEDS_REVIEW"
  - "dashboard 图表 PNG 保存在 docs/metrics/decay_trend_{YYYYMM}.png"

rollback_instructions: |
  1. 删除 src/zephyr/kb/decay_model.py, decay_dashboard.py
  2. git checkout -- src/zephyr/shared/schemas.py

depends_on: ["TASK-KB-0003"]
blocked_by: []
status: "created"
tags_fn:
  - "infra"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-KB-001"
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
