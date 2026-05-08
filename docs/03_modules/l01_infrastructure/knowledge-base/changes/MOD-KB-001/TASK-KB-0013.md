---
task_id: "TASK-KB-0013"
source_blueprint: "MOD-KB-001"
source_section: "§5.8 四模型审计流水线 + §5.8.1 范式边界缓解(#31/#37)"

title: "四模型审计流水线实现——GLM→Kimi→Qwen→Opus 全自动触发 + 跨模型盲区缓解 + prompt自引用侵蚀控制"
description: |
  实现蓝图 §5.8 定义的四模型审计流水线：(1)实现四阶段审计链——[GLM-5.1 全景扫描]识别缺口/分类正确性/KE-ID连续性→[Kimi K2.6 根因深挖]验证准确性/矛盾检测/关联图谱→[Qwen 3.6 Plus 落地执行]去重/格式化/索引构建/图谱更新→[Opus 4.7 终局裁决]元评审/质量评估/矛盾裁决/最终收口；(2)§5.8.1A 跨模型一致性过度检测——compute_cross_model_agreement() 四模型全票HIGH+理由embedding cosine>0.85→AGREEMENT_ANOMALY→quality_score×0.85；(3)§5.8.1B 代码实际状态覆盖审计——verify_against_codebase() KE声称内容vs pyproject.toml/justfile 实际状态→MISMATCH→quality_score×0.5+推Owner；(4)§5.8.1C prompt自引用侵蚀控制——审计prompt引用KE限定extraction_generation≤1 + 每季"prompt审计的审计" + prompt文本锁定到 src/zephyr/kb/prompts/ 目录Git管理。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\analyze.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\activate.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\kb_repo.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\audit_pipeline.py"
    description: "新建——四模型审计流水线实现：GLM/Kimi/Qwen/Opus 四阶段 + aggregate_verdict()"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\analyze.py"
    description: "追加 compute_cross_model_agreement() + verify_against_codebase() 两个缓解函数"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\prompts\\"
    description: "新建目录——存放审计prompt的Markdown文件（Git管理）"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\audit_pipeline.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\analyze.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\prompts\\"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\ingest.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\triage.py"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "ModelVerdict/CrossModelVerdict/CodeMatchVerdict Pydantic V2 模型"
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "路径合规"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
    reason: "§5.8 四模型审计 + §5.8.1 范式边界缓解——包含完整伪代码"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 15000
timeout_minutes: 60

acceptance_criteria:
  - "audit_pipeline.py 实现四阶段审计链——每阶段返回 ModelVerdict(verdict, confidence, reasons)"
  - "GLM阶段检查 KE-ID 连续性和分类正确性"
  - "Kimi阶段检查语义矛盾——与已有 KE 做 Cross-Encoder pair 比较"
  - "Qwen阶段执行去重+索引构建"
  - "Opus阶段做元评审——audit the auditors"
  - "compute_cross_model_agreement() 四模型全票HIGH+cosine>0.85→AGREEMENT_ANOMALY→quality_score×0.85"
  - "verify_against_codebase() 对比 pyproject.toml 实际 ruff 版本 vs KE 声明的版本"
  - "审计 prompt 文件路径为 src/zephyr/kb/prompts/*.md——Git可追踪变更"

rollback_instructions: |
  1. 删除 src/zephyr/kb/audit_pipeline.py, src/zephyr/kb/prompts/ 目录
  2. git checkout -- src/zephyr/kb/analyze.py
  3. git checkout -- src/zephyr/kb/activate.py（如有联动修改）

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
