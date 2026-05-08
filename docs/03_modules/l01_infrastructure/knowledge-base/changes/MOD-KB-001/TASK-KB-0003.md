---
task_id: "TASK-KB-0003"
source_blueprint: "MOD-KB-001"
source_section: "§3.1~§3.2 KE Schema 定义——31字段+字段稳定性分级"

title: "KE Schema 31字段定义落地——frozen/extendable/runtime_only三级稳定性分级实现"
description: |
  将蓝图 §3.1~§3.2 定义的 KE Schema 31 字段完整落地到代码层：(1)验证 src/zephyr/shared/schemas.py 中 KeEntry Pydantic 模型是否包含全部 31 字段（18 frontmatter + 5 runtime + 3 OPTIONAL date 字段 + 2 Phase 5 stubs + 3 Phase 4/5 reserved = 31）；(2)实现 §3.2 字段稳定性分级——frozen(11字段)/extendable(9字段)/runtime_only(5字段)——frozen字段3年不删不改类型；(3)§3.2.2 KE Markdown 物理格式——YAML frontmatter 18 字段 + body 5 段模板 + G1 6 条格式校验规则；(4)运行时字段 SQLite only 隔离——usage_count/adoption_count/helpfulness_score/last_used_at/_locked 不存在于 MD frontmatter。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
    description: "更新 KeEntry 模型——确保28字段完整 + stability 字段 + 字段级 frozen/extendable/runtime_only 注解"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\ingest.py"
    description: "更新 G1 格式校验——对接 §3.2.2 F-01~F-06 规则"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\ingest.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\kb_repo.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\triage.py"
  - "D:\\ZephyrAlpha\\docs\\08_knowledge\\**\\*.md"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2——禁止 dataclass"
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "路径架构合规"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
    reason: "§3.1~§3.2.2 定义了 KE Schema 28字段 + 字段稳定性分级 + G1 6校验规则"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
    reason: "现有 KeEntry 模型——需要对照蓝图更新"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 8000
timeout_minutes: 30

acceptance_criteria:
  - "KeEntry Pydantic 模型包含全部 31 字段（见 §3.2 字段总表）"
  - "frozen 字段（11个）有 Literal['frozen'] 类型注解——禁止删除或改类型"
  - "extendable 字段（9个）标注可追加但不可删改"
  - "runtime_only 字段（5个）标注不入 MD frontmatter"
  - "ingest.py 的 _validate_ke_format() 校验全部 F-01~F-06 规则"
  - "mypy 类型检查通过——新增字段类型完整"

rollback_instructions: |
  1. git checkout -- src/zephyr/shared/schemas.py
  2. git checkout -- src/zephyr/kb/ingest.py
  3. 确认 KeEntry model 回退到修改前状态——运行 pytest tests/unit/test_ingest.py 验证

depends_on: ["TASK-KB-0001"]
blocked_by: []
status: "done"
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
