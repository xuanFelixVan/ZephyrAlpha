# [A_module] module_id=MOD-CMP-compliance | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L10-001 | docs/03_modules/_domain_compliance/blueprint.md
# [MODULE] zephyr.compliance
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] immutable_core
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""D_COMPLIANCE Compliance — 包标记（DM-291 迁移后）

全部合规实现已迁移至 zephyr.governance / zephyr.gov_audit 等 canonical 包。
本包仅保留真实子包骨架（audit_trail/bridges 等），不再 re-export 任何符号。
5.60.8 治本：原 PEP 562 lazy re-export 壳与顶层 re-export 文件已移除（全仓 0 消费者）。
"""

from __future__ import annotations

__all__: list[str] = []
