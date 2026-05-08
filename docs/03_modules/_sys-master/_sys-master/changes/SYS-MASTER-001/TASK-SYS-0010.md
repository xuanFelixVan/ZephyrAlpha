---
task_id: "TASK-SYS-0010"
source_blueprint: "SYS-MASTER-001"
source_section: "§15 Vibe Coding 方法论 + §44 Vibe Coding 深度实践"

title: "Vibe Coding 三级指令(MUST/SHOULD/MAY) + 6项深度实践(provenance/multi-agent/context-recycling/prompt-AB/Git-workflow/AI-velocity)体系搭建"
description: |
  将 SYS-MASTER-001 §15 的 Vibe Coding 方法论与 §44 的深度实践工程化落地。
  §15: 三级指令体系——MUST（不可跳过，如 lock_files.py 协议）/ SHOULD（默认执行，可例外）/
  MAY（探索后择优固化为 SHOULD/MUST）。完整指令在 vibe-coding-rules.yaml 中声明。
  §44: 6 项深度实践——
  ① provenance tracking（每生成代码含 module_id/source_section/agent_session_id）
  ② multi-agent debate（≥2个不同模型辩论关键决策）
  ③ context recycling（跨 session 压缩上下文复用）
  ④ prompt A-B test（评估不同 prompt 效果）
  ⑤ Git workflow（规范 Git 操作流程）
  ⑥ AI velocity（测量 AI 产出速率）。
  本卡搭建 vibe_coding_enforcer.py + 对应6个 practice 实现。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\vibe_coding_enforcer.py"
    description: "§15 MUST/SHOULD/MAY 装饰器框架——运行时校验规则级别"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\provenance_tracker.py"
    description: "§44-① 溯源性追踪——自动嵌入 module_id/source_section/agent_session_id"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\agent_debate.py"
    description: "§44-② Multi-Agent 辩论——A/B model adjudication protocol"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\context_recycling.py"
    description: "§44-③ 跨 session 上下文复用引擎"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\vibe_coding_enforcer.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\provenance_tracker.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\agent_debate.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\context_recycling.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l0*\\**\\*.py"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"
    reason: "§15 MUST/SHOULD/MAY + §44 6项深度实践(provenance/multi-agent/recycling/ABtest/Git/velocity)"

assigned_model: "deepseek"
assigned_pipeline: "A/B hybrid"
pipeline_modules:
  - "M1"
  - "M2"
  - "M3"
estimated_tokens: 26000
timeout_minutes: 70

acceptance_criteria:
  - "vibe_coding_enforcer.py 实现 enforce(level: VibeRuleLevel)→检查当前操作是否符合 MUST/SHOULD/MAY 规约"
  - "provenance_tracker.py 生成代码时自动嵌入 __provenance__ dict——module_id/source_section/agent_session_id/generated_at"
  - "agent_debate.py A/B model 同时生成→差异对比→adjudicate(agree→输出/ disagree→human override)"
  - "context_recycling.py 跨 session context 压缩→存储→恢复"

rollback_instructions: |
  git rm src/zephyr/governance/vibe_coding_enforcer.py provenance_tracker.py agent_debate.py context_recycling.py
  从 script_manifest.yaml 移除注册

depends_on:
  - "TASK-SYS-0004"
blocked_by: []
status: "done"
tags_fn:
  - "methodology"
tags_ly: "cross_layer"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "SYS-MASTER-001"
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
