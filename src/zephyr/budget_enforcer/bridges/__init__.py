# [BLUEPRINT] MOD-INF-024 | 03_modules/l01_infrastructure/budget-enforcer/blueprint.md | §
"""
Budget Enforcer — MOD-INF-024

预算执行：Token/API配额 + 消耗限额 + 告警阈值.
"""
from . import alerts
from . import rbac_bridge

__all__ = ['alerts', 'rbac_bridge']


__version__ = "0.1.0"
__module_id__ = "MOD-INF-024"