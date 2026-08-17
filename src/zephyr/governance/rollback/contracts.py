# [BLUEPRINT] MOD-GOV_ROLLBACK | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] zephyr.governance.rollback.contracts
# [DOMAIN] D_INFRA_RECOVERY
# [DEPENDENCIES] zephyr.infrastructure.rollback.contracts (RollbackHandler)
# [CONSUMERS] zephyr.gov_audit.bridge
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] G-CT-002 Rollback 契约
# [MODIFY-GUARD] blueprint.md §4
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 桥接失败返回None
# [TESTS] tests/governance/audit/test_p0_i2_construction_order.py
# [A_module] module_id=MOD-GOV_ROLLBACK | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

rollback/contracts.py — G-CT-002 Rollback 契约（re-export）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 基础设施层 RollbackHandler 类 外部模块
#   fields: zephyr.infrastructure.rollback.contracts 定义的 G-CT-002 回滚契约处理器
#   code: zephyr.infrastructure.rollback.contracts.RollbackHandler L21
# 层: 算法
# - id: A1
#   name_zh: ① 契约 re-export 桥接
#   name_en: contracts (rollback 域桥接)
#   intro: 把基础设施层的回滚契约原样转口到 governance.rollback 域，统一引用入口
#   desc: from infrastructure.rollback.contracts import RollbackHandler + __all__ 导出；无任何运行逻辑；桥接失败返回 None（ERROR_CONTRACT）
#   inputs: I1
#   outputs: RollbackHandler 符号
#   invariant: G-CT-002 Rollback 契约
# 层: 输出
# - id: O1
#   name_zh: 回滚契约处理器
#   name_en: RollbackHandler
#   intro: 供治理审计桥按 G-CT-002 契约执行回滚的处理器符号
#   downstream: zephyr.gov_audit.bridge（[CONSUMERS]）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from zephyr.infrastructure.rollback.contracts import RollbackHandler  # noqa: F401

__all__ = ["RollbackHandler"]
