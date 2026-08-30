# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.orchestrator.quality.stability_guard
# [DOMAIN] D_ORCHESTRATOR
# [DEPENDENCIES] zephyr.orchestrator.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-039 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
API 稳定性守护（CT-STABILITY）——public API签名锁+breaking change检测。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: stability_guard.py
# 层: 算法
# - id: A1
#   name_zh: ① StabilityGuard
#   name_en: StabilityGuard
#   intro: class StabilityGuard 源码 L49-L55
#   desc: 公共方法（定义序）: lock_api, check_breaking；源码 L49-L55
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: StabilityGuard
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""


class StabilityGuard:
    def lock_api(self, module: str, exports: list[str]) -> dict:
        return {"module": module, "exports": exports, "locked": True}

    def check_breaking(self, old_exports: list[str], new_exports: list[str]) -> list[str]:
        removed = set(old_exports) - set(new_exports)
        return [f"BREAKING: {e} removed" for e in removed]
