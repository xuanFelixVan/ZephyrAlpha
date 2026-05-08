---
task_id: "TASK-KB-0026"
source_blueprint: "MOD-KB-001"
source_section: "§9.5 KB规则执行引擎 + §9.6 知识溯源追踪 + §9.7 KE版本历史 + §9.8 依赖级联更新"

title: "KB规则执行引擎 + 溯源追踪 + KE版本历史 + 依赖级联——规则推断→溯源图→增量演进→跨KE回传"
description: |
  实现蓝图 §9.5-§9.8 定义的演化回路四层：(1)§9.5 YAML规则→代码抽取/kb_rule_executor.py→规则激活三阶段(分析+触发+执行)——分析KE识别 需要干预的规则 + trigger 条件评估 + execute 动作应用——规则分级软/硬；(2)§9.6 知识溯源追踪——get_provenance_chain(ke_id)→溯源链[N层次]从头到尾追溯(初始来源→中间版本→最终版本) + provenance_dashboard() 合规审计留痕——任何已KE必须能追溯到源文档；(3)§9.7 KE版本历史——ke_version_history 表——auto B_ON_UPDATE→Diff记录(old_value/new_value/field_name/timestamp/triggered_by)→飞书推送+FrontMatter头部⚡stale属性+diff对比；(4)§9.8 依赖级联更新——依赖关系图谱→Target KE changed→BFS从target KE出发→检查所有 D->depend on target KE的KE→推 Owner update或dep 标记stale。
priority: "P2"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\kb_rule_repo.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\kb_repo.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\kb_rule_executor.py"
    description: "新建——load_rule→analyze_KE→trigger_check→execute_action→三阶段执行"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\knowledge_provenance.py"
    description: "新建——get_provenance_chain()→溯源链[N层] + provenance_dashboard()"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\ke_version_history.py"
    description: "新建——diff KE_to_diff→diff签名→push iceberg→飞书通知 + verify_history()"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\dependency_cascade.py"
    description: "新建——BFS从Target出发→沿 depends_on (下行) BFS→标记stale每1km(depth)"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\kb_repo.py"
    description: "追加 ke_version_history 表 schema"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\kb_rule_executor.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\knowledge_provenance.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\ke_version_history.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\dependency_cascade.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\kb_repo.py"
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
    reason: "§9.5-§9.8 定义了规则执行+溯源追踪+版本历史+依赖级联四层演化机制"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 12000
timeout_minutes: 45

acceptance_criteria:
  - "kb_rule_executor.py 三阶段——Analyze→Trigger→Execute——返回值 (changed:bool + reason:str)"
  - "get_provenance_chain(ke_id)→List[ProvenanceLevel]——包含src/version/author/timestamp字段 + 合规审计留痕"
  - "ke_version_history 表——UPDATE knowledge_entries→自动触发插入——diff id+old_value/new_value"
  - "ke_version_history 推送飞书 Messenger payload 含旧新值对比"
  - "BFS级联检测——max_depth=3→depth>3→WARN + 请求 manual override"

rollback_instructions: |
  1. 删除 src/zephyr/kb/kb_rule_executor.py, knowledge_provenance.py, ke_version_history.py, dependency_cascade.py
  2. git checkout -- src/zephyr/kb/kb_repo.py
  3. DROP TABLE IF EXISTS ke_version_history

depends_on: ["TASK-KB-0021"]
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
