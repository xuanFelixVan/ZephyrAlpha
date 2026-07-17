# [A_module] module_id=MOD-UNK_cross_asset | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""cross_asset 包初始化。

治本（2026-07-17）：risk_manager.py 和 risk_manager_base.py 已删除（DM-295 迁移后遗留死代码），
原 `from .risk_manager import *` / `from .risk_manager_base import *` 为悬空 import，导致整个包不可导入。
cross_market_data_adapter/ 子包自包含，无需包级 re-export。
无人引用包级符号（rg 验证），故清理为空 __init__。
"""
