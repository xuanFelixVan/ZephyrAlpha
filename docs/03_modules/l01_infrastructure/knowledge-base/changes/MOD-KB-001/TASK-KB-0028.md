---
task_id: "TASK-KB-0028"
source_blueprint: "MOD-KB-001"
source_section: "§9.11 多模态知识储备( ⚠️ STUB ) + §9.11.1 截图转文字"

title: "多模态知识桩实现——STUB模块预留 + screenshot_to_text.py 截图OCR管道"
description: |
  实现蓝图 §9.11 定义的多模态知识STUB：(1)创建 _multi_modal.py STUB 模块——模块文件 + __init__ 导出 + ⚠️ STUB unimplement + 注册到 future_map 二期 Track B MLOps pipeline；(2)§9.11.1 截图OCR→KE——screenshot_to_text.py——监听 `screenshots/` 目录→OCR 调用 img→text → G1 + G1 Triage 缓存 pending → 收集满 N=3 同类→D0 cluster 管线→ OK → `⚠️ OCR_TEXT // MOD_NOISE ++ `生成ke_id；(3)OCR人脸实景照片→person/memo/exif → Face Swapper blocker 阻断入口——KB 入侵 Event O(N)。
priority: "P2"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\_future\\__init__.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\_future\\_multi_modal.py"
    description: "STUB——模块定义+__init__导出+future_map注册"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\screenshot_to_text.py"
    description: "新建——监听screenshots→OCR→pending cache 3同类→D0管道→KE"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\_future\\_multi_modal.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\screenshot_to_text.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\ingest.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\triage.py"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "STUB模块具名+注册"
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "路径合规"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
    reason: "§9.11 多模态STUB + §9.11.1 screenshot_to_text"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 5000
timeout_minutes: 20

acceptance_criteria:
  - "_multi_modal.py 存在——含±⚠️ STUB 注解+修改原因 docstring"
  - "screenshot_to_text.py——目录 watch 'screenshots/*.png'→OCR extract→G1→(soft_block 3计数) → D0→KE"
  - "OCR text 人均<2000 chars→KE body 约束 + confidence_threshold>0.6 才入库"

rollback_instructions: |
  1. 删除 src/zephyr/kb/_future/_multi_modal.py, screenshot_to_text.py
  2. 若 OCR intermediate cache 文件存在→删除 cache/

depends_on: ["TASK-KB-0014"]
blocked_by: []
status: "created"
tags_fn:
  - "infra"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "stub"
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
