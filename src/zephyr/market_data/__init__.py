# [BLUEPRINT] MOD-MKT_DATA | (pending)
# [MODULE] zephyr.market_data
# [DOMAIN] D_MKT_DATA
# [DEPENDENCIES] zephyr.shared.contracts.market_data
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-MKT_DATA | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: NormalizedMarketData 契约
#   fields: 标准化行情数据契约（来自共享契约层）
#   code: zephyr.shared.contracts.market_data.NormalizedMarketData
# 层: 算法
# - id: A1
#   name_zh: ① 包入口再导出
#   name_en: zephyr.market_data.__init__
#   intro: 把共享契约里的标准化行情数据类型提为包级公开符号
#   desc: import + __all__ 导出 NormalizedMarketData，统一 D_MKT_DATA 域包级访问入口
#   inputs: I1
#   outputs: 包级符号 NormalizedMarketData
# 层: 输出
# - id: O1
#   name_zh: NormalizedMarketData 包级符号
#   name_en: NormalizedMarketData
#   intro: 域内各模块经包入口统一引用标准化行情数据契约
#   downstream: 无下游/内部使用（D_MKT_DATA 域内模块）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from zephyr.shared.contracts.market_data import NormalizedMarketData

__all__ = ["NormalizedMarketData"]

# NOTE(P1W16 2026-08-25): scaffold 注册器写入 eager import + 类名 append
# （#ARCH-228/235/238/241/245 同款 bug 复发），按各域包"纯模块名导出、
# 无导入无初始化逻辑"约定归一为模块名条目；NormalizedMarketData 既有导出行未动。
__all__.append("auction_data_manager")
