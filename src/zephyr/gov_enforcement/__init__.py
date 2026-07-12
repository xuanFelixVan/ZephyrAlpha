# [BLUEPRINT] D-GOV-ENFORCEMENT | docs/03_modules/_domain_governance/blueprint.md
# [MODULE] zephyr.gov_enforcement
# [DOMAIN] D_GOV_ENFORCEMENT
# [A_module] module_id=D-GOV-ENFORCEMENT | layer=domain | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""gov_enforcement package — 执行治理域（D_GOV_ENFORCEMENT）

域拆分 Phase 2 物理迁移目标包（ARCH-CAP-002 容量治理）：
  - behavioral_admission/ — 行为准入门禁（批次1 已迁移）
  - rule_bridge/          — 规则桥接（批次3 已迁移）
  - commit_gates/         — 提交门禁（批次5 已迁移）
  - rule_enforcement/     — 规则执行（批次9 已迁移）
"""
