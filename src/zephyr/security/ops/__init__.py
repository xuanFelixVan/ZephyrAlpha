# [DOMAIN] D_SECURITY
# [A_module] module_id=MOD-SEC-ops | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-053 | docs/03_modules/MOD-INF-053/
# [MODULE] zephyr.security.ops
# [TTL] permanent
"""security.ops — 自治运维闭环子包（16号文 §4.3/§4.4）。

统一事件流消费 → 诊断 → auto_fix_engine 三通道判决管线（incident_pipeline，
MOD-INF-053）与自治运维成熟度 A-L0→A-L2 状态机（ops_maturity，MOD-INF-055）。
"""

from . import incident_pipeline, ops_maturity

__all__ = [
    "incident_pipeline",
    "ops_maturity",
]
