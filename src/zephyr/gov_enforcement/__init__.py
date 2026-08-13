# [BLUEPRINT] MOD-GOV_ENFORCEMENT | docs/03_modules/_domain_governance/blueprint.md
# [MODULE] zephyr.gov_enforcement
# [DOMAIN] D_GOV_ENFORCEMENT
# [A_module] module_id=MOD-GOV_ENFORCEMENT | layer=domain | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

gov_enforcement package — 执行治理域（D_GOV_ENFORCEMENT）

域拆分 Phase 2 物理迁移目标包（ARCH-CAP-002 容量治理）：
  - behavioral_admission/ — 行为准入门禁（批次1 已迁移）
  - rule_bridge/          — 规则桥接（批次3 已迁移）
  - commit_gates/         — 提交门禁（批次5 已迁移）
  - rule_enforcement/     — 规则执行（批次9 已迁移）

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 执行治理域子包源码
#   fields: behavioral_admission / rule_bridge / commit_gates / rule_enforcement 四个子包目录
#   code: src/zephyr/gov_enforcement/（ARCH-CAP-002 域拆分 Phase 2 迁移目标包）
# 层: 算法
# - id: A1
#   name_zh: ① 域命名空间声明
#   name_en: zephyr.gov_enforcement（包 docstring）
#   intro: 纯包标记——只声明执行治理域命名空间和子包分组，不导出任何符号
#   desc: docstring L6-13 记录四个子包迁移状态；__all__ 为空列表 L15，无任何运行逻辑
#   inputs: I1
#   outputs: 空命名空间包对象
#   invariant: __all__=[] 不做显式导出
# 层: 输出
# - id: O1
#   name_zh: gov_enforcement 包命名空间
#   name_en: zephyr.gov_enforcement
#   intro: 供域内子模块以 zephyr.gov_enforcement.<sub> 形式被 import 的挂载点
#   downstream: 域内全部子模块（behavioral_admission / rule_bridge / commit_gates / rule_enforcement）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

__all__: list[str] = []
