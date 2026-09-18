# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_intake
# [MODULE] zephyr.ai_layer.intake
# [DOMAIN] D_GOVERNANCE
# [TTL] permanent
"""intake — AI 层 L2 收集段（原材料库）工程包：入库闸 / 卡库 / 查重 / 事件 / KPI 五件。

设计真源：``docs/_working/ai_layer_vision/L2_intake_library/DESIGN.md``。
生熟分离红线：本包只服务 PostgreSQL ``ai_intake`` schema（生食库），产线代码禁 import。
"""

__all__: list[str] = ["card_store", "dedup", "gate", "intake_events", "kpi"]
