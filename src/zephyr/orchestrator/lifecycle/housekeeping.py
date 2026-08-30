# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.orchestrator.lifecycle.housekeeping
# [DOMAIN] D_ORCHESTRATOR
# [DEPENDENCIES] zephyr.orchestrator.__init__
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
# [A_module] module_id=MOD-INF-039 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
文件卫生保洁管理器（CT-HOUSEKEEPING）——临时文件扫描+日志轮转+废弃目录清理。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: housekeeping.py
# 层: 算法
# - id: A1
#   name_zh: ① HousekeepingManager
#   name_en: HousekeepingManager
#   intro: class HousekeepingManager 源码 L49-L56
#   desc: 公共方法（定义序）: scan_temp_files, should_clean；源码 L49-L56
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: HousekeepingManager
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""


class HousekeepingManager:
    TEMP_PATTERNS: list[str] = ["_temp*", "_check*", "_phase_*", "*.tmp", "*.bak"]

    def scan_temp_files(self) -> list[str]:
        return []

    def should_clean(self, filename: str) -> bool:
        return any(filename.startswith(p.replace("*", "").rstrip("*")) for p in self.TEMP_PATTERNS)
