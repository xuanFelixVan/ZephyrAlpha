# [BLUEPRINT] MOD-INF-016 | (auto-injected by S4 reconciler) | §
# [A_module] module_id=MOD-EXE_risk | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# ARCH-GOV-SHIM-001 阶段1：删除5个零消费者 shim，仅保留 risk_limits（1消费者）
from .risk_limits import RiskLimits

__all__ = [
    "RiskLimits",
    "risk_limits",
]
