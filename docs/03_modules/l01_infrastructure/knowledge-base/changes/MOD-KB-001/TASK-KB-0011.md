---
task_id: "TASK-KB-0011"
source_blueprint: "MOD-KB-001"
source_section: "§5.1~§5.6 G1→G5 五门禁流水线"

title: "G1→G5 五门禁流水线验证与增强——逐门禁对齐蓝图定义的最新检查项"
description: |
  验证并增强已实现的 G1-G5 五门禁（ingest/triage/analyze/activate/extract.py）与蓝图 §5.2-§5.6 定义的最新检查项一致性：(1)G1 Ingest——确认 SQL注入/命令注入/XSS 输入消毒、KE Schema 必填字段完整性、KE-ID 连续递增、source_path 真实存在、UTF-8无BOM LF 换行 五项检查全部实现；(2)G2 Triage——确认 18类category分配、10域domain、14层layer、P0-P3优先级、0-1质量评分、五轴标签、>0.80向量相似度去重、TTL+half_life_days 八项检查；(3)G3 Analyze——确认深度评估、矛盾检测、depends_on依赖验证、freshness新鲜度计算、图谱连通性、CBAC评估六项；(4)G4 Activate——确认状态流转、向量化embedding、审计触发、索引更新、消费者通知五项；(5)G5 Extract——确认知识提取、外部注入、批量处理、质量门控四项。修正代码实现与蓝图的漂移。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\ingest.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\triage.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\analyze.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\activate.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\extract.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\ingest.py"
    description: "修正以对齐 §5.2 五项检查项"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\triage.py"
    description: "修正以对齐 §5.3 八项检查项"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\analyze.py"
    description: "修正以对齐 §5.4 六项检查项"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\activate.py"
    description: "修正以对齐 §5.5 五项检查项"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\extract.py"
    description: "修正以对齐 §5.6 四项检查项"
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\changes\\MOD-KB-001\\gates-audit.md"
    description: "G1-G5门禁审计报告——逐门禁逐检查项标注 IMPLEMENTED/PARTIAL/MISSING"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\ingest.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\triage.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\analyze.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\activate.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\extract.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\changes\\MOD-KB-001\\gates-audit.md"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\kb_repo.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\unified_memory_api.py"
  - "D:\\ZephyrAlpha\\docs\\08_knowledge\\**\\*.md"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
  - module_id: "PS-STD-001"
    section: "§6.12"
    reason: "修改后确保脚本注册不漂移"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
    reason: "§5.2-§5.6 定义了每道门禁的完整检查项清单"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 15000
timeout_minutes: 60

acceptance_criteria:
  - "gates-audit.md 列出 G1-G5 全部28项检查的 IMPLEMENTED/PARTIAL/MISSING 状态"
  - "所有 MISSING 项已实现代码补全"
  - "G1 输入消毒使用正则检测 SQL注入/命令注入/XSS 模式"
  - "G2 de-duplication 使用 ChromaDB 向量相似度>0.80判定"
  - "G3 矛盾检测能识别 '用 ruff' vs '用 pylint' 矛盾"
  - "G4 状态流转写入 kb_state_log"
  - "G5 质量门控——auto-extracted KE quality_score<0.6→HUMAN_REVIEW"
  - "现有11个单元测试无 regression"

rollback_instructions: |
  1. git checkout -- src/zephyr/kb/ingest.py src/zephyr/kb/triage.py src/zephyr/kb/analyze.py src/zephyr/kb/activate.py src/zephyr/kb/extract.py
  2. 删除 gates-audit.md
  3. 运行 pytest tests/unit/test_ingest.py test_triage.py test_analyze.py test_activate.py test_extract.py 确认恢复

depends_on: ["TASK-KB-0004", "TASK-KB-0007"]
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
