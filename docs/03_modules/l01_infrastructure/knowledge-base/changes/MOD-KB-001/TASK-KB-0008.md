---
task_id: "TASK-KB-0008"
source_blueprint: "MOD-KB-001"
source_section: "§3.9 知识来源矩阵 + §3.9.1 八条来源管线 + §3.9.2 Session Log YAML格式约定 + §3.9.3 聊天记录→知识提取器 + §3.9.4 聊天→KE决策树 + §3.9.5 决策记录模型"

title: "知识来源矩阵实现——八条来源管线落地 + 聊天记录→KE 提取器 + 三层决策记录模型"
description: |
  实现蓝图 §3.9 定义的知识来源矩阵：(1)§3.9.1 八条来源管线落地——Session Log自动(输入格式遵循§3.9.2 YAML约定)/ADR定稿/Blueprint变更/GitHub链接/arXiv论文/C4 Finding/KO晋升/CTR质量信号的触发条件+优先级+提取链路；(2)§3.9.3 聊天记录→知识提取器——S1语义分段器(按标题/话题转换切分) + S2三元判定器(🟢知识信号/🟡纯流程/🔵半信号) + N-01~N-04噪音四门槛 + 三触发时机(session结束/对话>30轮/Owner手动标记)，整体对接§3.9.4聊天→KE决策树的高层流程（auto-handoff-log→切片→G1→自动分流）；(3)§3.9.5 三层决策记录模型——L1 Owner画像Track C + L2 AGENTS.md §10历史决策 + L3 KE A2深度决策。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\extract.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\batch_ingest.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\source_matrix.py"
    description: "新建——八条来源管线配置+调度器"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\chat_extractor.py"
    description: "新建——S1语义分段器 + S2三元判定器 + N-01~N-04噪音过滤 + 三触发时机"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\decision_recorder.py"
    description: "新建——三层决策记录模型：L1 Track C/L2 AGENTS.md/L3 KE A2"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\extract.py"
    description: "扩展——对接到 source_matrix 和 chat_extractor"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\source_matrix.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\chat_extractor.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\decision_recorder.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\extract.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\kb_repo.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\ingest.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\activate.py"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "路径合规"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
    reason: "§3.9/§3.9.1/§3.9.2/§3.9.3/§3.9.4/§3.9.5 定义了来源矩阵+Session Log YAML格式+聊天提取器+决策树+决策记录模型"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 18000
timeout_minutes: 60

acceptance_criteria:
  - "source_matrix.py 实现8条来源管线——每条含触发条件+优先级+提取链路(G1-G5/D0)"
  - "chat_extractor.py 实现S1语义分段器——按H1/H2/H3/---/话题向量切换分段"
  - "chat_extractor.py 实现S2三元判定器——🟢知识信号/🟡纯流程/🔵半信号 三种分类"
  - "chat_extractor.py 实现N-01~N-04噪音四门槛——短句/纯命令/已存在/纯情绪过滤"
  - "decision_recorder.py 实现三层决策记录模型——L1/L2/L3 各自存储和查询"
  - "extract.py 能调用 source_matrix.get_pipeline(source_type) 获取对应提取管线"

rollback_instructions: |
  1. 删除 src/zephyr/kb/source_matrix.py, chat_extractor.py, decision_recorder.py
  2. git checkout -- src/zephyr/kb/extract.py
  3. 确认无残留引用——grep 上述三个新模块在 kb/ 目录中的 import

depends_on: ["TASK-KB-0007"]
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
