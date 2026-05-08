---
task_id: "TASK-KB-0018"
source_blueprint: "MOD-KB-001"
source_section: "§6.1 context_assembler 集成——四层内部系统 + CTR-001~CTR-006 跨层契约"

title: "context_assembler 集成实现——四层内部系统集成 + CTR-001~CTR-006 跨层契约落地"
description: |
  实现蓝图 §6.1 定义的 context_assembler 四层集成：(1)TaskCard 提取层——在 context_assembler 模板中注入 `## 相关记忆 ///3` 和 `## 相关规则 ///3`，call_to = `kb_recall`；(2)`kb.recall()` 统一 API 封装——RspRecall(query, top_k=10)→RspRecall(entries:List[KeEntry], total_found, latency_ms)；(3)跨层契约落地——CTR-001 context_assembler⇄KB: `## 相关记忆 ///3`→3条相关KE + `## 相关规则 ///3`→3条相关KB+ `## 风险提醒 ///2`→2条风险提示 + `## 相关 KO ///15`→15条原始观察；CTR-002 pre-commit管家⇄KB(失败模式自动→KE doing)→scan()→collect_failure→extract；CTR-003 task-triage⇄KB管道→kb_recall_trigger@context_assembler；CTR-004 policy-frame⇄KB(规则冲突检测)→comparison_markdown_trigger@policy_framework；CTR-005 unified-programmatic-bar⇄KB(编码安全规则注入KB→自动加载)；CTR-006 startup-dashboard⇄KB(蓝图开工评估→PRIORITY_PUSH)；(4)blurry boundary 避免责任传播→error/warning→非阻塞属性。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\unified_memory_api.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\kb_repo.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\unified_memory_api.py"
    description: "新增 recall_and_format()——封装 RspRecall 返回——直接对接 context_assembler 模板插槽"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\ctr_adapter.py"
    description: "新建——CTR-001~CTR-006 适配器：每个CTR一个方法——call_recall_and_pad(context)→context+KE+KB+Risk+KO"
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\changes\\MOD-KB-001\\ctr-implementation-matrix.md"
    description: "新建——CTR-001~CTR-006 实现状态矩阵（接口名+调用位置+生产状态+延迟+降级策略）"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\unified_memory_api.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\ctr_adapter.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\changes\\MOD-KB-001\\ctr-implementation-matrix.md"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\ingest.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\triage.py"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "RspRecall Pydantic V2"
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "路径合规"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
    reason: "§6.1 定义四层集成+CTR-001~CTR-006跨层契约详细规范"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 12000
timeout_minutes: 45

acceptance_criteria:
  - "recall_and_format(query)→str——直接输出 `## 相关记忆 ///3` + `## 相关规则 ///3` + `## 风险提醒 ///2` + `## 相关 KO ///15` 四段Markdown"
  - "ctr_adapter.py 中 ctr_001_context_assembler() 注入后 context 长度≤6000 token"
  - "CTR-001~CTR-006 全部6条契约对应方法实现"
  - "blurry boundary 场景→error=ERROR_BOUNDARY_VIOLATION→无阻返回+手动分配Owner+log"
  - "ctr-implementation-matrix.md 包含全部6条CTR的实现状态——生产状态/接口位置/延迟/降级策略"

rollback_instructions: |
  1. git checkout -- src/zephyr/kb/unified_memory_api.py
  2. 删除 src/zephyr/kb/ctr_adapter.py
  3. 删除 ctr-implementation-matrix.md

depends_on: ["TASK-KB-0012"]
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
