# [BLUEPRINT] MOD-INF-005 | scripts/governance/d6_security/price_cage/__init__.py | §
# [MODULE] scripts.governance.d6_security.price_cage
# [DOMAIN] D_GOV_SCRIPTS
# [TTL] permanent
# auto-created
"""裁定#535「unknown_reject 武装核证」观察窗工具子包。

FOLDER-CAPACITY-HARD-LIMIT 逃生通道：d6_security 平铺超限，裁定#535 两件
（供数采样器+武装核证判官）迁入本子目录。

- price_cage_supply_sampler: 交易时段三重新鲜度采样，证据追加 price_cage_supply.jsonl
- price_cage_unknown_reject_judge: 5 交易日逐日逐窗机械核证，PASS/FAIL/FAIL-BLOCKED
"""

__all__ = [
    "price_cage_supply_sampler",
    "price_cage_unknown_reject_judge",
]
