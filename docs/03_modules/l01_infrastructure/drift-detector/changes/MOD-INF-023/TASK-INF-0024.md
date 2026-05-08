---
task_id: "TASK-INF-0024"
title: "AI 施工场景专用检测器——6类AI特有漂移模式检测器实现"
module_id: "MOD-INF-023"
feature_id: "MOD-INF-023"
task_type: "implementation"
priority: "P0"
status: "draft"
estimated_effort: "12h"
depends_on: ["TASK-INF-0002"]
upstream_files: ["D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"]
downstream_outputs: ["D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\drift_engine.py"]
acceptance_criteria:
  - "ai_hallucination_import: AST解析import→交叉验证模块存在性→sys.path检查→zephyr内部模块验证→_detector_registry验证"
  - "ai_broken_logic: 三个子检查(context_window_truncation签名>5参数+实现<3行/not_implemented_without_fallback无try/except/todo_ratio>5%标记)"
  - "ai_duplicate_functionality: 函数签名归一化→Jaccard>0.7标记→参数签名对比→生成合并建议(推荐保留)"
  - "ai_session_style_drift: dataclass vs pydantic混用检测/sync vs async混用/命名规范一致性"
  - "ai_knowledge_pollution: 维护deprecated_api_kb.yaml→AST扫描函数调用→匹配废弃API→生成升级建议"
  - "ai_cross_session_repair_conflict: drift_events中同一drift_id被多session修复→冲突检测"
rollback_instructions: "git checkout src/zephyr/drift_detector/drift_engine.py"
context_assembly_manifest: [{file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md", sections: ["§4"]}]
tags: ["drift-detector","AI-detectors","ai-engineering"]
---
# TASK-INF-0024: AI 施工场景6类专用检测器
对标 §4 AI施工场景专用检测器。实现6类检测器：幻觉import(P0)/死码积累/逻辑断裂(P1含3子检查)/重复功能(P2/Jaccard>0.7)/风格漂移(P3)/知识污染(P2/deprecated_api_kb)/跨session修复冲突(P1)。
