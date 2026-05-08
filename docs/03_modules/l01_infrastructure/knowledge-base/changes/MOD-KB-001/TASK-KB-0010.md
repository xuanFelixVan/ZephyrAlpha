---
task_id: "TASK-KB-0010"
source_blueprint: "MOD-KB-001"
source_section: "§4.5 冷启动引导引擎"

title: "bootstrap.py 冷启动引导引擎实现——从存量文档自动生成首批 KE + MVKB 验收"
description: |
  实现蓝图 §4.5 定义的冷启动引导引擎(bootstrap.py)，填补盲点#2：(1)实现 bootstrap_from_existing_docs()——从 AGENTS.md + SSOT权威映射 + docs/03_modules/**/blueprint.md + session-logs/ 四路径全量扫描→语义分段→分类→走 G1-G5 标准管道→产出首批 VERIFIED KE(~50-80条)；(2)实现 verify_mvkb()——MVKB 三项验收标准(VERIFIED KE≥10 + 覆盖≥5 category + Context Precision≥0.70)，未达标→推送具体缺口；(3)实现 determinist_ke_hash()——sha256(category+title+source_hash)[:8]→确定性 KE ID 防止 bootstrap 多次运行产生不同 ID。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
  - "D:\\ZephyrAlpha\\AGENTS.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\ingest.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\triage.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\analyze.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\activate.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\extract.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\kb_repo.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\bootstrap.py"
    description: "新建——bootstrap_from_existing_docs() + verify_mvkb() + determinist_ke_hash() 三函数"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_bootstrap.py"
    description: "新建——bootstrap 单元测试：mock 空 ChromaDB+SQLite→验证产出 KE"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\bootstrap.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_bootstrap.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\ingest.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\triage.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\analyze.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\activate.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\extract.py"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2——BootstrapResult/MVKBStatus Pydantic 模型"
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "新建文件路径合规"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
    reason: "§4.5 定义了 bootstrap 完整 API 契约 + MVKB 验收标准 + 种子问题集"
  - file_path: "D:\\ZephyrAlpha\\AGENTS.md"
    reason: "项目宪法——冷启动的天然种子 KE 来源"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 15000
timeout_minutes: 60

acceptance_criteria:
  - "bootstrap_from_existing_docs() 接收 scan_paths list[str]→返回 BootstrapResult(total_scanned/candidates/indexed/rejected/elapsed_seconds/mvkb_achieved)"
  - "扫描真实 AGENTS.md 能提取 ≥3 条候选 KE"
  - "verify_mvkb() 返回 MVKBStatus——包含三项验收状态(is_ok+detail)"
  - "10 个种子问题全部可被 verify_mvkb() 的 Context Precision 衡量"
  - "determinist_ke_hash() 同一输入多次调用返回同一 KE ID"
  - "bootstrap 不修改已有 KE——仅追加"

rollback_instructions: |
  1. 删除 src/zephyr/kb/bootstrap.py
  2. 删除 tests/unit/test_bootstrap.py
  3. 若 bootstrap 执行后产出了 KE——删除 docs/08_knowledge/ 下由 bootstrap 生成的文件（batch_id=bootstrap）
  4. SQLite: DELETE FROM knowledge_entries WHERE source_type='bootstrap'
  5. ChromaDB: 按 batch_id=bootstrap 清理向量

depends_on: ["TASK-KB-0009"]
blocked_by: []
status: "created"
tags_fn:
  - "infra"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "experimental"
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
