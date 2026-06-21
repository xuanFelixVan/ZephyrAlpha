# [A_module] module_id=MOD-PRT_strategy_engine | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
"""Re-export wrapper: strategy_engine has migrated to zephyr.portfolio_core.core.strategy_engine"""
from zephyr.governance.strategy_engine import *  # noqa: F401,F403
__all__ = ['*']
