---
task_id: "TASK-KB-0037"
source_blueprint: "MOD-KB-001"
source_section: "全蓝图盲点追踪表(#2/#4/#5/#8/#10/#18/#19/#21/#22/#23/#26/#27/#28/#30/#31/#36/#37/#40)"

title: "18盲点逐一关闭——每个盲点产生可验证的代码/文档交付 + 交叉验证RAG覆盖率>0.70"
description: |
  关闭蓝图全部18个盲点——逐盲点验证、编码、回归測試：(1)盲点#2(冷启动KE)→TASK-KB-0010 bootstrap.py 验证完成；(2)盲点#4(KO→KE→KB漏斗触发频率)→TASK-KB-0005——验证漏斗自动化触发 ≥3 KO t+ D0 trigger；
  (3)盲点#5(检索自动修复) →TASK-KB-0029 Self-RAG 自动fix logic——检测→返回5criteria[recall/precision/novelty/contradiction/coverage] → auto→推送 result+
  (4)盲点#8(Token预算+限制) → Len(cascade)=TASK-KB-0027 token_throttle.py 实现Leaky Bucket+budget to stay within C4 allow pkg；
  (5)盲点#10(专家反馈差异大)→ implement agree≥0.80 formula→average out—/proceed( ) ；#18(审计末态 lost)→ activation_log→TASK-KB-0026 kb_state_log backfill→补 audit ACTIVATE INDX；... 
  所有盲点逐一验证：(a)盲点编号→状态(OPEN/CLOSED)→closed指代码存在+test pass+KE coverage>0.70；(b)若closed不足→push new subtask→自动创建` TASK-BP-XXXX`追加；(c)报告 closure_report.md→ 每个盲点'状态/关闭方法/验证结果/依赖TASK'。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\**\\*.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_*.py"
  - "D:\\ZephyrAlpha\\tests\\e2e\\test_blueprint_to_recall.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\changes\\MOD-KB-001\\blindspot-closure-report.md"
    description: "新建——18盲点全量关闭报告——逐盲点标注状态/关闭方法/验证结果/依赖TASK-KB-NNNN"
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\changes\\MOD-KB-001\\blindspot-coverage-audit.md"
    description: "新建——盲点交叉覆盖——每个盲点列出所属 category/section 和对应的KE#（当KE≥10可覆盖时）"

allowed_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\changes\\MOD-KB-001\\blindspot-closure-report.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\changes\\MOD-KB-001\\blindspot-coverage-audit.md"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\**\\*.py"

applicable_rules:
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "路径合规"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
    reason: "全蓝图18盲点分布汇总——需要逐点闭环编程/验证/测试"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 12000
timeout_minutes: 45

acceptance_criteria:
  - "blindspot-closure-report.md 列出全部18盲点编号的——状态( CLOSED / OPEN → WIP→depends_on TASK-KB-NNNN )"
  - "每个 CLOSED 盲点有对应的 KE（至少 1 条 category 覆盖该盲点领域）→测试 5 queries→ recall@10 CR>0.70"
  - "若open→有对应的 sub-TASK 文件存在路径 markers"
  - "盲点横向覆盖率——盲点的 category 树≥10→80%以下仍需work(补KE)"
  - "文档末尾展示 closure_summary_table——×18 rows ×6 columns(status/method/ke_count/cr%/dep_task/tester)"

rollback_instructions: |
  1. 删除 blindspot-closure-report.md, blindspot-coverage-audit.md
  2. 若有新建的TASK-BP-文件——删除

depends_on: ["TASK-KB-0024", "TASK-KB-0033"]
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
