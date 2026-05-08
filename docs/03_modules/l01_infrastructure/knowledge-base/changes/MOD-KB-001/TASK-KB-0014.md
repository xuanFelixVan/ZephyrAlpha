---
task_id: "TASK-KB-0014"
source_blueprint: "MOD-KB-001"
source_section: "§5.10 知识切片机制"

title: "知识切片机制实现——五级边界信号切片器 + KE body长度约束"
description: |
  实现蓝图 §5.10 定义的五级知识切片器(knowledge_slicer)：(1)五级边界信号按优先级实现——①Markdown标题 H1/H2/H3 正则 ^#{1,3}\\s+.+$；②显式分隔符 ---/***/___；③话题转换——相邻段向量cosine<0.3→新KE；④时间跳变>30min（仅Session Log）；⑤字符硬上限>2000字符；(2)KE body长度约束——最小200字符（不足合并）、最大2000字符（超长切分）、理想500-800字符（~200-300 tokens）；(3)Session Log→KE提取比 2000行→~15-25 KE（去噪）；(4)每个切片附带 source_path+章节上下文(对标Anthropic Contextual Retrieval)。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\extract.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\batch_ingest.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\knowledge_slicer.py"
    description: "新建——SliceConfig + slice_document()→List[KnowledgeSlice] 五级边界信号实现"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_knowledge_slicer.py"
    description: "新建——切片器单元测试：长文档→验证切分点位置+KE body长度约束"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\knowledge_slicer.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_knowledge_slicer.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\extract.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\batch_ingest.py"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "KnowledgeSlice Pydantic V2 模型"
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "路径合规"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
    reason: "§5.10 定义五级边界信号表 + KE body长度约束 + 对标 Anthropic LangChain Unstructured.io"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 10000
timeout_minutes: 40

acceptance_criteria:
  - "slice_document(markdown_text)→List[KnowledgeSlice]——每个slice含(slice_id/body/chunk_context/priority_signal/char_count)"
  - "H2标题 '## 为什么选择ChromaDB' 被检测为新KE起始边界"
  - "'---' 分隔线被检测为边界信号"
  - "KE body <200字符→合并到相邻KE（不产生孤立短KE）"
  - "KE body >2000字符→强制切分（输出warning）"
  - "每个slice.source_context 含来源文档路径+章节标题"
  - "2000行 Session Log→产出15-25条KE（去噪后）"

rollback_instructions: |
  1. 删除 src/zephyr/kb/knowledge_slicer.py
  2. 删除 tests/unit/test_knowledge_slicer.py

depends_on: ["TASK-KB-0011"]
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
