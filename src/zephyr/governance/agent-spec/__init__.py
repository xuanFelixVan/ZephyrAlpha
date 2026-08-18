# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §phase1-gate
# [MODULE] zephyr.governance.agent-spec
# [DOMAIN] D_GOVERNANCE
# [A_module] module_id=MOD-INF-019 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# Phase 1 gate marker (kebab-case dir). Implementation in zephyr.governance.context_governance.agent_spec.

"""agent-spec — Phase 1 gate marker 包（kebab-case 目录）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包导入
#   fields: import zephyr.governance.agent-spec
#   code: 模块级常量定义
# 层: 算法
# - id: A1
#   name_zh: 阶段标记声明
#   name_en: phase1_marker_declare
#   intro: 仅声明 AGENT_SPEC_PHASE1_MARKER；实现在 context_governance.agent_spec
# 层: 输出
# - id: O1
#   name_zh: 阶段门标记
#   name_en: phase1_marker
#   intro: AGENT_SPEC_PHASE1_MARKER = 'agent-spec-v1'
#   downstream: Phase 1 门禁检查
# [/ALGO_FLOW]
# 边: I1 --> A1 ; A1 --> O1
"""

AGENT_SPEC_PHASE1_MARKER = "agent-spec-v1"

__all__: list[str] = []
