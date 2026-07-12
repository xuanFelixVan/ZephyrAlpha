# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.orchestrator.quality.stability_guard
# [DOMAIN] D_ORCHESTRATOR
# [DEPENDENCIES] zephyr.orchestrator.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ORC_stability_guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""API 稳定性守护（CT-STABILITY）——public API签名锁+breaking change检测。"""


class StabilityGuard:
    def lock_api(self, module: str, exports: list[str]) -> dict:
        return {"module": module, "exports": exports, "locked": True}

    def check_breaking(self, old_exports: list[str], new_exports: list[str]) -> list[str]:
        removed = set(old_exports) - set(new_exports)
        return [f"BREAKING: {e} removed" for e in removed]
