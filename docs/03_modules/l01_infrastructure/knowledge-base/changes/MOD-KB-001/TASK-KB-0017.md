---
task_id: "TASK-KB-0017"
source_blueprint: "MOD-KB-001"
source_section: "§5.14 内容安全门禁(G3 Analyze阶段+Kimi K2.6+SAFE/CAUTION/UNSAFE三级+操纵性语言检测+高危分类增强)"

title: "内容安全门禁实现——G3 Analyze阶段Kimi K2.6安全审核(SAFE/CAUTION/UNSAFE)+操纵性语言正则+高危分类增强策略"
description: |
  在 G3 Analyze 阶段（质量分析完成后、G4 激活前）追加内容安全审核：(1)双重检测——①Kimi K2.6 结构化安全审核提示词：输入 KE body + category → 输出 SafetyVerdict(SAFE正常流转/CAUTION记录日志+quality_score-0.1推Owner通知/UNSAFE拒入库) + safety_reason；②4类操纵性语言正则预筛——
  模式1 绝对化否定 `本项目.*(不需要|不用|禁止|永远不)` HIGH→可能关闭安全约束，
  模式2 全面跳过 `跳过.*(所有|全部|任何).*(检查|测试|审计)` HIGH→可能关闭质量门禁，
  模式3 权限放宽 `(允许|可以).*(直接|不经).*(提交|部署|发布)` MEDIUM→可能绕过CI/CD，
  模式4 凭证硬编码 `(密码|token|key|secret).*=.*['\"][^'\"]+['\"]` EXTREME→密钥泄漏；
  (2)高危分类增强策略——A3(危险实现)KE→安全门禁MUST NOT被绕过；A4(已知漏洞)KE→CAUTION/UNSAFE→自动更新knowledge_dependencies标记所有受影响模块；A8(技术债务)KE→追加额外安全语义检查；A2(架构决策)KE→架构级安全影响评估。A3 A2 A4 三类 KE → 安全要求自动加强；(3)仅当 G3 Analyze 确认 KE 质量 OK 后才执行安全审核——防止在"质量不合格"的 KE 上浪费安全审核 Token。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\analyze.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\content_safety_gate.py"
    description: "新建——G3 Analyze追加安全审核：Kimi K2.6 prompt + 4类regex预筛 + SafetyVerdict(SAFE/CAUTION/UNSAFE)路由"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\content_safety_gate.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\analyze.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\ingest.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\triage.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "SafetyVerdict Pydantic V2 模型"
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "路径合规"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
    reason: "§5.14 G3阶段内容安全门禁——Kimi K2.6+4类操纵性语言regex+SAFE/CAUTION/UNSAFE三级+高危分类增强(A2/A3/A4/A8)"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 8000
timeout_minutes: 30

acceptance_criteria:
  - "content_safety_gate.py——Kimi K2.6 prompt输入(KE body + category)→输出SafetyVerdict(SAFE/CAUTION/UNSAFE)+safety_reason"
  - "4类正则预筛正确匹配：绝对化否定/全面跳过/权限放宽/凭证硬编码——对应HIGH/MEDIUM/EXTREME风险等级"
  - "SAFE→正常流转G4 / CAUTION→quality_score-0.1+ke_usage_log记录+推Owner通知 / UNSAFE→REJECTED不入库"
  - "高危分类增强：A3 MUST NOT绕过 / A4 CAUTION/UNSAFE→自动标记knowledge_dependencies受影响模块 / A2架构级评估 / A8额外检查"
  - "仅在G3 Analyze确认KE质量OK后才执行安全审核"
  - "analyze.py G3末尾追加调用 content_safety_gate.evaluate(ke_body, category)→SafetyVerdict"

rollback_instructions: |
  1. 删除 src/zephyr/kb/content_safety_gate.py
  2. git checkout -- src/zephyr/kb/analyze.py

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
