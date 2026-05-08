---
task_id: "TASK-KB-0005"
source_blueprint: "MOD-KB-001"
source_section: "§3.6 KO→KE→KB 三级知识漏斗 + §3.10 KO存储格式 + §3.11 KB存储格式"

title: "KO→KE→KB 三级知识漏斗实现——KO存储格式落地 + KB YAML规则格式落地 + 漏斗升格阀值自动化"
description: |
  实现蓝图 §3.6 定义的 KO→KE→KB 三级知识漏斗：(1)§3.10 KO 存储格式——OBSERVED→PROMOTING→PROMOTED 4状态机 + 轻量Markdown模板 + docs/08_knowledge/ko/ 目录结构（observed/promoting/discarded）；(2)§3.11 KB 存储格式——ACTIVE/SUPERSEDED/RETIRED 3状态机 + YAML rule 定义 + MINOR自动合并 + 90d冷却机制 + docs/08_knowledge/kb/ 目录结构（active/superseded/retired）；(3)漏斗升格阀值自动化——≥3 KO同主题→触发 D0 四轮流水线聚合为KE；≥5 KE同领域→触发 KB 升格评审提示。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\kb_repo.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\triage.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

downstream_outputs:
  - path: "D:\ZephyrAlpha\src\zephyr\kb\kb_repo.py"
    description: "新建——KO 仓储：4状态机 + 晋升逻辑 + 同类聚合检测"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\kb_rule_repo.py"
    description: "新建——KB 规则仓储：从 YAML 加载+执行+状态管理"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\_ko_models.py"
    description: "新建——KnowledgeObservation Pydantic 模型"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\_kb_rule_models.py"
    description: "新建——KBRule Pydantic 模型"
  - path: "D:\\ZephyrAlpha\\docs\\08_knowledge\\ko\\"
    description: "新建目录结构——observed/promoting/discarded 三层"
  - path: "D:\\ZephyrAlpha\\docs\\08_knowledge\\kb\\"
    description: "新建目录结构——active/superseded/retired 三层"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\ko_repo.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\kb_rule_repo.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\_ko_models.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\_kb_rule_models.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\triage.py"
  - "D:\\ZephyrAlpha\\docs\\08_knowledge\\ko\\"
  - "D:\\ZephyrAlpha\\docs\\08_knowledge\\kb\\"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\ingest.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\activate.py"
  - "D:\\ZephyrAlpha\\docs\\08_knowledge\\track_*\\**\\*.md"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "新建文件路径合规"
  - module_id: "PS-STD-001"
    section: "§6.12"
    reason: "新建 .py 立即注册到 script_manifest.yaml"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
    reason: "§3.6/§3.10/§3.11 定义了 KO/KB 完整格式和漏斗机制"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 15000
timeout_minutes: 60

acceptance_criteria:
  - "ko_repo.py 实现 KO 4状态机——OBSERVED/PROMOTING/PROMOTED/DISCARDED"
  - "kb_rule_repo.py 实现 KB 3状态机——ACTIVE/SUPERSEDED/RETIRED"
  - "≥3 KO同主题→自动触发 D0 四轮流水线聚合（相似度>0.75+同类别）"
  - "≥5 KE同领域→自动生成 KB 升格评审提示推送Owner"
  - "KO Markdown 文件格式符合 §3.10 模板"
  - "KB YAML 文件格式符合 §3.11 模板"
  - "90d冷却机制：同类型KB建议被拒绝3次→30d冷却期"

rollback_instructions: |
  1. 删除 src/zephyr/kb/ko_repo.py, kb_rule_repo.py, _ko_models.py, _kb_rule_models.py
  2. 删除 docs/08_knowledge/ko/ 和 docs/08_knowledge/kb/ 目录
  3. git checkout -- src/zephyr/kb/triage.py（如有修改）

depends_on: ["TASK-KB-0003", "TASK-KB-0004"]
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
