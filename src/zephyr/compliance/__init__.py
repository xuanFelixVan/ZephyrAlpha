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
"""

D_COMPLIANCE Compliance — 包标记（DM-291 迁移后）

全部合规实现已迁移至 zephyr.governance / zephyr.gov_audit 等 canonical 包。
本包仅保留真实子包骨架（audit_trail/bridges 等），不再 re-export 任何符号。
5.60.8 治本：原 PEP 562 lazy re-export 壳与顶层 re-export 文件已移除（全仓 0 消费者）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包导入请求 import zephyr.compliance
#   fields: 仅触发包初始化，无任何运行时参数或数据输入
#   code: src/zephyr/compliance/__init__.py
# 层: 算法
# - id: A1
#   name_zh: ① 空包骨架声明
#   name_en: zephyr.compliance 包标记
#   intro: 合规实现已全部迁至zephyr.governance/gov_audit等canonical包，本包只留子包骨架不导出任何符号
#   desc: DM-291迁移后仅保留audit_trail/bridges等真实子包；5.60.8治本移除PEP 562 lazy re-export壳（全仓0消费者）；__all__=[]（L13-22）
#   inputs: I1
#   outputs: 空命名空间（无符号）
#   invariant: 不再re-export任何符号
# 层: 输出
# - id: O1
#   name_zh: 空导出列表 __all__=[]
#   name_en: __all__
#   intro: 不导出任何符号，调用方应直连canonical包（zephyr.governance等）
#   downstream: 无下游/内部使用
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

__all__: list[str] = []
