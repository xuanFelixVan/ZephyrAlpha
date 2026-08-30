# [DOMAIN] D_SECURITY
# [A_module] module_id=MOD-SEC-ops | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-053 | docs/03_modules/MOD-INF-053/
# [MODULE] zephyr.security.ops
# [TTL] permanent
"""
security.ops — 自治运维闭环子包（16号文 §4.3/§4.4）。

统一事件流消费 → 诊断 → auto_fix_engine 三通道判决管线（incident_pipeline，
MOD-INF-053）、自治运维成熟度 A-L0→A-L2 状态机（ops_maturity，MOD-INF-055）
与修复模式挖掘 Learn 回写件（fix_pattern_miner，MOD-INF-055）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: __init__.py
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 fix_pattern_miner, incident_pipeline, ops_maturity（共 3 符号）
#   desc: __init__ import L0；__all__ 3 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（3 符号）
#   name_en: __all__
#   intro: fix_pattern_miner, incident_pipeline, ops_maturity
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from . import fix_pattern_miner, incident_pipeline, ops_maturity

__all__ = [
    "fix_pattern_miner",
    "incident_pipeline",
    "ops_maturity",
]
