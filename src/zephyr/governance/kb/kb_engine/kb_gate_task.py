# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain_knowledge/knowledge_base/blueprint.md | §
# [MODULE] zephyr.governance.kb.kb_engine.kb_gate_task (re-export shim)
# [DOMAIN] D_GOV_KB
# [DEPENDENCIES] zephyr.governance.kb.kb_gate_task
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] re-export shim — 真源在 zephyr.governance.kb.kb_gate_task（SSoT 收敛 2026-07-06）
# [MODIFY-GUARD] 禁止在此文件定义新符号；变更请到真源 kb/kb_gate_task.py
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-DAT_kb_gate_task | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Re-export shim — 真源在 zephyr.governance.kb.kb_gate_task（SSoT 收敛 2026-07-06）。

本文件仅重新导出根目录 kb_gate_task.py 的符号以保证向后兼容。
真源：src/zephyr/governance/kb/kb_gate_task.py
"""
from zephyr.governance.kb.kb_gate_task import build_kb_gate_eval_task

__all__ = ["build_kb_gate_eval_task"]
