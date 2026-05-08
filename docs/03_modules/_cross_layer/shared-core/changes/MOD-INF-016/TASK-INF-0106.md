---
task_id: "TASK-INF-0106"
source_blueprint: "MOD-INF-016"
source_section: "蓝图 §4 Phase 14 + §12 盲点 B27, B33, B34"

title: "Phase 14 施工——AI 团队可控：宪法自愈(B27) + Multi-Agent编排(B33) + Skill注册表(B34)"
description: |
  实现 AI 团队的自我进化与协调基础设施。
  B27：AGENTS.md 是静态的——AI 无法把"犯错-学到"写回宪法。
  需实现：ConstitutionalAutoUpdate——从 SessionAuditTrail 提取 learning → 写回 AGENTS.md。
  B33：Multi-Agent 团队编排基座——Agent role 定义 + task dispatch + result merge。
  需实现：AgentCard Protocol（A2A v1.0 对齐）/ TaskDispatch / ResultMerge。
  B34：prompt_registry.py 在 context_engine/ 而非 shared/。
  需实现：shared/ PromptTemplate + SkillDefinition Pydantic 模型。
  专业对标：Claude Code CLAUDE.md / A2A v1.0 / PydanticAI Agent Skills。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
  - "D:\\ZephyrAlpha\\AGENTS.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\prompt_registry.py"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\constitutional_update.py"
    description: "ConstitutionalAutoUpdate——从 SessionAuditTrail 提取 learning → 写回 AGENTS.md"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\multi_agent.py"
    description: "Multi-Agent 编排——AgentCard / TaskDispatch / ResultMerge Protocol"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\skill_registry.py"
    description: "Skill 注册基座——PromptTemplate / SkillDefinition Pydantic 模型"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_constitutional_update.py"
    description: "单元测试——验证 learning 提取、AGENTS.md 安全写入"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_multi_agent.py"
    description: "单元测试——验证 AgentCard 序列化、dispatch 逻辑"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_skill_registry.py"
    description: "单元测试——验证 PromptTemplate/SkillDefinition 模型校验"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\constitutional_update.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\multi_agent.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\skill_registry.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\__init__.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_constitutional_update.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_multi_agent.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_skill_registry.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\SHARED-QUICKREF.yml"
forbidden_touch:
  - "D:\\ZephyrAlpha\\AGENTS.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\prompt_registry.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

applicable_rules:
  - module_id: "GOV-DOC-002"
    section: "§5.5"
    reason: "shared/ 准入规则——被 ≥2 个 L01 模块消费"
  - module_id: "PS-STD-001"
    section: "§9.4"
    reason: "AgentRole 枚举——multi_agent 需与 AgentRole 对齐"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
    reason: "本蓝图 §12——B27/B33/B34 盲点详情与专业对标"
  - file_path: "D:\\ZephyrAlpha\\AGENTS.md"
    reason: "宪法文件——B27 需安全地读写 AGENTS.md"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\prompt_registry.py"
    reason: "当前 prompt_registry——B34 需定义 shared/ 抽象基座"

assigned_model: "claude-opus-4.7"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 35000
timeout_minutes: 90

acceptance_criteria:
  - "constitutional_update.py: ConstitutionalAutoUpdate 类——extract_learnings() + propose_update() + apply_update()"
  - "constitutional_update.py: AGENTS.md 写入前 MUST 备份——backup_and_rollback 集成"
  - "multi_agent.py: AgentCard Protocol——agent_id / role / capabilities / endpoint（A2A v1.0 对齐）"
  - "multi_agent.py: TaskDispatch Protocol——assign() / status() / result()"
  - "multi_agent.py: ResultMerge Protocol——merge_strategy（vote/chain/consensus）"
  - "skill_registry.py: PromptTemplate 模型含 template_str / variables / version"
  - "skill_registry.py: SkillDefinition 模型含 skill_id / name / prompt_template / input_schema / output_schema"
  - "pytest tests/unit/test_constitutional_update.py -v 全部通过"
  - "pytest tests/unit/test_multi_agent.py -v 全部通过"
  - "pytest tests/unit/test_skill_registry.py -v 全部通过"
  - "SHARED-QUICKREF.yml 更新——新增 3 个模块入口"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\shared\constitutional_update.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\shared\multi_agent.py
  3. 删除 D:\ZephyrAlpha\src\zephyr\shared\skill_registry.py
  4. 删除 D:\ZephyrAlpha\tests\unit\test_constitutional_update.py
  5. 删除 D:\ZephyrAlpha\tests\unit\test_multi_agent.py
  6. 删除 D:\ZephyrAlpha\tests\unit\test_skill_registry.py
  7. 还原 __init__.py 对应导出
  8. 还原 SHARED-QUICKREF.yml 对应条目

depends_on: ["TASK-INF-0104"]
blocked_by: []

status: "done"

tags_fn:
  - "infra"
tags_ly: "cross_layer"
tags_md: "claude-opus-4.7"
tags_st: "active"
tags_mo:
  - "MOD-INF-016"

completed_gates: []
blocked_gates: {}

artifact_paths: []

audit_findings: []

ke_entries: []

ai_autonomy_level: "supervised"
autonomy_checklist: []
---
